# Image Ideation

## Setup

1. Create and activate a virtual environment with `uv`.
2. Install dependencies:

```bash
uv sync --extra dev
```

3. Copy `.env.example` to `.env` and fill in your OpenAI API key.
4. Run the Streamlit app:

```bash
uv run streamlit run app.py
```

## Environment variables

- `OPENAI_API_KEY`
- `OPENAI_TEXT_MODEL` optional
- `OPENAI_IMAGE_MODEL` optional

## Notes

The app shell is in place. The upload and preview workflow will be added next.
