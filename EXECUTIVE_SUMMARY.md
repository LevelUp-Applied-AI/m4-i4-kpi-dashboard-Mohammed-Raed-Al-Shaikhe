# Executive Summary — Amman Digital Market Analytics

---

## Top Findings

1. The total revenue of the market is **48,701.5**, indicating a healthy overall business size, with a strong contribution from key product categories.

2. Revenue varies significantly across product categories, with **Books (11,274)** and **Electronics (11,005)** being the top-performing categories, while **Sports (4,405)** and **Food & Beverage (4,443.5)** generate the lowest revenue.

3. There is **no statistically significant difference in revenue between cities** (p-value = 0.935), meaning customer spending behavior is consistent across locations.

4. Product category has a **strong and statistically significant impact on revenue** (p-value ≈ 1.63e-55, η² ≈ 0.219), indicating it is a major driver of business performance.

5. The average order value is **109.94**, showing that customers spend a moderate amount per transaction.

---

## Supporting Data

- **Total Revenue KPI:** 48,701.5
  - Source: `compute_kpis()`
  - Visualization: _(none required, summary KPI)_

- **Revenue by Category:**
  - Books: 11,274
  - Electronics: 11,005
  - Clothing: 10,322
  - Visualization: `output/revenue_by_category.png`
  - Boxplot: `output/boxplot_category.png`

- **Revenue by City:**
  - Amman: 15,719
  - Irbid: 7,250.5
  - Visualization: `output/revenue_by_city.png`
  - Statistical Test:
    - Independent t-test
    - p-value = 0.935
    - Cohen’s d ≈ -0.008
    - Interpretation: No significant difference between cities

- **Category ANOVA Test:**
  - F-statistic: 60.38
  - p-value: 1.63e-55
  - Effect size (η²): 0.219
  - Interpretation: Strong statistically significant differences between categories

- **Average Order Value (AOV):** 109.94

- **Visualizations:**
  - `output/monthly_revenue.png`
  - `output/monthly_growth.png`
  - `output/heatmap.png`

---

## Recommendations

1. Focus marketing and inventory efforts on high-performing categories such as **Books, Electronics, and Clothing**, as they drive the majority of revenue.

2. Improve performance of low-performing categories (e.g., **Sports and Food & Beverage**) through promotions, discounts, or bundling strategies to increase demand.

3. Since city does not significantly impact revenue, prioritize **customer acquisition and retention strategies** rather than location-based strategies.

4. Monitor monthly revenue and growth trends using time-based KPIs to detect early signs of decline or growth and respond proactively.

---
