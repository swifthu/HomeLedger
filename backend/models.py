from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Index, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # cash/virtual/liability/investment/prepaid
    balance = Column(Float, default=0.0)
    currency = Column(String, default="CNY")
    color = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    deleted_at = Column(String, nullable=True)
    is_active = Column(Integer, default=1)

    __table_args__ = (
        Index("idx_accounts_type", "type"),
        Index("idx_accounts_deleted_at", "deleted_at"),
    )


class Record(Base):
    __tablename__ = "records"

    id = Column(String, primary_key=True)
    created_at = Column(String, nullable=False, default=datetime.utcnow)
    updated_at = Column(String, nullable=False, default=datetime.utcnow)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    status = Column(String, default="confirmed")
    source = Column(String, default="ai")
    ground_truth_category = Column(String, nullable=True)
    ground_truth_amount = Column(Float, nullable=True)
    user_corrected = Column(Integer, default=0)
    merchant = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    deleted_at = Column(String, nullable=True)
    year_month = Column(String, nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=True)

    __table_args__ = (
        Index("idx_records_created_at", "created_at"),
        Index("idx_records_status", "status"),
        Index("idx_records_category", "category"),
        Index("idx_records_category_created", "category", "created_at"),
    )


class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True)


class MonthlyStats(Base):
    __tablename__ = "monthly_stats"

    id = Column(String, primary_key=True)
    month = Column(String, unique=True, nullable=False)
    total_records = Column(Integer, default=0)
    ai_records = Column(Integer, default=0)
    rule_records = Column(Integer, default=0)
    manual_records = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    zero_miss_rate = Column(Float, default=0.0)
    computed_at = Column(String, nullable=True)
