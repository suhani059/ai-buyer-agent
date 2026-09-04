# ============================================================
# AI BUYER AGENT
# Security + Explicit Confirmation + Razorpay Test Order
# ============================================================

from audit_log import (
    log_confirmation,
    log_payment,
    log_security
)

from security import detect_prompt_injection
from razorpay_payment import create_test_order


# ============================================================
# CONFIRMATION FUNCTION
# ============================================================

def request_confirmation(product):

    print("\n" + "=" * 50)
    print("🛒 PURCHASE CONFIRMATION")
    print("=" * 50)

    print(f"Product  : {product.get('name', 'Unknown')}")
    print(f"Platform : {product.get('platform', 'Unknown')}")
    print(f"Price    : ₹{product.get('offer_price', 'N/A')}")
    print("=" * 50)

    print("\n⚠️ No payment/order will be created without your confirmation.")

    while True:

        answer = input(
            "\nDo you want to proceed? (yes/no): "
        ).strip().lower()

        if answer in ["yes", "y"]:

            log_confirmation(product, True)

            print("✅ Purchase confirmed.")

            return True

        elif answer in ["no", "n"]:

            log_confirmation(product, False)

            print("❌ Purchase cancelled.")

            return False

        else:

            print("Please enter yes or no.")


# ============================================================
# PAYMENT GATE
# ============================================================

def payment_gate(product):

    print("\n🔐 Running security checks...")

    # --------------------------------------------------------
    # 1. PROMPT INJECTION SECURITY CHECK
    # --------------------------------------------------------

    fields_to_check = [
        "name",
        "brand",
        "description"
    ]

    for field in fields_to_check:

        value = product.get(field)

        if value and detect_prompt_injection(value):

            print("\n🚨 SECURITY THREAT DETECTED!")

            print(
                f"Suspicious content found in: {field}"
            )

            log_security(
                product,
                "BLOCKED"
            )

            print(
                "❌ Purchase blocked for security reasons."
            )

            return False

    log_security(
        product,
        "SAFE"
    )

    print("✅ Security check passed.")

    # --------------------------------------------------------
    # 2. USER CONFIRMATION
    # --------------------------------------------------------

    confirmed = request_confirmation(product)

    if not confirmed:

        print(
            "\n🛑 Payment flow stopped by user."
        )

        return False

    # --------------------------------------------------------
    # 3. PRICE VALIDATION
    # --------------------------------------------------------

    try:

        amount = float(
            product.get("offer_price")
        )

        if amount <= 0:

            print(
                "\n❌ Invalid product price."
            )

            return False

    except (TypeError, ValueError):

        print(
            "\n❌ Invalid product price."
        )

        return False

    # --------------------------------------------------------
    # 4. CREATE RAZORPAY TEST ORDER
    # --------------------------------------------------------

    print(
        "\n💳 Creating Razorpay Test Mode order..."
    )

    order = create_test_order(amount)

    if not order:

        log_payment(
            order_id="N/A",
            amount=amount,
            status="ORDER_CREATION_FAILED"
        )

        print(
            "\n❌ Payment order could not be created."
        )

        return False

    # --------------------------------------------------------
    # 5. LOG PAYMENT ORDER
    # --------------------------------------------------------

    order_id = order.get(
        "id",
        "Unknown"
    )

    log_payment(
        order_id=order_id,
        amount=amount,
        status="TEST_ORDER_CREATED"
    )

    print("\n" + "=" * 50)

    print(
        "✅ RAZORPAY TEST ORDER CREATED"
    )

    print("=" * 50)

    print(
        f"Order ID : {order_id}"
    )

    print(
        f"Amount   : ₹{amount}"
    )

    print(
        "Mode     : TEST"
    )

    print(
        "💡 No real money has been charged."
    )

    print("=" * 50)

    return True


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_product = {

        "name": "Wireless Headphones",

        "brand": "Demo Brand",

        "description": "Wireless headphones",

        "platform": "Flipkart",

        "offer_price": 1499,

        "mrp": 2499,

        "rating": 4.4
    }

    payment_gate(test_product)