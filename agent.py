from catalog import PRODUCT_CATALOG
from security import screen_product


class BuyerAgent:

    def __init__(self):
        # Store the product catalog inside the agent
        self.catalog = PRODUCT_CATALOG

    def search_products(self, category, max_price):
        """
        Finds products that:
        1. Are safe from prompt injection
        2. Match the requested category
        3. Are within the user's maximum budget
        """

        safe_products = []

        for product in self.catalog:

            # --------------------------------
            # 1. SECURITY CHECK
            # --------------------------------
            is_safe, reason = screen_product(product)

            if not is_safe:
                print(
                    f"REJECTED: {product['name']} "
                    f"because {reason}"
                )
                continue

            # --------------------------------
            # 2. CATEGORY CHECK
            # --------------------------------
            if product["category"] != category:
                continue

            # --------------------------------
            # 3. HARD BUDGET CHECK
            # --------------------------------
            if product["price"] > max_price:
                continue

            # Product passed all checks
            safe_products.append(product)

        return safe_products

    def choose_product(self, products):
        """
        Selects the best product from the safe candidates.

        For now, the cheapest product is selected.
        Later, we can make this smarter using the LLM.
        """

        # No products available
        if not products:
            return None

        # Select the cheapest product
        best_product = min(
            products,
            key=lambda product: product["price"]
        )

        return best_product


# --------------------------------
# TEST THE BUYER AGENT
# --------------------------------

if __name__ == "__main__":

    # Create our agent
    agent = BuyerAgent()

    # Search for shoes under ₹3000
    products = agent.search_products(
        category="shoes",
        max_price=3000
    )

    # Choose the best product
    selected_product = agent.choose_product(products)

    print("\nSELECTED PRODUCT:")

    if selected_product:

        print(
            selected_product["name"],
            "- ₹",
            selected_product["price"]
        )

    else:

        print("No safe product found.")