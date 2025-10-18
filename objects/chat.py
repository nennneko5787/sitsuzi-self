from pydantic import BaseModel


class Color(BaseModel):
    r: int
    g: int
    b: int


class ChatResponse(BaseModel):
    yourName: str
    message: str
    color: Color


class ThreeSizes(BaseModel):
    b: int
    w: int
    h: int


class ChatResponseEx(ChatResponse):
    threeSizes: ThreeSizes
    weightKg: int
    heightCm: int
    age: int
    intimacyPercent: float
