"""
data.py — pandas layer
Učitava CSV i priprema sve transformacije koje app.py i charts.py koriste.
Sve što je "analitička logika" živi ovde, odvojeno od prikaza.
"""

import pandas as pd


def load_data(path: str = "ravenstack_churn_events.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["churn_date"])
    # Normalizacija
    df["refund_amount_usd"] = pd.to_numeric(df["refund_amount_usd"], errors="coerce").fillna(0)
    df["preceding_upgrade_flag"]   = df["preceding_upgrade_flag"].astype(str).str.strip().str.lower() == "true"
    df["preceding_downgrade_flag"] = df["preceding_downgrade_flag"].astype(str).str.strip().str.lower() == "true"
    df["is_reactivation"]          = df["is_reactivation"].astype(str).str.strip().str.lower() == "true"
    df["feedback_text"] = df["feedback_text"].fillna("(no feedback)")
    df["year_month"] = df["churn_date"].dt.to_period("M")
    df["quarter"]    = df["churn_date"].dt.to_period("Q")
    return df


# ── KPI strip ──────────────────────────────────────────────────────────────
def get_kpis(df: pd.DataFrame) -> dict:
    refunds_with_amount = df[df["refund_amount_usd"] > 0]
    top_reason = df["reason_code"].value_counts().idxmax()
    top_reason_count = df["reason_code"].value_counts().max()
    top_reason_pct = top_reason_count / len(df) * 100

    return {
        "total_churns":        len(df),
        "dec_2024_churns":     len(df[(df["churn_date"].dt.year == 2024) & (df["churn_date"].dt.month == 12)]),
        "total_refunds_usd":   df["refund_amount_usd"].sum(),
        "refund_event_count":  len(refunds_with_amount),
        "avg_refund_usd":      refunds_with_amount["refund_amount_usd"].mean(),
        "reactivations":       df["is_reactivation"].sum(),
        "reactivation_pct":    df["is_reactivation"].mean() * 100,
        "top_reason":          top_reason.capitalize(),
        "top_reason_count":    int(top_reason_count),
        "top_reason_pct":      top_reason_pct,
        "pre_upgrade_churns":  df["preceding_upgrade_flag"].sum(),
        "pre_upgrade_pct":     df["preceding_upgrade_flag"].mean() * 100,
    }


# ── Monthly volume ─────────────────────────────────────────────────────────
def get_monthly_volume(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby("year_month")
        .size()
        .reset_index(name="churns")
    )
    monthly["year_month_dt"] = monthly["year_month"].dt.to_timestamp()
    return monthly.sort_values("year_month_dt")


# ── Reason breakdown ───────────────────────────────────────────────────────
def get_reason_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    reasons = (
        df["reason_code"]
        .value_counts()
        .reset_index()
    )
    reasons.columns = ["reason", "count"]
    reasons["pct"] = (reasons["count"] / len(df) * 100).round(1)
    reasons["reason"] = reasons["reason"].str.capitalize()
    return reasons


# ── Feedback text ──────────────────────────────────────────────────────────
def get_feedback_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    feedback = (
        df["feedback_text"]
        .value_counts()
        .reset_index()
    )
    feedback.columns = ["feedback", "count"]
    feedback["pct"] = (feedback["count"] / len(df) * 100).round(1)
    # Capitalize nicely
    feedback["feedback"] = feedback["feedback"].str.replace(
        r"(\w+)", lambda m: m.group(0).capitalize(), regex=True
    )
    return feedback


# ── Pre-churn signals ──────────────────────────────────────────────────────
def get_signals(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    rows = [
        {"signal": "Preceded by Upgrade",   "count": int(df["preceding_upgrade_flag"].sum()),
         "pct": df["preceding_upgrade_flag"].mean() * 100},
        {"signal": "Preceded by Downgrade",  "count": int(df["preceding_downgrade_flag"].sum()),
         "pct": df["preceding_downgrade_flag"].mean() * 100},
        {"signal": "Reactivations",          "count": int(df["is_reactivation"].sum()),
         "pct": df["is_reactivation"].mean() * 100},
        {"signal": "No Prior Signal",        "count": total - int(df["preceding_upgrade_flag"].sum())
                                                             - int(df["preceding_downgrade_flag"].sum())
                                                             - int(df["is_reactivation"].sum()),
         "pct": None},
    ]
    result = pd.DataFrame(rows)
    result.loc[result["pct"].isna(), "pct"] = (
        result.loc[result["pct"].isna(), "count"] / total * 100
    )
    result["pct"] = result["pct"].round(1)
    return result


# ── Refund overview ────────────────────────────────────────────────────────
def get_refund_by_reason(df: pd.DataFrame) -> pd.DataFrame:
    total_by_reason = df.groupby("reason_code").size().rename("total")
    refund_by_reason = df[df["refund_amount_usd"] > 0].groupby("reason_code").size().rename("with_refund")
    combined = pd.concat([total_by_reason, refund_by_reason], axis=1).fillna(0).reset_index()
    combined["refund_rate_pct"] = (combined["with_refund"] / combined["total"] * 100).round(1)
    combined["reason_code"] = combined["reason_code"].str.capitalize()
    return combined.sort_values("refund_rate_pct", ascending=False)


# ── Heatmap: reason × feedback ────────────────────────────────────────────
def get_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    heat = (
        df.groupby(["reason_code", "feedback_text"])
        .size()
        .reset_index(name="count")
    )
    pivot = heat.pivot(index="reason_code", columns="feedback_text", values="count").fillna(0)
    pivot.index = pivot.index.str.capitalize()
    pivot.columns = [c.title() if isinstance(c, str) else c for c in pivot.columns]
    return pivot


# ── Quarterly trend ───────────────────────────────────────────────────────
def get_quarterly_trend(df: pd.DataFrame) -> pd.DataFrame:
    qtly = (
        df.groupby("quarter")
        .size()
        .reset_index(name="events")
        .sort_values("quarter")
    )
    qtly["quarter_str"] = qtly["quarter"].astype(str)
    qtly["pct_change"] = qtly["events"].pct_change() * 100
    return qtly
