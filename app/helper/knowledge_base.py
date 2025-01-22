from sqlalchemy.orm import Session
from app.models import Destination, KnowledgeBase
from app.schemas import KnowledgeBaseCreate
from app.helper.vector_store import add_document, delete_document

def create_knowledge_base(db: Session, knowledge_base: KnowledgeBaseCreate) -> KnowledgeBase:
    destination = db.query(Destination).filter(Destination.id == knowledge_base.destination_id).first()

    if not destination:
        raise Exception(f"Destination not found for id {knowledge_base.destination_id}")

    vector_db_document = add_document(knowledge_base.content, { 'destination': destination.name })

    new_kb = KnowledgeBase(
        content=knowledge_base.content,
        destination_id=knowledge_base.destination_id,
        vector_db_doc_id=vector_db_document.id_
    )
    db.add(new_kb)
    db.commit()
    db.refresh(new_kb)
    return new_kb


def get_knowledge_bases_for_destination(db: Session, destination_id: int):
    return db.query(KnowledgeBase).filter(KnowledgeBase.destination_id == destination_id).all()

def get_knowledge_base_by_id(db: Session, knowledge_base_id: int):
    return db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()


def update_knowledge_base(
    db: Session, knowledge_base_id: int, updates: KnowledgeBaseCreate
):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()

    if not kb:
        return None
    
    destination = db.query(Destination).filter(Destination.id == kb.destination_id).first()

    if not destination:
        raise Exception(f"Destination not found for id {kb.destination_id}")    
    
    delete_document(kb.vector_db_doc_id)
    vector_db_document = add_document(updates.content, { destination: destination.name })

    kb.content = updates.content
    kb.destination_id = updates.destination_id
    kb.vector_db_doc_id = vector_db_document.id_
    db.commit()
    db.refresh(kb)
    return kb


def delete_knowledge_base(db: Session, knowledge_base_id: int):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
    if not kb:
        return False

    delete_document(kb.vector_db_doc_id)

    db.delete(kb)
    db.commit()
    return True