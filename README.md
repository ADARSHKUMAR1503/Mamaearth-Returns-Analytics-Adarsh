# Mamaearth Returns & Growth Intelligence Pipeline

## Project Overview

This project builds an end-to-end **Returns and Growth Intelligence Pipeline** for Mamaearth using SQL, Python/Pandas, and Generative AI.

The pipeline is divided into three layers:

```text
Raw CSV Data
     ↓
SQL Relational Layer
     ↓
Python Data Cleaning + EDA
     ↓
findings.json
     ↓
GenAI Insight Narrator
     ↓
Business SCR Narrative
```

The objective is to identify revenue patterns, return-risk segments, data-quality issues, and actionable business insights.

---

# Repository Structure

```text
project/
│
├── README.md
├── .gitignore
│
├── data/
│   ├── customers.csv
│   ├── products.csv
│   └── orders.csv
│
├── sql/
│   ├── mamaearth.db
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
│
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
│
├── visualizations/
│   ├── return_rate_by_payment.png
│   └── monthly_revenue_trend.png
│
└── narrator/
    ├── findings.json
    ├── generate_narrative.py
    └── sample_output.txt
```

---

# Part 1 — SQL Relational Layer & Reporting

## Objective

The SQL layer creates a relational database from the three raw datasets and produces business reports for revenue, customers, products, returns, and acquisition analysis.

### Input Data

| Dataset | Rows |
|---|---:|
| Customers | 45 |
| Products | 16 |
| Orders | 180 |

### SQL Files

#### `schema.sql`

Creates the relational tables:

- `customers`
- `products`
- `orders`

Primary keys and foreign-key relationships are defined between the tables.

#### `seed_data.sql`

Loads the CSV datasets into SQLite and converts blank `discount_pct` and `rating` values into SQL `NULL`.

#### `reports.sql`

Contains the required business-reporting queries and expected outputs as comments above the queries.

## SQL Validation Results

| Metric | Result |
|---|---:|
| Customers | 45 |
| Products | 16 |
| Orders | 180 |
| Raw Revenue | ₹99,860.20 |
| Average Order Value | ₹554.78 |
| Customers with zero orders | C045 — Vihaan |
| Gold customers | 28 |
| Silver customers | 17 |

### High Return-Rate Cities

| City | Orders | Returns | Return Rate |
|---|---:|---:|---:|
| Jaipur | 19 | 8 | 42.1% |
| Lucknow | 49 | 15 | 30.6% |
| Bangalore | 33 | 8 | 24.2% |

### Top 5 Customers by Revenue

| Customer | Revenue |
|---|---:|
| C043 — Reyansh | ₹12,920.00 |
| C026 — Isha | ₹8,371.60 |
| C008 — Meera | ₹4,564.60 |
| C011 — Arjun | ₹4,111.00 |
| C042 — Sanya | ₹3,785.00 |

### Category Revenue

| Category | Orders | Revenue |
|---|---:|---:|
| Haircare | 54 | ₹44,956.10 |
| Skincare | 60 | ₹27,346.00 |
| Babycare | 30 | ₹16,805.00 |
| PersonalCare | 36 | ₹10,753.10 |

---

# Part 2 — Python Data Wrangling & EDA

## Objective

The Python layer independently reads the raw CSV files, cleans the data, identifies duplicates and outliers, performs exploratory analysis, and generates business-ready findings.

The SQL database is not used as the source for this analysis.

## `clean_and_eda.py`

The script performs the following tasks:

### 1. Raw Data Loading

Loads the customers, products, and orders CSV files.

Orders validation:

```text
180 rows × 9 columns
```

### 2. Payment Method Standardization

The raw payment values contain:

```text
COD
cod
Card
card
CARD
UPI
upi
```

After standardization:

| Payment Method | Orders |
|---|---:|
| CARD | 70 |
| UPI | 55 |
| COD | 55 |

### 3. Duplicate Detection

Duplicates are identified using the natural business key rather than `order_id`.

Five duplicate records are detected:

```text
O0176
O0177
O0178
O0179
O0180
```

After removing these duplicates:

```text
175 rows × 9 columns
```

### 4. Missing-Value Handling

Missing values found:

```text
discount_pct → 12
rating       → 15
```

Treatment:

- Missing discount → filled with `0`
- Missing rating → filled with median `3.0`

### 5. Revenue Reconciliation

Cleaned revenue:

```text
₹97,358.30
```

Raw reconstructed revenue:

```text
₹99,860.20
```

Duplicate reconciliation difference:

```text
₹2,501.90
```

The revenue difference is explained by the five duplicate orders. Missing-value imputations do not change the revenue calculation.

### 6. Quantity Outlier Detection

IQR method is used.

```text
Q1  = 1
Q3  = 2
IQR = 1

Lower Bound = -0.5
Upper Bound = 3.5
```

Two quantity outliers are flagged:

```text
O0011 → Quantity 25
O0098 → Quantity 30
```

These records are flagged rather than removed.

### 7. Return Rate by Payment Method

| Payment Method | Return Rate |
|---|---:|
| COD | 44.4% |
| CARD | 14.7% |
| UPI | 18.9% |

COD has the highest return rate.

### 8. Payment × City Tier Analysis

The highest-risk segment is:

```text
Payment Method : COD
City Tier      : 2
Return Rate    : 54.5%
```

For COD:

```text
Tier-1 → 37.5%
Tier-2 → 54.5%
```

### 9. Correlation and Hypothesis Testing

Correlation analysis is performed between:

- rating
- returned
- discount percentage
- quantity

The relationship between discount and returns is approximately:

```text
-0.09
```

Therefore, the hypothesis:

> Higher discounts reduce returns

is **BUSTED** based on the observed data.

### 10. Monthly Revenue and Outlier Correction

