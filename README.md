Project entrypoint

Run the chatbot from the project root using the module flag so package imports resolve correctly:

```bash
python -m app.main
```

Or, using the virtual environment created for the project:

```bash
.venv/bin/python -m app.main
```

Notes:
- Do not run the `app/main.py` file directly with `python app/main.py` — use `-m` so Python executes the package context and `from app.graph import build_graph` resolves.

