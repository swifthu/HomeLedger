"""AI 分类模块"""
from .rules import RuleEngine, match_rule, extract_amount, get_engine
from .classifier import Classifier, ClassifierResult, classify, get_classifier
from .client import AIClient, classify_with_ai, get_client
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

__all__ = [
    "RuleEngine",
    "match_rule",
    "extract_amount",
    "get_engine",
    "Classifier",
    "ClassifierResult",
    "classify",
    "get_classifier",
    "AIClient",
    "classify_with_ai",
    "get_client",
    "SYSTEM_PROMPT",
    "USER_PROMPT_TEMPLATE",
]
