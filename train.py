import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from datasets import Dataset


df = pd.read_csv("intents.csv")
train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)


label_mapping = {"generate image": 0, "chat": 1}
train_df["label"] = train_df["label"].map(label_mapping)
val_df["label"] = val_df["label"].map(label_mapping)

train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)


train_dataset = train_dataset.map(tokenize_function, batched=True)
val_dataset = val_dataset.map(tokenize_function, batched=True)

train_dataset = train_dataset.rename_column("label", "labels")
val_dataset = val_dataset.rename_column("label", "labels")

train_dataset.set_format("torch")
val_dataset.set_format("torch")

model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)


training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    use_cpu=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

trainer.train()


model.save_pretrained("fine_tuned_bert")
tokenizer.save_pretrained("fine_tuned_bert")
