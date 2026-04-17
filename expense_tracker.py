"""
Personal Expense Tracker
========================
A CLI-based expense tracking application with CSV storage,
budget alerts, and monthly summary reports.
"""

import csv
import os
import json
from datetime import datetime
from collections import defaultdict


# ── File paths ──────────────────────────────────────────────────────────────
DATA_FILE = "expenses.csv"
BUDGET_FILE = "budgets.json"
CSV_HEADERS = ["id", "date", "category", "description", "amount"]

CATEGORIES = [
    "Food", "Transport", "Shopping", "Entertainment",
    "Health", "Utilities", "Education", "Other"
]


# ── Helpers ──────────────────────────────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print("=" * 55)
    print("        💰  PERSONAL EXPENSE TRACKER  💰")
    print("=" * 55)


def press_enter():
    input("\n[Enter dabao jaari rakhne ke liye...]")


def load_expenses():
    """CSV se saare expenses padhta hai."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_expense(expense: dict):
    """Ek naya expense CSV mein likhta hai."""
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(expense)


def next_id(expenses):
    if not expenses:
        return 1
    return max(int(e["id"]) for e in expenses) + 1


def load_budgets():
    if not os.path.exists(BUDGET_FILE):
        return {}
    with open(BUDGET_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_budgets(budgets):
    with open(BUDGET_FILE, "w", encoding="utf-8") as f:
        json.dump(budgets, f, indent=2)


# ── Features ─────────────────────────────────────────────────────────────────
def add_expense():
    clear()
    banner()
    print("\n➕  NAYA EXPENSE ADD KARO\n")

    # Category choose karo
    print("Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")
    while True:
        try:
            choice = int(input("\nCategory number chunno: "))
            if 1 <= choice <= len(CATEGORIES):
                category = CATEGORIES[choice - 1]
                break
            print("  ❌ Sahi number likho.")
        except ValueError:
            print("  ❌ Sirf number likho.")

    description = input("Description (e.g. Lunch at dhaba): ").strip() or "N/A"

    while True:
        try:
            amount = float(input("Amount (₹): "))
            if amount <= 0:
                print("  ❌ Amount zero se zyada honi chahiye.")
                continue
            break
        except ValueError:
            print("  ❌ Sirf number likho.")

    date_input = input("Date (YYYY-MM-DD) [Enter = aaj]: ").strip()
    if not date_input:
        date_input = datetime.today().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            print("  ❌ Galat format. Aaj ki date use ho rahi hai.")
            date_input = datetime.today().strftime("%Y-%m-%d")

    expenses = load_expenses()
    expense = {
        "id": next_id(expenses),
        "date": date_input,
        "category": category,
        "description": description,
        "amount": f"{amount:.2f}",
    }
    save_expense(expense)
    print(f"\n  ✅ Expense save ho gaya! (ID: {expense['id']})")

    # Budget alert check
    budgets = load_budgets()
    if category in budgets:
        month = date_input[:7]
        total_cat = sum(
            float(e["amount"])
            for e in load_expenses()
            if e["category"] == category and e["date"].startswith(month)
        )
        limit = budgets[category]
        if total_cat > limit:
            print(f"\n  ⚠️  ALERT: '{category}' budget exceed ho gaya!")
            print(f"     Budget: ₹{limit:.2f} | Kharch: ₹{total_cat:.2f}")
        elif total_cat >= 0.8 * limit:
            print(f"\n  ⚠️  WARNING: '{category}' budget ka 80% use ho chuka hai.")

    press_enter()


def view_expenses():
    clear()
    banner()
    print("\n📋  SAARE EXPENSES\n")
    expenses = load_expenses()
    if not expenses:
        print("  Abhi koi expense nahi hai. Pehle add karo!")
        press_enter()
        return

    # Optional filter
    month_filter = input("Kisi mahine ke expenses dekhne hain? (YYYY-MM) [Enter = sab]: ").strip()
    if month_filter:
        expenses = [e for e in expenses if e["date"].startswith(month_filter)]
        if not expenses:
            print(f"  '{month_filter}' mein koi expense nahi mila.")
            press_enter()
            return

    print(f"\n  {'ID':<5} {'Date':<12} {'Category':<15} {'Description':<22} {'Amount':>8}")
    print("  " + "-" * 65)
    total = 0.0
    for e in expenses:
        amt = float(e["amount"])
        total += amt
        print(f"  {e['id']:<5} {e['date']:<12} {e['category']:<15} {e['description'][:20]:<22} ₹{amt:>7.2f}")
    print("  " + "-" * 65)
    print(f"  {'TOTAL':<54} ₹{total:>7.2f}")
    press_enter()


def monthly_summary():
    clear()
    banner()
    print("\n📊  MONTHLY SUMMARY\n")
    expenses = load_expenses()
    if not expenses:
        print("  Koi expense nahi hai.")
        press_enter()
        return

    month = input("Mahina likho (YYYY-MM) [Enter = current month]: ").strip()
    if not month:
        month = datetime.today().strftime("%Y-%m")

    month_expenses = [e for e in expenses if e["date"].startswith(month)]
    if not month_expenses:
        print(f"  '{month}' mein koi expense nahi mila.")
        press_enter()
        return

    cat_totals = defaultdict(float)
    for e in month_expenses:
        cat_totals[e["category"]] += float(e["amount"])

    grand_total = sum(cat_totals.values())
    budgets = load_budgets()

    print(f"\n  📅 Month: {month}")
    print(f"  {'Category':<18} {'Spent':>10} {'Budget':>10} {'Status'}")
    print("  " + "-" * 55)

    for cat, spent in sorted(cat_totals.items(), key=lambda x: -x[1]):
        budget = budgets.get(cat, None)
        budget_str = f"₹{budget:.2f}" if budget else "  N/A"
        if budget:
            status = "✅ OK" if spent <= budget else "❌ Over"
        else:
            status = "—"
        print(f"  {cat:<18} ₹{spent:>9.2f} {budget_str:>10}   {status}")

    print("  " + "-" * 55)
    print(f"  {'GRAND TOTAL':<18} ₹{grand_total:>9.2f}")

    # Simple bar chart
    print(f"\n  📈 Spending Chart ({month}):\n")
    max_spent = max(cat_totals.values())
    for cat, spent in sorted(cat_totals.items(), key=lambda x: -x[1]):
        bar_len = int((spent / max_spent) * 25)
        bar = "█" * bar_len
        print(f"  {cat:<14} {bar:<25} ₹{spent:.2f}")

    press_enter()


def delete_expense():
    clear()
    banner()
    print("\n🗑️  EXPENSE DELETE KARO\n")
    expenses = load_expenses()
    if not expenses:
        print("  Koi expense nahi hai.")
        press_enter()
        return

    try:
        exp_id = int(input("Delete karne wala Expense ID likho: "))
    except ValueError:
        print("  ❌ Galat ID.")
        press_enter()
        return

    new_expenses = [e for e in expenses if int(e["id"]) != exp_id]
    if len(new_expenses) == len(expenses):
        print(f"  ❌ ID {exp_id} ka koi expense nahi mila.")
    else:
        # Rewrite CSV
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(new_expenses)
        print(f"  ✅ ID {exp_id} ka expense delete ho gaya.")
    press_enter()


def set_budget():
    clear()
    banner()
    print("\n🎯  BUDGET SET KARO\n")
    budgets = load_budgets()

    print("Kaunsi category ka budget set karna hai?")
    for i, cat in enumerate(CATEGORIES, 1):
        current = budgets.get(cat, None)
        current_str = f" (current: ₹{current:.2f})" if current else ""
        print(f"  {i}. {cat}{current_str}")

    try:
        choice = int(input("\nCategory number: "))
        if not (1 <= choice <= len(CATEGORIES)):
            raise ValueError
        category = CATEGORIES[choice - 1]
    except ValueError:
        print("  ❌ Galat choice.")
        press_enter()
        return

    try:
        limit = float(input(f"'{category}' ke liye monthly budget (₹): "))
        if limit <= 0:
            raise ValueError
    except ValueError:
        print("  ❌ Galat amount.")
        press_enter()
        return

    budgets[category] = limit
    save_budgets(budgets)
    print(f"  ✅ '{category}' ka monthly budget ₹{limit:.2f} set ho gaya!")
    press_enter()


# ── Main Menu ────────────────────────────────────────────────────────────────
def main():
    while True:
        clear()
        banner()
        print("\n  1. ➕  Naya Expense Add Karo")
        print("  2. 📋  Saare Expenses Dekho")
        print("  3. 📊  Monthly Summary")
        print("  4. 🎯  Budget Set Karo")
        print("  5. 🗑️   Expense Delete Karo")
        print("  6. 🚪  Bahar Jao\n")

        choice = input("  Option chunno (1-6): ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            monthly_summary()
        elif choice == "4":
            set_budget()
        elif choice == "5":
            delete_expense()
        elif choice == "6":
            print("\n  👋 App band ho rahi hai. Khyaal rakhna!\n")
            break
        else:
            print("  ❌ Galat choice. 1-6 mein se kuch chunno.")
            press_enter()


if __name__ == "__main__":
    main()
