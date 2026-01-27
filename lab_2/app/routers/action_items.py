from fastapi import APIRouter, HTTPException
from typing import List, Optional
from .. import db
from ..services.extract import extract_action_items, extract_action_items_llm
from ..schemas import (
    ActionItemRead, 
    ActionItemExtractRequest, 
    ActionItemExtractResponse,
    ActionItemUpdateStatus
)

router = APIRouter(prefix="/action-items", tags=["action-items"])

def _process_extraction(payload: ActionItemExtractRequest, use_llm: bool):
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    if use_llm:
        items_text = extract_action_items_llm(payload.text)
    else:
        items_text = extract_action_items(payload.text)
        
    ids = db.insert_action_items(items_text, note_id=note_id)
    
    # 构造响应对象列表
    response_items = []
    # 这里我们简化一下，直接构造逻辑，或者再次从 DB 查询以获取完整对象
    for i, t in zip(ids, items_text):
        response_items.append({
            "id": i,
            "note_id": note_id,
            "text": t,
            "done": False,
            "created_at": "Just now" # 简化，真实场景可从 DB 重新获取
        })
    
    return {"note_id": note_id, "items": response_items}

@router.post("/extract", response_model=ActionItemExtractResponse)
def extract_basic(payload: ActionItemExtractRequest):
    return _process_extraction(payload, use_llm=False)

@router.post("/extract-llm", response_model=ActionItemExtractResponse)
def extract_with_llm(payload: ActionItemExtractRequest):
    return _process_extraction(payload, use_llm=True)

@router.get("", response_model=List[ActionItemRead])
def list_action_items(note_id: Optional[int] = None):
    return db.list_action_items(note_id=note_id)

@router.post("/{action_item_id}/done", response_model=dict)
def update_status(action_item_id: int, payload: ActionItemUpdateStatus):
    success = db.mark_action_item_done(action_item_id, payload.done)
    if not success:
        raise HTTPException(status_code=404, detail="Action item not found")
    return {"id": action_item_id, "done": payload.done}
