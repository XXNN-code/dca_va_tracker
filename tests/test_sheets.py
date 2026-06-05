"""sheets 模块测试"""
from dca_va_tracker.sheets import normalize_ticker


def test_normalize_ticker():
    # China fund code (pure digits, length <= 6)
    assert normalize_ticker("218") == "000218"
    assert normalize_ticker(218) == "000218"
    assert normalize_ticker("000218") == "000218"
    assert normalize_ticker("218", market="China") == "000218"

    # Canada stock code (not pure digits or length > 6)
    assert normalize_ticker("CGL.TO") == "CGL.TO"
    assert normalize_ticker("TSLA") == "TSLA"
