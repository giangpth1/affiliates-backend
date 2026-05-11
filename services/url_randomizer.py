"""
URL randomization utilities to avoid Shopee bot detection.
Randomizes all query parameter values while keeping structure.
"""
import random
import string
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def randomize_shopee_url(url: str) -> str:
    """
    Randomize all query parameter values in Shopee URL to avoid detection.
    
    Keeps URL structure but changes param values to random strings/numbers.
    
    Args:
        url: Original Shopee URL with tracking params
        
    Returns:
        URL with randomized parameter values
        
    Example:
        Input:  shopee.vn/abc-i.123.456?af_siteid=123&utm_source=xyz
        Output: shopee.vn/abc-i.123.456?af_siteid=789&utm_source=pqr
    """
    parsed = urlparse(url)
    
    if not parsed.query:
        # No params to randomize, return as-is
        return url
    
    params = parse_qs(parsed.query, keep_blank_values=True)
    randomized_params = {}
    
    for key, values in params.items():
        # Randomize each param value
        randomized_values = []
        for value in values:
            if not value:
                randomized_values.append('')
                continue
            
            # Detect value type and randomize accordingly
            randomized_value = _randomize_value(value, key)
            randomized_values.append(randomized_value)
        
        # Keep only first value (most params are single-valued)
        randomized_params[key] = randomized_values[0] if randomized_values else ''
    
    # Reconstruct URL with randomized params
    new_query = urlencode(randomized_params)
    randomized_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return randomized_url


def _randomize_value(value: str, key: str) -> str:
    """
    Randomize a single parameter value based on its type.
    
    Args:
        value: Original param value
        key: Param name (for context)
        
    Returns:
        Randomized value matching original format
    """
    # If value looks like a number (digits only)
    if value.isdigit():
        # Keep similar length but randomize digits
        num_digits = len(value)
        if num_digits <= 3:
            # Small number (e.g., siteid)
            return str(random.randint(100, 999))
        elif num_digits <= 6:
            # Medium number
            return str(random.randint(100000, 999999))
        else:
            # Large number (timestamp-like)
            return str(random.randint(10**(num_digits-1), 10**num_digits - 1))
    
    # If value looks like hex (alphanumeric, possibly with hyphens)
    if all(c in string.hexdigits + '-' for c in value) and len(value) > 8:
        # Looks like UUID or hash
        return _random_hex_string(len(value))
    
    # If value has mixed alphanumeric (like tracking codes)
    if any(c.isdigit() for c in value) and any(c.isalpha() for c in value):
        # Mixed alphanumeric - randomize while keeping structure
        result = []
        for char in value:
            if char.isdigit():
                result.append(str(random.randint(0, 9)))
            elif char.isalpha():
                if char.isupper():
                    result.append(random.choice(string.ascii_uppercase))
                else:
                    result.append(random.choice(string.ascii_lowercase))
            else:
                result.append(char)  # Keep special chars (-, _, etc.)
        return ''.join(result)
    
    # If value is alphabetic string
    if value.isalpha():
        # Keep length, randomize letters
        if value.isupper():
            return ''.join(random.choices(string.ascii_uppercase, k=len(value)))
        elif value.islower():
            return ''.join(random.choices(string.ascii_lowercase, k=len(value)))
        else:
            # Mixed case - keep case pattern
            result = []
            for char in value:
                if char.isupper():
                    result.append(random.choice(string.ascii_uppercase))
                else:
                    result.append(random.choice(string.ascii_lowercase))
            return ''.join(result)
    
    # Fallback: random alphanumeric of same length
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=len(value)))


def _random_hex_string(length: int) -> str:
    """Generate random hex-like string."""
    result = []
    for _ in range(length):
        char = random.choice(string.hexdigits.lower() + '-')
        result.append(char)
    return ''.join(result)


# Example usage
if __name__ == '__main__':
    test_urls = [
        'https://shopee.vn/abc-def-i.123456.789012?af_siteid=123&utm_source=xyz&aff_sid=abc123XYZ',
        'https://s.shopee.vn/abc123?utm_campaign=test&tracker=hash-123-abc',
    ]
    
    for url in test_urls:
        print(f"Original:   {url}")
        print(f"Randomized: {randomize_shopee_url(url)}")
        print()
