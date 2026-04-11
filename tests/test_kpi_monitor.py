from kpi_monitor import get_kpi_status,evaluate_kpis,main
from unittest.mock import MagicMock


def test_kpi_status():
    thresholds = {"green": 100, "yellow": 50}

    assert get_kpi_status(120, thresholds) == "green"
    assert get_kpi_status(70, thresholds) == "yellow"
    assert get_kpi_status(30, thresholds) == "red"


def test_evaluate_kpis():
    kpis = {
        "total_revenue": 1200,
        "avg_order_value": 40
    }

    config = {
        "total_revenue": {"green": 1000, "yellow": 500},
        "avg_order_value": {"green": 50, "yellow": 30}
    }

    results = evaluate_kpis(kpis, config)

    assert results["total_revenue"]["status"] == "green"
    assert results["avg_order_value"]["status"] == "yellow"


def test_main_runs(monkeypatch):
    monkeypatch.setattr("kpi_monitor.connect_db", lambda: MagicMock())
    monkeypatch.setattr("kpi_monitor.extract_data", lambda x: {})
    monkeypatch.setattr("kpi_monitor.compute_kpis", lambda x: {
        "total_revenue": 1000,
        "avg_order_value": 50,
        "monthly_growth": 0.1,
        "df": None
    })

    monkeypatch.setattr("kpi_monitor.create_kpi_dashboard", lambda x: None)
    monkeypatch.setattr("kpi_monitor.create_filtered_dashboard", lambda x: None)

    main()
