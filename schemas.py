from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)

class ItemOut(BaseModel):
    id: str
    name: str

class Config:
    from_attributes = True