# =========================================================
#           FOOD DELIVERY SIMULATOR — UPGRADED
# =========================================================
# New Features:
# ✅ Dataclasses for FoodItem (modern Python)
# ✅ Enum for OrderStatus
# ✅ Input validation (no crash on bad input)
# ✅ Wallet / balance system with top-up
# ✅ Item quantity support in cart
# ✅ Search / filter menu items
# ✅ Admin panel (add restaurant / food at runtime)
# ✅ Remove items from cart
# ✅ Estimated delivery time
# ✅ Order receipt with itemised breakdown
# ✅ Rich order history (view past receipts)
# ✅ JSON file storage (orders.json)
# ✅ OOP + Enums + Dataclasses
# =========================================================

import random
import json
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# =========================================================
# ENUMS
# =========================================================

class OrderStatus(Enum):
    CONFIRMED         = "Order Confirmed"
    PREPARING         = "Restaurant Preparing Food"
    PACKED            = "Food Packed"
    PICKED_UP         = "Delivery Partner Picked Up Order"
    OUT_FOR_DELIVERY  = "Out For Delivery"
    DELIVERED         = "Delivered Successfully"


class PaymentMethod(Enum):
    WALLET = "Wallet"
    CASH   = "Cash on Delivery"
    UPI    = "UPI"


# =========================================================
# FOOD ITEM  (dataclass — modern Python)
# =========================================================

@dataclass
class FoodItem:
    name:     str
    price:    float
    category: str = "General"
    is_veg:   bool = True

    def display(self, index: int) -> None:
        tag = "🟢 Veg" if self.is_veg else "🔴 Non-Veg"
        print(f"  {index}. [{self.category}] {self.name} - ₹{self.price:.0f}  ({tag})")


# =========================================================
# CART ITEM
# =========================================================

@dataclass
class CartItem:
    food:     FoodItem
    quantity: int = 1

    @property
    def subtotal(self) -> float:
        return self.food.price * self.quantity

    def __str__(self) -> str:
        return (
            f"  {self.food.name} x{self.quantity}"
            f"  ₹{self.food.price:.0f} × {self.quantity}"
            f" = ₹{self.subtotal:.0f}"
        )


# =========================================================
# RESTAURANT
# =========================================================

class Restaurant:

    def __init__(self, name: str, cuisine: str = "Multi-cuisine"):
        self.name    = name
        self.cuisine = cuisine
        self.menu:    list[FoodItem]  = []
        self.ratings: list[int]       = []
        self.reviews: list[str]       = []

    def add_food(self, food: FoodItem) -> None:
        self.menu.append(food)

    def show_menu(self, filter_text: str = "") -> None:
        print(f"\n{'=' * 50}")
        print(f"  {self.name}  ({self.cuisine})")
        print(f"  Rating: {self.average_rating()} ⭐  |  {len(self.menu)} items")
        print(f"{'=' * 50}")

        items = self.menu
        if filter_text:
            items = [
                f for f in self.menu
                if filter_text.lower() in f.name.lower()
                or filter_text.lower() in f.category.lower()
            ]
            if not items:
                print(f"  No items matching '{filter_text}'")
                return

        for i, item in enumerate(items, start=1):
            item.display(i)

    def search_item(self, query: str) -> list[tuple[int, FoodItem]]:
        results = []
        for i, item in enumerate(self.menu, start=1):
            if query.lower() in item.name.lower():
                results.append((i, item))
        return results

    def add_rating(self, rating: int) -> None:
        self.ratings.append(rating)

    def add_review(self, review: str) -> None:
        if review.strip():
            self.reviews.append(review.strip())

    def average_rating(self) -> float:
        if not self.ratings:
            return 0.0
        return round(sum(self.ratings) / len(self.ratings), 1)

    def show_reviews(self) -> None:
        print("\n----- Customer Reviews -----")
        if not self.reviews:
            print("  No reviews yet.")
            return
        for review in self.reviews:
            print(f"  • {review}")


# =========================================================
# WALLET
# =========================================================

