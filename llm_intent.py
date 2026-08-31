import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("API key NOT found!")
    raise SystemExit

client = anthropic.Anthropic(api_key=api_key)

print("Claude client created successfully!")

import re


def fallback_parse_intent(user_text):
    """
    Extracts a basic shopping intent without using an LLM.

    Returns:
        dict containing category, tags, and maximum price.
    """

    text = user_text.lower()

    # -----------------------------
    # Find the budget
    # -----------------------------

    price_match = re.search(
        r"(?:under|below|within|budget(?:\s+of)?|maximum|max)\s*[₹rs.]?\s*(\d+(?:,\d+)?)",
        text
    )

    if price_match:
        max_price = int(price_match.group(1).replace(",", ""))
    else:
        max_price = None

    # -----------------------------
    # Find the category
    # -----------------------------

    category = None
    tags = []

    if "shoe" in text or "running" in text:
        category = "shoes"
        tags.append("running" if "running" in text else "shoes")

    elif "sofa" in text or "furniture" in text:
        category = "furniture"
        tags.append("sofa" if "sofa" in text else "furniture")

    elif (
        "headphone" in text
        or "earphone" in text
        or "electronics" in text
    ):
        category = "electronics"

        if "headphone" in text:
            tags.append("headphones")

        if "wireless" in text:
            tags.append("wireless")

    elif "phone" in text or "smartphone" in text:
        category = "electronics"
        tags.append("smartphone")

    return {
        "category": category,
        "tags": tags,
        "max_price": max_price
    }


if __name__ == "__main__":

    request = "I need running shoes under 3000"

    result = fallback_parse_intent(request)

    print("User request:")
    print(request)

    print("\nParsed intent:")
    print(result)

def ask_claude(user_text):
    """
    Sends the user's shopping request to Claude
    and returns Claude's response.
    """

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"""
Understand this shopping request:

{user_text}

Tell me what product the user wants
and what their maximum budget is.
"""
            }
        ]
    )

    return response.content[0].text

if __name__ == "__main__":

    request = "I need running shoes under 3000"

    result = ask_claude(request)

    print("\nClaude response:")
    print(result)

response = client.messages.create(...)


def extract_budget(text):
    """
    Extract the maximum budget from a shopping request.

    Example:
        "I need shoes under 3000" 
    """

    numbers = re.findall(r"\d+(?:,\d+)*", text)

    if not numbers:
        return None

    # convert "3,000" -> 3000
    budget = numbers[-1].replace(",", "")

    return int(budget)


if __name__ == "__main__":

    test_request = "I need running shoes under 3000"

    budget = extract_budget(test_request)

    print("User request:", test_request)
    print("Extracted budget:", budget)
    