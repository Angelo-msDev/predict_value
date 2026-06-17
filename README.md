# Preditor de Preço de Veículos

Sistema completo de predição utilizando Machine Learning (Regressão) para estimar o preço de venda de carros usados.

**Base de dados:** [Car Details from Car Dekho](https://www.kaggle.com/datasets/nehalbirla/vehicle-dataset-from-cardekho) — 4.340 registros com informações de veículos.

## Estrutura do Projeto

```
predict_value/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── train_model.py       # Script de treinamento
│   ├── requirements.txt
│   └── model/
│       ├── CAR DETAILS FROM CAR DEKHO.csv
│       ├── car_price_model.pkl
│       ├── model_columns.pkl
│       └── metadata.pkl
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
└── notebooks/
    ├── etapa1_analise_descritiva.ipynb
    └── etapa2_experimentos_modelos.ipynb
```

## Como Executar

### 1. Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Treinar o modelo (opcional — modelos já exportados)

```bash
python train_model.py
```

### 3. Iniciar a API

```bash
uvicorn main:app --reload
```

A API estará em: http://127.0.0.1:8000

Documentação interativa: http://127.0.0.1:8000/docs

### 4. Abrir o frontend

Opção A — via API: http://127.0.0.1:8000/app/

Opção B — abrir `frontend/index.html` diretamente no navegador

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Status da API |
| GET | `/metadata` | Opções dos campos categóricos |
| POST | `/predict` | Realiza predição e salva no banco |
| GET | `/predictions` | Lista predições salvas |
| GET | `/predictions/{id}` | Consulta predição por ID |

## Modelo Escolhido

**Random Forest Regressor** — melhor desempenho nos experimentos (30 runs):

- R² médio: ~0.65
- MAE médio: ~147.725

## Notebooks (Google Colab)

Faça upload dos notebooks em `notebooks/` junto com o CSV para executar no Colab:

1. `etapa1_analise_descritiva.ipynb` — Análise exploratória
2. `etapa2_experimentos_modelos.ipynb` — Experimentos e exportação do modelo

## Tecnologias

- Python, Pandas, Scikit-learn
- FastAPI + Uvicorn
- SQLite (histórico de predições)
- HTML/CSS/JavaScript
