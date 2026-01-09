# inh-consulting-mbo-v2

This is the V2 Streamlit app for the INH Consulting MBO model, rebuilt cleanly alongside V1 for faster interaction and clearer separation of concerns while preserving the original financial logic.

## Architecture

Inputs → Model → UI

- Inputs live in `data/base_case.json` and are loaded into the typed `Assumptions` schema.
- The deterministic calculation core in `model/run_model.py` consumes `Assumptions` and produces a `ModelResult`.
- The Streamlit UI renders inputs and outputs without embedding any business logic.

## Persistence

JSON is the single source of truth. The UI loads `data/base_case.json` on startup and writes updated assumptions back to JSON on each change. Defaults exist only in code and are serialized to JSON for the initial base case.

## Run locally

```bash
streamlit run app.py
```

Note: This is V2, built cleanly alongside V1.
