import os
import pandas as pd

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

intent_path = os.path.join(DATA_DIR, "collections_intents.csv")
seed_path = os.path.join(DATA_DIR, "seed_scenarios.csv")

if not os.path.exists(intent_path):
    intents = [
        {"intent": "PAYMENT_ARRANGEMENT", "description": "The customer agrees to a payment plan."},
        {"intent": "DISPUTE_BALANCE", "description": "The customer disputes the amount owed."},
        {"intent": "HARDSHIP_REQUEST", "description": "The customer requests assistance due to financial hardship."},
        {"intent": "FALLBACK", "description": "Out of scope request."}
    ]
    pd.DataFrame(intents).to_csv(intent_path, index=False)
    print(f"Created {intent_path}")

if not os.path.exists(seed_path):
    seeds = [
        {"intent": "PAYMENT_ARRANGEMENT", "scenario": "Customer lost their job but just got a new one and wants to pay in installments."},
        {"intent": "DISPUTE_BALANCE", "scenario": "Customer claims they already paid the bill last week via bank transfer."},
        {"intent": "HARDSHIP_REQUEST", "scenario": "Customer is facing medical emergency and cannot pay this month."},
        {"intent": "FALLBACK", "scenario": "Customer asks about the weather in London."}
    ]
    pd.DataFrame(seeds).to_csv(seed_path, index=False)
    print(f"Created {seed_path}")
