from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Notes ---

class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, description="笔记内容")

class NoteRead(BaseModel):
    id: int
    content: str
    created_at: str

# --- Action Items ---

class ActionItemBase(BaseModel):
    text: str
    done: bool = False

class ActionItemRead(ActionItemBase):
    id: int
    note_id: Optional[int] = None
    created_at: str

class ActionItemExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)
    save_note: bool = False

class ActionItemExtractResponse(BaseModel):
    note_id: Optional[int] = None
    items: List[ActionItemRead]

class ActionItemUpdateStatus(BaseModel):
    done: bool = True
