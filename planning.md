# FitFindr — planning.md

---

## Tools

### Tool 1: search_listings

**What it does:**
Searches the mock listings dataset for secondhand items matching the user's description, size, and price. Returns a ranked list of matching items sorted by relevance.

**Input parameters:**
- `description` (str): Keywords describing what the user wants (e.g. "vintage graphic tee")
- `size` (str or None): Size to filter by (e.g. "M"), or None to skip size filtering
- `max_price` (float or None): Maximum price inclusive, or None to skip price filtering

**What it returns:**
A list of matching listing dicts sorted by relevance score. Each dict contains: id, title, description, category, style_tags, size, condition, price, colors, brand, platform. Returns empty list if nothing matches.

**What happens if it fails or returns nothing:**
The agent sets session["error"] with a helpful message telling the user what to try differently (broader keywords, different size, higher price) and returns early without calling the other tools.

---

### Tool 2: suggest_outfit

**What it does:**
Given a thrifted item and the user's wardrobe, uses an LLM to suggest 1-2 complete outfit combinations using pieces the user already owns.

**Input parameters:**
- `new_item` (dict): The listing dict for the item the user is considering buying
- `wardrobe` (dict): A wardrobe dict with an 'items' key containing a list of wardrobe item dicts

**What it returns:**
A non-empty string with specific outfit suggestions. If wardrobe is empty, returns general styling advice instead.

**What happens if it fails or returns nothing:**
If wardrobe is empty, the LLM is prompted for general styling ideas instead of crashing. The function always returns a non-empty string.

---

### Tool 3: create_fit_card

**What it does:**
Generates a short, casual Instagram-style caption for the thrifted outfit. Sounds like a real person posting an OOTD, not a product description.

**Input parameters:**
- `outfit` (str): The outfit suggestion string from suggest_outfit()
- `new_item` (dict): The listing dict for the thrifted item

**What it returns:**
A 2-4 sentence string usable as an Instagram caption mentioning the item name, price, and platform naturally.

**What happens if it fails or returns nothing:**
If outfit is empty or whitespace, returns a descriptive error message string instead of crashing.

---

## Planning Loop

The agent follows these steps in order:

1. Parse the user's query using regex to extract description, size, and max_price
2. Call search_listings() with parsed parameters
3. Check if results is empty — if yes, set session["error"] and return early. Do NOT call suggest_outfit with empty input.
4. If results found, set session["selected_item"] = results[0]
5. Call suggest_outfit() with selected_item and wardrobe
6. Call create_fit_card() with outfit_suggestion and selected_item
7. Return completed session

---

## State Management

All state is stored in a session dict initialized at the start of each interaction. Fields:
- session["parsed"] — stores extracted description, size, max_price from query
- session["search_results"] — stores full list returned by search_listings()
- session["selected_item"] — stores top result, passed into suggest_outfit()
- session["outfit_suggestion"] — stores string returned by suggest_outfit(), passed into create_fit_card()
- session["fit_card"] — stores final caption string
- session["error"] — set if anything fails, causes early return

---

## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Sets session["error"] with message telling user to try broader keywords, different size, or higher price. Returns early without calling other tools. |
| suggest_outfit | Wardrobe is empty | Prompts LLM for general styling advice instead of outfit combinations. Always returns a non-empty string. |
| create_fit_card | Outfit input is missing or empty | Returns descriptive error string "Error: No outfit suggestion available to create a fit card." without raising an exception. |

---

## Architecture