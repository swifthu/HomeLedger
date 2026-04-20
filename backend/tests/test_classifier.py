"""Tests for AI classifier with mocked httpx responses."""
import pytest
from unittest.mock import patch, MagicMock
from ai.classifier import Classifier, ClassifierResult, classify


class TestClassifierConfidence:
    """Test confidence-based status determination."""

    def test_high_confidence_confirmed(self):
        """Test: confidence >= 0.85 -> status='confirmed'."""
        with patch("ai.classifier.classify_with_ai") as mock_ai:
            mock_ai.return_value = {
                "category": "餐饮",
                "amount": 50.0,
                "confidence": 0.90,
            }
            classifier = Classifier()
            result = classifier.classify("测试文本")

            assert result.status == "confirmed"
            assert result.confidence == 0.90
            assert result.source == "ai"

    def test_low_confidence_pending_review(self):
        """Test: confidence < 0.85 -> status='pending_review'."""
        with patch("ai.classifier.classify_with_ai") as mock_ai:
            mock_ai.return_value = {
                "category": "购物",
                "amount": 100.0,
                "confidence": 0.70,
            }
            classifier = Classifier()
            result = classifier.classify("测试文本")

            assert result.status == "pending_review"
            assert result.confidence == 0.70

    def test_boundary_confidence_85_confirmed(self):
        """Test: confidence = 0.85 exactly -> status='confirmed'."""
        with patch("ai.classifier.classify_with_ai") as mock_ai:
            mock_ai.return_value = {
                "category": "交通",
                "amount": 30.0,
                "confidence": 0.85,
            }
            classifier = Classifier()
            result = classifier.classify("测试文本")

            assert result.status == "confirmed"

    def test_boundary_confidence_84_pending(self):
        """Test: confidence = 0.84 -> status='pending_review'."""
        with patch("ai.classifier.classify_with_ai") as mock_ai:
            mock_ai.return_value = {
                "category": "娱乐",
                "amount": 150.0,
                "confidence": 0.84,
            }
            classifier = Classifier()
            result = classifier.classify("测试文本")

            assert result.status == "pending_review"


class TestClassifierRuleFallback:
    """Test rule engine fallback to AI when no match."""

    def test_rule_match_returns_confirmed(self):
        """Test rule engine match returns confirmed status directly."""
        classifier = Classifier()
        result = classifier.check("点外卖")

        assert result is not None
        assert result.status == "confirmed"
        assert result.source == "rule"
        assert result.category == "餐饮"

    def test_no_rule_match_falls_back_to_ai(self):
        """Test non-matching text falls back to AI classification."""
        with patch("ai.classifier.classify_with_ai") as mock_ai:
            mock_ai.return_value = {
                "category": "其他",
                "amount": None,
                "confidence": 0.60,
            }
            classifier = Classifier()
            result = classifier.classify_text("random unknown text")

            assert result.source == "ai"
            assert result.status == "pending_review"

    def test_classify_text_full_flow_rule_hit(self):
        """Test full classify_text flow with rule match."""
        classifier = Classifier()
        result = classifier.classify_text("买早餐花了10元")

        assert result is not None
        assert result.source == "rule"
        assert result.status == "confirmed"

    def test_classify_text_full_flow_ai_fallback(self):
        """Test full classify_text flow with AI fallback."""
        with patch("ai.classifier.classify_with_ai") as mock_ai:
            mock_ai.return_value = {
                "category": "教育",
                "amount": 500.0,
                "confidence": 0.92,
            }
            classifier = Classifier()
            # Use text that doesn't match any rule pattern
            result = classifier.classify_text("这是一笔无法识别的消费描述xyz")

            assert result is not None
            assert result.source == "ai"
            assert result.category == "教育"
            assert result.status == "confirmed"


class TestClassifierResult:
    """Test ClassifierResult to_dict method."""

    def test_to_dict_contains_all_fields(self):
        """Test to_dict returns all required fields."""
        result = ClassifierResult(
            category="餐饮",
            amount=35.5,
            confidence=0.90,
            status="confirmed",
            source="rule",
        )
        d = result.to_dict()

        assert d["category"] == "餐饮"
        assert d["amount"] == 35.5
        assert d["confidence"] == 0.90
        assert d["status"] == "confirmed"
        assert d["source"] == "rule"


class TestClassifyConvenienceFunction:
    """Test classify convenience function."""

    def test_classify_returns_dict(self):
        """Test classify function returns dict."""
        with patch("ai.classifier.classify_with_ai") as mock_ai:
            mock_ai.return_value = {
                "category": "交通",
                "amount": 25.0,
                "confidence": 0.88,
            }
            result = classify("打车")

            assert isinstance(result, dict)
            assert result["category"] == "交通"
            assert result["status"] == "confirmed"
