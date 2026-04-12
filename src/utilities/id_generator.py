"""ID generation utilities"""
import time
import random
import string

def cuid() -> str:
    """
    Generate a cuid-like ID (collision-resistant unique identifier)
    Format: c + timestamp + counter + random
    """
    timestamp = str(int(time.time() * 1000))[-10:]  # Last 10 digits of millisecond timestamp
    counter = str(random.randint(0, 9999)).zfill(4)
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"c{timestamp}{counter}{random_part}"
