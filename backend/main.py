import hashlib
import io
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from db.database import SessionLocal, engine, init_db
from export.excel import export_records_to_excel
from models import Base, Category, MonthlyStats, Record
from ai.classifier import get_classifier

# ── Init ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="HomeLedger API")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

# ── Dependencies ───────────────────────────────────────────────────────────────

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Pydantic Schemas ───────────────────────────────────────────────────────────

class RecordCreate(BaseModel):
    category: str
    amount: float
    description: Optional[str] = None
    ai_confidence: Optional[float] = None
    status: str = "confirmed"
    source: str = "ai"
    ground_truth_category: Optional[str] = None
    ground_truth_amount: Optional[float] = None

class RecordUpdate(BaseModel):
    ground_truth_category: Optional[str] = None
    ground_truth_amount: Optional[float] = None
    user_corrected: bool = False

class RecordOut(BaseModel):
    id: str
    created_at: str
    updated_at: str
    category: str
    amount: float
    description: Optional[str] = None
    ai_confidence: Optional[float] = None
    status: str
    source: str
    ground_truth_category: Optional[str] = None
    ground_truth_amount: Optional[float] = None
    user_corrected: int

class CategoryOut(BaseModel):
    id: str
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None

class BackupRestore(BaseModel):
    sha256: str

class ClassifyRequest(BaseModel):
    text: str

class ClassifyResponse(BaseModel):
    category: str
    amount: Optional[float]
    confidence: float
    status: str  # confirmed | pending_review
    source: str  # rule | ai

class MonthlyStatsOut(BaseModel):
    month: str
    total_records: int
    ai_records: int
    rule_records: int
    manual_records: int
    accuracy_rate: Optional[float]
    zero_miss_rate: Optional[float]

# ── Helpers ─────────────────────────────────────────────────────────────────────

def recompute_monthly_stats(db: Session, month: str):
    """Recompute MonthlyStats for the given month (YYYY-MM)."""
    month_prefix = f"{month}%"
    total = db.query(func.count(Record.id)).filter(Record.created_at.like(month_prefix)).scalar() or 0
    ai_records = db.query(func.count(Record.id)).filter(
        Record.created_at.like(month_prefix), Record.source == "ai"
    ).scalar() or 0
    rule_records = db.query(func.count(Record.id)).filter(
        Record.created_at.like(month_prefix), Record.source == "rule"
    ).scalar() or 0
    manual_records = db.query(func.count(Record.id)).filter(
        Record.created_at.like(month_prefix), Record.source == "manual"
    ).scalar() or 0

    # accuracy = (ground_truth_category == category AND ground_truth_amount == amount) / ai_records
    if ai_records > 0:
        accurate = db.query(func.count(Record.id)).filter(
            Record.created_at.like(month_prefix),
            Record.source == "ai",
            Record.ground_truth_category == Record.category,
            Record.ground_truth_amount == Record.amount,
        ).scalar() or 0
        accuracy_rate = accurate / ai_records
    else:
        accuracy_rate = 1.0

    # zero_miss = auto-classified (source IN ('rule','ai') AND status='confirmed') / total
    if total > 0:
        zero_miss = db.query(func.count(Record.id)).filter(
            Record.created_at.like(month_prefix),
            Record.source.in_(["rule", "ai"]),
            Record.status == "confirmed",
        ).scalar() or 0
        zero_miss_rate = zero_miss / total
    else:
        zero_miss_rate = 1.0

    now = datetime.utcnow().isoformat()
    stats = db.query(MonthlyStats).filter(MonthlyStats.month == month).first()
    if stats:
        stats.total_records = total
        stats.ai_records = ai_records
        stats.rule_records = rule_records
        stats.manual_records = manual_records
        stats.accuracy_rate = accuracy_rate
        stats.zero_miss_rate = zero_miss_rate
        stats.computed_at = now
    else:
        stats = MonthlyStats(
            id=str(uuid.uuid4()),
            month=month,
            total_records=total,
            ai_records=ai_records,
            rule_records=rule_records,
            manual_records=manual_records,
            accuracy_rate=accuracy_rate,
            zero_miss_rate=zero_miss_rate,
            computed_at=now,
        )
        db.add(stats)
    db.commit()


def after_commit(db: Session, created_at: str):
    """Hook to recompute monthly stats after a record changes."""
    if created_at:
        month = created_at[:7]  # YYYY-MM
        recompute_monthly_stats(db, month)


# ── Health ──────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}

# ── AI Classify ────────────────────────────────────────────────────────────────

@app.post("/api/ai/classify", response_model=ClassifyResponse)
def classify_text(req: ClassifyRequest):
    """
    AI 分类端点：规则优先，AI 兜底
    - source='rule': 规则引擎直接命中
    - source='ai': 调用 AI 分类
    - confidence >= 0.85 → status='confirmed'
    - confidence < 0.85 → status='pending_review'
    """
    classifier = get_classifier()
    result = classifier.classify_text(req.text)
    return ClassifyResponse(
        category=result.category,
        amount=result.amount,
        confidence=result.confidence,
        status=result.status,
        source=result.source,
    )


# ── Image Understanding ────────────────────────────────────────────────────────

class ImageUnderstandRequest(BaseModel):
    prompt: str = "请分析这张图片，提取消费项目和金额，返回JSON格式"

class ImageUnderstandResponse(BaseModel):
    content: str
    items: list[dict] = []
    total: Optional[float] = None
    store: Optional[str] = None
    date: Optional[str] = None


