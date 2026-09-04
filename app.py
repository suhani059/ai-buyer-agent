# ============================================================
# AI BUYER AGENT - WEB APPLICATION
#
# Flow:
# User Request
#      ↓
# Intent Parsing
#      ↓
# Product Search
#      ↓
# Security Check
#      ↓
# Budget Filter
#      ↓
# Product Ranking
#      ↓
# Product Selection
#      ↓
# Explicit Confirmation
#      ↓
# Razorpay Test Order
#      ↓
# Razorpay Checkout
#      ↓
# Payment Signature Verification
#      ↓
# Audit Log
# ============================================================


from flask import Flask, render_template_string, request, jsonify

import os

from dotenv import load_dotenv

import razorpay


from llm_intent import parse_intent

from product_search import (
    search_on_online_products,
    apply_security,
    filter_by_budget,
    rank_products
)

from audit_log import (
    log_intent,
    log_recommendation,
    log_confirmation,
    log_security,
    log_payment
)

from security import detect_prompt_injection

from catalog import PRODUCT_CATALOG


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

KEY_ID = os.getenv(
    "RAZORPAY_KEY_ID"
)

KEY_SECRET = os.getenv(
    "RAZORPAY_KEY_SECRET"
)

DEMO_MODE = os.getenv(
    "DEMO_MODE",
    "false"
).lower() == "true"


# ============================================================
# RAZORPAY CLIENT
# ============================================================

