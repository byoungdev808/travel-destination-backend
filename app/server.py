from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from langchain_community.chat_models import ChatOpenAI
from app.react_agent import agent_executor
from langchain_openai import OpenAI
from langchain.agents import AgentExecutor, create_react_agent, initialize_agent
from langchain_core.tools import tool
from langchain import hub
from langchain.agents.agent_types import AgentType
from pydantic import BaseModel
from typing import Any
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.helper.destination import (
    create_destination,
    get_destinations,
    get_destination_by_id,
    update_destination,
    delete_destination,
)
from app.helper.knowledge_base import (
    create_knowledge_base,
    get_knowledge_bases_for_destination,
    get_knowledge_base_by_id,
    update_knowledge_base,
    delete_knowledge_base,
)
from app.schemas import DestinationCreate, DestinationResponse
from app.schemas import KnowledgeBaseCreate, KnowledgeBaseResponse

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.get("/destinations", response_model=list[DestinationResponse])
def read_destinations(db: Session = Depends(get_db)):
    return get_destinations(db)

@app.post("/destinations", response_model=DestinationResponse)
def create_new_destination(destination: DestinationCreate, db: Session = Depends(get_db)):
    return create_destination(db, destination)

@app.get("/destinations/{destination_id}", response_model=DestinationResponse)
def read_destination(destination_id: int, db: Session = Depends(get_db)):
    destination = get_destination_by_id(db, destination_id)
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    return destination

@app.put("/destinations/{destination_id}", response_model=DestinationResponse)
def update_exisiting_destination(
    destination_id: int, destination: DestinationCreate, db: Session = Depends(get_db)
):
    updated_destination = update_destination(db, destination_id, destination)
    if not updated_destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    return updated_destination

@app.delete("/destinations/{destination_id}")
def delete_existing_destination(destination_id: int, db: Session = Depends(get_db)):
    success = delete_destination(db, destination_id)
    if not success:
        raise HTTPException(status_code=404, detail="Destination not found")
    return {"message": "Destination deleted successfully"}

# Routes for KnowledgeBase
@app.get("/destinations/{destination_id}/knowledge_bases", response_model=list[KnowledgeBaseResponse])
def read_kbs(destination_id: int, db: Session = Depends(get_db)):
    return get_knowledge_bases_for_destination(db, destination_id)

@app.post("/destinations/{destination_id}/knowledge_bases", response_model=KnowledgeBaseResponse)
def create_kb(kb: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    return create_knowledge_base(db, kb)

@app.get("/knowledge_bases/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
def read_kb(knowledge_base_id: int, db: Session = Depends(get_db)):
    kb = get_knowledge_base_by_id(db, knowledge_base_id)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    return kb

@app.put("/knowledge_bases/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
def update_kb(knowledge_base_id: int, kb: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    updated_kb = update_knowledge_base(db, knowledge_base_id, kb)
    if not updated_kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    return updated_kb


@app.delete("/knowledge_bases/{knowledge_base_id}")
def delete_kb(knowledge_base_id: int, db: Session = Depends(get_db)):
    success = delete_knowledge_base(db, knowledge_base_id)
    if not success:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    return {"message": "KnowledgeBase deleted successfully"}

add_routes(app, agent_executor, path="/chat")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)