class Wallet:

    def __init__(self, balance: float = 0.0):
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    def top_up(self, amount: float) -> None:
        if amount <= 0:
            print("  ❌ Top-up amount must be positive.")
            return
        self._balance += amount
        print(f"  ✅ ₹{amount:.0f} added. New balance: ₹{self._balance:.0f}")

    def deduct(self, amount: float) -> bool:
        if amount > self._balance:
            print(
                f"  ❌ Insufficient balance. "
                f"Need ₹{amount:.0f}, have ₹{self._balance:.0f}"
            )
            return False
        self._balance -= amount
        return True

    def __str__(self) -> str:
        return f"₹{self._balance:.0f}"


# =========================================================
# CUSTOMER
# =========================================================

class Customer:

    def __init__(self, name: str, wallet_balance: float = 500.0):
        self.name          = name
        self.cart:          list[CartItem] = []
        self.order_history: list[dict]     = []
        self.wallet         = Wallet(wallet_balance)

    # --- cart helpers ---

    def add_to_cart(self, item: FoodItem, qty: int = 1) -> None:
        for ci in self.cart:
            if ci.food.name == item.name:
                ci.quantity += qty
                print(f"  ✅ {item.name} quantity updated to {ci.quantity}.")
                return
        self.cart.append(CartItem(item, qty))
        print(f"  ✅ {item.name} × {qty} added to cart.")

    def remove_from_cart(self, index: int) -> None:
        if 0 <= index < len(self.cart):
            removed = self.cart.pop(index)
            print(f"  ✅ {removed.food.name} removed from cart.")
        else:
            print("  ❌ Invalid item index.")

    def show_cart(self) -> None:
        print("\n========== Your Cart ==========")
        if not self.cart:
            print("  Cart is empty.")
            return
        for i, ci in enumerate(self.cart, start=1):
            print(f"  {i}. {ci}")
        print(f"\n  Subtotal: ₹{self.calculate_bill():.0f}")

    def calculate_bill(self) -> float:
        return sum(ci.subtotal for ci in self.cart)

    def clear_cart(self) -> None:
        self.cart.clear()

    # --- order history ---

    def save_order(self, order: dict) -> None:
        self.order_history.append(order)

    def show_order_history(self) -> None:
        print("\n========== Order History ==========")
        if not self.order_history:
            print("  No previous orders.")
            return
        for i, order in enumerate(self.order_history, start=1):
            print(f"\n  Order #{i}")
            print(f"    Restaurant : {order['restaurant']}")
            print(f"    Items      : {order['items']}")
            print(f"    Bill       : ₹{order['bill']}")
            print(f"    Payment    : {order['payment']}")
            print(f"    Partner    : {order['delivery_partner']}")
            print(f"    Date       : {order['date']}")
            print(f"    Status     : {order['status']}")


# =========================================================
# DELIVERY PARTNER
# =========================================================

class DeliveryPartner:

    def __init__(self, name: str, vehicle: str = "Bike"):
        self.name    = name
        self.vehicle = vehicle

    def track_delivery(self, eta_minutes: int = 0) -> None:
        print(f"\n========== Delivery Tracking ==========")
        print(f"  Partner : {self.name}  ({self.vehicle})")
        if eta_minutes:
            print(f"  ETA     : ~{eta_minutes} minutes\n")
        for status in OrderStatus:
            print(f"  ✔ {status.value}")


# =========================================================
# ADMIN PANEL
# =========================================================