The apparent January revenue peak is:

```text
January apparent revenue → ₹29,582.10
```

However, the January figure is inflated by quantity outliers.

After correcting for the outliers:

```text
January corrected revenue → ₹11,637.10
```

The true revenue peak is:

```text
March 2026 → ₹20,318.90
```

## Visualizations

`visualize.py` generates:

```text
visualizations/return_rate_by_payment.png
visualizations/monthly_revenue_trend.png
```

The visualizations communicate:

1. Return-rate comparison by payment method.
2. Outlier-corrected monthly revenue trend.

---

# Part 3 — GenAI-Powered Insight Narrator

## Objective

The GenAI layer converts the trusted Python-generated findings into a concise business narrative for Mamaearth regional operations and finance teams.

The GenAI layer does **not** calculate business metrics independently.

Instead:

```text
Python EDA
    ↓
findings.json
    ↓
Gemini
    ↓
SCR Narrative
```

This ensures that the narrative is based only on validated Python findings.

## `findings.json`

`clean_and_eda.py` programmatically generates:

```text
narrator/findings.json
```

Important figures passed to the narrator include:

```text
Cleaned Revenue              ₹97,358.30
Raw Revenue                  ₹99,860.20
Duplicate Delta              ₹2,501.90

COD Return Rate              44.4%
CARD Return Rate             14.7%
UPI Return Rate              18.9%

Highest Risk Segment         COD + Tier-2
Return Rate                 54.5%

True Peak Month              2026-03
True Peak Revenue            ₹20,318.90

Outlier-Inflated Month       2026-01
Apparent Revenue             ₹29,582.10
Corrected Revenue            ₹11,637.10
```

## `generate_narrative.py`

The script:

1. Loads `findings.json`.
2. Creates the Gemini client using `GEMINI_API_KEY`.
3. Sends only the Python-generated findings to Gemini.
4. Requests a three-section business narrative:
   - Situation
   - Complication
   - Resolution
5. Uses deterministic generation with `temperature = 0.0`.
6. Validates required business figures in the generated narrative.
7. Uses an offline deterministic fallback if Gemini is unavailable.
8. Saves the final narrative to `sample_output.txt`.

## GenAI Safety and Consistency

The prompt instructs Gemini that:

- Numbers must come only from `findings.json`.
- New statistics must not be invented.
- Existing values must not be changed or rounded differently.
- The output must contain Situation, Complication, and Resolution sections.

The script also performs numeric validation after generation.

Required figures checked include:

```text
₹97,358.30
44.4%
54.5%
₹2,501.90
March 2026
₹20,318.90
```

## Gemini API Configuration

The API key is read from an environment variable:

```text
GEMINI_API_KEY
```

The API key is not hardcoded in the source code.

Example PowerShell setup:

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

Then run:

```powershell
python narrator\generate_narrative.py
```

If Gemini is unavailable or no API key is configured, the script automatically uses the deterministic offline SCR fallback.

The fallback does not make any network request and uses the same figures from `findings.json`.

---

# Reproducibility

The project uses a Python virtual environment.

Create the environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install required packages:

```powershell
python -m pip install pandas matplotlib google-genai
```

---

# Execution Order

Run the project in the following order.

## 1. SQL

Use SQLite to execute:

```text
sql/schema.sql
sql/seed_data.sql
sql/reports.sql
```

## 2. Python Cleaning and EDA

From the project root:

```powershell
python analysis\clean_and_eda.py
```

This generates:

```text
narrator/findings.json
```

## 3. Visualizations

```powershell
python analysis\visualize.py
```

This generates:

```text
visualizations/return_rate_by_payment.png
visualizations/monthly_revenue_trend.png
```

## 4. GenAI Narrator

With the Gemini API key configured:

```powershell
python narrator\generate_narrative.py
```

This generates:

```text
narrator/sample_output.txt
```

If Gemini is unavailable, the script automatically uses the offline fallback.

---

# End-to-End Validation

| Layer | Validation |
|---|---|
| SQL Customers | 45 |
| SQL Products | 16 |
| SQL Orders | 180 |
| SQL Raw Revenue | ₹99,860.20 |
| Python Cleaned Orders | 175 |
| Python Cleaned Revenue | ₹97,358.30 |
| Duplicate Revenue Delta | ₹2,501.90 |
| Highest Payment Return Rate | COD — 44.4% |
| Highest Risk Segment | COD + Tier-2 — 54.5% |
| True Peak Month | March 2026 — ₹20,318.90 |
| GenAI Validation | PASSED |

---

# Key Business Findings

1. **COD is the highest-return payment method**, with a 44.4% return rate.
2. **COD + Tier-2 is the highest-risk segment**, with a 54.5% return rate.
3. Duplicate records account for a **₹2,501.90 revenue reconciliation difference**.
4. January appears to be the revenue peak before outlier correction, but the quantity outliers inflate that result.
5. After outlier correction, **March 2026 is the true peak month with ₹20,318.90 revenue**.
6. The observed correlation does not support the hypothesis that higher discounts reduce returns.

---

# GitHub Submission Checklist

Before submitting, verify that the repository contains:

```text
README.md                         ✓
sql/schema.sql                    ✓
sql/seed_data.sql                ✓
sql/reports.sql                  ✓

data/customers.csv               ✓
data/products.csv                ✓
data/orders.csv                  ✓

analysis/clean_and_eda.py        ✓
analysis/visualize.py            ✓

visualizations/return_rate_by_payment.png ✓
visualizations/monthly_revenue_trend.png ✓

narrator/findings.json            ✓
narrator/generate_narrative.py    ✓
narrator/sample_output.txt        ✓
```

Do not commit:

```text
.venv/
.env
API keys
```

The final repository should be publicly accessible on GitHub as required by the project submission instructions.