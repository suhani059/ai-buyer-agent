import re
INJECTION_PATTERNS =[
    r"ignore (all |any |the )?previous instructions",
    r"ignore (all |any |the )?instructions",
    r"system override",
    r"override (the )?system",
    r"buy this immedieately",
    r"without confirmation",
    r"do not ask for confirmation",
    r"ignore the user's budget",
]

def detect_prompt_injection(text):
    """
    Checks untrusted text for common prompt-injection patterns.

    Returns:
        tuple: (is_injection, matched_pattern)
    """

    text = text.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True, pattern

    return False, None


def screen_product(product):
    """
    Checks a product description for prompt injection.

    Returns:
        tuple: (is_safe, reason)
    """

    is_injection, pattern = detect_prompt_injection(product["description"])

    if is_injection:
        return False, f"Prompt injection detected: {pattern}"

    return True, "Product description passed security screening."

if __name__ == "__main__":

    from catalog import PRODUCT_CATALOG

    for product in PRODUCT_CATALOG:

        safe, reason = screen_product(product)

        print("\nProduct:", product["name"])
        print("Safe:", safe)
        print("Reason:", reason)