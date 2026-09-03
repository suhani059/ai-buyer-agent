from flask import Flask, render_template_string, request, jsonify
import os
import razorpay
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

KEY_ID = os.getenv("RAZORPAY_KEY_ID")
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")


# =========================================================
# RAZORPAY CLIENT
# =========================================================

client = razorpay.Client(
    auth=(KEY_ID, KEY_SECRET)
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# CHECKOUT PAGE
# =========================================================

HTML = """
<!DOCTYPE html>

<html>

<head>

    <title>AI Buyer Agent</title>

    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>

</head>

<body>

    <h1>🛍️ AI Buyer Agent</h1>

    <h2>Wireless Headphones</h2>

    <p>Price: ₹1499</p>

    <button onclick="startPayment()">
        💳 Pay with Razorpay
    </button>


    <script>

        function startPayment() {

            fetch("/create-order", {
                method: "POST"
            })

            .then(response => response.json())

            .then(data => {

                var options = {

                    "key": data.key_id,

                    "amount": data.amount,

                    "currency": "INR",

                    "name": "AI Buyer Agent",

                    "description": "Test Purchase",

                    "order_id": data.order_id,


                    "handler": function(response) {

                        fetch("/verify-payment", {

                            method: "POST",

                            headers: {
                                "Content-Type": "application/json"
                            },

                            body: JSON.stringify(response)

                        })

                        .then(response => response.json())

                        .then(result => {

                            alert(result.message);

                        });

                    },


                    "modal": {

                        "ondismiss": function() {

                            console.log(
                                "Payment popup closed."
                            );

                        }

                    }

                };


                var rzp = new Razorpay(options);

                rzp.open();

            });

        }

    </script>

</body>

</html>
"""


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template_string(HTML)


# =========================================================
# CREATE ORDER
# =========================================================

@app.route("/create-order", methods=["POST"])
def create_order():

    amount = 1499 * 100

    order_data = {

        "amount": amount,

        "currency": "INR"

    }

    order = client.order.create(
        data=order_data
    )

    return jsonify({

        "key_id": KEY_ID,

        "order_id": order["id"],

        "amount": amount

    })


# =========================================================
# VERIFY PAYMENT
# =========================================================

@app.route("/verify-payment", methods=["POST"])
def verify_payment():

    data = request.get_json()

    try:

        client.utility.verify_payment_signature({

            "razorpay_order_id":
                data["razorpay_order_id"],

            "razorpay_payment_id":
                data["razorpay_payment_id"],

            "razorpay_signature":
                data["razorpay_signature"]

        })

        print("\n✅ PAYMENT SIGNATURE VERIFIED")

        print(
            "Payment ID:",
            data["razorpay_payment_id"]
        )

        return jsonify({

            "success": True,

            "message":
                "✅ Payment verified successfully!"

        })


    except Exception as e:

        print("\n🚨 PAYMENT VERIFICATION FAILED")

        print(e)

        return jsonify({

            "success": False,

            "message":
                "❌ Payment verification failed."

        }), 400


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )