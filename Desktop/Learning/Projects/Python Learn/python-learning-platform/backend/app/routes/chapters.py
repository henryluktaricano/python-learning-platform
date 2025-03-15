"""
API routes for chapters and topics.
"""
from fastapi import APIRouter, Request
from typing import List, Dict, Any

from ..utils.file_utils import get_all_chapters, get_chapter_info

router = APIRouter()

@router.get("", name="get_all_chapters")
async def get_chapters(request: Request) -> List[Dict[str, Any]]:
    """
    Get all chapters with their topics.
    """
    return get_all_chapters()

@router.get("/{chapter_id}", name="get_chapter")
async def get_chapter(request: Request, chapter_id: str) -> Dict[str, Any]:
    """
    Get a specific chapter by ID.
    """
    chapter = get_chapter_info(chapter_id)
    if not chapter:
        return {"error": f"Chapter not found: {chapter_id}"}
    return chapter 