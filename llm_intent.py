import os
import re
import json
import anthropic
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")


# ============================================================
# CREATE CLAUDE CLIENT
# ============================================================

client = None

if api_key:
    client = anthropic.Anthropic(api_key=api_key)


# ============================================================
# RULE-BASED FALLBACK
# ============================================================

def fallback_parse_intent(user_text):
    """
    Extract shopping intent without using an LLM.

    This works as a fallback when Claude is unavailable
    or there are no API credits.
    """

    text = user_text.lower().strip()

    # --------------------------------------------------------
    # FIND BUDGET
    # --------------------------------------------------------

    max_price = None

    # Examples:
    # under 3000
    # below ₹3000
    # under Rs 3000
    # budget 3000
    # maximum 5000
    # max 5000

    price_match = re.search(
        r"(?:under|below|within|budget(?:\s+of)?|maximum|max)"
        r"\s*(?:₹|rs\.?|inr)?\s*"
        r"(\d+(?:,\d+)?)"
        r"\s*(?:k)?",
        text
    )

    if price_match:

        price_text = price_match.group(1).replace(",", "")

        max_price = int(price_text)

        # Handle values such as "3k"
        if "k" in price_match.group(0):
            max_price *= 1000

    # --------------------------------------------------------
    # CATEGORY AND TAGS
    # --------------------------------------------------------

    category = None
    tags = []

    # ========================================================
    # SHOES
    # ========================================================

    if any(word in text for word in [
        "shoe",
        "shoes",
        "sneaker",
        "sneakers",
        "running"
    ]):

        category = "shoes"

        if "running" in text:
            tags.append("running")

        if "sneaker" in text:
            tags.append("sneakers")

        if "casual" in text:
            tags.append("casual")

        if "formal" in text:
            tags.append("formal")

        if "sports" in text or "sport" in text:
            tags.append("sports")

    # ========================================================
    # FURNITURE
    # ========================================================

    elif any(word in text for word in [
        "sofa",
        "furniture",
        "chair",
        "table",
        "bed"
    ]):

        category = "furniture"

        if "sofa" in text:
            tags.append("sofa")

        if "chair" in text:
            tags.append("chair")

        if "table" in text:
            tags.append("table")

        if "bed" in text:
            tags.append("bed")

    # ========================================================
    # ELECTRONICS
    # ========================================================

    elif any(word in text for word in [
        "headphone",
        "headphones",
        "earphone",
        "earphones",
        "earbud",
        "earbuds",
        "phone",
        "smartphone",
        "laptop",
        "tablet",
        "electronics"
    ]):

        category = "electronics"

        if "headphone" in text:
            tags.append("headphones")

        if "earphone" in text:
            tags.append("earphones")

        if "earbud" in text:
            tags.append("earbuds")

        if "phone" in text or "smartphone" in text:
            tags.append("smartphone")

        if "laptop" in text:
            tags.append("laptop")

        if "tablet" in text:
            tags.append("tablet")

        if "wireless" in text:
            tags.append("wireless")

        if "gaming" in text:
            tags.append("gaming")

    # ========================================================
    # CLOTHING
    # ========================================================

    elif any(word in text for word in [
        "shirt",
        "tshirt",
        "t-shirt",
        "jeans",
        "dress",
        "jacket",
        "hoodie",
        "clothes",
        "clothing"
    ]):

        category = "clothing"

        if "shirt" in text:
            tags.append("shirt")

        if "tshirt" in text or "t-shirt" in text:
            tags.append("tshirt")

        if "jeans" in text:
            tags.append("jeans")

        if "dress" in text:
            tags.append("dress")

        if "jacket" in text:
            tags.append("jacket")

        if "hoodie" in text:
            tags.append("hoodie")

    # ========================================================
    # BEAUTY
    # ========================================================

    elif any(word in text for word in [
        "makeup",
        "lipstick",
        "foundation",
        "mascara",
        "skincare",
        "moisturizer",
        "serum",
        "sunscreen",
        "beauty"
    ]):

        category = "beauty"

        if "lipstick" in text:
            tags.append("lipstick")

        if "foundation" in text:
            tags.append("foundation")

        if "mascara" in text:
            tags.append("mascara")

        if "moisturizer" in text:
            tags.append("moisturizer")

        if "serum" in text:
            tags.append("serum")

        if "sunscreen" in text:
            tags.append("sunscreen")

    # ========================================================
    # BAGS
    # ========================================================

    elif any(word in text for word in [
        "bag",
        "handbag",
        "backpack",
        "purse"
    ]):

        category = "bags"

        if "handbag" in text:
            tags.append("handbag")

        if "backpack" in text:
            tags.append("backpack")

        if "purse" in text:
            tags.append("purse")

    # ========================================================
    # GENERIC FALLBACK
    # ========================================================

    else:
        """
        If the product is not in our predefined categories,
        use the user's text as the search query.

        This means the system can still search for products
        that we haven't explicitly programmed.
        """

        category = "general"

    # --------------------------------------------------------
    # REMOVE SHOPPING WORDS FROM GENERIC QUERY
    # --------------------------------------------------------

    search_text = text

    # Remove budget phrase
    search_text = re.sub(
        r"(?:under|below|within|budget(?:\s+of)?|maximum|max)"
        r"\s*(?:₹|rs\.?|inr)?\s*"
        r"\d+(?:,\d+)?\s*k?",
        "",
        search_text
    )

    # Remove common conversational phrases
    phrases_to_remove = [
        "i need",
        "i want",
        "i am looking for",
        "i'm looking for",
        "looking for",
        "find me",
        "find",
        "show me",
        "search for",
        "search",
        "please",
        "get me",
        "buy me",
        "can you find",
        "can you get"
    ]

    for phrase in phrases_to_remove:
        search_text = search_text.replace(phrase, " ")

    # --------------------------------------------------------
    # BUILD SEARCH QUERY
    # --------------------------------------------------------

    if category != "general":

        search_query = " ".join(tags)

        # If no useful tags were detected,
        # search using the category itself.
        if not search_query:
            search_query = category

    else:

        # For unknown products, use cleaned user text
        search_query = search_text

    # Clean extra spaces
    search_query = " ".join(search_query.split())

    # If cleaning accidentally produced nothing,
    # fall back to original text.
    if not search_query:
        search_query = text

    # --------------------------------------------------------
    # RETURN STRUCTURED INTENT
    # --------------------------------------------------------

    return {
        "category": category,
        "tags": tags,
        "max_price": max_price,
        "search_query": search_query
    }