@app.post("/api/ai/image", response_model=ImageUnderstandResponse)
def understand_image(
    file: UploadFile = File(...),
    prompt: str = Query("请分析这张小票/发票，提取所有消费项目和金额，返回JSON格式：{\"items\":[{\"name\":\"商品名称\",\"amount\":金额}],\"total\":总金额,\"store\":\"商店名称\"}，只返回JSON，不要其他文字。"),
):
    """
    图片理解端点：识别发票/小票图片，提取消费信息
    """
    from ai.image_client import understand_receipt

    image_data = file.file.read()
    result = understand_receipt(image_data)

    return ImageUnderstandResponse(
        content=result.get("content", ""),
        items=result.get("items", []),
        total=result.get("total"),
        store=result.get("store"),
        date=result.get("date"),
    )

# ── Monthly Stats ─────────────────────────────────────────────────────────────

@app.get("/api/stats/monthly", response_model=list[MonthlyStatsOut])
def get_monthly_stats(
    limit: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
):
    """获取月度统计"""
    stats = db.query(MonthlyStats).order_by(MonthlyStats.month.desc()).limit(limit).all()
    return [
        MonthlyStatsOut(
            month=s.month,
            total_records=s.total_records or 0,
            ai_records=s.ai_records or 0,
            rule_records=s.rule_records or 0,
            manual_records=s.manual_records or 0,
            accuracy_rate=s.accuracy_rate,
            zero_miss_rate=s.zero_miss_rate,
        )
        for s in stats
    ]

# ── Records CRUD ───────────────────────────────────────────────────────────────

class PageResultOut(BaseModel):
    items: list[RecordOut]
    total: int
    page: int
    page_size: int

@app.get("/api/records", response_model=PageResultOut)
def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Record)
    if start_date:
        q = q.filter(Record.created_at >= start_date)
    if end_date:
        q = q.filter(Record.created_at <= end_date)
    if status:
        q = q.filter(Record.status == status)

    total = q.count()
    offset = (page - 1) * page_size
    items = q.order_by(Record.created_at.desc()).offset(offset).limit(page_size).all()

    def to_record_out(r: Record) -> RecordOut:
        return RecordOut(
            id=r.id,
            created_at=r.created_at,
            updated_at=r.updated_at,
            category=r.category,
            amount=r.amount,
            description=r.description,
            ai_confidence=r.ai_confidence,
            status=r.status,
            source=r.source,
            ground_truth_category=r.ground_truth_category,
            ground_truth_amount=r.ground_truth_amount,
            user_corrected=r.user_corrected or 0,
        )

    return PageResultOut(items=[to_record_out(r) for r in items], total=total, page=page, page_size=page_size)


@app.post("/api/records", response_model=RecordOut, status_code=201)
def create_record(payload: RecordCreate, db: Session = Depends(get_db)):
    now = datetime.utcnow().isoformat()
    record = Record(
        id=str(uuid.uuid4()),
        created_at=now,
        updated_at=now,
        category=payload.category,
        amount=payload.amount,
        description=payload.description,
        ai_confidence=payload.ai_confidence,
        status=payload.status,
        source=payload.source,
        ground_truth_category=payload.ground_truth_category or payload.category,
        ground_truth_amount=payload.ground_truth_amount or payload.amount,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    after_commit(db, record.created_at)
    return record


@app.get("/api/records/{record_id}", response_model=RecordOut)
def get_record(record_id: str, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@app.put("/api/records/{record_id}", response_model=RecordOut)
def update_record(
    record_id: str,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    old_month = record.created_at[:7]
    if payload.ground_truth_category is not None:
        record.ground_truth_category = payload.ground_truth_category
    if payload.ground_truth_amount is not None:
        record.ground_truth_amount = payload.ground_truth_amount
    if payload.user_corrected is not None:
        record.user_corrected = 1 if payload.user_corrected else 0
    record.updated_at = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(record)
    new_month = record.created_at[:7]
    if old_month == new_month:
        recompute_monthly_stats(db, new_month)
    else:
        recompute_monthly_stats(db, old_month)
        recompute_monthly_stats(db, new_month)
    return record


@app.delete("/api/records/{record_id}", status_code=204)
def delete_record(record_id: str, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    month = record.created_at[:7]
    db.delete(record)
    db.commit()
    recompute_monthly_stats(db, month)


# ── Categories ──────────────────────────────────────────────────────────────────

@app.get("/api/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


# ── Backup / Restore ───────────────────────────────────────────────────────────

BACKUP_DIR = Path(__file__).parent.parent / "backups"

@app.post("/api/backup", status_code=201)
def create_backup(db: Session = Depends(get_db)):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"HomeLedger_{timestamp}.db"

    # Close and re-open to ensure WAL is checkpointed
    db.close()
    shutil.copy2(
        Path(__file__).parent.parent / "data" / "HomeLedger.db",
        backup_path,
    )
    # Re-bind session
    from db.database import SessionLocal
    db = SessionLocal()

    return {"backup_path": str(backup_path), "timestamp": timestamp}


@app.post("/api/backup/restore")
def restore_backup(payload: BackupRestore, db: Session = Depends(get_db)):
    backups = sorted(BACKUP_DIR.glob("HomeLedger_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backups:
        raise HTTPException(status_code=404, detail="No backup found")

    latest = backups[0]
    with open(latest, "rb") as f:
        actual_sha256 = hashlib.sha256(f.read()).hexdigest()

    if actual_sha256 != payload.sha256:
        raise HTTPException(status_code=400, detail="SHA256 mismatch — backup may be corrupted")

    # Replace active DB
    db.close()
    active_db = Path(__file__).parent.parent / "data" / "HomeLedger.db"
    shutil.copy2(latest, active_db)

    return {"restored_from": str(latest), "sha256": actual_sha256}


# ── Excel Export ───────────────────────────────────────────────────────────────

@app.get("/api/export/excel")
def export_excel(db: Session = Depends(get_db)):
    wb = export_records_to_excel(db)
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=HomeLedger_records.xlsx"},
    )
