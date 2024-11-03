import pytest
from hypothesis import given, example, strategies as st
from _code.codefree import (
    get_cyclic_shifts,
    is_periodic,
    is_prime_code,
    find_prime_codes,
    is_valid_commafree,
    find_maximal_commafree_codes
)

# Test cyclic shifts
@given(st.text(min_size=1, max_size=10))
def test_cyclic_shifts(word):
    shifts = get_cyclic_shifts(word)
    # Should return list of same-length strings
    assert all(len(s) == len(word) for s in shifts)
    # Should return exactly n shifts for length n word
    assert len(shifts) == len(word)
    # Original word should be in shifts
    assert word in shifts

# Test periodicity
@given(st.text(min_size=1, max_size=10))
def test_is_periodic(word):
    # Test known periodic words
    assert is_periodic(word * 2)  # Repeating any word is periodic
    # A single character repeated n times is periodic only if n > 1
    if len(word) > 1:
        assert is_periodic(word[0] * len(word))  # Repeating single char is periodic

@given(st.text(min_size=1, max_size=10))
def test_is_prime_code(word):
    shifts = get_cyclic_shifts(word)
    if is_prime_code(word):
        # If it's a prime code, it should be lexicographically minimal
        assert word == min(shifts)

# Test prime code finding
@given(st.integers(min_value=1, max_value=5), 
       st.lists(st.characters(min_codepoint=48, max_codepoint=57), min_size=1, max_size=3))
def test_find_prime_codes(n, alphabet):
    alphabet = list(set(alphabet))  # Remove duplicates
    if len(alphabet) > 0:
        codes = find_prime_codes(n, alphabet)
        # All codes should be of length n
        assert all(len(code) == n for code in codes)
        # All codes should use only characters from alphabet
        assert all(set(code).issubset(set(alphabet)) for code in codes)
        # All codes should be prime codes
        assert all(is_prime_code(code) for code in codes)
        # No code should be periodic
        assert all(not is_periodic(code) for code in codes)

# Test comma-free validation
def test_is_valid_commafree():
    # Test known valid cases
    assert not is_valid_commafree("01", ["10"])  # "01" and "10" do not overlap
    assert not is_valid_commafree("00", ["01", "10"])  # "00" does not overlap with "01" or "10"
    
    # Test known invalid cases
    assert not is_valid_commafree("01", ["01"])  # Same code
    assert not is_valid_commafree("11", [])  # Periodic
    assert not is_valid_commafree("01", ["001"])  # "01" is a prefix of "001"
    
    # Add more specific test cases
    assert is_valid_commafree("001", ["110"])  # Valid case
    assert not is_valid_commafree("001", ["100"])  # Invalid case - can overlap
    assert not is_valid_commafree("10", ["100"])  # "10" is a prefix of "100"

# Test maximal comma-free codes finding
@given(st.lists(st.text(min_size=2, max_size=2, alphabet="01"), min_size=1, max_size=5))
def test_find_maximal_commafree_codes(prime_codes):
    codes = find_maximal_commafree_codes(prime_codes)
    if codes:
        # All codes should be valid comma-free codes
        for i, code in enumerate(codes):
            assert is_valid_commafree(code, codes[:i] + codes[i+1:])

# Test specific examples
def test_specific_examples():
    # Test with known small examples
    alphabet = "01"
    n = 2
    prime_codes = find_prime_codes(n, alphabet)
    maximal_codes = find_maximal_commafree_codes(prime_codes)
    assert len(maximal_codes) > 0  # Should find at least one code

# Test caching behavior
def test_caching():
    # Test that repeated calls with same parameters return same result
    alphabet = "012"
    n = 3
    result1 = find_prime_codes(n, alphabet)
    result2 = find_prime_codes(n, alphabet)
    assert result1 == result2

if __name__ == "__main__":
    pytest.main([__file__]) 