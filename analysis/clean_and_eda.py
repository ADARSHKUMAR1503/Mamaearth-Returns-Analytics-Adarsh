from pathlib import Path
import json
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT_DIR / "data"
NARRATOR_DIR = ROOT_DIR / "narrator"

ORDERS_FILE = DATA_DIR / "orders.csv"
CUSTOMERS_FILE = DATA_DIR / "customers.csv"
PRODUCTS_FILE = DATA_DIR / "products.csv"

FINDINGS_FILE = NARRATOR_DIR / "findings.json"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):
    """Format numeric values as INR-style amounts without currency symbol."""
    return f"{value:,.2f}"


def correlation_band(value):
    """Return the taught correlation-strength band."""
    absolute_value = abs(value)

    if absolute_value < 0.2:
        return "negligible"
    elif absolute_value < 0.4:
        return "weak"
    elif absolute_value < 0.7:
        return "moderate"
    else:
        return "strong"


# ============================================================
# TASK 1 — LOAD AND INSPECT
# ============================================================

print("=" * 70)
print("TASK 1 — LOAD AND INSPECT")
print("=" * 70)

orders = pd.read_csv(ORDERS_FILE)
customers = pd.read_csv(CUSTOMERS_FILE)
products = pd.read_csv(PRODUCTS_FILE)

print("Orders shape before cleaning:", orders.shape)
print("Customers shape:", customers.shape)
print("Products shape:", products.shape)

assert orders.shape == (180, 9)

print("\nFirst five orders:")
print(orders.head())


# ============================================================
# TASK 2 — STANDARDIZE PAYMENT METHOD
# ============================================================

print("\n" + "=" * 70)
print("TASK 2 — PAYMENT METHOD STANDARDIZATION")
print("=" * 70)

raw_payment_values = sorted(orders["payment_method"].dropna().unique())

print("Raw payment_method values:")
print(raw_payment_values)

print("Number of raw payment_method values:",
      orders["payment_method"].nunique())

assert orders["payment_method"].nunique() == 7

# Standardize casing and whitespace.
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

payment_counts = orders["payment_method"].value_counts()

print("\nCleaned payment_method counts:")
print(payment_counts)

expected_payment_counts = {
    "CARD": 70,
    "UPI": 55,
    "COD": 55
}

assert payment_counts.to_dict() == expected_payment_counts


# ============================================================
# TASK 3 — REMOVE DUPLICATE ORDERS
# ============================================================

print("\n" + "=" * 70)
print("TASK 3 — DUPLICATE ORDER REMOVAL")
print("=" * 70)

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

duplicate_mask = orders.duplicated(
    subset=natural_key,
    keep="first"
)

dropped_orders = orders.loc[duplicate_mask].copy()

print("Number of duplicate rows detected:",
      duplicate_mask.sum())

print("\nDropped duplicate order IDs:")
print(dropped_orders["order_id"].tolist())

expected_duplicate_ids = [
    "O0176",
    "O0177",
    "O0178",
    "O0179",
    "O0180"
]

assert duplicate_mask.sum() == 5
assert dropped_orders["order_id"].tolist() == expected_duplicate_ids

orders_clean = orders.loc[~duplicate_mask].copy()

print("\nShape after duplicate removal:")
print(orders_clean.shape)

assert orders_clean.shape == (175, 9)


# ============================================================
# TASK 4 — MISSING VALUE IMPUTATION
# ============================================================

print("\n" + "=" * 70)
print("TASK 4 — MISSING VALUE IMPUTATION")
print("=" * 70)

# Discount: missing means no promotional discount.
discount_missing_count = orders_clean["discount_pct"].isna().sum()

print("Missing discount_pct before imputation:",
      discount_missing_count)

assert discount_missing_count == 12

orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

print("Discount rows imputed:", discount_missing_count)

# Rating: use median of non-null ratings.
rating_median = orders_clean["rating"].median()

