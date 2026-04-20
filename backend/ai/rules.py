"""规则引擎 - 基于正则表达式的消费分类"""
import re
from typing import Optional
import yaml
from pathlib import Path


class RuleEngine:
    """加载 rules.yaml 并进行规则匹配"""

    def __init__(self, rules_path: Optional[str] = None):
        if rules_path is None:
            rules_path = Path(__file__).parent / "rules.yaml"
        self.rules_path = Path(rules_path)
        self._rules: dict = {}
        self._amount_pattern: re.Pattern = None
        self._compile_patterns()
        self._load_rules()

    def _load_rules(self):
        """从 YAML 文件加载规则"""
        with open(self.rules_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self._rules = {}
        categories = data.get("categories", {})
        for cat_name, cat_data in categories.items():
            patterns = cat_data.get("patterns", [])
            self._rules[cat_name] = {
                "patterns": [re.compile(p, re.IGNORECASE) for p in patterns],
                "icon": cat_data.get("icon", "📦"),
                "color": cat_data.get("color", "#C0C0C0"),
            }

        # 编译金额正则
        amount_str = data.get("amount_pattern", r'¥?(\d+(?:\.\d+)?)\s*(?:元|块|rmb)?|(\d+(?:\.\d+)?)\s*$')
        self._amount_pattern = re.compile(amount_str)

    def _compile_patterns(self):
        """预编译所有正则表达式（可选优化）"""
        pass

    def extract_amount(self, text: str) -> Optional[float]:
        """从文本中提取金额"""
        match = self._amount_pattern.search(text)
        if match:
            # 两个捕获组，优先取有值的那个
            for group in match.groups():
                if group:
                    return float(group)
        return None

    def match(self, text: str) -> Optional[tuple[str, float, float]]:
        """
        尝试匹配规则
        返回: (category, amount, confidence) 或 None
        confidence 固定为 1.0（规则匹配）
        """
        for category, rule_data in self._rules.items():
            for pattern in rule_data["patterns"]:
                if pattern.search(text):
                    amount = self.extract_amount(text)
                    return (category, amount, 1.0)
        return None

    def get_all_categories(self) -> list[str]:
        """返回所有支持分类"""
        return list(self._rules.keys())


# 单例
_engine: Optional[RuleEngine] = None


def get_engine() -> RuleEngine:
    global _engine
    if _engine is None:
        _engine = RuleEngine()
    return _engine


def match_rule(text: str) -> Optional[tuple[str, float, float]]:
    """快捷函数：匹配规则"""
    return get_engine().match(text)


def extract_amount(text: str) -> Optional[float]:
    """快捷函数：提取金额"""
    return get_engine().extract_amount(text)
