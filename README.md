# FitFindr 🛍️

A multi-tool AI agent that helps users find secondhand clothing and figure out how to wear it.

---

## How to Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```
Then open http://localhost:7860 in your browser.

---

## Tool Inventory

### 1. search_listings
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None)
- **Output:** list of matching listing dicts sorted by relevance, each containing: id, title, description, category, style_tags, size, condition, price, colors, brand, platform
- **Purpose:** Searches the mock listings dataset for secondhand items matching the user's keywords, size, and price ceiling

### 2. suggest_outfit
- **Inputs:** `new_item` (dict), `wardrobe` (dict)
- **Output:** str — 1-2 outfit combinations using the new item and wardrobe pieces, or general styling advice if wardrobe is empty
- **Purpose:** Uses an LLM to suggest specific outfits by combining the thrifted item with pieces the user already owns

### 3. create_fit_card
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Output:** str — a 2-4 sentence casual Instagram-style caption mentioning the item name, price, and platform
- **Purpose:** Generates a shareable outfit caption that sounds like a real person posting an OOTD

---

## How the Planning Loop Works

The agent follows conditional logic in run_agent():

1. Parse the query with regex to extract description, size, and max_price
2. Call search_listings() with those parameters
3. **If results is empty** → set session["error"] with a helpful message and return early. suggest_outfit is never called with empty input.
4. **If results found** → set session["selected_item"] = results[0] and continue
5. Call suggest_outfit() with selected_item and wardrobe
6. Call create_fit_card() with outfit_suggestion and selected_item
7. Return the completed session

The key decision point is step 3 — the agent behaves differently based on what search_listings returns.

---

## State Management

All state is stored in a session dict created at the start of each interaction:

| Field | Set when | Used by |
|-------|----------|---------|
| session["parsed"] | After query parsing | search_listings |
| session["search_results"] | After search_listings | Planning loop check |
| session["selected_item"] | After search succeeds | suggest_outfit |
| session["outfit_suggestion"] | After suggest_outfit | create_fit_card |
| session["fit_card"] | After create_fit_card | Gradio UI |
| session["error"] | If any tool fails | Gradio UI, early return |

No data is re-entered by the user between steps — everything flows automatically through the session dict.

---

## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match | Sets session["error"]: "No listings found for '...' in size ... under $.... Try broader keywords, a different size, or a higher price." Returns early. |
| suggest_outfit | Wardrobe is empty | Prompts LLM for general styling advice instead of crashing. Always returns a non-empty string. |
| create_fit_card | Outfit string is empty | Returns "Error: No outfit suggestion available to create a fit card." without raising an exception. |

**Concrete example from testing:**
Running `python3 agent.py` with query "designer ballgown size XXS under $5" triggered the search_listings failure. The agent returned: "No listings found for 'designer ballgown' in size XXS under $5.0. Try broader keywords, a different size, or a higher price." — without crashing or calling the other tools.

---

## Spec Reflection

**One way the spec helped:** The requirement to test each tool in isolation before wiring them together saved a lot of debugging time. Finding the wardrobe field was named 'name' not 'title' was caught early because of isolated testing.

**One way implementation diverged:** The spec suggested using an LLM to parse the query. I used regex instead because it was faster, more predictable, and didn't require an extra API call for simple patterns like "under $30" and "size M".

---

## AI Usage

**Instance 1 — tools.py implementation:**
I gave Claude the Tool 1, 2, and 3 spec blocks from planning.md (inputs, return values, failure modes) and asked it to implement each function one at a time. Claude generated the keyword scoring logic for search_listings and the LLM prompts for suggest_outfit and create_fit_card. I overrode the wardrobe field from 'title' to 'name' after discovering the actual schema by running the data loader directly.

**Instance 2 — planning loop implementation:**
I gave Claude the agent diagram from planning.md and the Planning Loop section and asked it to implement run_agent() in agent.py. Claude generated the full session-based planning loop. I verified it correctly branched on empty search results and didn't call suggest_outfit unconditionally. I also switched query parsing from LLM-based to regex-based for reliability.