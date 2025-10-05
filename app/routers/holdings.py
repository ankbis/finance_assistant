from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.context import get_template_context
from app.schemas.holdings import StockHoldingCreate, StockHoldingUpdate
from app.db.crud.holdings import (
    create_stock_holding,
    get_user_stock_holdings,
    update_stock_holding,
    delete_stock_holding,
)
from app.db.crud.users import get_user_by_email
from typing import List

router = APIRouter(
    prefix="/holdings",
    tags=["holdings"]
)
templates = Jinja2Templates(directory="templates")

@router.get("/stocks", response_class=HTMLResponse, name="stock_holdings_page")
async def stock_holdings_page(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
        
    user = await get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    holdings = await get_user_stock_holdings(db, user.id)
    context = await get_template_context(request, db)
    context["holdings"] = holdings
    return templates.TemplateResponse("stock_holdings.html", context)

@router.post("/stocks", name="add_stock_holding")
async def add_stock_holding(
    holding: StockHoldingCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    user = await get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return await create_stock_holding(db, holding, user.id)

@router.put("/stocks/{holding_id}", name="edit_stock_holding")
async def update_holding(
    holding_id: str,
    holding: StockHoldingUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    user = await get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    updated = await update_stock_holding(db, holding_id, holding, user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Holding not found")
    return updated

@router.delete("/stocks/{holding_id}", name="delete_stock_holding")
async def remove_holding(
    holding_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    user = await get_user_by_email(db, current_user["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    success = await delete_stock_holding(db, holding_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Holding not found")
    return {"message": "Holding deleted successfully"}