# ============================================================
# CLAUDE INTENT PARSER
# ============================================================

def parse_with_claude(user_text):
    """
    Uses Claude to understand the user's shopping request.

    Returns a structured intent.
    """

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"""
You are a shopping intent parser.

Understand the following user request:

"{user_text}"

Return ONLY valid JSON in this exact format:

{{
    "category": "shoes",
    "tags": ["running"],
    "max_price": 3000,
    "search_query": "running shoes"
}}

Rules:

- category should be a simple product category.
- tags should contain useful product characteristics.
- max_price should be a number.
- If the user does not provide a budget, use null.
- search_query should contain the actual product terms
  that should be sent to a shopping search API.
- Remove conversational phrases such as
  "I need", "I want", "find me", etc.
- Do not include explanations.
"""
            }
        ]
    )

    response_text = response.content[0].text

    # Convert Claude's JSON string into a Python dictionary
    return json.loads(response_text)


# ============================================================
# MAIN INTENT PARSER
# ============================================================

def parse_intent(user_text):
    """
    Main intent parser.

    First tries Claude.
    If Claude is unavailable, it automatically
    uses the rule-based fallback.
    """

    # --------------------------------------------------------
    # Try Claude
    # --------------------------------------------------------

    if client:

        try:

            result = parse_with_claude(user_text)

            print("Intent parser: Claude")

            return result

        except Exception:

            print("Claude unavailable.")
            print("Using rule-based fallback.")

    # --------------------------------------------------------
    # Rule-based fallback
    # --------------------------------------------------------

    result = fallback_parse_intent(user_text)

    print("Intent parser: Rule-based")

    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    request = "I need running shoes under 3000"

    print("User request:")
    print(request)

    result = parse_intent(request)

    print("\nParsed intent:")
    print(result)