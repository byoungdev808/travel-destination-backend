from sqlalchemy.orm import Session
from app.models import Destination, KnowledgeBase
from app.schemas import DestinationCreate
from app.helper.knowledge_base import delete_knowledge_base

# Create a new destination
def create_destination(db: Session, destination: DestinationCreate) -> Destination:
    new_destination = Destination(name=destination.name)
    db.add(new_destination)
    db.commit()
    db.refresh(new_destination)
    return new_destination

# Retrieve all destinations
def get_destinations(db: Session):
    return db.query(Destination).all()

# Retrieve a single destination by ID
def get_destination_by_id(db: Session, destination_id: int):
    return db.query(Destination).filter(Destination.id == destination_id).first()

# Update a destination
def update_destination(db: Session, destination_id: int, destination: DestinationCreate):
    existing_destination = db.query(Destination).filter(Destination.id == destination_id).first()
    if not existing_destination:
        return None
    existing_destination.name = destination.name
    db.commit()
    db.refresh(existing_destination)
    return existing_destination

# Delete a destination
def delete_destination(db: Session, destination_id: int):
    destination = db.query(Destination).filter(Destination.id == destination_id).first()
    if not destination:
        return False
    kbs = db.query(KnowledgeBase).filter(KnowledgeBase.destination_id == destination.id)
    for kb in kbs:
        delete_knowledge_base(db, kb.id)
    db.delete(destination)
    db.commit()
    return True
