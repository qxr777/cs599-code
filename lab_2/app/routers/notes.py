from fastapi import APIRouter, HTTPException
from typing import List
from .. import db
from ..schemas import NoteCreate, NoteRead

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("", response_model=NoteRead)
def create_note(payload: NoteCreate):
    note_id = db.insert_note(payload.content)
    note = db.get_note(note_id)
    if not note:
        raise HTTPException(status_code=500, detail="Failed to retrieve created note")
    return note

@router.get("", response_model=List[NoteRead])
def list_notes():
    return db.list_notes()

@router.get("/{note_id}", response_model=NoteRead)
def get_single_note(note_id: int):
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
