from typing import List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Body, Response, Request
from documents_extra import DreamJournal
from core.ratelimit import limiter
from core.logging_config import get_logger
logger = get_logger(__name__)
from beanie.exceptions import CollectionWasNotInitialized
from core.security import get_api_key
from pydantic import BaseModel
from config import settings
try:
    from database import get_motor_db as _get_db
except Exception:
    # Fallback: create a local Motor DB getter if centralized helper is unavailable
    from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
    from config import settings as _settings  # type: ignore

    def _get_db():
        client = AsyncIOMotorClient(_settings.MONGO_URI)
        return client.get_database(_settings.MONGO_DB_NAME)
from bson import ObjectId
from beanie.exceptions import CollectionWasNotInitialized

router = APIRouter(
    prefix="/api/v1/dream-journals",
    tags=["Dream Journals"],
    dependencies=[Depends(get_api_key)],
)


class DreamJournalUpdate(BaseModel):
    model_id: Optional[str] = None
    dream_text: Optional[str] = None
    tags: Optional[List[str]] = None
    emotion_score: Optional[float] = None
    ai_summary: Optional[str] = None
    # meta can contain arbitrary nested keys
    meta: Optional[dict] = None

    class Config:
        extra = "ignore"


@router.get("/", response_model=List[dict])
async def list_dreams(
    response: Response,
    model_id: Optional[str] = None,
    tags: Optional[str] = None,
    from_: Optional[str] = None,
    to: Optional[str] = None,
    emotion_gte: Optional[float] = None,
    skip: int = 0,
    limit: int = 50,
    after_id: Optional[str] = None,
):
    logger.info(f"DreamJournal in router: {DreamJournal.__module__}@{id(DreamJournal)}")
    try:
        # Use a direct Motor DB to bypass Beanie validation on legacy docs
        db = _get_db()
        # Use explicit collection name to avoid beanie settings access during raw reads
        coll = db.get_collection('dream_journals')
        query: dict = {}
        if model_id:
            query["model_id"] = model_id
        if tags:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            if tag_list:
                query["tags"] = {"$all": tag_list}
        # Date range on `date` field
        from_dt = to_dt = None
        if from_ or to:
            try:
                if from_:
                    from_dt = datetime.fromisoformat(from_).replace(hour=0, minute=0, second=0, microsecond=0)
                if to:
                    to_dt = datetime.fromisoformat(to).replace(hour=23, minute=59, second=59, microsecond=999999)
            except Exception:
                from_dt = to_dt = None
        # Intentionally avoid pushing date filter into Mongo query due to mixed-type legacy data; we'll filter in-memory below.
        if emotion_gte is not None:
            try:
                query["emotion_score"] = {"$gte": float(emotion_gte)}
            except Exception:
                query["emotion_score"] = {"$gte": 0.0}
        # Optional cursor-based pagination: filter by _id < after_id when provided
        if after_id:
            try:
                query["_id"] = {"$lt": ObjectId(after_id)}
            except Exception:
                query["_id"] = {"$lt": after_id}
        # Stable sort by _id descending for consistent pagination
        page_limit = max(1, int(limit))
        cursor = (
            coll.find(query)
            .sort("_id", -1)
            .skip(max(0, int(skip)))
            .limit(page_limit)
        )
        docs = await cursor.to_list(length=page_limit)
        # Apply in-memory date filtering to support both string and datetime stored types
        if from_dt or to_dt:
            def _to_dt(val):
                from datetime import datetime as _dt
                if val is None:
                    return None
                if isinstance(val, _dt):
                    return val
                try:
                    # attempt ISO parse for strings
                    return _dt.fromisoformat(str(val))
                except Exception:
                    return None
            filtered = []
            for d in docs:
                dv = _to_dt(d.get('date'))
                if dv is None:
                    continue
                if from_dt and dv < from_dt:
                    continue
                if to_dt and dv > to_dt:
                    continue
                filtered.append(d)
            docs = filtered
        # Enforce page size and normalize ObjectId to string
        docs = docs[:page_limit]
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"]) 
        # Optional simple pagination headers
        if response is not None:
            try:
                total = await coll.count_documents(query)
            except Exception:
                total = -1
            response.headers["X-Page-Skip"] = str(skip)
            response.headers["X-Page-Limit"] = str(limit)
            response.headers["X-Returned"] = str(len(docs))
            response.headers["X-Next-Skip"] = str(skip + len(docs))
            if total >= 0:
                response.headers["X-Total-Count"] = str(total)
                has_more = (skip + len(docs)) < total
                response.headers["X-Has-More"] = "true" if has_more else "false"
            # Cursor header: last _id in page
            if docs:
                response.headers["X-Next-After-Id"] = docs[-1]["_id"]
        return docs
    except Exception as e:
        logger.exception("DreamJournal list failed: %s", e)
        raise HTTPException(status_code=500, detail=f"DreamJournal error: {e}")


def _normalize_doc(d: dict) -> dict:
    if d is None:
        return {}
    d = dict(d)
    if "_id" in d:
        d["_id"] = str(d["_id"]) 
    return d


@router.post("/", response_model=dict, status_code=201)
@limiter.limit("30/minute")
async def create_dream(request: Request, dream: dict = Body(...)):
    db = _get_db()
    coll = db.get_collection('dream_journals')
    try:
        doc = DreamJournal(**dream)
        await doc.insert()
        raw = await coll.find_one({"_id": doc.id})
        return _normalize_doc(raw)
    except CollectionWasNotInitialized:
        # Fallback to direct Motor insert when Beanie was not initialized for this Document class
        res = await coll.insert_one(dream)
        raw = await coll.find_one({"_id": res.inserted_id})
        return _normalize_doc(raw)


@router.get("/{dream_id}", response_model=dict)
async def get_dream(dream_id: str):
    db = _get_db()
    coll = db.get_collection('dream_journals')
    try:
        raw = await coll.find_one({"_id": ObjectId(dream_id)})
    except Exception:
        raw = await coll.find_one({"_id": dream_id})
    if not raw:
        raise HTTPException(status_code=404, detail="Dream not found")
    return _normalize_doc(raw)


@router.delete("/{dream_id}", status_code=204)
@limiter.limit("60/minute")
async def delete_dream(request: Request, dream_id: str):
    doc = await DreamJournal.get(dream_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Dream not found")
    await doc.delete()


@router.patch("/{dream_id}", response_model=dict)
@limiter.limit("60/minute")
async def patch_dream(request: Request, dream_id: str, patch: DreamJournalUpdate):
    doc = await DreamJournal.get(dream_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Dream not found")
    updates = patch.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(doc, k, v)
    await doc.save()
    db = _get_db()
    coll = db.get_collection('dream_journals')
    raw = await coll.find_one({"_id": doc.id})
    return _normalize_doc(raw)


@router.put("/{dream_id}", response_model=dict)
@limiter.limit("30/minute")
async def replace_dream(request: Request, dream_id: str, dream: Any):
    existing = await DreamJournal.get(dream_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Dream not found")
    # Preserve original id
    doc = DreamJournal(**(dream if isinstance(dream, dict) else dream.model_dump()))
    doc.id = existing.id
    await doc.replace()
    db = _get_db()
    coll = db.get_collection('dream_journals')
    raw = await coll.find_one({"_id": doc.id})
    return _normalize_doc(raw)