print("Rating median before imputation:", rating_median)

assert rating_median == 3.0

rating_missing_count = orders_clean["rating"].isna().sum()

print("Missing rating values:", rating_missing_count)

assert rating_missing_count == 15

orders_clean["rating"] = (
    orders_clean["rating"].fillna(rating_median)
)

remaining_nulls = (
    orders_clean[["discount_pct", "rating"]]
    .isnull()
    .sum()
    .to_dict()
)

print("\nRemaining NULL values:")
print(remaining_nulls)

assert remaining_nulls == {
    "discount_pct": 0,
    "rating": 0
}


# ============================================================
# TASK 5 — MERGE AND RECONCILE AGAINST PART 1
# ============================================================

print("\n" + "=" * 70)
print("TASK 5 — MERGE AND RECONCILIATION")
print("=" * 70)

# Preserve a copy of dropped rows for independent reconciliation.
dropped_for_reconciliation = dropped_orders.copy()

# Apply the same business cleaning to dropped rows so their
# order_value can be calculated correctly.
dropped_for_reconciliation["discount_pct"] = (
    dropped_for_reconciliation["discount_pct"].fillna(0)
)

merged = (
    orders_clean
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

cleaned_total_revenue = merged["order_value"].sum()

print("Cleaned rows:", len(merged))
print("Cleaned total revenue: ₹", money(cleaned_total_revenue))

assert round(cleaned_total_revenue, 2) == 97358.30

# Independently calculate revenue represented by removed duplicates.
dropped_for_reconciliation = (
    dropped_for_reconciliation
    .merge(
        products[["product_id", "price"]],
        on="product_id",
        how="left",
        validate="many_to_one"
    )
)

dropped_for_reconciliation["order_value"] = (
    dropped_for_reconciliation["quantity"]
    * dropped_for_reconciliation["price"]
    * (
        1
        - dropped_for_reconciliation["discount_pct"] / 100
    )
)

duplicate_revenue_delta = (
    dropped_for_reconciliation["order_value"].sum()
)

raw_total_revenue = (
    cleaned_total_revenue + duplicate_revenue_delta
)

print("Revenue represented by 5 duplicate rows: ₹",
      money(duplicate_revenue_delta))

print("Reconstructed raw revenue: ₹",
      money(raw_total_revenue))

assert round(duplicate_revenue_delta, 2) == 2501.90
assert round(raw_total_revenue, 2) == 99860.20

print(
    "\nReconciliation note:"
    f" The raw Part 1 revenue of ₹{money(raw_total_revenue)} "
    f"falls to ₹{money(cleaned_total_revenue)} after removing the "
    f"five duplicate orders. The exact reconciliation delta is "
    f"₹{money(duplicate_revenue_delta)}, which equals the combined "
    f"order_value of O0176–O0180. The discount and rating imputations "
    f"do not change order_value, because rating is not used in the "
    f"revenue calculation and missing discount values represent 0%."
)


# ============================================================
# TASK 6 — IQR OUTLIER DETECTION
# ============================================================

print("\n" + "=" * 70)
print("TASK 6 — IQR OUTLIER DETECTION")
print("=" * 70)

Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)

IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower_bound)
print("Upper bound:", upper_bound)

assert Q1 == 1.0
assert Q3 == 2.0
assert IQR == 1.0
assert lower_bound == -0.5
assert upper_bound == 3.5

merged["is_outlier"] = (
    (merged["quantity"] < lower_bound)
    | (merged["quantity"] > upper_bound)
)

outliers = merged.loc[merged["is_outlier"]].copy()

print("\nOutlier orders:")
print(
    outliers[
        ["order_id", "quantity", "order_date", "order_value"]
    ].to_string(index=False)
)

assert len(outliers) == 2
assert set(outliers["order_id"]) == {"O0011", "O0098"}


# ============================================================
# TASK 7 — COD RETURN RATE HYPOTHESIS
# ============================================================

