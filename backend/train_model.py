"""
Script de treinamento do modelo de predição de preço de veículos.
Executa experimentos com múltiplos algoritmos (30 runs) e exporta o melhor modelo.
"""
import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "model", "CAR DETAILS FROM CAR DEKHO.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")


def load_and_preprocess():
    df = pd.read_csv(DATA_PATH)
    df = df.drop_duplicates()
    df = df.dropna()

    df = df[(df["selling_price"] > 0) & (df["year"] >= 1990) & (df["km_driven"] >= 0)]

    df["brand"] = df["name"].apply(lambda x: str(x).split()[0])
    df = df.drop("name", axis=1)

    df_encoded = pd.get_dummies(
        df,
        columns=["brand", "fuel", "seller_type", "transmission", "owner"],
        drop_first=False,
    )

    X = df_encoded.drop("selling_price", axis=1)
    y = df_encoded["selling_price"]

    metadata = {
        "brands": sorted(df["brand"].unique().tolist()),
        "fuels": sorted(df["fuel"].unique().tolist()),
        "seller_types": sorted(df["seller_type"].unique().tolist()),
        "transmissions": sorted(df["transmission"].unique().tolist()),
        "owners": sorted(df["owner"].unique().tolist()),
        "target": "selling_price",
        "features_numeric": ["year", "km_driven"],
        "features_categorical": ["brand", "fuel", "seller_type", "transmission", "owner"],
    }

    return X, y, list(X.columns), metadata


def run_experiments(X, y, n_runs=30):
    model_templates = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(random_state=42, max_depth=15),
        "Random Forest": RandomForestRegressor(
            n_estimators=100, random_state=42, n_jobs=-1
        ),
        "SVR": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("svr", SVR(kernel="rbf", C=100, epsilon=0.1)),
            ]
        ),
    }

    results = {name: {"mae": [], "r2": []} for name in model_templates}

    for seed in range(n_runs):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=seed
        )

        for name, model in model_templates.items():
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            results[name]["mae"].append(mean_absolute_error(y_test, pred))
            results[name]["r2"].append(r2_score(y_test, pred))

    summary = {}
    for name, metrics in results.items():
        summary[name] = {
            "mae_mean": float(np.mean(metrics["mae"])),
            "mae_std": float(np.std(metrics["mae"])),
            "r2_mean": float(np.mean(metrics["r2"])),
            "r2_std": float(np.std(metrics["r2"])),
        }

    best_name = max(summary, key=lambda k: summary[k]["r2_mean"])
    return summary, best_name, model_templates[best_name]


def train_and_export():
    X, y, columns, metadata = load_and_preprocess()
    summary, best_name, best_template = run_experiments(X, y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    best_template.fit(X_train, y_train)
    pred = best_template.predict(X_test)

    final_metrics = {
        "model": best_name,
        "mae": float(mean_absolute_error(y_test, pred)),
        "r2": float(r2_score(y_test, pred)),
        "experiments": summary,
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(best_template, os.path.join(MODEL_DIR, "car_price_model.pkl"))
    joblib.dump(columns, os.path.join(MODEL_DIR, "model_columns.pkl"))
    joblib.dump(metadata, os.path.join(MODEL_DIR, "metadata.pkl"))

    with open(os.path.join(MODEL_DIR, "experiment_results.json"), "w", encoding="utf-8") as f:
        json.dump(final_metrics, f, indent=2, ensure_ascii=False)

    print(f"Melhor modelo: {best_name}")
    print(f"MAE final: {final_metrics['mae']:.2f}")
    print(f"R2 final: {final_metrics['r2']:.4f}")
    print("\nResumo dos experimentos (30 runs):")
    for name, stats in summary.items():
        print(
            f"  {name}: R2={stats['r2_mean']:.4f} (+/- {stats['r2_std']:.4f}), "
            f"MAE={stats['mae_mean']:.2f} (+/- {stats['mae_std']:.2f})"
        )
    print(f"\nArquivos salvos em: {MODEL_DIR}")


if __name__ == "__main__":
    train_and_export()
