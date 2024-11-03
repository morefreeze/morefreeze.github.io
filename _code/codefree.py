from functools import lru_cache

def get_cyclic_shifts(word):
    """Get all cyclic shifts of a word"""
    n = len(word)
    shifts = []
    for i in range(n):
        shifts.append(word[i:] + word[:i])
    return shifts

def is_periodic(word):
    """Check if a word is periodic"""
    n = len(word)
    for i in range(1, n):
        if n % i == 0:
            period = word[:i]
            if period * (n//i) == word:
                return True
    return False

def is_prime_code(word):
    """Check if a word is a prime code (lexicographically minimal in its shift class)"""
    shifts = get_cyclic_shifts(word)
    return word == min(shifts)

# Cache decorator for find_prime_codes
@lru_cache(maxsize=None)
def find_prime_codes_cached(n, alphabet_str):
    """Cached version that takes immutable parameters"""
    codes = []
    
    def generate_words(length, prefix=""):
        """Generate all possible words of given length"""
        if length == 0:
            if not is_periodic(prefix) and is_prime_code(prefix):
                codes.append(prefix)
            return
            
        for letter in alphabet_str:
            generate_words(length-1, prefix + letter)
    
    generate_words(n)
    return tuple(sorted(codes))  # Return immutable tuple for caching

def find_prime_codes(n, alphabet):
    """Wrapper function that handles mutable alphabet parameter"""
    # Convert alphabet to immutable string for caching
    alphabet_str = ''.join(sorted(alphabet))
    return list(find_prime_codes_cached(n, alphabet_str))

def is_valid_commafree(word, existing_codes):
    """Check if adding word would maintain comma-free property"""
    n = len(word)
    
    # Check if word is periodic
    if is_periodic(word):
        return False
        
    # Check if word is a cyclic shift of any existing code
    shifts = get_cyclic_shifts(word)
    for code in existing_codes:
        if code in shifts:
            return False
            
    # Check concatenations with existing codes
    for code in existing_codes:
        # Check concatenations in both orders
        concat1 = code + word
        concat2 = word + code
        
        # Check all n-length substrings
        for i in range(1, n):
            substring1 = concat1[i:i+n]
            substring2 = concat2[i:i+n]
            
            # Check if any substring is a cyclic shift of any existing code
            for existing in existing_codes:
                if substring1 in existing or substring2 in existing:
                    return False
                
    return True

def find_maximal_commafree_codes(prime_codes):
    """Find maximal comma-free codes by selecting from prime codes"""
    maximal_codes = []
    
    def try_add_code(codes_to_try, current_set):
        """Try to add more codes to current set"""
        # Early pruning: if remaining codes + current set can't beat maximal_codes
        if len(codes_to_try) + len(current_set) <= len(maximal_codes):
            return
            
        if not codes_to_try:
            # If this set is larger than our current maximal set, replace it
            if len(current_set) > len(maximal_codes):
                maximal_codes.clear()
                maximal_codes.extend(current_set)
            return
            
        # Try adding the next code
        code = codes_to_try[0]
        remaining = codes_to_try[1:]
        
        # Check if we can add this code
        if is_valid_commafree(code, current_set):
            # Try with this code added
            try_add_code(remaining, current_set + [code])
        
        # Try without this code
        try_add_code(remaining, current_set)
    
    # Start with empty set and try to add codes
    try_add_code(prime_codes, [])
    return maximal_codes

# Example usage
if __name__ == "__main__":
    alphabet = "012"
    n = 4
    
    prime_codes = find_prime_codes(n, alphabet)
    print(f"Prime codes of length {n} over alphabet {alphabet}:")
    for code in prime_codes:
        print(f"{code} -> {get_cyclic_shifts(code)}")
    print(f"Total prime codes found: {len(prime_codes)}")
    
    print("\nMaximal comma-free codes:")
    codes = find_maximal_commafree_codes(prime_codes)
    codes.sort()
    for code in codes:
        print(code)
    print(f"Total codes found: {len(codes)}")