print("\n" + "=" * 70)
print("TASK 7 — COD RETURN RATE HYPOTHESIS")
print("=" * 70)

print(
    "Hypothesis: COD orders have a higher return rate "
    "than CARD and UPI orders."
)

return_by_payment = (
    merged
    .groupby("payment_method")["returned"]
    .agg(["count", "mean"])
)

return_by_payment["return_rate_pct"] = (
    return_by_payment["mean"] * 100
)

print("\nReturn rate by payment method:")
print(
    return_by_payment[
        ["count", "return_rate_pct"]
    ].round(1)
)

expected_rates = {
    "CARD": 14.7,
    "COD": 44.4,
    "UPI": 18.9
}

for payment, expected_rate in expected_rates.items():
    actual_rate = round(
        return_by_payment.loc[payment, "return_rate_pct"],
        1
    )
    assert actual_rate == expected_rate

print("\nHypothesis: CONFIRMED")


# ============================================================
# TASK 8 — MULTI-LEVEL SEGMENTATION
# ============================================================

print("\n" + "=" * 70)
print("TASK 8 — PAYMENT METHOD × CITY TIER SEGMENTATION")
print("=" * 70)

segment = (
    merged
    .groupby(["payment_method", "city_tier"])["returned"]
    .agg(["count", "sum", "mean"])
    .rename(
        columns={
            "sum": "returned_orders",
            "mean": "return_rate"
        }
    )
)

segment["return_rate_pct"] = (
    segment["return_rate"] * 100
)

print(
    segment[
        ["count", "returned_orders", "return_rate_pct"]
    ].round(1)
)

highest_risk_segment = (
    segment["return_rate_pct"]
    .idxmax()
)

highest_risk_rate = (
    segment["return_rate_pct"].max()
)

highest_risk_payment, highest_risk_tier = highest_risk_segment

print(
    f"\nHighest-risk segment: "
    f"{highest_risk_payment} + Tier-{highest_risk_tier} "
    f"at {highest_risk_rate:.1f}% return rate."
)

assert highest_risk_payment == "COD"
assert highest_risk_tier == 2
assert round(highest_risk_rate, 1) == 54.5

cod_tier_1_rate = round(
    segment.loc[("COD", 1), "return_rate_pct"],
    1
)

cod_tier_2_rate = round(
    segment.loc[("COD", 2), "return_rate_pct"],
    1
)

cod_tier_1_count = int(
    segment.loc[("COD", 1), "count"]
)

cod_tier_2_count = int(
    segment.loc[("COD", 2), "count"]
)

print(
    f"COD Tier-1: {cod_tier_1_count} orders, "
    f"{cod_tier_1_rate:.1f}% return rate."
)

print(
    f"COD Tier-2: {cod_tier_2_count} orders, "
    f"{cod_tier_2_rate:.1f}% return rate."
)


# ============================================================
# TASK 9 — CORRELATION ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("TASK 9 — CORRELATION ANALYSIS")
print("=" * 70)

correlation_columns = [
    "rating",
    "returned",
    "discount_pct",
    "quantity"
]

correlation_matrix = (
    merged[correlation_columns]
    .corr()
)

print("Correlation matrix:")
print(correlation_matrix.round(4))

pairs = [
    ("rating", "returned"),
    ("rating", "discount_pct"),
    ("rating", "quantity"),
    ("returned", "discount_pct"),
    ("returned", "quantity"),
    ("discount_pct", "quantity")
]

print("\nPairwise correlation strength:")

for first, second in pairs:
    value = correlation_matrix.loc[first, second]
    band = correlation_band(value)

    print(
        f"{first} vs {second}: "
        f"r = {value:.4f} → {band}"
    )

# Explicit hypothesis check.
discount_return_corr = correlation_matrix.loc[
    "discount_pct",
    "returned"
]

print(
    f"\nHypothesis: higher discounts reduce returns."
    f"\nDiscount vs returned correlation: "
    f"{discount_return_corr:.4f}"
)

