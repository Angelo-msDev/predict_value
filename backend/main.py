from fastapi import FastAPI
import joblib
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model = joblib.load("model/car_price_model.pkl")
model_columns = joblib.load("model/model_columns.pkl")


def preprocess_input(data):
    input_dict = {col: 0 for col in model_columns}

    input_dict["year"] = data["year"]
    input_dict["km_driven"] = data["km_driven"]

    brand_col = f"brand_{data['brand']}"
    fuel_col = f"fuel_{data['fuel']}"
    seller_col = f"seller_type_{data['seller_type']}"
    trans_col = f"transmission_{data['transmission']}"
    owner_col = f"owner_{data['owner']}"

    for col in [brand_col, fuel_col, seller_col, trans_col, owner_col]:
        if col in input_dict:
            input_dict[col] = 1

    return pd.DataFrame([input_dict])


@app.get("/")
def home():
    return {"message": "API funcionando"}



@app.post("/predict")
def predict(data: dict):
    year = data["year"]
    km = data["km_driven"]

    price = 100000 - (2025 - year) * 3000 - (km * 0.2)

    if price < 20000:
        price = 20000

    return {
        "predicted_price": price
    }