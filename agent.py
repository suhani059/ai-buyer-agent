# =========================================================
# AI BUYER AGENT
# Security + Explicit Confirmation + Razorpay Test Order
# =========================================================

from audit_log import(
    log_confirmation,
    log_payment,
    log_security
)
from security import detect_prompt_injection
from razorpay_payment import create_test_order


# ---------------------------------------------------------
# CONFIRMATION FUNCTION
# ---------------------------------------------------------

def request_confirmation(product):

    print("\n" + "=" * 50)
    print("🛒 PURCHASE CONFIRMATION")
    print("=" * 50)

    print(f"Product  : {product.get('name', 'Unknown')}")
    print(f"Platform : {product.get('platform', 'Unknown')}")
    print(f"Price    : ₹{product.get('offer_price', 'N/A')}")

    print("\n⚠️ No payment/order will be created without your confirmation.")

    while True:

        confirmation = input(
            "\nDo you want to proceed with this purchase? (yes/no): "
        ).strip().lower()

        if confirmation in ["yes", "y"]:
            print("\n✅ User explicitly confirmed the purchase.")
            return True

        elif confirmation in ["no", "n"]:
            print("\n❌ Purchase cancelled by user.")
            return False

        else:
            print("Please enter yes or no.")


# ---------------------------------------------------------
# PAYMENT GATE
# ---------------------------------------------------------

def payment_gate(product):

    # -----------------------------------------------------
    # SECURITY CHECK
    # -----------------------------------------------------

    fields_to_check = [
        "name",
        "brand",
        "description"
    ]

    for field in fields_to_check:

        value = str(product.get(field, ""))

        if detect_prompt_injection(value):

            print("\n🚨 SECURITY BLOCK")
            print(
                f"Suspicious instructions detected "
                f"in product {field}."
            )

            print("❌ Purchase blocked.")

            return False


    # -----------------------------------------------------
    # EXPLICIT USER CONFIRMATION
    # -----------------------------------------------------

    confirmed = request_confirmation(product)

    if not confirmed:
        return False


    # -----------------------------------------------------
    # PRICE VALIDATION
    # -----------------------------------------------------

    amount = product.get("offer_price")

    try:
        amount = float(
            str(amount)
            .replace("₹", "")
            .replace(",", "")
        )

    except (ValueError, TypeError):

        print("\n❌ Invalid product price.")
        return False


    if amount <= 0:

        print("\n❌ Invalid payment amount.")
        return False


    # -----------------------------------------------------
    # RAZORPAY TEST ORDER
    # -----------------------------------------------------

    print("\n💳 Creating Razorpay Test Mode order...")

    order = create_test_order(amount)

    if not order:

        print("\n❌ Payment order could not be created.")

        return False


    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    print("\n" + "=" * 50)
    print("🎉 TEST ORDER CREATED")
    print("=" * 50)

    print(f"Order ID : {order['id']}")
    print(f"Amount   : ₹{amount}")
    print("Mode     : Razorpay TEST MODE 🧪")

    print("\n💡 No real money has been charged.")

    return True


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

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