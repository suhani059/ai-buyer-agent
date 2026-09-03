import os
import razorpay
from dotenv import load_dotenv

#load enviornment variables
load_dotenv()

#razorpay test mode credentials
KEY_ID = os.getenv("RAZORPAY_KEY_ID")
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

#CREATE RAZORPAY CLIENT
client = razorpay.Client(
    auth=(KEY_ID, KEY_SECRET))

# ---------------------------------------------------------
# CREATE RAZORPAY TEST ORDER
# ---------------------------------------------------------

def create_test_order(amount):
    #convert amount to paise (1 INR = 100 paise)
    amount_in_paise = int(float(amount) * 100)

    order_data = {
        "amount": amount_in_paise,
        "currency": "INR",
    }

    try:
        order = client.order.create(
            data=order_data)

        print("\n✅ Razorpay Test Order Created")
        print(f"Order ID: {order['id']}")
        print(f"Amount: ₹{amount}")

        return order
    except Exception as e:

        print("\n❌ Razorpay Order Creation Failed")
        print(e)

        return None


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    test_amount = 1499

    order = create_test_order(test_amount)

    if order:

        print("\n🧪 TEST MODE")
        print("No real money has been charged.")
