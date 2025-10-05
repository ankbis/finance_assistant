from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
from app.schemas.holdings import StockHoldingCreate, StockHoldingUpdate
from app.db.crud import (
    create_stock_holding,
    get_user_stock_holdings,
    update_stock_holding,
    delete_stock_holding,
)
from typing import List

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/holdings/stocks", response_class=HTMLResponse)
async def stock_holdings_page(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    holdings = get_user_stock_holdings(db, current_user["id"])
    return templates.TemplateResponse(
        "stock_holdings.html",
        {"request": request, "holdings": holdings}
    )

@router.post("/holdings/stocks")
async def add_stock_holding(
    holding: StockHoldingCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_stock_holding(db, holding, current_user["id"])

@router.put("/holdings/stocks/{holding_id}")
async def update_holding(
    holding_id: str,
    holding: StockHoldingUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated = update_stock_holding(db, holding_id, holding, current_user["id"])
    if not updated:
        raise HTTPException(status_code=404, detail="Holding not found")
    return updated

@router.delete("/holdings/stocks/{holding_id}")
async def remove_holding(
    holding_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = delete_stock_holding(db, holding_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Holding not found")
    return {"message": "Holding deleted successfully"}