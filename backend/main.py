import os
import sqlite3
from datetime import datetime
from typing import Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# OBSERVAÇÃO: Ajuste aqui caso sua pasta 'model' esteja fora de 'backend'
# Se 'model' estiver na raiz do projeto (fora de backend), mude para: os.path.join(BASE_DIR, "..", "model")
MODEL_DIR = os.path.join(BASE_DIR, "model") 
DB_PATH = os.path.join(BASE_DIR, "predictions.db")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# Carregamento seguro dos arquivos PKL
try:
    model = joblib.load(os.path.join(MODEL_DIR, "car_price_model.pkl"))
    model_columns = joblib.load(os.path.join(MODEL_DIR, "model_columns.pkl"))
    metadata = joblib.load(os.path.join(MODEL_DIR, "metadata.pkl"))
except Exception as e:
    print(f"ERRO CRÍTICO AO CARREGAR OS MODELOS: {e}")
    # Tentativa de fallback subindo um nível caso a estrutura mude no deploy
    ALT_MODEL_DIR = os.path.join(BASE_DIR, "..", "model")
    model = joblib.load(os.path.join(ALT_MODEL_DIR, "car_price_model.pkl"))
    model_columns = joblib.load(os.path.join(ALT_MODEL_DIR, "model_columns.pkl"))
    metadata = joblib.load(os.path.join(ALT_MODEL_DIR, "metadata.pkl"))

app = FastAPI(title="Car Price Predictor API")

# Middleware de CORS 100% liberado para receber a Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionInput(BaseModel):
    year: int = Field(..., ge=1990, le=2025)
    km_driven: int = Field(..., ge=0)
    brand: str
    fuel: str
    seller_type: str
    transmission: str
    owner: str

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            km_driven INTEGER,
            brand TEXT,
            fuel TEXT,
            seller_type TEXT,
            transmission TEXT,
            owner TEXT,
            predicted_price REAL,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def preprocess_input(data: PredictionInput) -> pd.DataFrame:
    input_dict = {col: 0 for col in model_columns}
    input_dict["year"] = data.year
    input_dict["km_driven"] = data.km_driven

    for prefix, value in [
        ("brand", data.brand),
        ("fuel", data.fuel),
        ("seller_type", data.seller_type),
        ("transmission", data.transmission),
        ("owner", data.owner),
    ]:
        col = f"{prefix}_{value}"
        if col in input_dict:
            input_dict[col] = 1

    return pd.DataFrame([input_dict], columns=model_columns)

def save_prediction(data: PredictionInput, price: float) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        """
        INSERT INTO predictions
        (year, km_driven, brand, fuel, seller_type, transmission, owner, predicted_price, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.year,
            data.km_driven,
            data.brand,
            data.fuel,
            data.seller_type,
            data.transmission,
            data.owner,
            price,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home():
    return {"message": "API de predição de preço de veículos funcionando de forma pública"}

@app.get("/metadata")
def get_metadata():
    return metadata

@app.post("/predict")
def predict(data: PredictionInput):
    df = preprocess_input(data)
    predicted = float(model.predict(df)[0])
    predicted = max(predicted, 0)
    prediction_id = save_prediction(data, predicted)

    return {
        "id": prediction_id,
        "predicted_price": round(predicted, 2),
    }

@app.get("/predictions")
def list_predictions(limit: Optional[int] = 50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM predictions ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/predictions/{prediction_id}")
def get_prediction(prediction_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM predictions WHERE id = ?",
        (prediction_id,),
    ).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Predição não encontrada")

    return dict(row)

if os.path.isdir(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# CORREÇÃO CRÍTICA PARA O RAILWAY FUNCIONAR:
if __name__ == "__main__":
    import uvicorn
    # Pega a porta injetada pelo Railway automaticamente, se não houver usa a 8080
    port = int(os.environ.get("PORT", 8080))
    # Host DEVE ser 0.0.0.0 para aceitar requisições de fora (da Vercel)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)