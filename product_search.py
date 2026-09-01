import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("QUICKCOMMERCE_API_KEY")
API_URL = "https://api.quickcommerceapi.com/v1/search"

# Platforms we want our AI Buyer Agent to search
PLATFORMS = [
    "BlinkIt",
    "Flipkart",
    "Myntra",
    "Amazon"
]


def search_on_online_products(query):

    all_products = []

    for platform in PLATFORMS:

        print(f"\n🔍 Searching on {platform}...")

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
                headers=headers
            )

            response.raise_for_status()

            data = response.json()
            products = data.get("data", {}).get("products", [])

            print(f"✅ Found {len(products)} products on {platform}")

            # Add platform name to every product
            for product in products:
                product["platform"] = platform

            all_products.extend(products)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error on {platform}: {e}")

    return all_products


if __name__ == "__main__":

    # Take search query from the user
    query = input("\n🛍️ What are you looking for? ")

    # Search across all platforms
    products = search_on_online_products(query)

    print("\n" + "=" * 60)
    print(f"TOTAL PRODUCTS FOUND: {len(products)}")
    print("=" * 60)

    for product in products[:20]:

        print("\nPlatform:", product.get("platform"))
        print("Name:", product.get("name"))
        print("Price:", product.get("offer_price"))
        print("MRP:", product.get("mrp"))