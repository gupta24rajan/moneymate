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