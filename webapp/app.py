import os
import pandas as pd
import random
from flask import Flask, request, jsonify, render_template
from generator import SyntheticDataGenerator
from datetime import datetime
import json

app = Flask(__name__)

# Configuration
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Global generator instance
generator = SyntheticDataGenerator()

# Helper to load data
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
    if "model_name" in data:
        generator.model_name = data["model_name"]
    if "temperature" in data:
        generator.temperature = float(data["temperature"])
    if "num_scenarios" in data:
        generator.num_scenarios = int(data["num_scenarios"])
    if "num_variants" in data:
        generator.num_variants = int(data["num_variants"])
    if "sentiments" in data:
        generator.sentiments = data["sentiments"]
    if "sentiment_probs" in data:
        generator.sentiment_probs = data["sentiment_probs"]
    if "user_speech" in data:
        generator.user_speech = data["user_speech"]
    if "user_speech_probs" in data:
        generator.user_speech_probs = data["user_speech_probs"]
    
    return jsonify({"status": "success", "config": data})

@app.route("/api/load_model", methods=["POST"])
def load_model():
    try:
        generator.load_model()
        return jsonify({"status": "success", "message": "Model loaded successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/intents", methods=["GET", "POST"])
def handle_intents():
    intent_path = os.path.join(DATA_DIR, "collections_intents.csv")
    if request.method == "POST":
        data = request.json
        df = pd.DataFrame(data)
        df.to_csv(intent_path, index=False)
        generator.intent_df = df
        return jsonify({"status": "success"})
    else:
        if os.path.exists(intent_path):
            df = pd.read_csv(intent_path)
            return jsonify(df.to_dict(orient="records"))
        return jsonify([])

@app.route("/api/seed", methods=["GET", "POST"])
def handle_seed():
    seed_path = os.path.join(DATA_DIR, "seed_scenarios.csv")
    if request.method == "POST":
        data = request.json
        df = pd.DataFrame(data)
        df.to_csv(seed_path, index=False)
        generator.seed_df = df
        return jsonify({"status": "success"})
    else:
        if os.path.exists(seed_path):
            df = pd.read_csv(seed_path)
            return jsonify(df.to_dict(orient="records"))
        return jsonify([])

@app.route("/api/generate/scenario", methods=["POST"])
def generate_single_scenario():
    data = request.json
    intent = data.get("intent")
    description = data.get("description")
    try:
        scenarios = generator.generate_scenarios(intent, description)
        return jsonify({"status": "success", "scenarios": scenarios})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/generate/all_scenarios", methods=["POST"])
def generate_all_scenarios():
    try:
        if generator.intent_df is None or generator.seed_df is None:
            return jsonify({"status": "error", "message": "Intents or Seed data not loaded"}), 400
        
        all_new_scenarios = []
        for idx, row in generator.intent_df.iterrows():
            intent = row['intent']
            description = row['description']
            scs = generator.generate_scenarios(intent, description)
            for s in scs:
                all_new_scenarios.append({"intent": intent, "scenario": s})
        
        # Save to a new file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(DATA_DIR, f"scenarios_generated_{timestamp}.csv")
        pd.DataFrame(all_new_scenarios).to_csv(output_path, index=False)
        
        return jsonify({"status": "success", "file": output_path, "count": len(all_new_scenarios)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/generate/conversations", methods=["POST"])
def generate_conversations():
    data = request.json
    name_folder = data.get("name_folder", "default")
    scenario_file = data.get("scenario_file") # Optional: specific scenario file to use
    
    try:
        if scenario_file and os.path.exists(scenario_file):
            scenarios_df = pd.read_csv(scenario_file)
        else:
            # Look for the latest generated scenarios file
            scenario_files = [f for f in os.listdir(DATA_DIR) if f.startswith("scenarios_generated_")]
            if not scenario_files:
                return jsonify({"status": "error", "message": "No scenarios found. Generate scenarios first."}), 400
            latest_file = sorted(scenario_files)[-1]
            scenarios_df = pd.read_csv(os.path.join(DATA_DIR, latest_file))

        all_convos = []
        for idx, row in scenarios_df.iterrows():
            intent = row['intent']
            scenario = row['scenario']
            
            for _ in range(generator.num_variants):
                sentiment = random.choices(generator.sentiments, weights=generator.sentiment_probs, k=1)[0]
                speech = random.choices(generator.user_speech, weights=generator.user_speech_probs, k=1)[0]
                
                if intent == "FALLBACK":
                    convo = generator.generate_oos_conversation(scenario, sentiment, speech)
                else:
                    convo = generator.generate_conversation(scenario, intent, sentiment, speech)
                
                all_convos.append({
                    "intent": intent,
                    "scenario": scenario,
                    "conversation_text": convo,
                    "sentiment": sentiment,
                    "user_speech_type": speech
                })

        # Track conversations in folder name_folder_parameter + tweaked_datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{name_folder}_{timestamp}"
        output_dir = os.path.join(DATA_DIR, folder_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, "conversations.csv")
        pd.DataFrame(all_convos).to_csv(output_file, index=False)
        
        return jsonify({"status": "success", "folder": output_dir, "count": len(all_convos)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
