import pytest
from app.utils.code_generator import generate_random_code

def test_generate_random_code_default_length():
    """Test that generate_random_code returns a code with default length 6"""
    code = generate_random_code()
    assert len(code) == 6
    assert code.isdigit()

def test_generate_random_code_custom_length():
    """Test that generate_random_code returns a code with custom length"""
    code = generate_random_code(length=8)
    assert len(code) == 8
    assert code.isdigit()

def test_generate_random_code_uniqueness():
    """Test that generate_random_code generates different codes on multiple calls"""
    code1 = generate_random_code()
    code2 = generate_random_code()
    assert code1 != code2  # This could theoretically fail but is extremely unlikely 