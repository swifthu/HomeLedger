"""Tests for accuracy metrics calculation."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import uuid


class TestAccuracyCalculation:
    """Test accuracy_rate and zero_miss_rate calculations."""

    def test_accuracy_rate_calculation(self):
        """Mock 100 records, simulate 85 correct, verify accuracy = 0.85."""
        from main import recompute_monthly_stats
        from models import Record, MonthlyStats
        from db.database import SessionLocal, engine, init_db
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Create in-memory database for testing
        test_engine = create_engine("sqlite:///:memory:")
        from models import Base
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(bind=test_engine)
        db = TestSession()

        # Create 100 mock AI records with known ground truth
        for i in range(100):
            is_correct = i < 85  # First 85 are correct, last 15 are wrong
            record = Record(
                id=str(uuid.uuid4()),
                created_at="2026-03-15T10:00:00",
                updated_at="2026-03-15T10:00:00",
                category="餐饮" if is_correct else "购物",
                amount=50.0 if is_correct else 60.0,
                description=f"Test record {i}",
                ai_confidence=0.90,
                status="confirmed",
                source="ai",
                ground_truth_category="餐饮",
                ground_truth_amount=50.0,
            )
            db.add(record)
        db.commit()

        # Compute stats
        recompute_monthly_stats(db, "2026-03")

        # Verify accuracy_rate = 85/100 = 0.85
        stats = db.query(MonthlyStats).filter(MonthlyStats.month == "2026-03").first()
        assert stats is not None
        assert stats.total_records == 100
        assert stats.ai_records == 100
        assert stats.accuracy_rate == 0.85

        db.close()

    def test_zero_miss_rate_formula(self):
        """Test zero_miss_rate = auto_classified_confirmed / total."""
        from main import recompute_monthly_stats
        from models import Record, MonthlyStats
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models import Base

        test_engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(bind=test_engine)
        db = TestSession()

        # Create 100 records:
        # - 60 from rule/ai with status=confirmed (auto-classified correct)
        # - 20 from rule/ai with status=pending_review
        # - 20 manual
        for i in range(100):
            if i < 60:
                source = "rule" if i < 30 else "ai"
                status = "confirmed"
            elif i < 80:
                source = "ai"
                status = "pending_review"
            else:
                source = "manual"
                status = "confirmed"

            record = Record(
                id=str(uuid.uuid4()),
                created_at="2026-04-10T10:00:00",
                updated_at="2026-04-10T10:00:00",
                category="餐饮",
                amount=50.0,
                description=f"Test {i}",
                ai_confidence=0.90,
                status=status,
                source=source,
                ground_truth_category="餐饮",
                ground_truth_amount=50.0,
            )
            db.add(record)
        db.commit()

        # Compute stats
        recompute_monthly_stats(db, "2026-04")

        # Verify zero_miss_rate = 60/100 = 0.60
        stats = db.query(MonthlyStats).filter(MonthlyStats.month == "2026-04").first()
        assert stats is not None
        assert stats.total_records == 100
        assert stats.zero_miss_rate == 0.60

        db.close()

    def test_zero_miss_rate_all_auto_confirmed(self):
        """Test zero_miss_rate when all records are auto-confirmed."""
        from main import recompute_monthly_stats
        from models import Record, MonthlyStats
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models import Base

        test_engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(bind=test_engine)
        db = TestSession()

        # All 50 records are auto-classified and confirmed
        for i in range(50):
            record = Record(
                id=str(uuid.uuid4()),
                created_at="2026-05-01T10:00:00",
                updated_at="2026-05-01T10:00:00",
                category="餐饮",
                amount=50.0,
                description=f"Test {i}",
                ai_confidence=0.90,
                status="confirmed",
                source="ai" if i % 2 == 0 else "rule",
                ground_truth_category="餐饮",
                ground_truth_amount=50.0,
            )
            db.add(record)
        db.commit()

        recompute_monthly_stats(db, "2026-05")

        stats = db.query(MonthlyStats).filter(MonthlyStats.month == "2026-05").first()
        assert stats is not None
        assert stats.total_records == 50
        assert stats.zero_miss_rate == 1.0

        db.close()

    def test_accuracy_rate_no_ai_records(self):
        """Test accuracy_rate defaults to 1.0 when no AI records."""
        from main import recompute_monthly_stats
        from models import Record, MonthlyStats
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models import Base

        test_engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(bind=test_engine)
        db = TestSession()

        # Only manual records
        for i in range(10):
            record = Record(
                id=str(uuid.uuid4()),
                created_at="2026-06-01T10:00:00",
                updated_at="2026-06-01T10:00:00",
                category="餐饮",
                amount=50.0,
                description=f"Manual record {i}",
                status="confirmed",
                source="manual",
            )
            db.add(record)
        db.commit()

        recompute_monthly_stats(db, "2026-06")

        stats = db.query(MonthlyStats).filter(MonthlyStats.month == "2026-06").first()
        assert stats is not None
        assert stats.ai_records == 0
        assert stats.accuracy_rate == 1.0
        assert stats.zero_miss_rate == 0.0  # No auto-classified confirmed

        db.close()

    def test_zero_miss_rate_no_records(self):
        """Test zero_miss_rate defaults to 1.0 when no records."""
        from main import recompute_monthly_stats
        from models import MonthlyStats
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models import Base

        test_engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(bind=test_engine)
        db = TestSession()

        recompute_monthly_stats(db, "2026-07")

        stats = db.query(MonthlyStats).filter(MonthlyStats.month == "2026-07").first()
        assert stats is not None
        assert stats.total_records == 0
        assert stats.zero_miss_rate == 1.0

        db.close()
