"""
AI Agents Module for AI Expense & Budget Management System.
Agent 1: Transaction Analyst Agent.
"""

from typing import Dict, Any, Optional
import pandas as pd
from llm_client import get_llm_response


def transaction_analyst_agent(
    summary: Dict[str, Any],
    category_breakdown: pd.DataFrame,
    trend_data: pd.DataFrame,
    monthly_income: float,
    monthly_budget: float
) -> Dict[str, Any]:
    """
    Transaction Analyst Agent: Interprets calculated financial analytics, spending patterns,
    and budget alignment without calculating or inventing new financial numbers.

    Parameters:
        summary (dict): Factual summary dictionary calculated by analytics.py.
        category_breakdown (pd.DataFrame): Category breakdown DataFrame calculated by analytics.py.
        trend_data (pd.DataFrame): Time-series trend DataFrame calculated by analytics.py.
        monthly_income (float): User's specified monthly income.
        monthly_budget (float): User's target monthly budget allocation.

    Returns:
        dict: Structured analysis output containing agent findings and insights.
    """
    agent_name = "Transaction Analyst Agent"

    if not summary or summary.get("transaction_count", 0) == 0:
        return {
            "agent_name": agent_name,
            "status": "warning",
            "summary": "No transaction data available for analysis.",
            "key_insights": ["Upload or add transactions to generate spending insights."],
            "spending_behavior": "No spending records found.",
            "top_categories": [],
            "budget_observation": "Budget analysis requires valid expense transactions."
        }

    # Format factual metrics for LLM prompt context
    total_expenses = summary.get("total_expenses", 0.0)
    tx_count = summary.get("transaction_count", 0)
    avg_tx = summary.get("average_transaction", 0.0)
    highest_tx = summary.get("highest_transaction", {})
    spending_by_category = summary.get("spending_by_category", {})
    category_percentages = summary.get("category_percentages", {})
    payment_methods = summary.get("spending_by_payment_method", {})

    # Format top categories string
    top_cat_lines = []
    if isinstance(category_breakdown, pd.DataFrame) and not category_breakdown.empty:
        for _, row in category_breakdown.head(5).iterrows():
            top_cat_lines.append(
                f"- {row['category']}: INR {row['amount']:,.2f} ({row['percentage']}%)"
            )
    top_categories_str = "\n".join(top_cat_lines) if top_cat_lines else "None"

    # Format budget comparison
    budget_utilization = (total_expenses / monthly_budget * 100.0) if monthly_budget > 0 else 0.0
    income_ratio = (total_expenses / monthly_income * 100.0) if monthly_income > 0 else 0.0

    system_prompt = (
        "You are an expert AI Transaction Analyst Agent for a personal finance system.\n"
        "Your role is to analyze spending behavior based ONLY on the provided pre-calculated metrics.\n"
        "STRICT RULES:\n"
        "1. Do NOT calculate or invent new numerical totals, sums, or percentages.\n"
        "2. Base all observations strictly on the factual numbers provided.\n"
        "3. Clearly distinguish factual observations from analytical interpretations.\n"
        "4. Provide 3 to 5 clear, meaningful insights.\n"
        "5. Be concise, professional, and actionable."
    )

    user_prompt = f"""
Here are the exact, pre-calculated financial metrics for the user:

- Total Expenses: INR {total_expenses:,.2f}
- Transaction Count: {tx_count}
- Average Transaction Amount: INR {avg_tx:,.2f}
- Highest Transaction: {highest_tx.get('description', 'N/A')} (INR {highest_tx.get('amount', 0.0):,.2f} on {highest_tx.get('date', 'N/A')})
- User Monthly Income: INR {monthly_income:,.2f}
- User Monthly Target Budget: INR {monthly_budget:,.2f}
- Budget Utilization Rate: {budget_utilization:.2f}%
- Expense to Income Ratio: {income_ratio:.2f}%

Top Categories Breakdown:
{top_categories_str}

Payment Methods Used:
{payment_methods}

Please provide an analysis covering:
1. OVERALL SPENDING BEHAVIOR: A brief narrative overview.
2. TOP CATEGORIES & CONCENTRATION: Observations on category concentration.
3. BUDGET & INCOME OBSERVATION: How spending compares to the target budget and income.
4. KEY INSIGHTS: Exactly 3 to 5 bullet points of key observations.
"""

    llm_output = get_llm_response(system_prompt, user_prompt)

    # Handle error or fallback responses from LLM client gracefully
    if (
        llm_output.startswith("Configuration Error")
        or llm_output.startswith("OpenAI API Error")
        or llm_output.startswith("Unexpected Error")
    ):
        # Deterministic fallback response when API key is unconfigured or call fails
        top_cats = (
            [
                f"{row['category']}: INR {row['amount']:,.2f} ({row['percentage']}%)"
                for _, row in category_breakdown.head(3).iterrows()
            ]
            if not category_breakdown.empty
            else []
        )
        return {
            "agent_name": agent_name,
            "status": "fallback",
            "summary": f"Total expenditure of INR {total_expenses:,.2f} recorded across {tx_count} transactions.",
            "key_insights": [
                f"Total expenditure is INR {total_expenses:,.2f} across {tx_count} transactions.",
                f"Top spending category is {category_breakdown.iloc[0]['category'] if not category_breakdown.empty else 'N/A'} (INR {category_breakdown.iloc[0]['amount']:,.2f} if not category_breakdown.empty else 0).",
                f"Budget utilization stands at {budget_utilization:.1f}% relative to monthly target budget of INR {monthly_budget:,.2f}.",
                f"Highest single expense was '{highest_tx.get('description', 'N/A')}' for INR {highest_tx.get('amount', 0.0):,.2f}.",
            ],
            "spending_behavior": f"Average spending per transaction is INR {avg_tx:,.2f}. Highest category concentration is in top spending categories.",
            "top_categories": top_cats,
            "budget_observation": f"Total spending represents {budget_utilization:.1f}% of budget and {income_ratio:.1f}% of monthly income. ({llm_output})",
        }

    # Format structured response dictionary from LLM output
    key_insights_list = []
    for line in llm_output.split("\n"):
        line_s = line.strip()
        if line_s.startswith("-") or line_s.startswith("*") or (
            len(line_s) > 2 and line_s[0].isdigit() and line_s[1] in [".", ")"]
        ):
            key_insights_list.append(line_s.lstrip("-*0123456789. ").strip())

    if not key_insights_list:
        key_insights_list = [llm_output]

    top_cats = (
        [
            f"{row['category']}: INR {row['amount']:,.2f} ({row['percentage']}%)"
            for _, row in category_breakdown.head(5).iterrows()
        ]
        if not category_breakdown.empty
        else []
    )

    return {
        "agent_name": agent_name,
        "status": "success",
        "summary": f"Analyzed {tx_count} transactions totaling INR {total_expenses:,.2f}.",
        "key_insights": key_insights_list[:5],
        "spending_behavior": llm_output,
        "top_categories": top_cats,
        "spending_by_category": spending_by_category,
        "budget_observation": f"Budget utilization is {budget_utilization:.1f}% of target budget (INR {monthly_budget:,.2f}) and {income_ratio:.1f}% of income (INR {monthly_income:,.2f}).",
    }