client = razorpay.Client(
    auth=(
        KEY_ID,
        KEY_SECRET
    )
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# DEMO CATALOG SEARCH
# ============================================================

def search_demo_catalog(intent):

    category = intent.get(
        "category",
        "general"
    )

    results = []


    for product in PRODUCT_CATALOG:

        product_category = product.get(
            "category",
            ""
        ).lower()


        # ----------------------------------------------------
        # CATEGORY FILTER
        # ----------------------------------------------------

        if category != "general":

            if product_category != category.lower():

                continue


        # ----------------------------------------------------
        # STANDARD PRODUCT FORMAT
        # ----------------------------------------------------

        demo_product = {

            "id": product.get(
                "id"
            ),

            "name": product.get(
                "name"
            ),

            "brand": product.get(
                "brand",
                "Demo Brand"
            ),

            "category": product.get(
                "category"
            ),

            "description": product.get(
                "description"
            ),

            "image": product.get(
                "image"
            ),

            "offer_price": product.get(
                "price"
            ),

            "mrp": product.get(
                "mrp",
                product.get("price")
            ),

            "rating": product.get(
                "rating",
                4.2
            ),

            "available": True,

            "platform": "Demo Catalog"
        }


        results.append(
            demo_product
        )


    return results


# ============================================================
# HTML
# ============================================================

HTML = """

<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>
        AI Buyer Agent
    </title>


    <!-- Razorpay Checkout -->

    <script src=
        "https://checkout.razorpay.com/v1/checkout.js">
    </script>


    <style>


        /* ==================================================
           GLOBAL
           ================================================== */

        * {

            box-sizing: border-box;

        }


        body {

            margin: 0;

            font-family:
                Arial,
                Helvetica,
                sans-serif;

            background:
                #f5f3ff;

            color:
                #1f2937;

        }


        .container {

            max-width:
                1200px;

            margin:
                auto;

            padding:
                35px 25px 60px;

        }


        /* ==================================================
           HEADER
           ================================================== */

        .header {

            text-align:
                center;

            margin-bottom:
                30px;

        }


        .header h1 {

            margin:
                0;

            font-size:
                42px;

            color:
                #5b21b6;

        }


        .header p {

            color:
                #6b7280;

            font-size:
                17px;

            margin-top:
                10px;

        }


        /* ==================================================
           SEARCH
           ================================================== */

        .search-box {

            background:
                white;

            padding:
                22px;

            border-radius:
                18px;

            box-shadow:
                0 5px 20px
                rgba(0,0,0,0.08);

            display:
                flex;

            gap:
                12px;

        }


        .search-input {

            flex:
                1;

            padding:
                15px 18px;

            border:
                1px solid #d1d5db;

            border-radius:
                10px;

            font-size:
                16px;

            outline:
                none;

        }


        .search-input:focus {

            border-color:
                #7c3aed;

        }


        .search-button {

            padding:
                15px 28px;

            background:
                #6d28d9;

            color:
                white;

            border:
                none;

            border-radius:
                10px;

            font-size:
                16px;

            font-weight:
                bold;

            cursor:
                pointer;

        }


        .search-button:hover {

            background:
                #5b21b6;

        }


        /* ==================================================
           STATUS
           ================================================== */

        #status {

            text-align:
                center;

            margin:
                22px 0;

            font-weight:
                bold;

            font-size:
                16px;

        }

        /* ==================================================
           AI INTENT
           ================================================== */

        .intent-box {

            background:
                white;

            border-left:
                5px solid #7c3aed;

            padding:
                18px 22px;

            border-radius:
                12px;

            margin-bottom:
                25px;

            box-shadow:
                0 3px 12px
                rgba(0,0,0,0.06);

        }


        .intent-box h3 {

            margin:
                0 0 10px;

            color:
                #5b21b6;

        }


        .intent-details {

            color:
                #4b5563;

        }


        /* ==================================================
           PRODUCT GRID
           ================================================== */

        .products {

            display:
                grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(260px, 1fr)
                );

            gap:
                22px;

        }


        /* ==================================================
           PRODUCT CARD
           ================================================== */

        .product-card {

            background:
                white;

            border-radius:
                18px;

            overflow:
                hidden;

            box-shadow:
                0 5px 18px
                rgba(0,0,0,0.08);

            transition:
                transform 0.2s,
                box-shadow 0.2s;

        }


        .product-card:hover {

            transform:
                translateY(-4px);

            box-shadow:
                0 8px 25px
                rgba(0,0,0,0.12);

        }


        /* ==================================================
           PRODUCT IMAGE
           ================================================== */

        .product-image-container {

            width:
                100%;

            height:
                240px;

            background:
                #f9fafb;

            display:
                flex;

            align-items:
                center;

            justify-content:
                center;

            overflow:
                hidden;

        }


        .product-image {

            width:
                100%;

            height:
                100%;

            object-fit:
                contain;

            padding:
                15px;

        }


        .image-placeholder {

            font-size:
                60px;

            color:
                #c4b5fd;

        }


        /* ==================================================
           PRODUCT INFORMATION
           ================================================== */

        .product-info {

            padding:
                20px;

        }


        .product-name {

            font-size:
                19px;

            font-weight:
                bold;

            line-height:
                1.35;

            margin-bottom:
                10px;

        }


        .platform {

            color:
                #6b7280;

            font-size:
                14px;

            margin-bottom:
                10px;

        }


        .price {

            font-size:
                25px;

            font-weight:
                bold;

            color:
                #5b21b6;

            margin:
                8px 0;

        }


        .rating {

            display:
                inline-block;

            background:
                #fef3c7;

            padding:
                5px 9px;

            border-radius:
                7px;

            font-size:
                14px;

            margin-bottom:
                15px;

        }


        .select-button {

            width:
                100%;

            padding:
                13px;

            background:
                #111827;

            color:
                white;

            border:
                none;

            border-radius:
                9px;

            font-size:
                15px;

            font-weight:
                bold;

            cursor:
                pointer;

        }


        .select-button:hover {

            background:
                #374151;

        }


        /* ==================================================
           SECURITY BOX
           ================================================== */

        .security-box {

            margin-top:
                30px;

            background:
                #ecfdf5;

            border:
                1px solid #10b981;

            padding:
                17px 20px;

            border-radius:
                12px;

            color:
                #065f46;

            font-weight:
                bold;

        }


        /* ==================================================
           CONFIRMATION
           ================================================== */

        .confirmation {

            background:
                white;

            margin-top:
                30px;

            padding:
                28px;

            border-radius:
                18px;

            text-align:
                center;

            box-shadow:
                0 5px 20px
                rgba(0,0,0,0.08);

        }


        .confirmation h2 {

            color:
                #5b21b6;

        }


        .selected-product {

            background:
                #f5f3ff;

            padding:
                18px;

            border-radius:
                12px;

            margin:
                20px 0;

            font-size:
                17px;

            line-height:
                1.7;

        }


        .confirm-button {

            background:
                #16a34a;

            color:
                white;

            padding:
                13px 25px;

            border:
                none;

            border-radius:
                9px;

            font-weight:
                bold;

            cursor:
                pointer;

            margin-right:
                8px;

        }


        .cancel-button {

            background:
                #dc2626;

            color:
                white;

            padding:
                13px 25px;

            border:
                none;

            border-radius:
                9px;

            font-weight:
                bold;

            cursor:
                pointer;

        }


        /* ==================================================
           MODE
           ================================================== */

        .mode {

            text-align:
                center;

            margin-top:
                30px;

            color:
                #6b7280;

            font-size:
                13px;

        }


        /* ==================================================
           HIDDEN
           ================================================== */

        .hidden {

            display:
                none;

        }


        /* ==================================================
           MOBILE
           ================================================== */

        @media (
            max-width: 650px
        ) {

            .search-box {

                flex-direction:
                    column;

            }


            .header h1 {

                font-size:
                    32px;

            }

        }


    </style>

</head>


<body>


<div class="container">


    <!-- ====================================================
         HEADER
         ==================================================== -->

    <div class="header">

        <h1>
            🛍️ AI Buyer Agent
        </h1>

        <p>
            Secure autonomous shopping
            with human-controlled payments
        </p>

    </div>


    <!-- ====================================================
         SEARCH
         ==================================================== -->

    <div class="search-box">

        <input
            id="userQuery"
            class="search-input"
            type="text"
            placeholder="Try: running shoes under ₹5000"
        >


        <button
            class="search-button"
            onclick="searchProducts()"
        >

            🔍 Search

        </button>

    </div>


    <!-- ====================================================
         STATUS
         ==================================================== -->


    <div id="status"></div>

    <!-- ====================================================
         AI INTENT
         ==================================================== -->

    <div
        id="intentBox"
        class="intent-box hidden"
    >

        <h3>
            🧠 AI Understanding
        </h3>

        <div
            id="intentText"
            class="intent-details"
        ></div>

    </div>


    <!-- ====================================================
         PRODUCTS
         ==================================================== -->

    <div
        id="products"
        class="products"
    ></div>


    <!-- ====================================================
         SECURITY
         ==================================================== -->

    <div
        id="securityBox"
        class="security-box hidden"
    >

        🛡️ Security Check Passed

        <br><br>

        External product content was checked
        for prompt injection before purchase.

    </div>


    <!-- ====================================================
         CONFIRMATION
         ==================================================== -->

    <div
        id="confirmation"
        class="confirmation hidden"
    >

        <h2>
            🛒 Purchase Confirmation
        </h2>


        <div
            id="selectedProduct"
            class="selected-product"
        ></div>


        <p>
            ⚠️ No payment/order will be created
            without your confirmation.
        </p>


        <button
            class="confirm-button"
            onclick="confirmPurchase()"
        >

            ✅ Confirm Purchase

        </button>


        <button
            class="cancel-button"
            onclick="cancelPurchase()"
        >

            ❌ Cancel

        </button>

    </div>


    <!-- ====================================================
         MODE
         ==================================================== -->

    <div class="mode">

        {% if demo_mode %}

            🧪 Demo Mode — QuickCommerce credits are not used

        {% else %}

            🌐 Live Marketplace Search

        {% endif %}

    </div>


</div>


<script>


// ==========================================================
// SELECTED PRODUCT
// ==========================================================

let selectedProduct = null;


// ==========================================================
// FORMAT RATING
// ==========================================================

function formatRating(rating) {

    if (
        rating === null ||
        rating === undefined ||
        rating === ""
    ) {

        return "N/A";

    }


    const number =
        Number(rating);


    if (isNaN(number)) {

        return "N/A";

    }


    return number.toFixed(1);

}


// ==========================================================
// FIND PRODUCT IMAGE
// ==========================================================

function getProductImage(product) {

    /*
        Different marketplace APIs can use
        different image field names.

        We check several possible fields.
    */


    const possibleImages = [

        product.image,

        product.image_url,

        product.imageUrl,

        product.thumbnail,

        product.thumbnail_url,

        product.product_image,

        product.productImage,

        product.img,

        product.photo

    ];


    for (
        const image of possibleImages
    ) {

        if (
            typeof image === "string" &&
            image.trim() !== ""
        ) {

            return image;

        }

    }


    // Some APIs may return an array

    if (
        Array.isArray(product.images) &&
        product.images.length > 0
    ) {

        const firstImage =
            product.images[0];


        if (
            typeof firstImage === "string"
        ) {

            return firstImage;

        }


        if (
            firstImage &&
            typeof firstImage === "object"
        ) {

            return (
                firstImage.url ||
                firstImage.image ||
                ""
            );

        }

    }


    return "";

}


// ==========================================================
// SEARCH PRODUCTS
// ==========================================================

function searchProducts() {


    const query =
        document
            .getElementById("userQuery")
            .value
            .trim();


    if (!query) {

        alert(
            "Please enter a product request."
        );

        return;

    }


    // Reset

    document
        .getElementById("products")
        .innerHTML = "";


    document
        .getElementById("intentBox")
        .classList.add("hidden");


    document
        .getElementById("securityBox")
        .classList.add("hidden");


    document
        .getElementById("confirmation")
        .classList.add("hidden");


    document
        .getElementById("status")
        .innerText =
            "🧠 Understanding your request...";
    fetch(
        "/search",
        {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/json"

            },

            body: JSON.stringify({

                query: query

            })

        }
    )


    .then(
        response => {

            return response.json();

        }
    )


    .then(
        data => {


            if (!data.success) {

                document
                    .getElementById("status")
                    .innerText =
                        "❌ " +
                        data.message;

                return;

            }


            document
                .getElementById("status")
                .innerText =
                    "✅ Products found";


            // =================================================
            // SHOW INTENT
            // =================================================

            document
                .getElementById("intentBox")
                .classList
                .remove("hidden");


            let intentHTML =

                "<strong>Category:</strong> " +
                (data.intent.category || "General");


            if (
                data.intent.search_query
            ) {

                intentHTML +=

                    " &nbsp; | &nbsp; " +

                    "<strong>Search:</strong> " +

                    data.intent.search_query;

            }


            if (
                data.intent.max_price
            ) {

                intentHTML +=

                    " &nbsp; | &nbsp; " +

                    "<strong>Budget:</strong> ₹" +

                    data.intent.max_price;

            }


            document
                .getElementById("intentText")
                .innerHTML =
                    intentHTML;


            // =================================================
            // SECURITY STATUS
            // =================================================

            document
                .getElementById("securityBox")
                .classList
                .remove("hidden");


            // =================================================
            // PRODUCT CARDS
            // =================================================

            const container =
                document
                    .getElementById("products");


            data.products.forEach(
                product => {


                    const card =
                        document
                            .createElement("div");


                    card.className =
                        "product-card";


                    const image =
                        getProductImage(
                            product
                        );


                    const rating =
                        formatRating(
                            product.rating
                        );


                    let imageHTML;


                    if (image) {

                        imageHTML = `

                            <img
                                src="${image}"
                                class="product-image"
                                alt="Product image"
                                onerror="
                                    this.style.display='none';
                                    this.nextElementSibling.style.display='flex';
                                "
                            >

                            <div
                                class="image-placeholder"
                                style="display:none;"
                            >
                                🛍️
                            </div>

                        `;

                    } else {

                        imageHTML = `

                            <div
                                class="image-placeholder"
                            >
                                🛍️
                            </div>

                        `;

                    }


                    card.innerHTML = `

                        <div
                            class="product-image-container"
                        >

                            ${imageHTML}

                        </div>


                        <div
                            class="product-info"
                        >

                            <div
                                class="product-name"
                            >

                                ${
                                    product.name ||
                                    "Unknown Product"
                                }

                            </div>


                            <div
                                class="platform"
                            >

                                🛒

                                ${
                                    product.platform ||
                                    "Unknown"
                                }

                            </div>


                            <div
                                class="price"
                            >

                                ₹${
                                    product.offer_price ||
                                    "N/A"
                                }

                            </div>


                            <div
                                class="rating"
                            >

                                ⭐ ${rating}

                            </div>


                            <button
                                class="select-button"
                                onclick='selectProduct(${JSON.stringify(product)})'
                            >

                                Select Product

                            </button>

                        </div>

                    `;


                    container.appendChild(
                        card
                    );


                }
            );


        }
    )


    .catch(
        error => {

            console.error(
                error
            );


            document
                .getElementById("status")
                .innerText =
                    "❌ Something went wrong.";

        }
    );

}


// ==========================================================
// SELECT PRODUCT
// ==========================================================

function selectProduct(product) {


    selectedProduct =
        product;


    document
        .getElementById("confirmation")
        .classList
        .remove("hidden");


    document
        .getElementById("selectedProduct")
        .innerHTML = `

            <strong>
                ${product.name}
            </strong>

            <br>

            🛒 Platform:
            ${product.platform || "Unknown"}

            <br>

            💰 Price:
            ₹${product.offer_price}

            <br>

            ⭐ Rating:
            ${formatRating(product.rating)}

        `;


    window.scrollTo({

        top:
            document.body.scrollHeight,

        behavior:
            "smooth"

    });

}


// ==========================================================
// CANCEL PURCHASE
// ==========================================================

function cancelPurchase() {


    selectedProduct =
        null;


    document
        .getElementById("confirmation")
        .classList
        .add("hidden");


    document
        .getElementById("status")
        .innerText =
            "❌ Purchase cancelled.";

}


// ==========================================================
// CONFIRM PURCHASE
// ==========================================================

function confirmPurchase() {


    if (!selectedProduct) {

        return;

    }


    document
        .getElementById("status")
        .innerText =
            "🔐 Running final security checks...";


    fetch(
        "/confirm-purchase",
        {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/json"

            },

            body: JSON.stringify({

                product:
                    selectedProduct

            })

        }
    )


    .then(
        response =>
            response.json()
    )


    .then(
        data => {


            if (!data.success) {

                document
                    .getElementById("status")
                    .innerText =
                        "❌ " +
                        data.message;

                return;

            }


            document
                .getElementById("status")
                .innerText =
                    "💳 Opening Razorpay Test Checkout...";


            openRazorpayCheckout(
                data
            );


        }
    )


    .catch(
        error => {

            console.error(
                error
            );


            document
                .getElementById("status")
                .innerText =
                    "❌ Purchase failed.";

        }
    );

}


// ==========================================================
// RAZORPAY CHECKOUT
// ==========================================================

function openRazorpayCheckout(
    data
) {


    var options = {


        "key":
            data.key_id,


        "amount":
            data.amount,


        "currency":
            "INR",


        "name":
            "AI Buyer Agent",


        "description":
            data.product_name,


        "order_id":
            data.order_id,


        // ====================================================
        // PAYMENT HANDLER
        // ====================================================

        "handler":
            function(response) {


                document
                    .getElementById("status")
                    .innerText =
                        "🔐 Verifying payment...";


                fetch(
                    "/verify-payment",
                    {

                        method: "POST",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body:
                            JSON.stringify(
                                response
                            )

                    }
                )


                .then(
                    response =>
                        response.json()
                )


                .then(
                    result => {


                    document
                        .getElementById("status")
                        .innerText =
                            result.message;


                });


            },


        // ====================================================
        // CHECKOUT CLOSED
        // ====================================================

        "modal": {

            "ondismiss":
                function() {

                    document
                        .getElementById("status")
                        .innerText =
                            "ℹ️ Checkout closed.";

                }

        }

    };


    var rzp =
        new Razorpay(
            options
        );


    rzp.open();

}


// ==========================================================
// ENTER KEY SUPPORT
// ==========================================================

document
    .getElementById("userQuery")
    .addEventListener(
        "keypress",
        function(event) {

            if (
                event.key === "Enter"
            ) {

                searchProducts();

            }

        }
    );


</script>


</body>

</html>

"""


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
def home():

    return render_template_string(
        HTML,
        demo_mode=DEMO_MODE
    )


# ============================================================
# SEARCH ROUTE
# ============================================================

@app.route(
    "/search",
    methods=["POST"]
)
def search():

    data = request.get_json() or {}

    user_text = data.get(
        "query",
        ""
    ).strip()


    if not user_text:

        return jsonify({

            "success": False,

            "message":
                "Please enter a product request."

        })


    # ========================================================
    # INTENT PARSING
    # ========================================================

    intent = parse_intent(user_text)


    log_intent(
        user_text,
        intent
    )


    query = intent.get(
        "search_query",
        ""
    )


    max_price = intent.get(
        "max_price"
    )


    if not query:

        return jsonify({

            "success": False,

            "message":
                "Could not understand the product request."

        })


    # ========================================================
    # PRODUCT SEARCH
    # ========================================================

    if DEMO_MODE:

        print(
            "\n🧪 DEMO MODE"
        )

        print(
            "Using local product catalog."
        )

        products =search_demo_catalog(intent)

    else:

        print(
            "\n🔎 Searching marketplaces..."
        )


        products =search_on_online_products(query)

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if not products:

            print(
                "\n⚠️ Live search unavailable."
            )

            print(
                "🔄 Using Demo Catalog..."
            )

            products =search_demo_catalog(intent)


    if not products:

        return jsonify({

            "success": False,

            "message":
                "No products found."

        })


    # ========================================================
    # SECURITY
    # ========================================================

    products =apply_security(products)


    if not products:

        return jsonify({

            "success": False,

            "message":
                "No safe products available."

        })


    # ========================================================
    # BUDGET
    # ========================================================

    if max_price:

        products =filter_by_budget(
                products,
                max_price
            )


    if not products:

        return jsonify({

            "success": False,

            "message":
                "No products found within your budget."

        })


    # ========================================================
    # RANKING
    # ========================================================

    products =rank_products(products)


    # ========================================================
    # TOP 5
    # ========================================================

    top_products =products[:5]


    return jsonify({

        "success": True,

        "intent":
            intent,

        "products":
            top_products

    })


# ============================================================
# CONFIRM PURCHASE
# ============================================================

@app.route(
    "/confirm-purchase",
    methods=["POST"]
)
def confirm_purchase():

    data =request.get_json() or {}


    product =data.get(
            "product"
        )


    if not product:

        return jsonify({

            "success": False,

            "message":
                "No product selected."

        })


    # ========================================================
    # FINAL SECURITY CHECK
    # ========================================================

    # Never allow a product already flagged by the initial
    # security scan to proceed to payment.
    if product.get("security_flag") is True:

        log_security(
            product,
            "BLOCKED"
        )

        return jsonify({

            "success": False,

            "message":
                "🚨 Suspicious product content detected. Purchase blocked."

        }), 403


    fields_to_check = [

        "name",

        "brand",

        "description"

    ]


    for field in fields_to_check:

        value =product.get(
                field
            )


        if value and detect_prompt_injection(
            value
        ):

            log_security(
                product,
                "BLOCKED"
            )


            return jsonify({

                "success": False,

                "message":
                    "🚨 Suspicious product content detected. Purchase blocked."

            })


    # ========================================================
    # SECURITY PASSED
    # ========================================================

    log_security(
        product,
        "SAFE"
    )


    # ========================================================
    # USER CONFIRMATION
    # ========================================================

    log_confirmation(
        product,
        True
    )


    # ========================================================
    # PRICE VALIDATION
    # ========================================================

    try:

        amount =float(
                product.get(
                    "offer_price"
                )
            )


        if amount <= 0:

            return jsonify({

                "success": False,

                "message":
                    "Invalid product price."

            })


    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Invalid product price."

        })


    # ========================================================
    # CREATE RAZORPAY TEST ORDER
    # ========================================================

    amount_in_paise =int(
            amount * 100
        )


    order_data = {

        "amount":
            amount_in_paise,

        "currency":
            "INR"

    }


    try:

        order =client.order.create(
                data=order_data
            )


    except Exception as e:

        print(
            "\n❌ Razorpay order creation failed:"
        )

        print(e)


        log_payment(

            order_id="N/A",

            amount=amount,

            status=
                "ORDER_CREATION_FAILED"

        )


        return jsonify({

            "success": False,

            "message":
                "Could not create Razorpay test order."

        })


    # ========================================================
    # LOG PAYMENT
    # ========================================================

    log_payment(

        order_id=
            order["id"],

        amount=
            amount,

        status=
            "TEST_ORDER_CREATED"

    )


    return jsonify({

        "success": True,

        "key_id":
            KEY_ID,

        "order_id":
            order["id"],

        "amount":
            amount_in_paise,

        "product_name":
            product.get(
                "name",
                "Product"
            )

    })


# ============================================================
# VERIFY PAYMENT
# ============================================================

@app.route(
    "/verify-payment",
    methods=["POST"]
)
def verify_payment():

    data =request.get_json() or {}


    try:

        client.utility.verify_payment_signature({

            "razorpay_order_id":
                data[
                    "razorpay_order_id"
                ],

            "razorpay_payment_id":
                data[
                    "razorpay_payment_id"
                ],

            "razorpay_signature":
                data[
                    "razorpay_signature"
                ]

        })


        print(
            "\n✅ PAYMENT SIGNATURE VERIFIED"
        )


        print(
            "Payment ID:",
            data[
                "razorpay_payment_id"
            ]
        )


        return jsonify({

            "success": True,

            "message":
                "✅ Payment verified successfully!"

        })


    except Exception as e:

        print(
            "\n🚨 PAYMENT VERIFICATION FAILED"
        )

        print(e)


        return jsonify({

            "success": False,

            "message":
                "❌ Payment verification failed."

        }), 400


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    # Local development + Render-compatible fallback.
    # Gunicorn remains the recommended Render start command.
    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )