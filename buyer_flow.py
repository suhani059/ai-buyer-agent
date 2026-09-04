# ============================================================
# AI BUYER AGENT - END TO END FLOW
# Live Search + Demo Fallback
# Intent → Search → Security → Budget → Ranking
# → Confirmation → Razorpay Test Order → Audit Log
# ============================================================

import os

from llm_intent import parse_intent

from product_search import (
    search_on_online_products,
    apply_security,
    filter_by_budget,
    rank_products
)

from audit_log import log_intent, log_recommendation
from agent import payment_gate

from catalog import PRODUCT_CATALOG


# ============================================================
# DEMO MODE
# ============================================================

# Set DEMO_MODE=true when you want to run without
# using QuickCommerce API credits.

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


# ============================================================
# DEMO CATALOG SEARCH
# ============================================================

def search_demo_catalog(intent):

    category = intent.get("category", "general")
    search_query = intent.get("search_query", "").lower()

    results = []

    for product in PRODUCT_CATALOG:

        product_category = product.get("category", "").lower()

        # Category matching
        if category != "general":
            if product_category != category.lower():
                continue

        # Convert catalog format into our standard product format
        demo_product = {
            "id": product.get("id"),
            "name": product.get("name"),
            "brand": product.get("brand", "Demo Brand"),
            "category": product.get("category"),
            "description": product.get("description"),
            "offer_price": product.get("price"),
            "mrp": product.get("price"),
            "rating": product.get("rating", 4.2),
            "available": True,
            "platform": "Demo Catalog"
        }

        results.append(demo_product)

    return results


# ============================================================
# MAIN BUYER FLOW
# ============================================================

def run_buyer_agent():

    print("\n" + "=" * 60)
    print("🛍️  AI BUYER AGENT")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. USER REQUEST
    # --------------------------------------------------------

    user_text = input(
        "\nWhat are you looking for?\n> "
    ).strip()

    if not user_text:
        print("❌ Please enter a product request.")
        return

    # --------------------------------------------------------
    # 2. INTENT PARSING
    # --------------------------------------------------------

    print("\n🧠 Understanding your request...")

    intent = parse_intent(user_text)

    print("\n✅ Intent detected:")
    print(intent)

    log_intent(user_text, intent)

    query = intent.get("search_query", "")
    max_price = intent.get("max_price")

    if not query:
        print("❌ Could not understand the product request.")
        return

    # --------------------------------------------------------
    # 3. PRODUCT SEARCH
    # --------------------------------------------------------

    if DEMO_MODE:

        print("\n🧪 DEMO MODE ENABLED")
        print("Using local product catalog.")
        print("💡 QuickCommerce credits are NOT being used.")

        products = search_demo_catalog(intent)

    else:

        print("\n🔎 Searching online marketplaces...")
        print("Platforms: Blinkit | Flipkart | Myntra | Amazon")

        products = search_on_online_products(query)

        # ----------------------------------------------------
        # FALLBACK IF LIVE SEARCH FAILS
        # ----------------------------------------------------

        if not products:

            print("\n⚠️ Live product search unavailable.")
            print("🔄 Switching to Demo Catalog...")

            products = search_demo_catalog(intent)

    if not products:

        print("\n❌ No products found.")
        return

    print(f"\n✅ Found {len(products)} products.")

    # --------------------------------------------------------
    # 4. SECURITY CHECK
    # --------------------------------------------------------

    print("\n🛡️ Running prompt-injection security checks...")

    products = apply_security(products)

    if not products:

        print("❌ No safe products available.")
        return

    print(
        f"✅ {len(products)} products passed security checks."
    )

    # --------------------------------------------------------
    # 5. BUDGET FILTER
    # --------------------------------------------------------

    if max_price:

        print(f"\n💰 Applying budget: ₹{max_price}")

        products = filter_by_budget(
            products,
            max_price
        )

        if not products:

            print(
                "\n❌ No products found within your budget."
            )

            return

        print(
            f"✅ {len(products)} products are within your budget."
        )

    # --------------------------------------------------------
    # 6. PRODUCT RANKING
    # --------------------------------------------------------

    print("\n📊 Ranking products...")

    products = rank_products(products)

    if not products:

        print("❌ Could not rank products.")
        return

    # --------------------------------------------------------
    # 7. SHOW TOP PRODUCTS
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("🏆 TOP RECOMMENDATIONS")
    print("=" * 60)

    top_products = products[:5]

    for index, product in enumerate(top_products, start=1):

        print(f"\n[{index}] {product.get('name', 'Unknown')}")

        print(
            f"    Platform : {product.get('platform', 'Unknown')}"
        )

        print(
            f"    Price    : ₹{product.get('offer_price', 'N/A')}"
        )

        print(
            f"    Rating   : ⭐ {product.get('rating', 'N/A')}"
        )

    # --------------------------------------------------------
    # 8. USER SELECTS PRODUCT
    # --------------------------------------------------------

    print("\n" + "-" * 60)

    while True:

        choice = input(
            f"\nSelect a product (1-{len(top_products)}) "
            "or 0 to cancel: "
        ).strip()

        try:

            choice = int(choice)

            if choice == 0:

                print("\n❌ Purchase cancelled.")
                return

            if 1 <= choice <= len(top_products):

                selected_product = top_products[choice - 1]

                break

            print("Please select a valid number.")

        except ValueError:

            print("Please enter a number.")

    # --------------------------------------------------------
    # 9. LOG RECOMMENDATION
    # --------------------------------------------------------

    log_recommendation(selected_product)

    print("\n✅ Product selected:")

    print(
        f"{selected_product.get('name', 'Unknown')} "
        f"— ₹{selected_product.get('offer_price', 'N/A')}"
    )

    # --------------------------------------------------------
    # 10. SECURITY + CONFIRMATION + PAYMENT
    # --------------------------------------------------------

    payment_gate(selected_product)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    run_buyer_agent()