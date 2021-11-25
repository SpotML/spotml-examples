# 1. Preparing the datasets

from datasets import load_dataset

raw_datasets = load_dataset("imdb")

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")


def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)


tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)

small_train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(1000))
small_eval_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(1000))
full_train_dataset = tokenized_datasets["train"]
full_eval_dataset = tokenized_datasets["test"]

# 2. Fine-tuning in PyTorch with the Trainer API

from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=2)

from transformers import TrainingArguments

checkpoint_directory = "test_trainer"
training_args = TrainingArguments(output_dir=checkpoint_directory, num_train_epochs=2, save_strategy="epoch")

from transformers import Trainer
import os

trainer = Trainer(
    model=model, args=training_args, train_dataset=small_train_dataset, eval_dataset=small_eval_dataset
)

# Load the last checkpoint in configured output_dir "test_trainer".
if any(File.endswith(".pt") for File in os.listdir(checkpoint_directory)):
    trainer.train(resume_from_checkpoint=True)
else:
    trainer.train()

import numpy as np
from datasets import load_metric

metric = load_metric("accuracy")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train_dataset,
    eval_dataset=small_eval_dataset,
    compute_metrics=compute_metrics,
)
trainer.evaluate()
