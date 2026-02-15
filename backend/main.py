from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User, Transaction

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Cashflow OS (Users + DB) running 🚀"}

# 1) Create a user
@app.post("/users")
def create_user(name: str, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created", "user_id": user.id, "name": user.name}

# 2) Add transaction for a user
@app.post("/users/{user_id}/transaction")
def create_transaction_for_user(
    user_id: int,
    type: str,
    category: str,
    amount: float,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    t = Transaction(type=type, category=category, amount=amount, user_id=user_id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"message": "Transaction saved", "id": t.id, "user_id": user_id}

# 3) Get user transactions
@app.get("/users/{user_id}/transactions")
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

# 4) Get summary for a user
@app.get("/users/{user_id}/summary")
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()

    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")

    return {
        "user_id": user_id,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }
