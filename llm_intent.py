import os
import re
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

    This is our fallback system in case Claude is
    unavailable or there are no API credits.
    """

    text = user_text.lower()

    # --------------------------------------------------------
    # Find budget
    # --------------------------------------------------------

    price_match = re.search(
        r"(?:under|below|within|budget(?:\s+of)?|maximum|max)"
        r"\s*[₹rs.]?\s*(\d+(?:,\d+)?)",
        text
    )

    if price_match:
        max_price = int(price_match.group(1).replace(",", ""))
    else:
        max_price = None

    # --------------------------------------------------------
    # Find category and tags
    # --------------------------------------------------------

    category = None
    tags = []

    # SHOES
    if "shoe" in text or "running" in text or "sneaker" in text:

        category = "shoes"

        if "running" in text:
            tags.append("running")

        if "sneaker" in text:
            tags.append("sneakers")

        if "casual" in text:
            tags.append("casual")

        if "formal" in text:
            tags.append("formal")

        if "sports" in text:
            tags.append("sports")

        if not tags:
            tags.append("shoes")

    # FURNITURE
    elif (
        "sofa" in text
        or "furniture" in text
        or "chair" in text
        or "table" in text
        or "bed" in text
    ):

        category = "furniture"

        if "sofa" in text:
            tags.append("sofa")

        if "chair" in text:
            tags.append("chair")

        if "table" in text:
            tags.append("table")

        if "bed" in text:
            tags.append("bed")

        if not tags:
            tags.append("furniture")

    # ELECTRONICS
    elif (
        "headphone" in text
        or "earphone" in text
        or "earbud" in text
        or "phone" in text
        or "smartphone" in text
        or "laptop" in text
        or "tablet" in text
        or "electronics" in text
    ):

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

        if not tags:
            tags.append("electronics")

    return {
        "category": category,
        "tags": tags,
        "max_price": max_price
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
    "max_price": 3000
}}

Rules:
- category should be a simple product category.
- tags should contain useful product characteristics.
- max_price should be a number.
- If the user does not provide a budget, use null.
- Do not include explanations.
"""
            }
        ]
    )

    response_text = response.content[0].text

    return response_text


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

        except Exception as error:

            print("Claude unavailable.")
            print("Using rule-based fallback.")

    # --------------------------------------------------------
    # Fallback
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