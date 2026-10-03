import json
import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.foundation.llm_client import LLMClient
from ai.foundation.prompts.templates import FINANCIAL_AGENT_PROMPT
from ai.schemas.agents import AgentAction, AgentRunResponse
from app.models.category import Category
from app.models.expense import Expense

logger = logging.getLogger(__name__)

MAX_STEPS = 4
FINAL_ANSWER = "FINAL"


class AgentState(TypedDict):
    task: str
    user_id: int
    db: AsyncSession
    steps: Annotated[list[dict[str, Any]], lambda a, b: a + b]
    actions: Annotated[list[AgentAction], lambda a, b: a + b]
    answer: str
    finished: bool


class FinancialAgent:
    """ReAct style loop: LLM ek tool choose karta hai, tool DB se data laata hai, phir final answer."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.graph = self._build_graph()

    async def run(
        self,
        db: AsyncSession,
        user_id: int,
        task: str
    ) -> AgentRunResponse:
        state: AgentState = {
            "task": task,
            "user_id": user_id,
            "db": db,
            "steps": [],
            "actions": [],
            "answer": "",
            "finished": False
        }

        try:
            final_state = await self.graph.ainvoke(state)
        except Exception as exc:
            logger.exception("Financial agent run failed")
            return AgentRunResponse(
                status="error",
                response=f"Agent run failed: {type(exc).__name__}",
                actions=[]
            )

        return AgentRunResponse(
            status="success",
            response=final_state["answer"],
            actions=final_state["actions"]
        )

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("plan", self._plan)
        graph.add_node("act", self._act)
        graph.add_node("finalize", self._finalize)

        graph.add_edge(START, "plan")
        graph.add_conditional_edges(
            "plan",
            self._route,
            {"tools": "act", "final": "finalize"}
        )
        graph.add_edge("act", "plan")
        graph.add_edge("finalize", END)

        return graph.compile()

    def _route(self, state: AgentState) -> str:
        if state["finished"] or len(state["actions"]) >= MAX_STEPS:
            return "final"
        return "tools"

    async def _plan(self, state: AgentState) -> dict[str, Any]:
        prompt = FINANCIAL_AGENT_PROMPT.format(
            task=state["task"],
            tools=self.tool_descriptions(),
            steps=self._render_steps(state["steps"]),
            tool_names=self.tool_names()
        )

        try:
            decision = (await self.llm_client.generate(prompt)).strip()
        except Exception:
            logger.exception("LLM failed while planning agent step")
            return {"finished": True, "answer": self._offline_answer(state)}

        if decision.startswith(FINAL_ANSWER):
            return {
                "finished": True,
                "answer": decision[len(FINAL_ANSWER):].strip()
            }

        return {"steps": [{"observation": decision}]}

    async def _act(self, state: AgentState) -> dict[str, Any]:
        decision = state["steps"][-1]["observation"]
        tool_name, arguments = self._parse_tool_call(decision)

        if tool_name not in self.tool_names():
            observation = f"Error: unknown tool '{tool_name}'."
        else:
            try:
                observation = await self._run_tool(
                    tool_name,
                    arguments,
                    state["db"],
                    state["user_id"]
                )
            except Exception as exc:
                logger.exception("Agent tool %s failed", tool_name)
                observation = f"Error: {type(exc).__name__}"

        action = AgentAction(
            tool=tool_name,
            arguments=arguments,
            observation=observation
        )

        return {
            "steps": [{"observation": observation}],
            "actions": [action]
        }

    async def _finalize(self, state: AgentState) -> dict[str, Any]:
        if state["answer"]:
            return {}

        return {"answer": self._offline_answer(state)}

    def _offline_answer(self, state: AgentState) -> str:
        if not state["actions"]:
            return "I could not gather enough recorded expense data to answer this."

        return (
            "I could not finish the analysis, but here is the expense data "
            "gathered so far: " + " | ".join(
                action.observation for action in state["actions"]
            )
        )

    def _parse_tool_call(self, decision: str) -> tuple[str, dict[str, Any]]:
        try:
            payload = json.loads(decision)
            return str(payload["tool"]), dict(payload.get("arguments") or {})
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return decision.strip(), {}

    def _render_steps(self, steps: list[dict[str, Any]]) -> str:
        if not steps:
            return "No tool has been called yet."

        return "\n".join(
            f"- {step['observation']}" for step in steps
        )

    def tool_names(self) -> list[str]:
        return ["get_spending_summary", "get_largest_expenses", "get_category_trend"]

    def tool_descriptions(self) -> str:
        return (
            "get_spending_summary(days) - total amount, expense count and "
            "category breakdown for the last N days.\n"
            "get_largest_expenses(limit) - the biggest individual expenses.\n"
            "get_category_trend(category, months) - month over month total for "
            "one category."
        )

    async def _run_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        db: AsyncSession,
        user_id: int
    ) -> str:
        if tool_name == "get_spending_summary":
            return await self.get_spending_summary(
                db, user_id, int(arguments.get("days", 30))
            )
        if tool_name == "get_largest_expenses":
            return await self.get_largest_expenses(
                db, user_id, int(arguments.get("limit", 5))
            )
        if tool_name == "get_category_trend":
            return await self.get_category_trend(
                db, user_id, str(arguments.get("category", "")), int(arguments.get("months", 3))
            )
        raise ValueError(f"unknown tool '{tool_name}'")

    async def get_spending_summary(
        self,
        db: AsyncSession,
        user_id: int,
        days: int
    ) -> str:
        window_start = date.today() - timedelta(days=days)

        totals = (
            select(
                func.coalesce(func.sum(Expense.amount), Decimal("0.00")),
                func.count(Expense.id)
            )
            .where(Expense.user_id == user_id, Expense.expense_date >= window_start)
        )
        total_amount, total_count = (await db.execute(totals)).one()

        breakdown = (
            select(Category.name, func.coalesce(func.sum(Expense.amount), Decimal("0.00")))
            .join(Category, Expense.category_id == Category.id)
            .where(Expense.user_id == user_id, Expense.expense_date >= window_start)
            .group_by(Category.name)
            .order_by(func.sum(Expense.amount).desc())
        )
        rows = (await db.execute(breakdown)).all()

        if not rows:
            return f"No expenses recorded in the last {days} days."

        breakdown_text = ", ".join(f"{name}: {amount}" for name, amount in rows)
        return (
            f"Last {days} days - total {total_amount} across {total_count} expenses. "
            f"By category: {breakdown_text}"
        )

    async def get_largest_expenses(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int
    ) -> str:
        stmt = (
            select(Expense.description, Expense.amount, Expense.expense_date, Category.name)
            .join(Category, Expense.category_id == Category.id)
            .where(Expense.user_id == user_id)
            .order_by(Expense.amount.desc())
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()

        if not rows:
            return "No expenses recorded yet."

        return " | ".join(
            f"{category} {amount} on {expense_date} ({description})"
            for description, amount, expense_date, category in rows
        )

    async def get_category_trend(
        self,
        db: AsyncSession,
        user_id: int,
        category: str,
        months: int
    ) -> str:
        window_start = date.today().replace(day=1) - timedelta(days=31 * months)
        stmt = (
            select(Expense.expense_date, Expense.amount)
            .join(Category, Expense.category_id == Category.id)
            .where(
                Expense.user_id == user_id,
                Category.name.ilike(f"%{category}%"),
                Expense.expense_date >= window_start
            )
        )
        rows = (await db.execute(stmt)).all()

        if not rows:
            return f"No '{category}' expenses recorded in the last {months} months."

        monthly: dict[str, Decimal] = {}
        for expense_date, amount in rows:
            key = f"{expense_date.year}-{expense_date.month:02d}"
            monthly[key] = monthly.get(key, Decimal("0.00")) + amount

        trend_text = ", ".join(
            f"{month}: {monthly[month]}" for month in sorted(monthly)
        )
        return f"{category} month over month - {trend_text}"


financial_agent = FinancialAgent(LLMClient())
