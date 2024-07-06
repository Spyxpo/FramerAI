from flask import (
    Flask,
    request,
    jsonify,
    render_template,
)
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BertForSequenceClassification,
    BertTokenizer,
)
from diffusers import StableDiffusionPipeline
import torch
from sklearn.preprocessing import LabelEncoder
import os
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

if not os.path.exists("static"):
    os.makedirs("static")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

chat_model_name = "microsoft/DialoGPT-medium"
chat_model = AutoModelForCausalLM.from_pretrained(chat_model_name).to(device)
chat_tokenizer = AutoTokenizer.from_pretrained(chat_model_name)


intent_model = BertForSequenceClassification.from_pretrained("fine_tuned_bert").to(
    device
)
intent_tokenizer = BertTokenizer.from_pretrained("fine_tuned_bert")


intents = ["generate image", "chat"]
encoder = LabelEncoder()
encoder.fit(intents)


model_id = "CompVis/stable-diffusion-v1-4"
image_pipe = StableDiffusionPipeline.from_pretrained(model_id).to(device)


def generate_image(prompt):
    image_path = f"static/{secure_filename(prompt)}.png"
    image = image_pipe(prompt).images[0]
    image.save(image_path)
    return image_path


def generate_chat_response(prompt, chat_history_ids=None):
    new_input_ids = chat_tokenizer.encode(
        prompt + chat_tokenizer.eos_token, return_tensors="pt"
    ).to(device)
    bot_input_ids = (
        torch.cat([chat_history_ids, new_input_ids], dim=-1)
        if chat_history_ids is not None
        else new_input_ids
    )
    chat_history_ids = chat_model.generate(
        bot_input_ids, max_length=1000, pad_token_id=chat_tokenizer.eos_token_id
    )
    response = chat_tokenizer.decode(
        chat_history_ids[:, bot_input_ids.shape[-1] :][0], skip_special_tokens=True
    )
    return response, chat_history_ids


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/message", methods=["POST"])
def handle_message():
    data = request.json
    user_input = data.get("message", "").strip()

    logging.debug(f"User input: {user_input}")

    if not user_input:
        return jsonify({"response": "Please provide a valid input."})

    intent = classify_intent(user_input)
    logging.debug(f"Detected intent: {intent}")

    if intent == "generate image":
        prompt = user_input.lower().replace("generate image", "").strip()
        logging.debug(f"Image generation prompt: {prompt}")
        if prompt:
            image_path = generate_image(prompt)
            logging.debug(f"Generated image path: {image_path}")
            return jsonify(
                {
                    "response": f"Generated an image based on your prompt. <a href='/{image_path}' target='_blank'>View Image</a>"
                }
            )
        else:
            return jsonify(
                {"response": "Please provide a prompt for the image generation."}
            )

    else:
        logging.debug(f"Chat prompt: {user_input}")
        response, _ = generate_chat_response(user_input)
        logging.debug(f"Chat response: {response}")
        return jsonify({"response": response})


def classify_intent(user_input):
    user_input = user_input.lower().strip()
    inputs = intent_tokenizer(
        user_input, return_tensors="pt", padding=True, truncation=True, max_length=512
    ).to(device)
    outputs = intent_model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    logging.debug(f"Model predictions: {predictions}")
    intent_idx = torch.argmax(predictions, dim=-1).item()
    logging.debug(f"Predicted intent index: {intent_idx}")
    intent = encoder.inverse_transform([intent_idx])[0]
    logging.debug(f"Decoded intent: {intent}")
    return intent


if __name__ == "__main__":
    app.run(debug=True)
