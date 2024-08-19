import random

class APIKeyGenerator:
    def __init__(self):
        pass

    def generate(self, multiplier):
        # Characters to choose from: 0-9, a-z, A-Z
        characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        # Generate segments of random characters
        segment_lengths = [8, 4, 4, 4, 12]
        segments = []
        
        for length in segment_lengths:
            # Generate a random segment
            random_chars = ''.join(random.choices(characters, k=length))
            
            # Convert to an integer using base 36 (since we have digits + letters)
            segment_value = int(random_chars, 36)
            
            # Multiply by the given multiplier
            multiplied_value = segment_value * multiplier
            
            # Convert back to a string in base 36, ensuring it's the correct length
            multiplied_str = self.base36_encode(multiplied_value)
            segments.append(multiplied_str.zfill(length)[:length])
        
        # Combine segments with hyphens
        custom_uuid = '-'.join(segments)
        
        return custom_uuid

    def base36_encode(self, number):
        """Converts an integer to a base36 string."""
        assert number >= 0, 'Number must be non-negative'
        if number == 0:
            return '0'
        
        base36 = ''
        while number:
            number, i = divmod(number, 36)
            base36 = "0123456789abcdefghijklmnopqrstuvwxyz"[i] + base36
        
        return base36
