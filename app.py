from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    url_for,
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


ai_processing = False


def generate_image(prompt):
    global ai_processing
    ai_processing = True

    image_filename = f"{secure_filename(prompt)}.png"
    image_path = os.path.join("static", image_filename)
    image = image_pipe(prompt).images[0]
    image.save(image_path)

    ai_processing = False
    return image_filename


def generate_chat_response(prompt, chat_history_ids=None):
    global ai_processing
    ai_processing = True

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

    ai_processing = False
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
        if prompt:
            image_filename = generate_image(prompt)
            image_url = url_for("static", filename=image_filename)
            return jsonify(
                {
                    "response": f"Generated an image based on your prompt. <img src='{image_url}' alt='Generated Image' style='max-width: 100%;'>"
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


@app.route("/stop", methods=["POST"])
def stop():
    global ai_processing
    if ai_processing:
        ai_processing = False
        return jsonify({"response": "AI process stopped."})
    return jsonify({"response": "No AI process to stop."})


def classify_intent(user_input):
    user_input = user_input.lower().strip()
    if "generate image" in user_input:
        return "generate image"
    elif user_input.startswith("chat"):
        return "chat"

    inputs = intent_tokenizer(
        user_input, return_tensors="pt", padding=True, truncation=True, max_length=512
    ).to(device)
    outputs = intent_model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    intent_idx = torch.argmax(predictions, dim=-1).item()
    intent = encoder.inverse_transform([intent_idx])[0]
    return intent


if __name__ == "__main__":
    app.run(debug=True)
