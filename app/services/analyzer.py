from typing import List, Dict
from collections import defaultdict

def calculate_total_income(transactions):
    total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
    return round(total_income, 2)

def calculate_total_expense(transactions):
    total_expense = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
    return round(total_expense, 2)

def calculate_net_savings(transactions):
    total_income = calculate_total_income(transactions)
    total_expense = calculate_total_expense(transactions)
    net_savings = total_income - total_expense
    return round(net_savings, 2)

def categorize_transactions(transactions):
    expense_categories = {
        "Groceries": ["Grocery", "Supermarket", "Mart"],
        "Utilities": ["Electricity", "Water Bill", "Gas"],
        "Shopping": ["Amazon", "Online Shopping", "Store"],
        "Travel": ["Uber", "Taxi", "Flight", "Train"],
        "Entertainment": ["Netflix", "Cinema", "Movie", "Spotify"],
    }

    income_categories = {
        "Salary": ["Salary", "Income", "Paycheck", "Salary Credit"],
        "Refund": ["Refund", "Cashback"],
        "Transfer In": ["Transfer In", "Bank Transfer"],
    }

    categorized_expenses = defaultdict(float)
    categorized_incomes = defaultdict(float)

    for t in transactions:
        description = t["description"].lower()
        amount = t["amount"]

        if amount < 0:  # Expense
            matched_category = None
            for category, keywords in expense_categories.items():
                if any(keyword.lower() in description for keyword in keywords):
                    matched_category = category
                    break

            category_to_update = matched_category if matched_category else "Others"
            categorized_expenses[category_to_update] += abs(amount)

        elif amount > 0:  # Income
            matched_category = None
            for category, keywords in income_categories.items():
                if any(keyword.lower() in description for keyword in keywords):
                    matched_category = category
                    break

            category_to_update = matched_category if matched_category else "Others"
            categorized_incomes[category_to_update] += amount

    # Convert to regular dict and round off values
    categorized_expenses = {k: round(v, 2) for k, v in categorized_expenses.items() if v > 0}
    categorized_incomes = {k: round(v, 2) for k, v in categorized_incomes.items() if v > 0}

    return categorized_expenses, categorized_incomes


def find_highest_expense(transactions):
    highest_expense = None
    max_amount = 0

    for t in transactions:
        if t["amount"] < 0 and abs(t["amount"]) > max_amount:
            max_amount = abs(t["amount"])
            highest_expense = t

    if highest_expense:
        return {
            "date": highest_expense["date"],
            "description": highest_expense["description"],
            "amount": round(highest_expense["amount"], 2),
            "balance": round(highest_expense["balance"], 2)
        }
    else:
        return None

def generate_analysis_summary(transactions: List[Dict]) -> str:
    income = calculate_total_income(transactions)
    expense = calculate_total_expense(transactions)
    savings = calculate_net_savings(transactions)
    exp_cat, inc_cat = categorize_transactions(transactions)
    top_exp = find_highest_expense(transactions)

    summary = f"Summary of Financial Analysis:\n"
    summary += f"Total Income: ₹{income}\n"
    summary += f"Total Expenses: ₹{expense}\n"
    summary += f"Net Savings: ₹{savings}\n\n"

    summary += f"Income Categories:\n"
    for k, v in inc_cat.items():
        summary += f"- {k}: ₹{v}\n"

    summary += f"\nExpense Categories:\n"
    for k, v in exp_cat.items():
        summary += f"- {k}: ₹{v}\n"

    if top_exp:
        summary += f"\nHighest Expense:\n"
        summary += f"- Date: {top_exp['date']}, Description: {top_exp['description']}, Amount: ₹{abs(top_exp['amount'])}, Balance: ₹{top_exp['balance']}\n"

    return summary