import difflib

def resolve_entity(token: str, known_entities: list[str]) -> tuple[str | None, float]:
    if not token:
        return None, 0.0
        
    token = token.lower().strip()
    
    for entity in known_entities:
        if token == entity.lower():
            return entity, 1.0
            
    for entity in known_entities:
        if entity.lower().startswith(token) or token.startswith(entity.lower()):
            return entity, 0.9
            
    matches = difflib.get_close_matches(token, [e.lower() for e in known_entities], n=1, cutoff=0.75)
    if matches:
        best_lower = matches[0]
        best_match = next(e for e in known_entities if e.lower() == best_lower)
        similarity = difflib.SequenceMatcher(None, token, best_lower).ratio()
        return best_match, similarity
        
    return None, 0.0
