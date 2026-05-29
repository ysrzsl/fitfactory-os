"""知识库 API（RAG 检索）"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from src.ai.rag import search_knowledge, get_knowledge_base

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


@router.get("/search")
def search(query: str = Query(...), top_k: int = 3):
    """搜索工艺标准和 SOP"""
    results = search_knowledge(query, top_k)
    return {"query": query, "count": len(results), "results": results}


@router.post("/search")
def search_post(req: SearchRequest):
    """搜索工艺标准和 SOP (POST)"""
    results = search_knowledge(req.query, req.top_k)
    return {"query": req.query, "count": len(results), "results": results}


@router.get("/stats")
def kb_stats():
    """知识库统计"""
    kb = get_knowledge_base()
    return {"total_documents": len(kb.documents), "status": "ready"}
