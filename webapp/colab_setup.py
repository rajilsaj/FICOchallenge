import os
import subprocess
import sys

def setup_colab():
    print("🚀 Starting Google Colab Setup for Synthetic Data Generator...")

    # 1. Install Unsloth and dependencies
    print("📦 Installing Unsloth and core dependencies (this takes a few minutes)...")
    commands = [
        "pip install --no-deps \"unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git\"",
        "pip install --no-deps \"xformers<0.0.29\" \"trl<0.9.0\" peft accelerate bitsandbytes",
        "pip install flask pandas flask-cors"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        subprocess.check_call(cmd, shell=True)

    # 2. Create Directory Structure
    print("📁 Creating directory structure...")
    os.makedirs("data", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)

    # 3. Write Files
    print("✍️ Writing application files...")

    # generator.py
    with open("generator.py", "w") as f:
        f.write('''import os
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
            filtered_seed = self.seed_df

        examples = f"EXAMPLE:\\n**Input**: Generate 3 realistic and varied collections outreach scenarios where the resulting customer intent is {intent}.\\n**Output**:\\n"
        
        n_samples = min(3, len(filtered_seed))
        random_sample = filtered_seed.sample(n=n_samples)
        for i in range(n_samples):
            examples += f"{i+1}. {random_sample['scenario'].iloc[i]}\\n"

        system_prompt = (
            "You are a scenario generation engine for outbound banking chatbot conversations."
            " The bank initiates contact with the customer about collection on a past-due balance."
            " Your task is to generate realistic and logically consistent scenarios in which this outbound contact results in the customer taking a specific action or forming a final intent."
            " Each scenario should describe the relevant situation, context, and reasoning that leads from the outbound topic to the customer's concluding intent.\\n"
            "Output strictly as a numbered list with each scenario on a new line. Do not include any commentary or explanation.\\n\\n"
            f"{examples}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate {self.num_scenarios} realistic and varied scenarios where the bank reaches out to the customer about a collection and the resulting customer intent is {intent}. The intent is defined here: {description}."}
        ]

        inputs = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to(self.device)
        output_ids = self.model.generate(input_ids=inputs, max_new_tokens=1024, temperature=self.temperature, use_cache=True)
        output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        marker = ".assistant"
        if marker in output:
            output = output[output.find(marker) + len(marker):]

        scenarios = []
        for line in output.split("\\n"):
            line = line.strip()
            if re.match(r"^\\d+\\.", line):
                scenario_text = line.split(".", 1)[1].strip()
                if scenario_text:
                    scenarios.append(scenario_text)
        return scenarios[:self.num_scenarios]

    def generate_conversation(self, scenario, intent, sentiment, user_speech):
        if self.model is None:
            raise ValueError("Model not loaded")

        all_intents = self.intent_df["intent"].tolist()
        system_prompt = (
            "You are a conversation generation engine for outbound banking chatbot interactions.\\n"
            "Generate natural, multi-turn dialogues between a helpful, professional banking chatbot and a realistic customer. "
            f"The customer messages should express the sentiment '{sentiment}' and speech type '{user_speech}'.\\n"
            f"The conversation must avoid overlapping with any other intents. Specifically, avoid: {', '.join([i for i in all_intents if i != intent])}\\n"
            "Alternate between chatbot and customer messages, prefacing each line with 'Bot:' or 'User:'. Do not include summaries."
        )

        user_prompt = (
            f"Customer Intent: {intent}\\n"
            f"Customer Sentiment: {sentiment}\\n"
            f"Customer Speech Type: {user_speech}\\n"
            f"Scenario: {scenario}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        output_ids = self.model.generate(
            **self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt").to(self.device),
            max_new_tokens=1024, temperature=self.temperature
        )
        output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        marker = ".assistant"
        if marker in output:
            output = output[output.find(marker) + len(marker):]
        
        return output.strip()

    def generate_oos_conversation(self, scenario, sentiment, user_speech):
        if self.model is None: raise ValueError("Model not loaded")
        system_prompt = "You are a conversation engine. The customer makes an out-of-scope request."
        user_prompt = f"OUT_OF_SCOPE. Sentiment: {sentiment}, Speech: {user_speech}, Scenario: {scenario}"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        output_ids = self.model.generate(**self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt").to(self.device), max_new_tokens=1024)
        output = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return output.strip()
''')

    # app.py (adapted for Colab)
    with open("app.py", "w") as f:
        f.write('''import os
import pandas as pd
import random
from flask import Flask, request, jsonify, render_template
from generator import SyntheticDataGenerator
from datetime import datetime
import json

app = Flask(__name__)
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
generator = SyntheticDataGenerator()

def load_default_data():
    intent_path = os.path.join(DATA_DIR, "collections_intents.csv")
    seed_path = os.path.join(DATA_DIR, "seed_scenarios.csv")
    if os.path.exists(intent_path) and os.path.exists(seed_path):
        intent_df = pd.read_csv(intent_path)
        seed_df = pd.read_csv(seed_path)
        generator.set_data(intent_df, seed_df)
        return True
    return False

@app.route("/")
def index():
    load_default_data()
    return render_template("index.html", 
                           model_name=generator.model_name,
                           config=json.dumps({
                               "temperature": generator.temperature,
                               "num_scenarios": generator.num_scenarios,
                               "num_variants": generator.num_variants,
                               "sentiments": generator.sentiments,
                               "sentiment_probs": generator.sentiment_probs,
                               "user_speech": generator.user_speech,
                               "user_speech_probs": generator.user_speech_probs
                           }))

@app.route("/api/config", methods=["POST"])
def update_config():
    data = request.json
    for key in data:
        if hasattr(generator, key):
            setattr(generator, key, data[key])
    return jsonify({"status": "success"})

@app.route("/api/load_model", methods=["POST"])
def load_model():
    try:
        generator.load_model()
        return jsonify({"status": "success", "message": "Model loaded successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/intents", methods=["GET", "POST"])
def handle_intents():
    path = os.path.join(DATA_DIR, "collections_intents.csv")
    if request.method == "POST":
        pd.DataFrame(request.json).to_csv(path, index=False)
        generator.intent_df = pd.DataFrame(request.json)
        return jsonify({"status": "success"})
    return jsonify(pd.read_csv(path).to_dict(orient="records") if os.path.exists(path) else [])

@app.route("/api/seed", methods=["GET", "POST"])
def handle_seed():
    path = os.path.join(DATA_DIR, "seed_scenarios.csv")
    if request.method == "POST":
        pd.DataFrame(request.json).to_csv(path, index=False)
        generator.seed_df = pd.DataFrame(request.json)
        return jsonify({"status": "success"})
    return jsonify(pd.read_csv(path).to_dict(orient="records") if os.path.exists(path) else [])

@app.route("/api/generate/scenario", methods=["POST"])
def generate_single_scenario():
    try:
        scs = generator.generate_scenarios(request.json["intent"], request.json["description"])
        return jsonify({"status": "success", "scenarios": scs})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/generate/all_scenarios", methods=["POST"])
def generate_all_scenarios():
    try:
        res = []
        for _, row in generator.intent_df.iterrows():
            scs = generator.generate_scenarios(row['intent'], row['description'])
            for s in scs: res.append({"intent": row['intent'], "scenario": s})
        path = os.path.join(DATA_DIR, f"scenarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        pd.DataFrame(res).to_csv(path, index=False)
        return jsonify({"status": "success", "file": path})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/generate/conversations", methods=["POST"])
def generate_conversations():
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.startswith("scenarios_")]
        if not files: return jsonify({"status": "error", "message": "No scenarios found"}), 400
        df = pd.read_csv(os.path.join(DATA_DIR, sorted(files)[-1]))
        convs = []
        for _, row in df.iterrows():
            for _ in range(generator.num_variants):
                sent = random.choices(generator.sentiments, weights=generator.sentiment_probs)[0]
                sp = random.choices(generator.user_speech, weights=generator.user_speech_probs)[0]
                c = generator.generate_conversation(row['scenario'], row['intent'], sent, sp)
                convs.append({"intent": row['intent'], "scenario": row['scenario'], "text": c, "sentiment": sent})
        out_dir = os.path.join(DATA_DIR, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)
        pd.DataFrame(convs).to_csv(os.path.join(out_dir, "convs.csv"), index=False)
        return jsonify({"status": "success", "folder": out_dir})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
''')

    # templates/index.html
    # (Simplified for writing)
    with open("templates/index.html", "w") as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Synthetic Data Gen (Colab)</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://cdn.jsdelivr.net/npm/vue@2.6.14/dist/vue.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <div id="app" class="container">
        <h1>Synthetic Data Generator</h1>
        <section class="card">
            <h2>Model</h2>
            <input type="text" v-model="model_name">
            <button @click="loadModel" :disabled="loading">Load Model</button>
        </section>
        <section class="card">
            <h2>Schema</h2>
            <table class="data-table">
                <tr v-for="i in intents"><td><input v-model="i.intent"></td><td><input v-model="i.description"></td></tr>
            </table>
            <button @click="saveIntents">Save Schema</button>
        </section>
        <section class="card">
            <h2>Actions</h2>
            <button @click="generateAllScenarios" :disabled="loading" class="primary">1. Generate Scenarios</button>
            <button @click="generateConversations" :disabled="loading" class="secondary">2. Generate Conversations</button>
        </section>
        <div v-if="status" :class="status.type">{{ status.message }}</div>
        <div v-if="loading">Processing... (Check Colab logs)</div>
    </div>
    <script>
        new Vue({
            el: '#app',
            data: { model_name: 'unsloth/Meta-Llama-3.1-8B-Instruct', intents: [], loading: false, status: null },
            mounted() { axios.get('/api/intents').then(r => this.intents = r.data); },
            methods: {
                loadModel() { this.loading = true; axios.post('/api/load_model').then(r => { this.status = {type:'success', message:r.data.message}; this.loading=false; }); },
                saveIntents() { axios.post('/api/intents', this.intents).then(() => alert('Saved')); },
                generateAllScenarios() { this.loading=true; axios.post('/api/generate/all_scenarios').then(r => { this.status={type:'success', message:'Done: ' + r.data.file}; this.loading=false; }); },
                generateConversations() { this.loading=true; axios.post('/api/generate/conversations', {name_folder:'colab'}).then(r => { this.status={type:'success', message:'Done: ' + r.data.folder}; this.loading=false; }); }
            }
        });
    </script>
</body>
</html>''')

    # static/style.css
    with open("static/style.css", "w") as f:
        f.write('''body { font-family: sans-serif; background: #f4f7f6; padding: 20px; }
.container { max-width: 800px; margin: auto; }
.card { background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table td { border: 1px solid #eee; padding: 5px; }
button { padding: 10px; cursor: pointer; border: none; border-radius: 4px; background: #3498db; color: white; }
.primary { background: #2ecc71; } .secondary { background: #9b59b6; }
.success { color: green; padding: 10px; }''')

    # 4. Setup Initial Data
    print("📊 Setting up initial data...")
    import pandas as pd
    intents = [
        {"intent": "PAYMENT_ARRANGEMENT", "description": "Agrees to payment plan"},
        {"intent": "DISPUTE_BALANCE", "description": "Disputes amount"},
        {"intent": "HARDSHIP_REQUEST", "description": "Financial hardship"},
        {"intent": "FALLBACK", "description": "Out of scope"}
    ]
    pd.DataFrame(intents).to_csv("data/collections_intents.csv", index=False)
    
    seeds = [
        {"intent": "PAYMENT_ARRANGEMENT", "scenario": "New job, wants installments"},
        {"intent": "DISPUTE_BALANCE", "scenario": "Paid last week"},
        {"intent": "HARDSHIP_REQUEST", "scenario": "Medical emergency"},
        {"intent": "FALLBACK", "scenario": "Weather in London"}
    ]
    pd.DataFrame(seeds).to_csv("data/seed_scenarios.csv", index=False)

    print("✅ Setup Complete!")
    print("----------------------------------------------------------------")
    print("👉 TO RUN THE APP:")
    print("1. In a NEW CELL, run the following code to expose the server:")
    print("   from google.colab.output import serve_kernel_port_as_window")
    print("   serve_kernel_port_as_window(5000)")
    print("2. Then, run the app in this cell or another one:")
    print("   !python app.py")
    print("----------------------------------------------------------------")

if __name__ == "__main__":
    setup_colab()
