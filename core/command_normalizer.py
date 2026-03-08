import re

def normalize_command(raw_input: str) -> tuple[str, str]:
    # strip leading/trailing whitespace and convert to lowercase
    normalized = raw_input.strip().lower()
    
    # collapse multiple spaces into single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # detect if string is exact duplicate halves and reduce to one
    length = len(normalized)
    if length > 0 and length % 2 == 0:
        half = length // 2
        if normalized[:half] == normalized[half:]:
            normalized = normalized[:half].strip()
            
    return raw_input, normalized
