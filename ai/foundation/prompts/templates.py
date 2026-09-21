EXPENSE_CATEGORIZATION_PROMPT = """
You are an expert financial classifier. Categorize the given transaction into EXACTLY ONE of these categories:
- Food
- Travel
- Shopping
- Bills
- Investment
- Other

Transaction: {transaction}
Category:
"""

FINANCIAL_ADVICE_PROMPT = """
You are a personal finance assistant. Analyze the user's spending summary and give 2 short actionable tips.

Summary: {summary}
Advice:
"""

MONTHLY_COMPARISON_PROMPT = """
You are a financial advisor for 'MoneyMate'.

Analyze the user's month-over-month spending comparison and generate:
1. A concise 2-sentence explanation.
2. Two short practical money-saving tips.

Month 1 ({month1}/{year1}) Total: ₹{total_month1}
Month 2 ({month2}/{year2}) Total: ₹{total_month2}
Overall Percentage Change: {change_percent}%
Overall Direction: {change_direction}

Month 1 Category Breakdown:
{breakdown_month1}

Month 2 Category Breakdown:
{breakdown_month2}

Category-wise Comparison:
{category_comparison}

Top Increased Category: {top_increased_category}
Top Decreased Category: {top_decreased_category}

Keep the tone helpful, practical, and easy to understand.
Do not use Markdown formatting.
"""
