import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.pipeline.cost_calc import CostCalculator

def test_calc_slab():
    calc = CostCalculator()
    result = calc.calculate_slab(10, 8)
    assert result["type"] == "УШП утепленная шведская плита"
    assert result["total"] > 0
    assert result["materials"] > 0
    assert result["work"] > 0

def test_calc_piles():
    calc = CostCalculator()
    result = calc.calculate_piles(10, 8, 20)
    assert result["type"] == "Свайно-винтовой фундамент"
    assert result["pile_count"] == 20
    assert result["total"] > 0

def test_calc_piles_auto_count():
    calc = CostCalculator()
    result = calc.calculate_piles(10, 8)
    assert result["pile_count"] >= 4
    assert result["total"] > 0

def test_calculate_with_self_build():
    calc = CostCalculator()
    params = {"width": 10, "length": 8, "self_build": True}
    result = calc.calculate("Ленточный фундамент", params)
    assert result["work"] == 0
    assert result["self_build"] == True
    assert result["total"] == result["materials"] + result["delivery"] + result["overhead"]

def test_calculate_without_self_build():
    calc = CostCalculator()
    params = {"width": 10, "length": 8, "self_build": False}
    result = calc.calculate("Ленточный фундамент", params)
    assert result["work"] > 0

def test_calculate_slab_different_sizes():
    calc = CostCalculator()
    result_6x6 = calc.calculate_slab(6, 6)
    result_12x12 = calc.calculate_slab(12, 12)
    assert result_12x12["total"] > result_6x6["total"]