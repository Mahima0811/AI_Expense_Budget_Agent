"""
Analytics Engine for AI Expense & Budget Management System.
Deterministic financial metrics calculations using pandas and numpy.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


def load_transactions(csv_path: str = "sample_data.csv") -> pd.DataFrame:
    """
    Loads expense transactions from a CSV file, validates required columns,
    parses dates, and cleans invalid rows.

    Parameters:
        csv_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Cleaned DataFrame containing expense records.
    """
    required_columns = {"date", "category", "description", "amount", "payment_method"}

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Transaction file not found at path: {csv_path}")
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {str(e)}")

    missing_cols = required_columns - set(df.columns)
    if missing_cols:
        raise ValueError(f"CSV file is missing required columns: {missing_cols}")

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Coerce numeric amount column
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Drop rows where critical fields are missing or amount is non-positive
    df = df.dropna(subset=["date", "amount", "category"]).copy()
    df = df[df["amount"] > 0].copy()

    # Ensure clean string values
    df["category"] = df["category"].astype(str).str.strip()
    df["description"] = df["description"].astype(str).str.strip()
    df["payment_method"] = df["payment_method"].astype(str).str.strip()

    # Sort chronologically
    df = df.sort_values(by="date").reset_index(drop=True)

    return df


def calculate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates overall summary metrics from transaction data.

    Parameters:
        df (pd.DataFrame): Expense transactions DataFrame.

    Returns:
        dict: Summary statistics including totals, averages, and breakdowns.
    """
    if df.empty:
        return {
            "total_expenses": 0.0,
            "transaction_count": 0,
            "average_transaction": 0.0,
            "highest_transaction": None,
            "spending_by_category": {},
            "category_percentages": {},
            "spending_by_payment_method": {},
            "daily_spending": {},
            "monthly_spending": {},
        }

    total_expenses = float(df["amount"].sum())
    transaction_count = len(df)
    average_transaction = float(df["amount"].mean())

    # Highest transaction details
    max_idx = df["amount"].idxmax()
    highest_row = df.loc[max_idx]
    highest_transaction = {
        "date": highest_row["date"].strftime("%Y-%m-%d"),
        "category": highest_row["category"],
        "description": highest_row["description"],
        "amount": float(highest_row["amount"]),
        "payment_method": highest_row["payment_method"],
    }

    # Spending by category
    cat_series = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    spending_by_category = {k: float(v) for k, v in cat_series.items()}

    # Category percentages
    category_percentages = {
        k: round((v / total_expenses) * 100, 2) if total_expenses > 0 else 0.0
        for k, v in spending_by_category.items()
    }

    # Spending by payment method
    pay_series = df.groupby("payment_method")["amount"].sum().sort_values(ascending=False)
    spending_by_payment_method = {k: float(v) for k, v in pay_series.items()}

    # Daily spending (formatted date string)
    df_temp = df.copy()
    df_temp["date_str"] = df_temp["date"].dt.strftime("%Y-%m-%d")
    daily_series = df_temp.groupby("date_str")["amount"].sum()
    daily_spending = {k: float(v) for k, v in daily_series.items()}

    # Monthly spending (formatted month string YYYY-MM)
    df_temp["month_str"] = df_temp["date"].dt.strftime("%Y-%m")
    monthly_series = df_temp.groupby("month_str")["amount"].sum()
    monthly_spending = {k: float(v) for k, v in monthly_series.items()}

    # Calculate date range and normalized monthly span
    min_date = df["date"].min()
    max_date = df["date"].max()
    days_span = (max_date - min_date).days + 1 if pd.notnull(min_date) and pd.notnull(max_date) else 30
    months_spanned = max(round(days_span / 30.4375, 2), 1.0)
    monthly_average_expenses = round(total_expenses / months_spanned, 2)

    return {
        "total_expenses": total_expenses,
        "transaction_count": transaction_count,
        "average_transaction": average_transaction,
        "months_spanned": months_spanned,
        "monthly_average_expenses": monthly_average_expenses,
        "highest_transaction": highest_transaction,
        "spending_by_category": spending_by_category,
        "category_percentages": category_percentages,
        "spending_by_payment_method": spending_by_payment_method,
        "daily_spending": daily_spending,
        "monthly_spending": monthly_spending,
    }



