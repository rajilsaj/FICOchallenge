import time
import random

def generate_synthetic_data(intent, seed, temp, num):
    """
    Mocks the synthetic data generation step that normally uses Unsloth/Llama-3.1-8B.
    Note: To integrate the real notebook code, replace this function body with the
    Unsloth model loading, tokenizer, and generation code. Make sure to run this 
    asynchronously or in a worker queue if deploying to production.
    """
    time.sleep(2) # Simulate LLM generation delay
    
    scenarios = []
    base_texts = [
        "The customer is looking to {intent}.",
        "A user contacts support regarding {intent}.",
        "Customer inquiry about their {intent}.",
        "The user wants to know more about {intent}."
    ]
    
    for i in range(num):
        # Slightly randomized texts to make it look realistic
        text = random.choice(base_texts).format(intent=intent.replace("_", " "))
        text += f" Case #{random.randint(1000, 9999)}."
        scenarios.append({
            "id": i + 1,
            "scenario": text,
            "intent": intent,
            "confidence_score": round(random.uniform(0.7, 0.99), 2)
        })
        
    return scenarios


def prepare_data(split_ratio):
    """
    Mocks the data preparation step where the dataset is split.
    Note: To integrate real code, replace with Pandas operations to read generated
    CSV, clean, and split the data into train/test sets, then save them.
    """
    time.sleep(1) # Simulate data processing
    
    total_samples = 5000 # hypothetical large dataset
    train_pct = float(split_ratio) / 100.0
    test_pct = 1.0 - train_pct
    
    train_samples = int(total_samples * train_pct)
    test_samples = total_samples - train_samples
    
    return {
        "status": "success",
        "total_samples": total_samples,
        "train_samples": train_samples,
        "test_samples": test_samples,
        "distributions": {
            "balance_inquiry": int(total_samples * 0.4),
            "payment_issue": int(total_samples * 0.3),
            "fraud_report": int(total_samples * 0.2),
            "fallback": int(total_samples * 0.1)
        }
    }


def train_classifier(model_type, epochs):
    """
    Mocks the fine-tuning of BERT/Qwen.
    Note: Replace with actual HuggingFace Trainer/unsloth code. Note that training
    in a synchronous web request will almost certainly timeout. Either use Celery/Redis
    or WebSockets for progress streaming.
    """
    # Simulate a longer delay for "training"
    time.sleep(3)
    
    return {
        "status": "completed",
        "model_type": model_type,
        "epochs_run": epochs,
        "final_loss": round(random.uniform(0.1, 0.3), 4),
        "accuracy": round(random.uniform(0.85, 0.98), 4),
        "message": f"{model_type.upper()} classifier fine-tuning finished successfully!"
    }


def classify_intent(text):
    """
    Mocks the inference of the trained model.
    Note: Replace with standard HuggingFace pipeline inference using the trained weights.
    """
    time.sleep(1) # Simulate inference delay
    
    intents = ["balance_inquiry", "payment_issue", "fraud_report", "fallback"]
    
    # Simple keyword matching for demo purposes
    text_lower = text.lower()
    predicted = "fallback"
    if "balance" in text_lower or "how much" in text_lower:
        predicted = "balance_inquiry"
    elif "pay" in text_lower or "bill" in text_lower:
        predicted = "payment_issue"
    elif "fraud" in text_lower or "stolen" in text_lower or "unauthorized" in text_lower:
        predicted = "fraud_report"
    else:
        # random chance to pick something or fallback
        if random.random() > 0.5:
            predicted = random.choice(intents[:-1])
            
    return {
        "input_text": text,
        "predicted_intent": predicted,
        "confidence": round(random.uniform(0.7, 0.99), 2)
    }
