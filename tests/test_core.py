import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from emi_calculator.core import amortization_schedule, calculate_emi


def test_emi_known_value():
    # 100,000 @ 10% for 12 months ~ 8,791.59
    assert round(calculate_emi(100_000, 10, 12), 2) == 8791.59


def test_zero_rate():
    assert calculate_emi(12_000, 0, 12) == 1000


def test_schedule_closes_to_zero_and_defaults():
    df = amortization_schedule(1_500_000, 4.5, None, "Home Loan")
    assert len(df) == 300
    assert df["Left-over Principal (AED)"].iloc[-1] == 0
    assert abs(df["Principal Paid (AED)"].sum() - 1_500_000) < 1
