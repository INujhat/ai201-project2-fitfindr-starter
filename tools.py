import os
import re
from dotenv import load_dotenv
from groq import Groq
from utils.data_loader import load_listings

load_dotenv()

def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set.")
    return Groq(api_key=api_key)

def search_listings(description, size=None, max_price=None):
    listings = load_listings()
    keywords = description.lower().split()
    filtered = []
    for item in listings:
        if max_price is not None and item["price"] > max_price:
            continue
        if size is not None and size.lower() not in item["size"].lower():
            continue
        filtered.append(item)
    scored = []
    for item in filtered:
        text = (item["title"] + " " + item["description"] + " " + " ".join(item["style_tags"])).lower()
        score = sum(1 for word in keywords if word in text)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored]

def suggest_outfit(new_item, wardrobe):
    client = _get_groq_client()
    item_desc = f"{new_item['title']} ({new_item['condition']}, ${new_item['price']}, {new_item['platform']})"
    if not wardrobe.get("items"):
        prompt = f"I just thrifted: {item_desc}. Give me 1-2 general outfit ideas. Be specific about vibe and style."
    else:
        wardrobe_text = "\n".join(f"- {w['name']} ({w.get('category', '')})" for w in wardrobe["items"])
        prompt = f"I just thrifted: {item_desc}.\n\nMy wardrobe:\n{wardrobe_text}\n\nSuggest 1-2 specific outfit combinations using pieces from my wardrobe."
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content

def create_fit_card(outfit, new_item):
    if not outfit or not outfit.strip():
        return "Error: No outfit suggestion available to create a fit card."
    client = _get_groq_client()
    prompt = f"""Write a casual 2-3 sentence Instagram caption for this thrifted outfit.
Item: {new_item['title']} — ${new_item['price']} from {new_item['platform']}
Outfit: {outfit}
Rules:
- Sound like a real person posting on Instagram
- Mention the item name, price, and platform naturally once each
- Use specific words about the vibe
- Keep it short and fun"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=1.2,
    )
    return response.choices[0].message.content