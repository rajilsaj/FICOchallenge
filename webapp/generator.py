import os
import pandas as pd
import random
import re
import torch
from datetime import datetime
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template

class SyntheticDataGenerator:
    def __init__(self, model_name="unsloth/Meta-Llama-3.1-8B-Instruct", device="cuda"):
        self.model_name = model_name
        self.device = device if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.temperature = 0.7
        self.num_scenarios = 5
        self.num_variants = 5
        self.sentiments = ["angry", "confused", "neutral"]
        self.sentiment_probs = [0.15, 0.3, 0.55]
        self.user_speech = ["casual", "professional", "slang", "typos"]
        self.user_speech_probs = [0.5, 0.2, 0.1, 0.2]
        self.intent_df = None
        self.seed_df = None

    def load_model(self, model_name=None):
        if model_name:
            self.model_name = model_name
        print(f"Loading model: {self.model_name} on {self.device}")
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(self.model_name)
        self.tokenizer = get_chat_template(
            self.tokenizer,
            chat_template="llama-3.1"
        )
        FastLanguageModel.for_inference(self.model)

    def set_data(self, intent_df, seed_df):
        self.intent_df = intent_df
        self.seed_df = seed_df

    def generate_scenarios(self, intent, description):
        if self.model is None:
            raise ValueError("Model not loaded")
        
        filtered_seed = self.seed_df[self.seed_df["intent"] == intent]
        if filtered_seed.empty:
            filtered_seed = self.seed_df # Fallback to any seed if none for intent

        examples = f"EXAMPLE:\n**Input**: Generate 3 realistic and varied collections outreach scenarios where the resulting customer intent is {intent}.\n**Output**:\n"
        
        n_samples = min(3, len(filtered_seed))
        random_sample = filtered_seed.sample(n=n_samples)
        for i in range(n_samples):
            examples += f"{i+1}. {random_sample['scenario'].iloc[i]}\n"

        system_prompt = (
            "You are a scenario generation engine for outbound banking chatbot conversations."
            " The bank initiates contact with the customer about collection on a past-due balance."
            " Your task is to generate realistic and logically consistent scenarios in which this outbound contact results in the customer taking a specific action or forming a final intent."
            " Each scenario should describe the relevant situation, context, and reasoning that leads from the outbound topic to the customer's concluding intent. The scenarios must reflect believable situations that could occur in real-world banking conversations, including appropriate motivations, financial circumstances, or customer behavior.\n"
            "Output strictly as a numbered list with each scenario on a new line. Do not include any commentary or explanation or additional lines.\n\n"
            f"{examples}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate {self.num_scenarios} realistic and varied scenarios where the bank reaches out to the customer about a collection and the resulting customer intent is {intent}. The intent is defined here: {description}."}
        ]

        inputs = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to(self.device)
        output_ids = self.model.generate(input_ids=inputs, max_new_tokens=1024, temperature=self.temperature, use_cache=True)
        output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        # Parse output
        marker = ".assistant"
        if marker in output:
            output = output[output.find(marker) + len(marker):]

        scenarios = []
        for line in output.split("\n"):
            line = line.strip()
            if re.match(r"^\d+\.", line):
                scenario_text = line.split(".", 1)[1].strip()
                if scenario_text:
                    scenarios.append(scenario_text)
        return scenarios[:self.num_scenarios]

    def generate_conversation(self, scenario, intent, sentiment, user_speech):
        if self.model is None:
            raise ValueError("Model not loaded")

        all_intents = self.intent_df["intent"].tolist()
        system_prompt = (
            "You are a conversation generation engine for outbound banking chatbot interactions. You simulate realistic conversations where the bank initiates contact with the customer about collections on a past-due balance.\n"
            "Generate natural, multi-turn dialogues between a helpful, professional banking chatbot and a realistic customer. "
            "The chatbot should initiate the conversation and stay focused on the context provided in the scenario. "
            f"The customer messages should express the sentiment '{sentiment}' and speech type '{user_speech}'. However, the customer messages should align with the provided scenario and intent '{intent}' above all else.\n"
            f"The conversation must avoid overlapping with any other intents. Specifically, avoid: {', '.join([i for i in all_intents if i != intent])}\n"
            "Avoid including any account numbers or Social Security numbers.\n"
            "The chatbot messages should consistently be professional and friendly regardless of the customer's tone.\n"
            "Alternate between chatbot and customer messages, prefacing each line with 'Bot:' or 'User:'. Do not include summaries, commentary, or headings — output only the dialogue."
        )

        user_prompt = (
            f"Customer Intent: {intent}\n"
            f"Customer Sentiment: {sentiment}\n"
            f"Customer Speech Type: {user_speech}\n"
            f"Scenario: {scenario}\n"
            f"Generate a realistic conversation."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        output_ids = self.model.generate(
            **self.tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(self.device),
            max_new_tokens=1024,
            temperature=self.temperature,
            top_p=0.95,
            top_k=128
        )
        output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        marker = ".assistant"
        if marker in output:
            output = output[output.find(marker) + len(marker):]
        
        return output.strip()

    def generate_oos_conversation(self, scenario, sentiment, user_speech):
        # Similar logic but for OOS
        if self.model is None:
            raise ValueError("Model not loaded")

        system_prompt = (
            "You are a conversation generation engine for outbound banking chatbot interactions. You simulate realistic conversations where the bank initiates contact with the customer about collections on a past-due balance and the customer makes an out-of-scope request in response.\n"
            "Generate natural, multi-turn dialogues between a helpful, professional banking chatbot and a customer. "
            "The chatbot should initiate the conversation and stay focused on the context provided in the scenario. "
            f"The customer messages should express the sentiment '{sentiment}' and speech type '{user_speech}'. However, the customer messages should align with the provided scenario above all else. The purpose of the scenario is to describe a customer that is making an out-of-scope request that the banking chatbot can't fulfill.\n"
            "The chatbot messages should consistently be professional and friendly regardless of the customer's tone.\n"
            "Alternate between chatbot and customer messages, prefacing each line with 'Bot:' or 'User:'. Do not include summaries, commentary, or headings — output only the dialogue."
        )

        user_prompt = (
            f"Customer Intent: OUT_OF_SCOPE\n"
            f"Customer Sentiment: {sentiment}\n"
            f"Customer Speech Type: {user_speech}\n"
            f"Scenario: {scenario}\n"
            f"Generate a realistic conversation."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        output_ids = self.model.generate(
            **self.tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(self.device),
            max_new_tokens=1024,
            temperature=self.temperature,
            top_p=0.95,
            top_k=128
        )
        output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        marker = ".assistant"
        if marker in output:
            output = output[output.find(marker) + len(marker):]
        
        return output.strip()
