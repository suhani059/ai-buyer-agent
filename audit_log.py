import json
from datetime import datetime


AUDIT_FILE = "audit_log.jsonl"


def log_event(event_type, details):
    """
    Store one auditable event in JSON Lines format.
    Each event is written as a separate line.
    """

    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "details": details
    }

    with open(AUDIT_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"📝 Audit Log: {event_type}")


def log_intent(user_text, intent):
    log_event(
        "intent_parsed",
        {
            "user_input": user_text,
            "intent": intent
        }
    )


def log_security(product, status):
    log_event(
        "security_check",
        {
            "product": product.get("name"),
            "platform": product.get("platform"),
            "status": status
        }
    )


def log_recommendation(product):
    log_event(
        "recommendation",
        {
            "product": product.get("name"),
            "platform": product.get("platform"),
            "price": product.get("offer_price"),
            "rating": product.get("rating")
        }
    )


def log_confirmation(product, confirmed):
    log_event(
        "user_confirmation",
        {
            "product": product.get("name"),
            "price": product.get("offer_price"),
            "confirmed": confirmed
        }
    )


def log_payment(order_id, amount, status):
    log_event(
        "payment",
        {
            "order_id": order_id,
            "amount": amount,
            "status": status
        }
    )