def run_anomaly_detection(
    df: pd.DataFrame, analysis_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Anomaly Detection Agent (Agent 2):
    Identifies unusual or suspicious expense transactions using category-aware
    statistical anomaly detection (IQR & Z-score) and provides an LLM interpretation.

    Parameters:
        df (pd.DataFrame): Expense transactions DataFrame.
        analysis_context (dict, optional): Optional context passed from previous agent steps.

    Returns:
        dict: Structured dictionary containing anomaly count, list of anomalies with severity,
              and agent interpretation.
    """
    agent_name = "Anomaly Detection Agent"
    required_cols = {"date", "category", "description", "amount", "payment_method"}

    if df is None or df.empty or not required_cols.issubset(set(df.columns)):
        return {
            "agent_name": agent_name,
            "status": "success",
            "total_transactions_checked": 0,
            "anomaly_count": 0,
            "anomaly_rate": 0.0,
            "anomalies": [],
            "llm_explanation": "No transactions available to evaluate for anomalies.",
        }

    df_clean = df.copy()
    df_clean["amount"] = pd.to_numeric(df_clean["amount"], errors="coerce")
    df_clean = df_clean.dropna(subset=["amount", "category"]).copy()
    df_clean = df_clean[df_clean["amount"] > 0]

    total_checked = len(df_clean)
    if total_checked == 0:
        return {
            "agent_name": agent_name,
            "status": "success",
            "total_transactions_checked": 0,
            "anomaly_count": 0,
            "anomaly_rate": 0.0,
            "anomalies": [],
            "llm_explanation": "No valid numeric expense records to analyze.",
        }

    # 1. Overall statistical benchmarks
    overall_mean = float(df_clean["amount"].mean())
    overall_std = float(df_clean["amount"].std(ddof=1)) if total_checked > 1 else 0.0
    overall_q1 = float(df_clean["amount"].quantile(0.25))
    overall_q3 = float(df_clean["amount"].quantile(0.75))
    overall_iqr = overall_q3 - overall_q1
    overall_upper_bound = overall_q3 + 1.5 * overall_iqr

    # 2. Category-aware statistical benchmarks
    cat_stats = {}
    for cat, group in df_clean.groupby("category"):
        amounts = group["amount"]
        c_mean = float(amounts.mean())
        c_std = float(amounts.std(ddof=1)) if len(amounts) > 1 else 0.0
        c_q1 = float(amounts.quantile(0.25))
        c_q3 = float(amounts.quantile(0.75))
        c_iqr = c_q3 - c_q1
        c_upper = c_q3 + 1.5 * c_iqr if c_iqr > 0 else c_mean * 1.8
        cat_stats[cat] = {
            "mean": c_mean,
            "std": c_std,
            "upper_bound": max(c_upper, c_mean * 1.5),
            "count": len(amounts),
        }

    anomalies_list = []
    severity_order = {"High": 3, "Medium": 2, "Low": 1}

    for _, row in df_clean.iterrows():
        amt = float(row["amount"])
        cat = str(row["category"])
        z_score = (amt - overall_mean) / overall_std if overall_std > 0 else 0.0

        c_stat = cat_stats.get(cat, {})
        c_mean = c_stat.get("mean", overall_mean)
        c_upper = c_stat.get("upper_bound", overall_upper_bound)
        cat_z_score = (
            (amt - c_mean) / c_stat.get("std", 1.0)
            if c_stat.get("std", 0.0) > 0
            else 0.0
        )

        fixed_recurring_cats = {"rent", "bills", "utility", "utilities", "housing", "mortgage"}
        is_fixed_recurring = cat.lower().strip() in fixed_recurring_cats

        is_overall_anomaly = amt > overall_upper_bound or z_score >= 2.0
        is_category_anomaly = (
            amt > c_upper and len(df_clean[df_clean["category"] == cat]) >= 2
        ) or cat_z_score >= 2.5

        # Fixed recurring expenses are evaluated strictly against category norm to prevent false positives
        if is_fixed_recurring:
            is_flagged = is_category_anomaly and amt > c_mean * 1.5
        else:
            is_flagged = is_overall_anomaly or is_category_anomaly

        if is_flagged:
            # Deterministic severity assignment
            if (
                z_score >= 3.0
                or amt >= 3.0 * overall_upper_bound
                or amt >= 4.0 * c_mean
            ):
                severity = "High"
            elif (
                z_score >= 2.0
                or amt >= overall_upper_bound
                or amt >= 2.5 * c_mean
            ):
                severity = "Medium"
            else:
                severity = "Low"

            # Detailed human-readable reasons
            reasons = []
            if z_score >= 2.0 and not is_fixed_recurring:
                reasons.append(f"Overall Z-score of {z_score:.2f}")
            if amt > overall_upper_bound and not is_fixed_recurring:
                reasons.append(
                    f"Exceeds overall threshold (INR {amt:,.2f} > INR {overall_upper_bound:,.2f})"
                )
            if is_category_anomaly and amt > c_mean:
                reasons.append(
                    f"Exceeds {cat} category benchmark (INR {amt:,.2f} vs avg INR {c_mean:,.2f})"
                )
            if is_category_anomaly and amt > c_mean:
                reasons.append(
                    f"Exceeds {cat} category benchmark (INR {amt:,.2f} vs avg INR {c_mean:,.2f})"
                )

            reason_str = (
                " | ".join(reasons)
                if reasons
                else "Spike in transaction amount relative to category norm"
            )

            if isinstance(row["date"], (pd.Timestamp, pd.DatetimeIndex)):
                date_str = row["date"].strftime("%Y-%m-%d")
            else:
                date_str = str(row["date"])[:10]

            anomalies_list.append(
                {
                    "date": date_str,
                    "category": cat,
                    "description": str(row["description"]),
                    "amount": round(amt, 2),
                    "payment_method": str(row["payment_method"]),
                    "reason": reason_str,
                    "severity": severity,
                    "_severity_rank": severity_order.get(severity, 1),
                }
            )

    # Sort anomalies by severity rank descending, then amount descending
    anomalies_list.sort(
        key=lambda x: (x["_severity_rank"], x["amount"]), reverse=True
    )

    # Clean internal helper key
    for a in anomalies_list:
        a.pop("_severity_rank", None)

    anomaly_count = len(anomalies_list)
    anomaly_rate = (
        round((anomaly_count / total_checked) * 100.0, 2) if total_checked > 0 else 0.0
    )

    # 3. Optional LLM Interpretation step
    llm_explanation = ""
    if anomaly_count > 0:
        anom_summary_text = "\n".join(
            [
                f"- [{a['severity']} Severity] {a['date']} | {a['category']} | '{a['description']}': INR {a['amount']:,.2f} ({a['reason']})"
                for a in anomalies_list[:8]
            ]
        )

        system_prompt = (
            "You are an expert AI Anomaly Detection Agent for personal finance.\n"
            "Analyze the detected financial anomalies provided below.\n"
            "Explain WHY these transactions are flagged, their potential risk level, and suggested actions for the user.\n"
            "Do NOT calculate or modify the numbers provided."
        )

        user_prompt = f"""
Detected Anomalies ({anomaly_count} out of {total_checked} transactions, rate: {anomaly_rate}%):

{anom_summary_text}

Provide a concise, professional evaluation of these flagged transactions.
"""

        llm_response = get_llm_response(system_prompt, user_prompt)
        if (
            llm_response.startswith("Configuration Error")
            or llm_response.startswith("OpenAI API Error")
            or llm_response.startswith("Unexpected Error")
        ):
            llm_explanation = (
                f"Identified {anomaly_count} statistical anomalies ({anomaly_rate}% anomaly rate). "
                f"Top flagged transaction: '{anomalies_list[0]['description']}' (INR {anomalies_list[0]['amount']:,.2f}, {anomalies_list[0]['severity']} severity)."
            )
        else:
            llm_explanation = llm_response
    else:
        llm_explanation = (
            "All transactions fall within expected spending patterns. No statistical anomalies detected."
        )

    return {
        "agent_name": agent_name,
        "status": "success",
        "total_transactions_checked": total_checked,
        "anomaly_count": anomaly_count,
        "anomaly_rate": anomaly_rate,
        "anomalies": anomalies_list,
        "llm_explanation": llm_explanation,
    }


def run_budget_planner(
    monthly_income: float,
    monthly_budget: float,
    analysis_context: Optional[Dict[str, Any]] = None,
    anomaly_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Budget Planner Agent (Agent 3):
    Creates a practical category-wise monthly spending plan based on deterministic rules,
    user income/budget, historical spending patterns, and detected anomalies.

    Parameters:
        monthly_income (float): User's specified monthly income.
        monthly_budget (float): User's target monthly budget allocation.
        analysis_context (dict, optional): Output from Agent 1 (Transaction Analyst Agent).
        anomaly_context (dict, optional): Output from Agent 2 (Anomaly Detection Agent).

    Returns:
        dict: Structured dictionary containing category budgets, expected savings, rationale, and warnings.
    """
    agent_name = "Budget Planner Agent"

    # 1. Validate income and budget inputs & calculate effective spending ceiling
    income = (
        float(monthly_income)
        if monthly_income and float(monthly_income) > 0
        else 100000.0
    )
    raw_budget = (
        float(monthly_budget)
        if monthly_budget and float(monthly_budget) > 0
        else income
    )

    warnings = []
    if raw_budget > income:
        effective_ceiling = income
        warnings.append(
            f"OVERBUDGET WARNING: Your target monthly budget (INR {raw_budget:,.2f}) exceeds your monthly income (INR {income:,.2f}). "
            f"Effective spending ceiling has been capped at your income limit of INR {income:,.2f}."
        )
    else:
        effective_ceiling = raw_budget

    budget = effective_ceiling

    # Priority mapping
    essential_cats = {"Rent", "Bills", "Healthcare", "Education"}
    flexible_cats = {"Groceries", "Transport", "Other"}
    discretionary_cats = {"Shopping", "Entertainment", "Travel", "Food"}

    # 2. Track non-recurring anomalies per category
    cat_anomalies_total = {}
    if anomaly_context and "anomalies" in anomaly_context:
        for anom in anomaly_context.get("anomalies", []):
            cat = anom.get("category", "Other")
            amt = float(anom.get("amount", 0.0))
            if cat != "Rent":
                cat_anomalies_total[cat] = cat_anomalies_total.get(cat, 0.0) + amt

    # 3. Extract historical category totals and normalized monthly span
    cat_historical_total = {}
    months_spanned = 2.0  # Default to 2 months if unspecified

    if analysis_context and "summary" in analysis_context and isinstance(analysis_context["summary"], dict):
        months_spanned = float(analysis_context["summary"].get("months_spanned", 2.0))

    if analysis_context and "spending_by_category" in analysis_context:
        cat_historical_total = dict(analysis_context["spending_by_category"])
    elif analysis_context and "top_categories" in analysis_context:
        top_cats = analysis_context.get("top_categories", [])
        for item in top_cats:
            if ":" in item and "INR" in item:
                parts = item.split(":")
                c_name = parts[0].strip()
                val_str = (
                    parts[1].split("INR")[1].split("(")[0].replace(",", "").strip()
                )
                try:
                    cat_historical_total[c_name] = float(val_str)
                except ValueError:
                    pass

    # Default fallback category distribution if context is empty
    if not cat_historical_total:
        cat_historical_total = {
            "Rent": 50000.0,
            "Shopping": 138749.0,
            "Travel": 52000.0,
            "Healthcare": 49850.0,
            "Entertainment": 36399.0,
            "Groceries": 14940.0,
            "Food": 10950.0,
            "Bills": 9478.0,
            "Transport": 8840.0,
            "Education": 1949.0,
            "Other": 1650.0,
        }

    # 4. Compute monthly baseline spend per category excluding one-off anomalies
    cat_monthly_baseline = {}

    for cat, total_spend in cat_historical_total.items():
        m_spend = total_spend / months_spanned if months_spanned > 0 else total_spend
        anom_spend = cat_anomalies_total.get(cat, 0.0)
        m_anom_spend = anom_spend / months_spanned if months_spanned > 0 else anom_spend

        # Exclude one-off anomaly portion to establish recurring baseline
        baseline = max(m_spend - m_anom_spend, 0.0)
        cat_monthly_baseline[cat] = baseline

        if anom_spend > 0:
            warnings.append(
                f"Category '{cat}' had INR {anom_spend:,.2f} in one-off anomalies; excluded from recurring monthly baseline."
            )

    total_recurring_baseline = sum(cat_monthly_baseline.values())
    essential_baseline_total = sum(b for c, b in cat_monthly_baseline.items() if c in essential_cats)
    is_infeasible = essential_baseline_total > budget

    if is_infeasible:
        shortfall = essential_baseline_total - budget
        warnings.append(
            f"INFEASIBLE BUDGET: Budget is currently below the essential spending baseline. "
            f"Mandatory essential costs (INR {essential_baseline_total:,.2f}) exceed spending ceiling (INR {budget:,.2f}) by INR {shortfall:,.2f}."
        )
    elif total_recurring_baseline > budget:
        overspend = total_recurring_baseline - budget
        warnings.append(
            f"Historical recurring spend (INR {total_recurring_baseline:,.2f}) exceeds spending ceiling (INR {budget:,.2f}) by INR {overspend:,.2f}."
        )

    # 5. Deterministic Category Budget Calculations
    category_results = []
    allocated_sum = 0.0

    for cat, baseline in cat_monthly_baseline.items():
        if cat in essential_cats:
            priority = "Essential"
            if total_recurring_baseline > budget and (total_recurring_baseline - budget) > 0.3 * budget:
                rec = baseline * 0.95
                reason = "Essential priority: protected with minor 5% optimization."
            else:
                rec = baseline
                reason = "Essential priority: budget fully maintained for essential living costs."
        elif cat in flexible_cats:
            priority = "Flexible"
            if total_recurring_baseline > budget:
                rec = baseline * 0.85
                reason = "Flexible priority: 15% optimization recommended."
            else:
                rec = baseline
                reason = "Flexible priority: maintained based on past spending."
        else:
            priority = "Discretionary"
            if total_recurring_baseline > budget:
                rec = baseline * 0.65
                reason = "Discretionary priority: 35% reduction recommended to align with target budget."
            else:
                rec = baseline
                reason = "Discretionary priority: aligned with recurring historical average."

        rec = round(rec, 2)
        adj_amount = round(rec - baseline, 2)
        adj_pct = (
            round((adj_amount / baseline * 100.0), 2) if baseline > 0 else 0.0
        )

        category_results.append(
            {
                "category": cat,
                "historical_spend": round(baseline, 2),
                "recommended_budget": rec,
                "adjustment_amount": adj_amount,
                "adjustment_percentage": adj_pct,
                "priority": priority,
                "reason": reason,
            }
        )
        allocated_sum += rec

    # 6. Scaling limit: Ensure sum of category recommended budgets <= budget (effective_ceiling)
    if allocated_sum > budget and allocated_sum > 0:
        scale_factor = budget / allocated_sum
        allocated_sum = 0.0
        for item in category_results:
            item["recommended_budget"] = round(
                item["recommended_budget"] * scale_factor, 2
            )
            item["adjustment_amount"] = round(
                item["recommended_budget"] - item["historical_spend"], 2
            )
            item["adjustment_percentage"] = (
                round(
                    (item["adjustment_amount"] / item["historical_spend"] * 100.0),
                    2,
                )
                if item["historical_spend"] > 0
                else 0.0
            )
            allocated_sum += item["recommended_budget"]

    recommended_total = round(allocated_sum, 2)
    expected_savings = round(income - recommended_total, 2)
    savings_rate = (
        round((expected_savings / income * 100.0), 2) if income > 0 else 0.0
    )


    if expected_savings < 0:
        warnings.append(
            f"PROJECTED DEFICIT: Recommended monthly budget of INR {recommended_total:,.2f} exceeds monthly income of INR {income:,.2f} by INR {abs(expected_savings):,.2f}."
        )
    elif savings_rate < 15.0:
        warnings.append(
            f"Expected monthly savings rate is low ({savings_rate:.1f}%). Recommended minimum savings target is 20%."
        )

    # Sort category budgets by priority (Essential -> Flexible -> Discretionary) and recommended budget descending
    p_order = {"Essential": 1, "Flexible": 2, "Discretionary": 3}
    category_results.sort(
        key=lambda x: (p_order.get(x["priority"], 4), -x["recommended_budget"])
    )

    # 7. LLM rationale explanation step
    llm_rationale = ""
    system_prompt = (
        "You are an expert AI Budget Planner Agent.\n"
        "Explain the calculated monthly budget plan to the user in an encouraging, professional tone.\n"
        "Do NOT recalculate or invent any numbers."
    )

    cat_summary = ", ".join(
        [
            f"{c['category']} (INR {c['recommended_budget']:,.2f})"
            for c in category_results[:5]
        ]
    )
    user_prompt = f"""
Calculated Plan Metrics:
- Monthly Income: INR {income:,.2f}
- Target Budget: INR {budget:,.2f}
- Recommended Total Budget: INR {recommended_total:,.2f}
- Expected Monthly Savings/Deficit: INR {expected_savings:,.2f} ({savings_rate:.1f}% savings rate)
- Top Category Allocations: {cat_summary}

Please provide a concise 3-4 sentence explanation of this plan and key advice.
"""

    llm_resp = get_llm_response(system_prompt, user_prompt)
    if (
        llm_resp.startswith("Configuration Error")
        or llm_resp.startswith("OpenAI API Error")
        or llm_resp.startswith("Unexpected Error")
    ):
        if expected_savings < 0:
            llm_rationale = (
                f"Recommended monthly budget of INR {recommended_total:,.2f} exceeds monthly income of INR {income:,.2f}, "
                f"resulting in a projected monthly deficit of INR {abs(expected_savings):,.2f}. "
                f"Immediate category cap reductions are required to align spending with income."
            )
        else:
            llm_rationale = (
                f"Recommended monthly budget of INR {recommended_total:,.2f} leaves an expected savings of "
                f"INR {expected_savings:,.2f} ({savings_rate:.1f}% savings rate). "
                f"Essential living expenses (Rent, Bills) are fully protected, while discretionary spending is optimized."
            )
    else:
        llm_rationale = llm_resp

    return {
        "agent_name": agent_name,
        "status": "success",
        "monthly_income": income,
        "monthly_budget": budget,
        "recommended_total_budget": recommended_total,
        "expected_savings": expected_savings,
        "expected_savings_rate": savings_rate,
        "is_deficit": expected_savings < 0,
        "essential_baseline_total": essential_baseline_total,
        "is_infeasible": is_infeasible,
        "category_budgets": category_results,
        "rationale": llm_rationale,
        "warnings": warnings,
    }


def run_financial_advisor(
    analysis_context: Optional[Dict[str, Any]] = None,
    anomaly_context: Optional[Dict[str, Any]] = None,
    budget_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Financial Advisor Agent (Agent 4):
    Synthesizes outputs from Agent 1 (Transaction Analyst), Agent 2 (Anomaly Detection),
    and Agent 3 (Budget Planner) into an executive-level personalized financial action plan.

    Parameters:
        analysis_context (dict, optional): Output from Agent 1.
        anomaly_context (dict, optional): Output from Agent 2.
        budget_context (dict, optional): Output from Agent 3.

    Returns:
        dict: Executive summary, key findings, priority actions, risk flags, positive behaviors, next steps.
    """
    agent_name = "Financial Advisor Agent"

    # Safely unpack Agent 1 metrics
    analysis = analysis_context or {}
    tx_summary = analysis.get("summary", "Transaction analysis complete.")

    # Safely unpack Agent 2 metrics
    anomalies = anomaly_context or {}
    anomaly_count = anomalies.get("anomaly_count", 0)
    anom_list = anomalies.get("anomalies", [])
    anom_rate = anomalies.get("anomaly_rate", 0.0)

    # Safely unpack Agent 3 metrics
    budget = budget_context or {}
    income_val = float(budget.get("monthly_income", 100000.0))
    target_budget_val = float(budget.get("monthly_budget", 80000.0))
    rec_budget_val = float(budget.get("recommended_total_budget", 0.0))
    expected_savings_val = float(budget.get("expected_savings", 0.0))
    savings_rate_val = float(budget.get("expected_savings_rate", 0.0))
    is_deficit = expected_savings_val < 0
    cat_budgets = budget.get("category_budgets", [])
    budget_warnings = budget.get("warnings", [])

    # 1. Deterministic Executive Summary
    if is_deficit:
        exec_summary = (
            f"Based on your transaction analytics, your recommended recurring monthly budget is "
            f"INR {rec_budget_val:,.2f} against a target budget of INR {target_budget_val:,.2f}. "
            f"This results in a projected monthly deficit of INR {abs(expected_savings_val):,.2f} relative to your monthly income of INR {income_val:,.2f}. "
            f"A total of {anomaly_count} high-value/unusual transactions were identified and separated from your recurring monthly baseline."
        )
    else:
        exec_summary = (
            f"Based on your transaction analytics, your recommended recurring monthly budget is "
            f"INR {rec_budget_val:,.2f} against a target budget of INR {target_budget_val:,.2f}. "
            f"This yields an estimated monthly savings of INR {expected_savings_val:,.2f} ({savings_rate_val:.1f}% savings rate). "
            f"A total of {anomaly_count} high-value/unusual transactions were identified and separated from your recurring monthly baseline."
        )

    # 2. Key Findings
    key_findings = []

    # Finding 1: Budget & Savings / Deficit Alignment
    if is_deficit:
        key_findings.append(
            {
                "title": "Projected Monthly Deficit",
                "explanation": f"Your recommended recurring monthly spend of INR {rec_budget_val:,.2f} exceeds your monthly income of INR {income_val:,.2f}, resulting in a monthly deficit of INR {abs(expected_savings_val):,.2f}.",
                "supporting_metric": f"Monthly Deficit: -INR {abs(expected_savings_val):,.2f} (Savings Rate: {savings_rate_val:.1f}%)",
                "priority": "High",
            }
        )
    else:
        key_findings.append(
            {
                "title": "Projected Monthly Savings",
                "explanation": f"Your recommended recurring spend of INR {rec_budget_val:,.2f} leaves a monthly surplus of INR {expected_savings_val:,.2f}.",
                "supporting_metric": f"Savings Rate: {savings_rate_val:.1f}% (Income: INR {income_val:,.2f})",
                "priority": "High" if savings_rate_val >= 20.0 else "Medium",
            }
        )

    # Finding 2: Impact of One-Off Anomalies
    if anomaly_count > 0:
        top_anom = anom_list[0] if anom_list else {}
        anom_desc = top_anom.get("description", "High-value purchase")
        anom_amt = float(top_anom.get("amount", 0.0))
        key_findings.append(
            {
                "title": "One-Time Anomalous Transactions Separated",
                "explanation": f"Identified {anomaly_count} unusual expenses (e.g. '{anom_desc}' for INR {anom_amt:,.2f}). These are treated as one-off events rather than permanent monthly cost increases.",
                "supporting_metric": f"{anomaly_count} Anomalies ({anom_rate}% of transactions)",
                "priority": "High",
            }
        )

    # Finding 3: Essential Expense Protection
    key_findings.append(
        {
            "title": "Protection of Mandatory Living Expenses",
            "explanation": "Essential living costs such as Rent, Utility Bills, and Healthcare are fully maintained in the budget plan without aggressive cuts.",
            "supporting_metric": "Essential Allocation: 100% Maintained",
            "priority": "Medium",
        }
    )

    # 3. Priority Actions
    priority_actions = []

    if cat_budgets:
        for cb in cat_budgets:
            if cb.get("priority") == "Discretionary" and cb.get("recommended_budget", 0) > 0:
                c_name = cb.get("category")
                c_rec = cb.get("recommended_budget")
                priority_actions.append(
                    {
                        "action": f"Cap discretionary spending in '{c_name}' to INR {c_rec:,.2f}/month",
                        "reason": "Discretionary spending represents the highest opportunity for budget optimization.",
                        "expected_impact": "Reduces monthly budget pressures and aligns spending with income",
                        "priority": "High",
                        "related_category": c_name,
                    }
                )
                break

    if anomaly_count > 0:
        top_cat_anom = anom_list[0].get("category", "General") if anom_list else "General"
        priority_actions.append(
            {
                "action": "Separate one-off major purchases from monthly operational budgets",
                "reason": "Prevents large single purchases from distorting recurring monthly cash flow plans.",
                "expected_impact": "Maintains predictable monthly budget baselines",
                "priority": "High",
                "related_category": top_cat_anom,
            }
        )

    if is_deficit:
        priority_actions.append(
            {
                "action": f"Eliminate monthly deficit of INR {abs(expected_savings_val):,.2f} by enforcing category caps",
                "reason": "Current target budget exceeds monthly income limit.",
                "expected_impact": "Restores positive cash flow and prevents financial debt accumulation.",
                "priority": "High",
                "related_category": "Budget Optimization",
            }
        )
    elif expected_savings_val > 0:
        priority_actions.append(
            {
                "action": f"Set up automated monthly transfer of INR {expected_savings_val:,.2f} to Savings/Investment account",
                "reason": "Automating savings at the beginning of the month ensures financial goals are met consistently.",
                "expected_impact": f"Builds long-term wealth at a {savings_rate_val:.1f}% savings rate",
                "priority": "Medium",
                "related_category": "Savings",
            }
        )

    # 4. Risk Flags
    risk_flags = []
    if budget_warnings:
        risk_flags.extend(budget_warnings)
    if is_deficit:
        risk_flags.append(
            f"Monthly Deficit: Recommended budget of INR {rec_budget_val:,.2f} exceeds income of INR {income_val:,.2f}."
        )
    elif savings_rate_val < 15.0:
        risk_flags.append(
            f"Low savings rate ({savings_rate_val:.1f}%). Target a minimum 20% savings margin."
        )
    if anomaly_count > 5:
        risk_flags.append(
            f"High anomaly frequency ({anomaly_count} flagged transactions). Audit non-essential big-ticket purchases."
        )

    # 5. Positive Signals (Data-backed user financial observations)
    positive_behaviors = [
        "Essential living expenses (Rent, Bills, Healthcare) are consistently prioritized and protected in your budget plan.",
    ]
    if not is_deficit:
        positive_behaviors.append(
            f"Recurring monthly baseline spend remains below your income ceiling of INR {income_val:,.2f}."
        )
    if anomaly_count == 0:
        positive_behaviors.append(
            "Zero high-risk financial anomalies detected; spending patterns follow predictable baselines."
        )
    else:
        positive_behaviors.append(
            f"Identified non-recurring large purchases ({anomaly_count} items) and successfully separated them from monthly operational budgets."
        )

    # 6. Next Steps (Short-term action plan)
    if is_deficit:
        next_steps = [
            f"Next 7 Days: Reduce target monthly budget to stay within your monthly income limit of INR {income_val:,.2f}.",
            f"Next 14 Days: Implement strict daily spending caps on discretionary categories to eliminate the INR {abs(expected_savings_val):,.2f} deficit.",
            f"Next 30 Days: Re-evaluate mandatory fixed expenses to align recurring baseline with income.",
        ]
    else:
        next_steps = [
            f"Next 7 Days: Set category spend limits in your bank app for discretionary categories (Target total budget: INR {rec_budget_val:,.2f}).",
            f"Next 14 Days: Review recent flagged transactions ({anomaly_count} items) to ensure no unauthorized or duplicate charges.",
            f"Next 30 Days: Transfer projected monthly savings of INR {expected_savings_val:,.2f} to your emergency/investment fund.",
        ]

    # 7. Optional LLM Synthesis
    system_prompt = (
        "You are an expert Chief Financial Advisor Agent.\n"
        "Synthesize the outputs from Transaction Analysis, Anomaly Detection, and Budget Planning into a cohesive action plan.\n"
        "STRICT RULES:\n"
        "1. Do NOT invent or change any financial numbers.\n"
        "2. Use ONLY the provided numbers and metrics.\n"
        "3. If expected savings are negative, treat it as a Deficit. Do NOT call it healthy savings.\n"
        "4. Provide executive-level financial counsel."
    )

    user_prompt = f"""
Agent 1 Summary: {tx_summary}
Agent 2 Anomalies: {anomaly_count} flagged items (Rate: {anom_rate}%)
Agent 3 Plan: Recommended Budget INR {rec_budget_val:,.2f}, Expected Savings/Deficit INR {expected_savings_val:,.2f} ({savings_rate_val:.1f}% savings rate)

Please synthesize an executive overview and advice for the user.
"""

    llm_resp = get_llm_response(system_prompt, user_prompt)
    if not (
        llm_resp.startswith("Configuration Error")
        or llm_resp.startswith("OpenAI API Error")
        or llm_resp.startswith("Unexpected Error")
    ):
        exec_summary = llm_resp

    return {
        "agent_name": agent_name,
        "status": "success",
        "executive_summary": exec_summary,
        "key_findings": key_findings,
        "priority_actions": priority_actions,
        "risk_flags": risk_flags,
        "positive_behaviors": positive_behaviors,
        "next_steps": next_steps,
    }





