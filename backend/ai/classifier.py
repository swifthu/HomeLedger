"""AI 分类器 - 规则引擎 + AI 两阶段分类"""
from typing import Optional
from .rules import match_rule, RuleEngine
from .client import classify_with_ai
from .prompts import SYSTEM_PROMPT


class ClassifierResult:
    def __init__(
        self,
        category: str,
        amount: Optional[float],
        confidence: float,
        status: str,  # "confirmed" | "pending_review"
        source: str,  # "rule" | "ai"
    ):
        self.category = category
        self.amount = amount
        self.confidence = confidence
        self.status = status  # confirmed 或 pending_review
        self.source = source

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "amount": self.amount,
            "confidence": self.confidence,
            "status": self.status,
            "source": self.source,
        }


class Classifier:
    """两级分类器：规则优先，AI 兜底"""

    def __init__(self, rule_engine: Optional[RuleEngine] = None):
        self.rule_engine = rule_engine or RuleEngine()

    def check(self, text: str) -> Optional[ClassifierResult]:
        """
        第一阶段：规则检查
        返回 None 表示规则未命中，需要 AI 分类
        """
        result = match_rule(text)
        if result:
            category, amount, confidence = result
            return ClassifierResult(
                category=category,
                amount=amount,
                confidence=confidence,
                status="confirmed",  # 规则匹配直接确认
                source="rule",
            )
        return None

    def classify(self, text: str) -> ClassifierResult:
        """
        第二阶段：AI 分类（规则未命中时）
        根据 AI confidence 决定 status
        """
        ai_result = classify_with_ai(text, SYSTEM_PROMPT)

        category = ai_result.get("category", "其他")
        amount = ai_result.get("amount")
        confidence = ai_result.get("confidence", 0.5)

        # 根据置信度决定状态
        if confidence >= 0.85:
            status = "confirmed"
        else:
            status = "pending_review"

        return ClassifierResult(
            category=category,
            amount=amount,
            confidence=confidence,
            status=status,
            source="ai",
        )

    def classify_text(self, text: str) -> ClassifierResult:
        """
        完整分类流程：规则 -> AI -> 结果
        """
        rule_result = self.check(text)
        if rule_result:
            return rule_result
        return self.classify(text)


# 单例
_classifier: Optional[Classifier] = None


def get_classifier() -> Classifier:
    global _classifier
    if _classifier is None:
        _classifier = Classifier()
    return _classifier


def classify(text: str) -> dict:
    """快捷函数：完整分类"""
    return get_classifier().classify_text(text).to_dict()
