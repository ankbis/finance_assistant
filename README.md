# FinanceAssistant
This respository contains code for virtual finanacial assistant developed using Python, FastAPI, Postgres, LLM, MCP etc.

## Local Dev
```bash
cp .env.sample .env # and fill DATABASE_URL (can be Neon or local)
export $(grep -v '^#' .env | xargs) # mac/linux
pip install -r requirements.txt
uvicorn app:app --reload