class AdminPanel:

    def __init__(self, restaurants: list[Restaurant]):
        self._restaurants = restaurants

    def run(self) -> None:
        while True:
            print("\n===== Admin Panel =====")
            print("  1. Add New Restaurant")
            print("  2. Add Food Item to Restaurant")
            print("  3. Back")
            choice = safe_input_int("  Choice: ")
            if choice == 1:
                self._add_restaurant()
            elif choice == 2:
                self._add_food_item()
            elif choice == 3:
                break
            else:
                print("  ❌ Invalid choice.")

    def _add_restaurant(self) -> None:
        name    = input("  Restaurant name: ").strip()
        cuisine = input("  Cuisine type: ").strip()
        if name:
            self._restaurants.append(Restaurant(name, cuisine))
            print(f"  ✅ '{name}' added.")

    def _add_food_item(self) -> None:
        if not self._restaurants:
            print("  No restaurants available.")
            return
        for i, r in enumerate(self._restaurants, start=1):
            print(f"  {i}. {r.name}")
        idx = safe_input_int("  Select restaurant: ") - 1
        if not (0 <= idx < len(self._restaurants)):
            print("  ❌ Invalid selection.")
            return
        rest     = self._restaurants[idx]
        name     = input("  Food name: ").strip()
        price    = safe_input_float("  Price (₹): ")
        category = input("  Category (e.g. Starters, Main, Dessert): ").strip() or "General"
        veg_in   = input("  Veg? (yes/no): ").strip().lower()
        is_veg   = veg_in != "no"
        if name and price > 0:
            rest.add_food(FoodItem(name, price, category, is_veg))
            print(f"  ✅ '{name}' added to {rest.name}.")


# =========================================================
# COUPON SYSTEM
# =========================================================

COUPONS: dict[str, int] = {
    "SAVE50":     50,
    "WELCOME100": 100,
    "FOOD30":     30,
    "DISCOUNT20": 20,
}


# =========================================================
# INPUT HELPERS  (safe — never crash)
# =========================================================

