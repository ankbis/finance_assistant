from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None

class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None

class ItemOut(BaseModel):
    id: str
    name: str
    description: str | None

    model_config = {"from_attributes": True}
