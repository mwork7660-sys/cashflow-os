from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Amount(BaseModel):
    amount: int

class Bank:
    def __init__(self):
        self.transactions = []

    def income(self, amount: int):
        self.transactions.append(amount)

    def expense(self, amount: int):
        self.transactions.append(-amount)

    def balance(self) -> int:
        return sum(self.transactions)

    def summary(self):
        income = 0
        expense = 0
        for t in self.transactions:
            if t > 0:
                income += t
            else:
                expense += -t
        return {"income": income, "expense": expense, "balance": income - expense}

bank = Bank()

@app.post("/income")
def add_income(data: Amount):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    bank.income(data.amount)
    return bank.summary()

@app.post("/expense")
def add_expense(data: Amount):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    bank.expense(data.amount)
    return bank.summary()

@app.get("/transactions")
def transactions():
    return {"transactions": bank.transactions}

@app.get("/summary")
def summary():
    return bank.summary()

@app.post("/reset")
def reset():
    bank.transactions.clear()
    return {"message": "reset done", "transactions": bank.transactions}
