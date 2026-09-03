import os
import requests
from dotenv import load_dotenv

from llm_intent import parse_intent
from security import sanitize_product, validate_product


# Load environment variables
load_dotenv()

API_KEY = os.getenv("QUICKCOMMERCE_API_KEY")

API_URL = "https://api.quickcommerceapi.com/v1/search"

# Platforms we want to search
PLATFORMS = [
    "BlinkIt",
    "Flipkart",
    "Myntra",
    "Amazon"
]


# ---------------------------------------------------------
# SEARCH PRODUCTS ACROSS MULTIPLE PLATFORMS
# ---------------------------------------------------------

def search_on_online_products(query):

    all_products = []

    for platform in PLATFORMS:

        print(f"\nSearching on {platform}...")

        params = {
            "q": query,
            "lat": 28.6139,
            "lon": 77.2090,
            "platform": platform
        }

        headers = {
            "X-API-Key": API_KEY
        }

        try:

            response = requests.get(
                API_URL,
                params=params,
                headers=headers,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            products = data.get("data", {}).get("products", [])

            for product in products:

                # Store platform name
                product["platform"] = platform

                all_products.append(product)

        except requests.exceptions.RequestException as e:

            print(f"Error searching {platform}: {e}")

    return all_products


# ---------------------------------------------------------
# SECURITY CHECK
# ---------------------------------------------------------

def apply_security(products):

    safe_products = []

    for product in products:

        # Validate product for prompt injection
        if not validate_product(product):

            print(
                f"⚠️ Security threat detected in product: "
                f"{product.get('name', 'Unknown')}"
            )

            # Sanitize suspicious content
            product = sanitize_product(product)

        safe_products.append(product)

    return safe_products


# ---------------------------------------------------------
# FILTER PRODUCTS BY BUDGET
# ---------------------------------------------------------

def filter_by_budget(products, max_price):

    if max_price is None:
        return products

    filtered_products = []

    for product in products:

        price = product.get("offer_price")

        if price is None:
            continue

        try:

            price = str(price)

            # Remove currency symbols and commas
            price = price.replace("₹", "").replace(",", "").strip()

            price = float(price)

            if price <= max_price:
                filtered_products.append(product)

        except (ValueError, TypeError):

            continue

    return filtered_products


# ---------------------------------------------------------
# RANK PRODUCTS
# ---------------------------------------------------------

def rank_products(products):

    if not products:
        return []

    def get_score(product):

        # -------------------------
        # Rating
        # -------------------------

        try:
            rating = float(product.get("rating", 0))
        except (ValueError, TypeError):
            rating = 0


        # -------------------------
        # Price / Discount
        # -------------------------

        try:
            mrp = float(
                str(product.get("mrp", 0))
                .replace("₹", "")
                .replace(",", "")
            )
        except (ValueError, TypeError):
            mrp = 0


        try:
            offer_price = float(
                str(product.get("offer_price", 0))
                .replace("₹", "")
                .replace(",", "")
            )
        except (ValueError, TypeError):
            offer_price = 0


        # Calculate discount percentage
        discount = 0

        if mrp > 0 and offer_price > 0:

            discount = (
                (mrp - offer_price) / mrp
            ) * 100


        # -------------------------
        # Availability
        # -------------------------

        availability_score = 1 if product.get(
            "available", True
        ) else 0


        # -------------------------
        # Final Score
        # -------------------------

        score = (
            rating * 10
            + discount * 0.2
            + availability_score * 5
        )

        return score


    # Sort highest score first
    return sorted(
        products,
        key=get_score,
        reverse=True
    )


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":

    # Get user's request
    user_request = input(
        "\n🛍️ What are you looking for? "
    )


    # -------------------------
    # STEP 1: Understand Intent
    # -------------------------

    intent = parse_intent(user_request)

    print("\n🧠 Detected Intent:")
    print(intent)


    query = intent.get(
        "search_query",
        ""
    )

    max_price = intent.get(
        "max_price"
    )


    # -------------------------
    # STEP 2: Search Online
    # -------------------------

    products = search_on_online_products(query)

    print(
        f"\n🔎 Products found: {len(products)}"
    )


    # -------------------------
    # STEP 3: Security
    # -------------------------

    products = apply_security(products)

    print(
        f"🔐 Security check completed."
    )


    # -------------------------
    # STEP 4: Budget Filter
    # -------------------------

    products = filter_by_budget(
        products,
        max_price
    )

    print(
        f"💰 Products within budget: "
        f"{len(products)}"
    )


    # -------------------------
    # STEP 5: Ranking
    # -------------------------

    products = rank_products(products)


    # -------------------------
    # STEP 6: Display Results
    # -------------------------

    print("\n🏆 BEST PRODUCTS:\n")


    for i, product in enumerate(
        products[:20],
        start=1
    ):

        print(
            f"{i}. {product.get('name', 'Unknown')}"
        )

        print(
            f"   Platform: "
            f"{product.get('platform', 'Unknown')}"
        )

        print(
            f"   Price: "
            f"₹{product.get('offer_price', 'N/A')}"
        )

        print(
            f"   MRP: "
            f"₹{product.get('mrp', 'N/A')}"
        )

        print(
            f"   Rating: "
            f"{product.get('rating', 'N/A')}"
        )

        print(
            f"   Security Flag: "
            f"{product.get('security_flag', False)}"
        )

        print()