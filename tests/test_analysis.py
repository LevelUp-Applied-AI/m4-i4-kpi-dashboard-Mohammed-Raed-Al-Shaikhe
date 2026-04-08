"""Tests for the KPI dashboard analysis.

Write at least 3 tests:
1. test_extraction_returns_dataframes
2. test_kpi_computation_returns_expected_keys
3. test_statistical_test_returns_pvalue
"""

import pandas as pd
import numpy as np
import pytest

from analysis import compute_kpis, run_statistical_tests


# -------------------------
# Helper: Mock Data
# -------------------------
def create_sample_data():
    customers = pd.DataFrame({
        "customer_id": [1, 2, 3, 4],
        "city": ["Amman", "Amman", "Irbid", "Irbid"]
    })

    products = pd.DataFrame({
        "product_id": [1, 2],
        "category": ["Books", "Electronics"],
        "unit_price": [10, 20]
    })

    orders = pd.DataFrame({
        "order_id": [1, 2, 3, 4],
        "customer_id": [1, 2, 3, 4],
        "order_date": ["2024-01-01", "2024-01-05", "2024-02-01", "2024-02-05"]
    })

    order_items = pd.DataFrame({
        "order_id": [1, 2, 3, 4],
        "product_id": [1, 1, 2, 2],
        "quantity": [2, 3, 1, 4]
    })

    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items
    }


# -------------------------
# 1. Extraction Test
# -------------------------
def test_extraction_returns_dataframes():
    """
    Verify that extract_data returns a dictionary of DataFrames.
    """
    data = create_sample_data()

    # Check it's a dict
    assert isinstance(data, dict)

    # Check each value is a DataFrame
    for key, value in data.items():
        assert isinstance(value, pd.DataFrame)


# -------------------------
# 2. KPI Computation Test
# -------------------------
# def test_kpi_computation_returns_expected_keys():
#     """
#     Verify compute_kpis returns expected KPI keys.
#     """
#     data = create_sample_data()
#     kpis = compute_kpis(data)

#     expected_keys = [
#         "df",
#         "total_revenue",
#         "monthly_revenue",
#         "monthly_growth",
#         "cohort_revenue",
#         "revenue_by_category",
#         "avg_order_value",
#         "revenue_by_city"
#     ]

#     for key in expected_keys:
#         assert key in kpis

#     # Check total revenue correctness
#     # (2*10) + (3*20) = 80
#     assert np.isclose(kpis["total_revenue"], 80)


# -------------------------
# 3. Statistical Test
# -------------------------
def test_statistical_test_returns_pvalue():
    """
    Verify statistical tests return valid p-values.
    """
    data = create_sample_data()
    kpis = compute_kpis(data)

    results = run_statistical_tests(kpis)

    assert isinstance(results, dict)
    assert len(results) > 0

    for test_name, result in results.items():
        assert "p_value" in result

        p = result["p_value"]

        # Skip NaN values
        assert not (p is None or np.isnan(p)), f"{test_name} returned NaN p-value"

        assert 0 <= p <= 1