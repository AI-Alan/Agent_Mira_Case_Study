from pydantic import BaseModel

class Property(BaseModel):
    id: str
    title: str
    price: float
    location: str
    bedrooms: int
    image: str