def detect_anomalies(df: pd.DataFrame, z_threshold: float = 2.0) -> pd.DataFrame:
    """
    Detects financial anomalies using statistical methods (IQR & Z-score).

    Parameters:
        df (pd.DataFrame): Expense transactions DataFrame.
        z_threshold (float): Z-score cutoff for anomaly detection (default 2.0).

    Returns:
        pd.DataFrame: DataFrame containing detected anomalous transactions with score and reason.
    """
    if df.empty or len(df) < 3:
        return pd.DataFrame()

    amounts = df["amount"]
    q1 = amounts.quantile(0.25)
    q3 = amounts.quantile(0.75)
    iqr = q3 - q1
    iqr_upper_bound = q3 + 1.5 * iqr

    mean_amt = amounts.mean()
    std_amt = amounts.std(ddof=1) if len(df) > 1 else 0.0

    anomalies = []
    for idx, row in df.iterrows():
        amt = row["amount"]
        z_score = (amt - mean_amt) / std_amt if std_amt > 0 else 0.0

        is_iqr_anomaly = amt > iqr_upper_bound
        is_z_anomaly = z_score >= z_threshold

        if is_iqr_anomaly or is_z_anomaly:
            reasons = []
            if is_z_anomaly:
                reasons.append(f"High Z-score ({z_score:.2f} >= {z_threshold})")
            if is_iqr_anomaly:
                reasons.append(f"Exceeds IQR upper bound (INR {amt:,.2f} > INR {iqr_upper_bound:,.2f})")

            anomaly_row = row.to_dict()
            anomaly_row["date"] = row["date"].strftime("%Y-%m-%d")
            anomaly_row["anomaly_score"] = round(float(z_score), 2)
            anomaly_row["anomaly_reason"] = " | ".join(reasons)
            anomalies.append(anomaly_row)

    if not anomalies:
        return pd.DataFrame()

    anom_df = pd.DataFrame(anomalies)
    return anom_df.sort_values(by="anomaly_score", ascending=False).reset_index(drop=True)


def calculate_budget_metrics(
    df: pd.DataFrame, monthly_income: float, monthly_budget: float
) -> Dict[str, Any]:
    """
    Calculates budget utilization, remaining allowance, and savings/deficit figures.

    Parameters:
        df (pd.DataFrame): Expense transactions DataFrame.
        monthly_income (float): User's specified monthly income.
        monthly_budget (float): User's target monthly budget allocation.

    Returns:
        dict: Key budget and savings metric indicators.
    """
    summary = calculate_summary(df)
    total_spending = summary["total_expenses"]

    remaining_budget = monthly_budget - total_spending
    budget_utilization_pct = (
        (total_spending / monthly_budget) * 100.0 if monthly_budget > 0 else 0.0
    )
    savings_or_deficit = monthly_income - total_spending

    cat_breakdown = get_category_breakdown(df)
    top_categories = (
        cat_breakdown.head(3).to_dict(orient="records") if not cat_breakdown.empty else []
    )

    return {
        "monthly_income": float(monthly_income),
        "monthly_budget": float(monthly_budget),
        "total_spending": float(total_spending),
        "remaining_budget": float(remaining_budget),
        "budget_utilization_pct": round(float(budget_utilization_pct), 2),
        "savings_or_deficit": float(savings_or_deficit),
        "is_over_budget": total_spending > monthly_budget,
        "is_deficit": total_spending > monthly_income,
        "top_spending_categories": top_categories,
    }


def get_category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns category-level aggregated spending data formatted for charting.

    Parameters:
        df (pd.DataFrame): Expense transactions DataFrame.

    Returns:
        pd.DataFrame: DataFrame with columns ['category', 'amount', 'percentage'].
    """
    if df.empty:
        return pd.DataFrame(columns=["category", "amount", "percentage"])

    grouped = df.groupby("category")["amount"].sum().reset_index()
    grouped = grouped.sort_values(by="amount", ascending=False).reset_index(drop=True)
    total = grouped["amount"].sum()

    grouped["percentage"] = (
        (grouped["amount"] / total * 100.0).round(2) if total > 0 else 0.0
    )
    return grouped


def get_trend_data(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """
    Returns time-series aggregate spending data suitable for Plotly line charts.

    Parameters:
        df (pd.DataFrame): Expense transactions DataFrame.
        freq (str): Aggregation frequency ('D' for Daily, 'W' for Weekly, 'M' for Monthly).

    Returns:
        pd.DataFrame: Resampled time-series DataFrame with columns ['date', 'amount', 'cumulative_amount'].
    """
    if df.empty:
        return pd.DataFrame(columns=["date", "amount", "cumulative_amount"])

    df_copy = df.copy()
    df_copy = df_copy.set_index("date")

    # Resample by date frequency
    resampled = df_copy["amount"].resample(freq).sum().reset_index()
    resampled["date_str"] = resampled["date"].dt.strftime("%Y-%m-%d")
    resampled["cumulative_amount"] = resampled["amount"].cumsum()

    return resampled