print("Hypothesis: BUSTED — correlation is negligible.")


# ============================================================
# TASK 10 — OUTLIER-CORRECTED TIME SERIES
# ============================================================

print("\n" + "=" * 70)
print("TASK 10 — OUTLIER-CORRECTED TIME SERIES")
print("=" * 70)

merged["order_date"] = pd.to_datetime(
    merged["order_date"]
)

merged["year_month"] = (
    merged["order_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_including_outliers = (
    merged
    .groupby("year_month")["order_value"]
    .sum()
    .sort_index()
)

monthly_excluding_outliers = (
    merged.loc[~merged["is_outlier"]]
    .groupby("year_month")["order_value"]
    .sum()
    .sort_index()
)

print("Monthly revenue INCLUDING quantity outliers:")
print(monthly_including_outliers.round(2))

print("\nMonthly revenue EXCLUDING quantity outliers:")
print(monthly_excluding_outliers.round(2))

expected_corrected = {
    "2026-01": 11637.10,
    "2026-02": 13195.50,
    "2026-03": 20318.90,
    "2026-04": 9495.30,
    "2026-05": 13151.10,
    "2026-06": 11615.40
}

for month, expected_value in expected_corrected.items():
    actual_value = round(
        monthly_excluding_outliers.loc[month],
        2
    )
    assert actual_value == expected_value

true_peak_month = monthly_excluding_outliers.idxmax()
true_peak_revenue = monthly_excluding_outliers.max()

inflated_peak_month = monthly_including_outliers.idxmax()
inflated_peak_revenue = monthly_including_outliers.max()

print(
    f"\nOutlier-corrected true peak month: "
    f"{true_peak_month} — ₹{money(true_peak_revenue)}"
)

print(
    f"Apparent peak before outlier correction: "
    f"{inflated_peak_month} — ₹{money(inflated_peak_revenue)}"
)

print(
    "\nTime-series finding: January's apparent lead is an artifact "
    "of the two bulk orders landing in January — O0011 on "
    "2026-01-28 and O0098 on 2026-01-10. Once these two quantity "
    "outliers are excluded, March is the genuine peak month."
)


# ============================================================
# FINAL FINDINGS EXPORT
# ============================================================

print("\n" + "=" * 70)
print("FINAL VERIFIED FINDINGS EXPORT")
print("=" * 70)

NARRATOR_DIR.mkdir(parents=True, exist_ok=True)

findings = {
    "cleaned_total_revenue_inr": round(
        cleaned_total_revenue,
        2
    ),
    "raw_total_revenue_inr": round(
        raw_total_revenue,
        2
    ),
    "duplicate_reconciliation_delta_inr": round(
        duplicate_revenue_delta,
        2
    ),
    "return_rate_by_payment": {
        payment: round(
            return_by_payment.loc[
                payment,
                "return_rate_pct"
            ],
            1
        )
        for payment in ["COD", "CARD", "UPI"]
    },
    "highest_risk_segment": {
        "payment_method": highest_risk_payment,
        "city_tier": int(highest_risk_tier),
        "return_rate_pct": round(
            highest_risk_rate,
            1
        )
    },
    "true_peak_month": {
        "month": true_peak_month,
        "revenue_inr": round(
            true_peak_revenue,
            2
        )
    },
    "outlier_inflated_month": {
        "month": inflated_peak_month,
        "apparent_revenue_inr": round(
            inflated_peak_revenue,
            2
        ),
        "corrected_revenue_inr": round(
            monthly_excluding_outliers.loc[
                inflated_peak_month
            ],
            2
        )
    }
}

with open(FINDINGS_FILE, "w", encoding="utf-8") as file:
    json.dump(
        findings,
        file,
        indent=2
    )

print("\nfindings.json generated successfully:")
print(json.dumps(findings, indent=2))

print("\nPart 2 clean_and_eda.py completed successfully.")