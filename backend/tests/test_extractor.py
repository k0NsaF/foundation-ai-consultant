import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.pipeline.extractor import ParameterExtractor

def test_extractor_material():
    extractor = ParameterExtractor()
    result = extractor.extract("Дом из газобетона")
    assert result["material"] == "газобетон"

def test_extractor_brick():
    extractor = ParameterExtractor()
    result = extractor.extract("кирпичный дом")
    assert result["material"] == "кирпич"

def test_extractor_wood():
    extractor = ParameterExtractor()
    result = extractor.extract("дом из бруса")
    assert result["material"] == "брус"

def test_extractor_floors():
    extractor = ParameterExtractor()
    result = extractor.extract("2 этажа")
    assert result["floors"] == 2

def test_extractor_size():
    extractor = ParameterExtractor()
    result = extractor.extract("10х8 метров")
    assert result["width"] == 10
    assert result["length"] == 8

def test_extractor_city():
    extractor = ParameterExtractor()
    result = extractor.extract("строим в Сургуте")
    assert result["city"] == "сургут"

def test_extractor_soil():
    extractor = ParameterExtractor()
    result = extractor.extract("грунт суглинок")
    assert result["soil"] == "суглинок"

def test_extractor_budget():
    extractor = ParameterExtractor()
    result = extractor.extract("бюджет 500000")
    assert result["budget"] == 500000

def test_extractor_self_build():
    extractor = ParameterExtractor()
    result = extractor.extract("буду строить своими руками")
    assert result["self_build"] == True

def test_extractor_desired_month():
    extractor = ParameterExtractor()
    result = extractor.extract("хочу начать в июне")
    assert result["desired_month"] == "июнь"

def test_extractor_silnopuchinistaya():
    extractor = ParameterExtractor()
    result = extractor.extract("грунт сильнопучинистая глина")
    assert result["soil"] == "сильнопучинистая глина"