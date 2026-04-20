"""Tests for rule engine and amount extraction."""
import pytest
from ai.rules import RuleEngine, match_rule, extract_amount


@pytest.fixture
def engine():
    return RuleEngine()


class TestRuleEnginePatterns:
    """Test all patterns from rules.yaml."""

    def test_dining_patterns(self, engine):
        """Test 餐饮 patterns."""
        assert engine.match("点外卖") is not None
        assert engine.match("下馆子") is not None
        assert engine.match("请客吃饭") is not None
        assert engine.match("买早餐") is not None
        assert engine.match("团购火锅") is not None
        assert engine.match("喝奶茶") is not None
        assert engine.match("吃火锅") is not None
        assert engine.match("订餐") is not None
        result = engine.match("餐厅小吃")
        assert result is not None
        assert result[0] == "餐饮"

    def test_transport_patterns(self, engine):
        """Test 交通 patterns."""
        assert engine.match("打车") is not None
        assert engine.match("加油") is not None
        assert engine.match("停车费") is not None
        assert engine.match("坐地铁") is not None
        assert engine.match("坐公交") is not None
        assert engine.match("地铁出行") is not None
        result = engine.match("打车费")
        assert result is not None
        assert result[0] == "交通"

    def test_shopping_patterns(self, engine):
        """Test 购物 patterns."""
        assert engine.match("买衣服") is not None
        assert engine.match("网购") is not None
        assert engine.match("超市购物") is not None
        assert engine.match("便利店") is not None
        assert engine.match("京东网购") is not None
        result = engine.match("天猫购物")
        assert result is not None
        assert result[0] == "购物"

    def test_housing_patterns(self, engine):
        """Test 居住 patterns."""
        assert engine.match("房租") is not None
        assert engine.match("水电费") is not None
        assert engine.match("物业费") is not None
        assert engine.match("话费") is not None
        assert engine.match("网费") is not None
        assert engine.match("燃气费") is not None
        result = engine.match("水电费")
        assert result is not None
        assert result[0] == "居住"

    def test_medical_patterns(self, engine):
        """Test 医疗 patterns."""
        assert engine.match("买药") is not None
        assert engine.match("去医院看病") is not None
        assert engine.match("药店") is not None
        assert engine.match("体检") is not None
        assert engine.match("门诊") is not None
        result = engine.match("医院")
        assert result is not None
        assert result[0] == "医疗"

    def test_entertainment_patterns(self, engine):
        """Test 娱乐 patterns."""
        assert engine.match("看电影") is not None
        assert engine.match("玩游戏") is not None
        assert engine.match("KTV唱歌") is not None
        assert engine.match("演唱会") is not None
        assert engine.match("旅游景点") is not None
        assert engine.match("门票") is not None
        result = engine.match("电影")
        assert result is not None
        assert result[0] == "娱乐"

    def test_education_patterns(self, engine):
        """Test 教育 patterns."""
        assert engine.match("培训课程") is not None
        assert engine.match("买书") is not None
        assert engine.match("学费") is not None
        assert engine.match("学习培训") is not None
        assert engine.match("考试") is not None
        result = engine.match("教育")
        assert result is not None
        assert result[0] == "教育"

    def test_other_patterns(self, engine):
        """Test 其他 patterns."""
        assert engine.match("红白喜事") is not None
        assert engine.match("随礼") is not None
        assert engine.match("送礼") is not None
        assert engine.match("买保险") is not None
        result = engine.match("捐款")
        assert result is not None
        assert result[0] == "其他"

    def test_non_matching_returns_none(self, engine):
        """Test non-matching text returns None."""
        assert engine.match("hello world") is None
        assert engine.match("这是一个测试") is None
        assert engine.match("random text 123") is None
        assert match_rule("not a expense") is None


class TestAmountExtraction:
    """Test amount extraction with various formats."""

    def test_chinese_yuan(self, engine):
        """Test 元 format."""
        assert engine.extract_amount("35.5元") == 35.5
        assert engine.extract_amount("100元") == 100.0
        assert engine.extract_amount("123.45元") == 123.45

    def test_chinese_kuai(self, engine):
        """Test 块 format."""
        assert engine.extract_amount("68块") == 68.0
        assert engine.extract_amount("30.5块") == 30.5

    def test_yen_symbol(self, engine):
        """Test ¥ format."""
        assert engine.extract_amount("¥100") == 100.0
        assert engine.extract_amount("¥50.5") == 50.5
        assert engine.extract_amount("¥25") == 25.0

    def test_plain_number(self, engine):
        """Test plain number format."""
        assert engine.extract_amount("100") == 100.0
        assert engine.extract_amount("99.99") == 99.99

    def test_with_text(self, engine):
        """Test amount embedded in text."""
        assert engine.extract_amount("花了35.5元买东西") == 35.5
        assert engine.extract_amount("消费68块") == 68.0
        assert engine.extract_amount("¥100的外卖") == 100.0

    def test_no_amount(self, engine):
        """Test text with no amount returns None."""
        assert engine.extract_amount("随便买点东西") is None
        assert engine.extract_amount("hello") is None

    def test_extract_amount_function(self):
        """Test standalone extract_amount function."""
        assert extract_amount("35.5元") == 35.5
        assert extract_amount("68块") == 68.0
        assert extract_amount("¥100") == 100.0
        assert extract_amount("100") == 100.0
        assert extract_amount("no amount here") is None


class TestRuleMatchConvenienceFunction:
    """Test match_rule convenience function."""

    def test_match_rule_returns_tuple(self):
        """Test match_rule returns (category, amount, confidence)."""
        result = match_rule("点外卖花了35.5元")
        assert result is not None
        category, amount, confidence = result
        assert category == "餐饮"
        assert amount == 35.5
        assert confidence == 1.0

    def test_match_rule_none_for_non_matching(self):
        """Test match_rule returns None for non-matching text."""
        assert match_rule("hello world") is None


class TestGetAllCategories:
    """Test get_all_categories method."""

    def test_returns_all_categories(self, engine):
        categories = engine.get_all_categories()
        assert "餐饮" in categories
        assert "交通" in categories
        assert "购物" in categories
        assert "居住" in categories
        assert "医疗" in categories
        assert "娱乐" in categories
        assert "教育" in categories
        assert "其他" in categories
