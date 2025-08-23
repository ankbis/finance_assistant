from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.api.router.items import router as items_router

app = FastAPI(title=settings.APP_NAME)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", include_in_schema=False)
def root():
    return {"message": f"{settings.APP_NAME} is running", "docs": "/docs", "health": "/health"}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return RedirectResponse(url="https://fastapi.tiangolo.com/img/favicon.png")

app.include_router(items_router)
