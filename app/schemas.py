from pydantic import BaseModel
from typing import List, Union
from datetime import datetime
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

class ChatInputType(BaseModel):
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]]
    # thread_id: str

class DestinationCreate(BaseModel):
    name: str

class DestinationResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True

class KnowledgeBaseCreate(BaseModel):
    content: str
    destination_id: int


class KnowledgeBaseResponse(BaseModel):
    id: int
    content: str
    destination_id: int
    created_at: datetime

    class Config:
        orm_mode = True