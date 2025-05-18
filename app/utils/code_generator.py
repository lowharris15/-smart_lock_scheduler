import random
import string

def generate_random_code(length=6):
    """
    Generate a random numeric code of specified length
    
    Args:
        length (int): Length of the code to generate (default: 6)
        
    Returns:
        str: A random numeric code
    """
    return ''.join(random.choices(string.digits, k=length))
