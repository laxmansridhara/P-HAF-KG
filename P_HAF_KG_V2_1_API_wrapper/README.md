# P-HAF-KG V2.1 API wrapper

This is a thin REST API around the existing dissertation implementation.

It does NOT recreate the model.

It imports these functions from the real `src/predict_food.py`:

- `load_knowledge_base`
- `run_kg`
- `run_svm`
- `hybrid_decision`
- `personalised_decision`

## Install

From the dissertation project root:

```bash
python3 -m pip install -r /path/to/api_integration/requirements-api.txt
```

## Copy

Copy `api_server.py` into the dissertation project root.

Expected layout:

```text
Dissertation_Project_Starter/
├── api_server.py
├── src/
│   └── predict_food.py
├── data/
│   └── processed/
│       └── ingredient_allergen_knowledge_14.csv
└── models/
    └── svm_allergen/
        ├── tfidf_vectorizer.joblib
        └── svm_allergen_model.joblib
```

## Start

From the dissertation project root:

```bash
python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

Then test:

```text
http://127.0.0.1:8000/health
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Test prediction

```bash
curl -X POST http://127.0.0.1:8000/analyze-food   -H "Content-Type: application/json"   -d '{
    "ingredient_text": "wheat flour, milk powder, soy lecithin",
    "allergies": ["milk", "peanut"]
  }'
```

Expected decision:

```text
NOT SUITABLE
```

with milk appearing in the user-confirmed matches.

## Important

The API is a presentation/demo wrapper around the research implementation. It does not change the reported dissertation evaluation.

For a public deployment, replace the demo CORS policy with the exact frontend origin and add authentication.
