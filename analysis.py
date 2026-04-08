"""
Integration 4 — KPI Dashboard: Amman Digital Market Analytics
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sqlalchemy import create_engine


# -------------------------
# Database Connection
# -------------------------
def connect_db():
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5433/amman_market"
    )
    engine = create_engine(DATABASE_URL)
    return engine


# -------------------------
# Data Extraction
# -------------------------
def extract_data(engine):
    customers = pd.read_sql("SELECT * FROM customers", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    orders = pd.read_sql("SELECT * FROM orders WHERE status != 'cancelled'", engine)
    order_items = pd.read_sql(
        "SELECT * FROM order_items WHERE quantity <= 100", engine
    )

    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
    }


# -------------------------
# KPI Computation
# -------------------------
def compute_kpis(data_dict):
    import pandas as pd

    customers = data_dict["customers"]
    products = data_dict["products"]
    orders = data_dict["orders"]
    order_items = data_dict["order_items"]

    # Merge all tables
    df = (
        order_items
        .merge(orders, on="order_id")
        .merge(products, on="product_id")
        .merge(customers, on="customer_id")
    )

    # Ensure datetime format
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Compute revenue per row
    df["revenue"] = df["quantity"] * df["unit_price"]

    # -----------------------
    # KPI 1: Total Revenue
    # -----------------------
    total_revenue = df["revenue"].sum()

    # -----------------------
    # KPI 2: Monthly Revenue (TIME-BASED)
    # -----------------------
    monthly_revenue = (
        df.groupby(df["order_date"].dt.to_period("M"))["revenue"]
        .sum()
    )

    # -----------------------
    # KPI 3: Month-over-Month Growth (TIME-BASED)
    # -----------------------
    monthly_growth = monthly_revenue.pct_change()

    # -----------------------
    # KPI 4: Customer Cohort Revenue (COHORT KPI)
    # -----------------------
    # First purchase date per customer
    df["first_order_date"] = df.groupby("customer_id")["order_date"].transform("min")

    # Cohort = first purchase month
    df["cohort"] = df["first_order_date"].dt.to_period("M")

    # Revenue per cohort
    cohort_revenue = df.groupby("cohort")["revenue"].sum()

    # -----------------------
    # KPI 5: Revenue by Category
    # -----------------------
    revenue_by_category = (
        df.groupby("category")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    # -----------------------
    # KPI 6 (Optional but useful): Average Order Value
    # -----------------------
    avg_order_value = (
        df.groupby("order_id")["revenue"]
        .sum()
        .mean()
    )

    # -----------------------
    # Revenue by City (useful segmentation)
    # -----------------------
    revenue_by_city = (
        df.groupby("city")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    return {
        "df": df,

        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "monthly_growth": monthly_growth,

        "cohort_revenue": cohort_revenue,

        "revenue_by_category": revenue_by_category,
        "avg_order_value": avg_order_value,
        "revenue_by_city": revenue_by_city,
    }


# -------------------------
# Statistical Tests
# -------------------------
def run_statistical_tests(data_dict):
    import numpy as np
    from scipy import stats

    df = data_dict["df"]
    results = {}

    # -------------------------
    # Helper: Cohen's d
    # -------------------------
    def cohens_d(x, y):
        return (np.mean(x) - np.mean(y)) / np.sqrt((np.std(x)**2 + np.std(y)**2) / 2)

    # -------------------------
    # TEST 1: T-test (City comparison)
    # -------------------------
    cities = df["city"].dropna().unique()

    if len(cities) >= 2:
        # Use two specific cities (more controlled)
        city1 = df[df["city"] == cities[0]]["revenue"]
        city2 = df[df["city"] == cities[1]]["revenue"]

        t_stat, p_val = stats.ttest_ind(city1, city2, equal_var=False)

        d = cohens_d(city1, city2)

        results["city_ttest"] = {
            "test": "Independent t-test",
            "t_stat": t_stat,
            "p_value": p_val,
            "effect_size_cohens_d": d,
            "hypothesis": {
                "H0": "No difference in revenue between cities",
                "H1": "There is a difference in revenue between cities"
            },
            "interpretation": (
                "Statistically significant difference between cities"
                if p_val < 0.05
                else "No statistically significant difference between cities"
            )
        }

    # -------------------------
    # TEST 2: ANOVA (Category comparison)
    # -------------------------
    groups = [
        df[df["category"] == c]["revenue"].dropna()
        for c in df["category"].dropna().unique()
    ]

    if len(groups) > 1:
        f_stat, p_val = stats.f_oneway(*groups)

        # Effect size: Eta squared
        grand_mean = df["revenue"].mean()
        ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
        ss_total = sum((df["revenue"] - grand_mean) ** 2)
        eta_squared = ss_between / ss_total if ss_total != 0 else 0

        results["category_anova"] = {
            "test": "One-way ANOVA",
            "f_stat": f_stat,
            "p_value": p_val,
            "effect_size_eta_squared": eta_squared,
            "hypothesis": {
                "H0": "All categories have the same average revenue",
                "H1": "At least one category is different"
            },
            "interpretation": (
                "Statistically significant differences between categories"
                if p_val < 0.05
                else "No statistically significant differences between categories"
            )
        }

    return results


# -------------------------
# Visualizations
# -------------------------
def create_visualizations(kpi_results, stat_results):
    import os
    import matplotlib.pyplot as plt
    import seaborn as sns

    os.makedirs("output", exist_ok=True)

    df = kpi_results["df"]

    # -------------------------
    # 1. Monthly Revenue Trend
    # -------------------------
    plt.figure()
    monthly = kpi_results["monthly_revenue"].copy()
    monthly.index = monthly.index.astype(str)

    monthly.plot()
    plt.title("Revenue Growth Over Time (Monthly Trend)")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig("output/monthly_revenue.png")
    plt.close()

    # -------------------------
    # 2. Month-over-Month Growth
    # -------------------------
    plt.figure()
    growth = kpi_results["monthly_growth"].copy()
    growth.index = growth.index.astype(str)

    growth.plot()
    plt.title("Month-over-Month Revenue Growth Trend")
    plt.xlabel("Month")
    plt.ylabel("Growth Rate")
    plt.tight_layout()
    plt.savefig("output/monthly_growth.png")
    plt.close()

    # -------------------------
    # 3. Revenue by City
    # -------------------------
    plt.figure()
    kpi_results["revenue_by_city"].plot(kind="bar")
    plt.title("Revenue Distribution Across Cities")
    plt.xlabel("City")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/revenue_by_city.png")
    plt.close()

    # -------------------------
    # 4. Revenue by Category
    # -------------------------
    plt.figure()
    kpi_results["revenue_by_category"].plot(kind="bar")
    plt.title("Top Performing Product Categories")
    plt.xlabel("Category")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/revenue_by_category.png")
    plt.close()

    # -------------------------
    # 5. Revenue Distribution by Category
    # -------------------------
    plt.figure()
    sns.boxplot(data=df, x="category", y="revenue")
    plt.title("Revenue Distribution Across Categories")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/boxplot_category.png")
    plt.close()

    # -------------------------
    # 6. Heatmap (City vs Category)
    # -------------------------
    pivot = df.pivot_table(
        values="revenue",
        index="city",
        columns="category",
        aggfunc="sum"
    )

    plt.figure()
    sns.heatmap(pivot, cmap="viridis")
    plt.title("Revenue Relationship: City vs Category")
    plt.tight_layout()
    plt.savefig("output/heatmap.png")
    plt.close()


# -------------------------
# Main
# -------------------------
def main():
    engine = connect_db()

    data = extract_data(engine)
    kpis = compute_kpis(data)
    stats_results = run_statistical_tests(kpis)

    create_visualizations(kpis, stats_results)

    print("\n=== KPI SUMMARY ===")
    print("Total Revenue:", kpis["total_revenue"])
    print("Average Order Value:", kpis["avg_order_value"])
    print("\nRevenue by City:\n", kpis["revenue_by_city"])
    print("\nRevenue by Category:\n", kpis["revenue_by_category"])

    print("\n=== STATISTICAL TESTS ===")
    for test, result in stats_results.items():
        print(f"\n{test}:")
        print(result)


if __name__ == "__main__":
    main()