import random
from faker import Faker
from datetime import datetime, timedelta
import json

fake = Faker()

def generate_transactions(num=10):
    transactions = []
    client_id = fake.uuid4()
    
    for _ in range(num):
        transaction = {
            "client_id": client_id,
            "transaction_id": str(fake.uuid4()),
            "amount": round(random.uniform(50, 5000), 2),
            "mcc_code": random.choice([5812, 4111, 5411, 5960, 5998, 5542]),
            "date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            "card_type": random.choices(["debit", "credit"], weights=[0.7, 0.3])[0]
        }
        transactions.append(transaction)
    
    return transactions

if __name__ == "__main__":
    data = generate_transactions(20)
    with open("test_data.json", "w") as f:
        json.dump({"transactions": data}, f, indent=2)