def safe_input_int(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if min_val is not None and value < min_val:
                print(f"  ❌ Please enter a number ≥ {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"  ❌ Please enter a number ≤ {max_val}.")
                continue
            return value
        except ValueError:
            print("  ❌ Invalid input — please enter a whole number.")


def safe_input_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value < 0:
                print("  ❌ Value cannot be negative.")
                continue
            return value
        except ValueError:
            print("  ❌ Invalid input — please enter a number.")


# =========================================================
# PRINT RECEIPT
# =========================================================

def print_receipt(
    customer:   Customer,
    restaurant: Restaurant,
    partner:    DeliveryPartner,
    total_bill: float,
    discount:   float,
    payment:    str,
    eta:        int,
) -> None:

    gross = customer.calculate_bill()
    width = 46

    print("\n" + "=" * width)
    print(f"{'FOOD DELIVERY — RECEIPT':^{width}}")
    print("=" * width)
    print(f"  Customer   : {customer.name}")
    print(f"  Restaurant : {restaurant.name}")
    print(f"  Date       : {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    print("-" * width)
    print(f"  {'Item':<28} {'Amount':>10}")
    print("-" * width)

    for ci in customer.cart:
        label = f"{ci.food.name} × {ci.quantity}"
        print(f"  {label:<28} ₹{ci.subtotal:>8.0f}")

    print("-" * width)
    print(f"  {'Subtotal':<28} ₹{gross:>8.0f}")
    if discount:
        print(f"  {'Discount':<28} -₹{discount:>7.0f}")
    print(f"  {'Total Paid':<28} ₹{total_bill:>8.0f}")
    print("-" * width)
    print(f"  Payment    : {payment}")
    print(f"  Delivery   : {partner.name} ({partner.vehicle})")
    print(f"  ETA        : ~{eta} min")
    print("=" * width)


# =========================================================
# FILE STORAGE
# =========================================================

def save_order_to_file(order_data: dict) -> None:
    try:
        with open("orders.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(order_data)

    with open("orders.json", "w") as f:
        json.dump(data, f, indent=4)


def load_orders() -> None:
    try:
        with open("orders.json", "r") as f:
            data = json.load(f)
        if not data:
            print("\n  No saved orders found.")
            return
        print(f"\n========== Saved Orders ({len(data)}) ==========")
        for i, order in enumerate(data, start=1):
            print(
                f"\n  #{i} | {order.get('restaurant')} | "
                f"₹{order.get('bill')} | {order.get('date', '')[:16]}"
            )
    except (FileNotFoundError, json.JSONDecodeError):
        print("\n  No previous order data found.")


# =========================================================
# MAIN
# =========================================================

def main() -> None:

    # ----- restaurants -----
    pizza_hub    = Restaurant("Pizza Hub",    "Italian")
    burger_point = Restaurant("Burger Point", "American")
    indian_spice = Restaurant("Indian Spice", "Indian")

    pizza_hub.add_food(FoodItem("Margherita Pizza",   250, "Pizza",    True))
    pizza_hub.add_food(FoodItem("Cheese Burst Pizza", 400, "Pizza",    True))
    pizza_hub.add_food(FoodItem("Farmhouse Pizza",    350, "Pizza",    True))
    pizza_hub.add_food(FoodItem("Garlic Bread",       120, "Starters", True))

    burger_point.add_food(FoodItem("Veg Burger",    120, "Burgers",  True))
    burger_point.add_food(FoodItem("Cheese Burger", 180, "Burgers",  True))
    burger_point.add_food(FoodItem("Chicken Burger",220, "Burgers",  False))
    burger_point.add_food(FoodItem("French Fries",  100, "Sides",    True))
    burger_point.add_food(FoodItem("Coleslaw",       80, "Sides",    True))

    indian_spice.add_food(FoodItem("Butter Chicken",       320, "Main",    False))
    indian_spice.add_food(FoodItem("Paneer Butter Masala", 280, "Main",    True))
    indian_spice.add_food(FoodItem("Biryani",              250, "Rice",    False))
    indian_spice.add_food(FoodItem("Veg Biryani",          200, "Rice",    True))
    indian_spice.add_food(FoodItem("Dal Tadka",            180, "Main",    True))
    indian_spice.add_food(FoodItem("Gulab Jamun",           80, "Dessert", True))

    restaurants: list[Restaurant] = [pizza_hub, burger_point, indian_spice]

    delivery_partners = [
        DeliveryPartner("Rahul", "Bike"),
        DeliveryPartner("Aman",  "Scooter"),
        DeliveryPartner("Rohit", "Bike"),
        DeliveryPartner("Vikas", "Cycle"),
    ]

    admin = AdminPanel(restaurants)

    # ----- welcome -----
    print("\n" + "=" * 44)
    print("       FOOD DELIVERY SIMULATOR")
    print("=" * 44)

    customer_name = input("\nEnter your name: ").strip() or "Guest"
    starting_bal  = safe_input_float(f"Enter starting wallet balance (₹): ")
    customer      = Customer(customer_name, starting_bal)

    print(f"\n  Welcome, {customer.name}! 🎉")
    print(f"  Wallet: {customer.wallet}")

    # ----- main loop -----
    while True:

        print("\n========== Main Menu ==========")
        print("  1. Browse & Order Food")
        print("  2. View Cart")
        print("  3. Top-Up Wallet")
        print("  4. View My Order History")
        print("  5. View Saved Orders (File)")
        print("  6. Admin Panel")
        print("  7. Exit")

        choice = input("\n  Choice: ").strip()

        # ── 1. BROWSE & ORDER ──────────────────────────
        if choice == "1":

            print("\n========== Restaurants ==========")
            for i, r in enumerate(restaurants, start=1):
                print(f"  {i}. {r.name}  [{r.cuisine}]  ⭐ {r.average_rating()}")

            r_choice = safe_input_int("  Select restaurant: ") - 1
            if not (0 <= r_choice < len(restaurants)):
                print("  ❌ Invalid selection.")
                continue

            sel_rest = restaurants[r_choice]

            while True:
                filter_q = input(
                    "\n  Search item (press Enter to show all): "
                ).strip()
                sel_rest.show_menu(filter_q)

                item_num = safe_input_int("  Select item number (0 to go back): ")
                if item_num == 0:
                    break

                items = sel_rest.menu
                if filter_q:
                    items = [
                        f for f in sel_rest.menu
                        if filter_q.lower() in f.name.lower()
                        or filter_q.lower() in f.category.lower()
                    ]

                if not (1 <= item_num <= len(items)):
                    print("  ❌ Invalid item number.")
                    continue

                selected_food = items[item_num - 1]
                qty = safe_input_int("  Quantity: ", min_val=1)
                customer.add_to_cart(selected_food, qty)

                more = input("\n  Add more items? (yes/no): ").strip().lower()
                if more != "yes":
                    break

            if not customer.cart:
                continue

            # show cart
            customer.show_cart()

            # remove items?
            while True:
                rem = input(
                    "\n  Remove an item? Enter item number or press Enter to continue: "
                ).strip()
                if not rem:
                    break
                try:
                    customer.remove_from_cart(int(rem) - 1)
                    customer.show_cart()
                except ValueError:
                    print("  ❌ Invalid input.")

            if not customer.cart:
                print("  Cart is now empty — returning to menu.")
                continue

            # coupon
            gross_bill = customer.calculate_bill()
            discount   = 0

            coupon = input(
                "\n  Enter coupon code (Enter to skip): "
            ).strip().upper()

            if coupon in COUPONS:
                discount   = COUPONS[coupon]
                gross_bill = max(0, gross_bill - discount)
                print(f"  ✅ Coupon applied! Discount: ₹{discount}")
            elif coupon:
                print("  ❌ Invalid coupon code.")

            total_bill = gross_bill
            print(f"\n  Final bill: ₹{total_bill:.0f}")

            # payment method
            print("\n  Payment Method:")
            for i, method in enumerate(PaymentMethod, start=1):
                print(f"    {i}. {method.value}")
            p_choice = safe_input_int("  Select payment: ", 1, len(list(PaymentMethod)))
            payment  = list(PaymentMethod)[p_choice - 1]

            if payment == PaymentMethod.WALLET:
                success = customer.wallet.deduct(total_bill)
                if not success:
                    print("  Switching to Cash on Delivery.")
                    payment = PaymentMethod.CASH
                else:
                    print(
                        f"  ✅ Paid ₹{total_bill:.0f} from wallet. "
                        f"Remaining: {customer.wallet}"
                    )
            else:
                print(f"  ✅ Payment via {payment.value} confirmed.")

            # assign delivery partner
            partner = random.choice(delivery_partners)
            eta     = random.randint(20, 50)

            # receipt
            print_receipt(
                customer, sel_rest, partner,
                total_bill, discount, payment.value, eta
            )

            # tracking
            partner.track_delivery(eta)

            # rating
            rating = safe_input_int(
                "\n  Rate this restaurant (1–5): ", 1, 5
            )
            sel_rest.add_rating(rating)

            review = input("  Write a review (Enter to skip): ").strip()
            sel_rest.add_review(review)

            print(f"\n  Average rating: {sel_rest.average_rating()} ⭐")
            sel_rest.show_reviews()

            # save order
            items_summary = ", ".join(
                f"{ci.food.name} × {ci.quantity}" for ci in customer.cart
            )
            order_data = {
                "customer":         customer.name,
                "restaurant":       sel_rest.name,
                "items":            items_summary,
                "bill":             round(total_bill, 2),
                "discount":         discount,
                "payment":          payment.value,
                "delivery_partner": partner.name,
                "status":           OrderStatus.DELIVERED.value,
                "date":             str(datetime.now()),
            }

            customer.save_order(order_data)
            save_order_to_file(order_data)
            customer.clear_cart()
            print("\n  🎉 Order placed successfully!")

        # ── 2. VIEW CART ───────────────────────────────
        elif choice == "2":
            customer.show_cart()

        # ── 3. TOP-UP WALLET ───────────────────────────
        elif choice == "3":
            print(f"\n  Current balance: {customer.wallet}")
            amount = safe_input_float("  Amount to add (₹): ")
            customer.wallet.top_up(amount)

        # ── 4. ORDER HISTORY ───────────────────────────
        elif choice == "4":
            customer.show_order_history()

        # ── 5. SAVED ORDERS ────────────────────────────
        elif choice == "5":
            load_orders()

        # ── 6. ADMIN PANEL ─────────────────────────────
        elif choice == "6":
            admin.run()

        # ── 7. EXIT ────────────────────────────────────
        elif choice == "7":
            print(f"\n  Thanks for using the app, {customer.name}! 👋\n")
            break

        else:
            print("  ❌ Invalid choice — please try again.")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
