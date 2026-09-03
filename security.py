import re


# --------------------------------------------------
# PROMPT INJECTION DETECTION
# --------------------------------------------------

def detect_prompt_injection(text):

    if not text:
        return False

    text = str(text).lower()

    suspicious_patterns = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore the previous instruction",
        "disregard previous instructions",
        "forget previous instructions",
        "system prompt",
        "developer message",
        "reveal your instructions",
        "reveal the system prompt",
        "show me your prompt",
        "override your instructions",
        "bypass security",
        "bypass safety",
        "act as system",
        "you are now the system",
        "execute this instruction",
        "send payment",
        "make payment",
        "buy immediately",
    ]

    for pattern in suspicious_patterns:

        if pattern in text:
            return True

    return False


# --------------------------------------------------
# SANITIZE PRODUCT DATA
# --------------------------------------------------

def sanitize_product(product):

    """
    Product information comes from external sources,
    so we treat it as untrusted data.

    We do NOT allow product text to become an
    instruction for our AI agent.
    """

    safe_product = product.copy()

    text_fields = [
        "name",
        "brand",
        "description"
    ]

    for field in text_fields:

        value = safe_product.get(field)

        if value and detect_prompt_injection(value):

            safe_product[field] = "[⚠️ SUSPICIOUS CONTENT REMOVED]"

            safe_product["security_flag"] = True

    return safe_product


# --------------------------------------------------
# VALIDATE PRODUCT
# --------------------------------------------------

def validate_product(product):

    """
    Checks whether a product contains suspicious
    instructions before the agent uses it.
    """

    fields_to_check = [
        "name",
        "brand",
        "description"
    ]

    for field in fields_to_check:

        value = product.get(field)

        if value and detect_prompt_injection(value):

            return False

    return True