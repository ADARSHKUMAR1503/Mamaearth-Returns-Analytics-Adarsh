from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATH CONFIGURATION
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "visualizations"

ORDERS_FILE = DATA_DIR / "orders.csv"
CUSTOMERS_FILE = DATA_DIR / "customers.csv"
PRODUCTS_FILE = DATA_DIR / "products.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD RAW DATA
# ============================================================

orders = pd.read_csv(ORDERS_FILE)
customers = pd.read_csv(CUSTOMERS_FILE)
products = pd.read_csv(PRODUCTS_FILE)


# ============================================================
# REPRODUCE PART 2 CLEANING
# ============================================================

orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

natural_key = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

orders = orders.loc[
    ~orders.duplicated(
        subset=natural_key,
        keep="first"
    )
].copy()

orders["discount_pct"] = (
    orders["discount_pct"].fillna(0)
)

orders["rating"] = (
    orders["rating"]
    .fillna(orders["rating"].median())
)


# ============================================================
# MERGE DATA
# ============================================================

merged = (
    orders
    .merge(
        products,
        on="product_id",
        how="left",
        validate="many_to_one"
    )
    .merge(
        customers,
        on="customer_id",
        how="left",
        validate="many_to_one"
    )
)

merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)


# ============================================================
# CHART 1 — RETURN RATE BY PAYMENT
# ============================================================

return_rate = (
    merged
    .groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    return_rate.index,
    return_rate.values,
    color=["#d62728", "#1f77b4", "#2ca02c"]
)

for bar, value in zip(bars, return_rate.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.8,
        f"{value:.1f}%",
        ha="center",
        va="bottom",
        fontweight="bold"
    )

ax.set_title(
    "COD Returns at 44.4% — 3x Card",
    fontsize=14,
    fontweight="bold"
)

ax.set_xlabel("Payment Method")
ax.set_ylabel("Return Rate (%)")

ax.set_ylim(
    0,
    max(return_rate.values) + 10
)

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.tight_layout()

return_chart = OUTPUT_DIR / "return_rate_by_payment.png"

plt.savefig(
    return_chart,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {return_chart}")


# ============================================================
# OUTLIER DETECTION FOR MONTHLY REVENUE
# ============================================================

Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)

IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

merged["is_outlier"] = (
    (merged["quantity"] < lower_bound)
    | (merged["quantity"] > upper_bound)
)

merged["order_date"] = pd.to_datetime(
    merged["order_date"]
)

merged["year_month"] = (
    merged["order_date"]
    .dt.to_period("M")
    .astype(str)
)


# ============================================================
# OUTLIER-CORRECTED MONTHLY REVENUE
# ============================================================

monthly_revenue = (
    merged.loc[~merged["is_outlier"]]
    .groupby("year_month")["order_value"]
    .sum()
    .sort_index()
)

peak_month = monthly_revenue.idxmax()
peak_revenue = monthly_revenue.max()


# ============================================================
# CHART 2 — MONTHLY REVENUE TREND
# ============================================================

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(
    monthly_revenue.index,
    monthly_revenue.values,
    marker="o",
    linewidth=2.5,
    color="#2ca02c"
)

# Highlight true peak month.
peak_position = list(monthly_revenue.index).index(
    peak_month
)

ax.scatter(
    peak_month,
    peak_revenue,
    color="#d62728",
    s=80,
    zorder=5
)

ax.annotate(
    f"Peak: {peak_month}\n₹{peak_revenue:,.2f}",
    xy=(peak_month, peak_revenue),
    xytext=(10, 15),
    textcoords="offset points",
    fontsize=10,
    fontweight="bold",
    arrowprops=dict(
        arrowstyle="->",
        color="black"
    )
)

ax.set_title(
    f"Outlier-Corrected Monthly Revenue — Peak: {peak_month}",
    fontsize=14,
    fontweight="bold"
)

ax.set_xlabel("Month")
ax.set_ylabel("Revenue (INR)")

ax.grid(
    linestyle="--",
    alpha=0.3
)

plt.xticks(rotation=45)

plt.tight_layout()

monthly_chart = OUTPUT_DIR / "monthly_revenue_trend.png"

plt.savefig(
    monthly_chart,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print(f"Saved: {monthly_chart}")

print("\nVisualization pipeline completed successfully.")
print(f"True peak month: {peak_month}")
print(f"True peak revenue: ₹{peak_revenue:,.2f}")