import re
from tools import search_listings, suggest_outfit, create_fit_card

def _new_session(query, wardrobe):
    return {
        "query": query,
        "parsed": {},
        "search_results": [],
        "selected_item": None,
        "wardrobe": wardrobe,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None,
    }

def _parse_query(query):
    size_match = re.search(r'\bsize\s+(\w+)\b|\b(XS|S|M|L|XL|XXL|XXS)\b', query, re.IGNORECASE)
    price_match = re.search(r'under\s+\$?(\d+)', query, re.IGNORECASE)
    size = size_match.group(1) or size_match.group(2) if size_match else None
    max_price = float(price_match.group(1)) if price_match else None
    description = re.sub(r'(size\s+\w+|under\s+\$?\d+|in\s+size\s+\w+)', '', query, flags=re.IGNORECASE).strip()
    return {"description": description, "size": size, "max_price": max_price}

def run_agent(query, wardrobe):
    session = _new_session(query, wardrobe)
    parsed = _parse_query(query)
    session["parsed"] = parsed
    results = search_listings(parsed["description"], parsed["size"], parsed["max_price"])
    session["search_results"] = results
    if not results:
        session["error"] = (
            f"No listings found for '{parsed['description']}'"
            + (f" in size {parsed['size']}" if parsed["size"] else "")
            + (f" under ${parsed['max_price']}" if parsed["max_price"] else "")
            + ". Try broader keywords, a different size, or a higher price."
        )
        return session
    session["selected_item"] = results[0]
    session["outfit_suggestion"] = suggest_outfit(session["selected_item"], wardrobe)
    session["fit_card"] = create_fit_card(session["outfit_suggestion"], session["selected_item"])
    return session

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe
    print("=== Happy path: graphic tee ===\n")
    session = run_agent("looking for a vintage graphic tee under $30", get_example_wardrobe())
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")
    print("\n\n=== No-results path ===\n")
    session2 = run_agent("designer ballgown size XXS under $5", get_example_wardrobe())
    print(f"Error message: {session2['error']}")