# utils/serialize.py
from bson import ObjectId

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON serializable dict"""
    if not doc:
        return doc
    doc = dict(doc)
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc

def serialize_docs(docs: list) -> list:
    """Serialize a list of documents"""
    return [serialize_doc(d) for d in docs]
