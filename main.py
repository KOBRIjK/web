from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import random

app = FastAPI()

# Модель входных данных
class Transaction(BaseModel):
    client_id: str
    transaction_id: str
    amount: float
    mcc_code: int
    date: str
    card_type: str  # "debit" или "credit"

class AnalysisRequest(BaseModel):
    transactions: List[Transaction]

# Модель выходных данных
class Recommendation(BaseModel):
    service: str
    description: str
    priority: int  # 1-5 (1 - самое важное)

class AnalysisResponse(BaseModel):
    client_id: str
    recommendations: List[Recommendation]

# База знаний MCC кодов и соответствующих услуг
mcc_to_service = {
    5812: ("Кредитная карта «Премиум»", "Кешбэк 5% на развлечения и рестораны"),
    4111: ("Автокредит", "0% годовых на покупку автомобиля"),
    5411: ("Сберегательный счет", "Доходность 8% годовых"),
    5960: ("Страховой полис", "Скидка 15% на путешествия"),
    5998: ("Корпоративный счет", "Бесплатное обслуживание для бизнеса"),
}

# Алгоритм анализа
def analyze_transactions(transactions: List[Transaction]) -> List[Recommendation]:
    recommendations = []
    transaction_counts = {}
    total_spend = 0

    for tx in transactions:
        total_spend += tx.amount
        mcc = tx.mcc_code
        if mcc in transaction_counts:
            transaction_counts[mcc] += 1
        else:
            transaction_counts[mcc] = 1

    # Рекомендации по MCC
    for mcc, count in transaction_counts.items():
        if count > 3 and mcc in mcc_to_service:
            service, desc = mcc_to_service[mcc]
            recommendations.append(Recommendation(
                service=service,
                description=desc,
                priority=5
            ))
    
    # Рекомендации по типу карты
    credit_usage = sum(1 for tx in transactions if tx.card_type == "credit")
    if credit_usage > 5:
        recommendations.append(Recommendation(
            service="Лимит увеличения",
            description="Увеличение кредитного лимита на 30%",
            priority=4
        ))
    
    # Рекомендации по сумме
    if total_spend > 50000:
        recommendations.append(Recommendation(
            service="Инвестиционный счет",
            description="Управляемые инвестиции с доходностью до 12%",
            priority=3
        ))
    
    # Удаление дубликатов
    seen = set()
    unique_recs = []
    for rec in recommendations:
        if (rec.service, rec.description) not in seen:
            seen.add((rec.service, rec.description))
            unique_recs.append(rec)
    
    # Сортировка по приоритету
    unique_recs.sort(key=lambda x: -x.priority)
    return unique_recs[:3]  # Максимум 3 рекомендации

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    if not request.transactions:
        raise HTTPException(status_code=400, detail="Нет транзакций")
    
    client_id = request.transactions[0].client_id
    recommendations = analyze_transactions(request.transactions)
    
    return AnalysisResponse(
        client_id=client_id,
        recommendations=recommendations
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)