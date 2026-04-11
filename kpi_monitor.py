import json
import pandas as pd
import plotly.graph_objects as go
from analysis import connect_db, extract_data, compute_kpis


# -----------------------------
# Load thresholds
# -----------------------------
def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# KPI Status Logic
# -----------------------------
def get_kpi_status(value, thresholds):
    if value >= thresholds["green"]:
        return "green"
    elif value >= thresholds["yellow"]:
        return "yellow"
    else:
        return "red"


# -----------------------------
# Evaluate all KPIs
# -----------------------------
def evaluate_kpis(kpis, config):
    results = {}

    for kpi_name, thresholds in config.items():
        value = kpis.get(kpi_name)

        # Handle series (like monthly_growth)
        if isinstance(value, pd.Series):
            value = value.dropna().iloc[-1]

        status = get_kpi_status(value, thresholds)

        results[kpi_name] = {
            "value": float(value),
            "status": status
        }

    return results


# -----------------------------
# Create Gauge Dashboard
# -----------------------------
def create_kpi_dashboard(kpi_results):
    fig = go.Figure()

    positions = [0, 0.33, 0.66]

    for i, (kpi, result) in enumerate(kpi_results.items()):
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=result["value"],
            title={"text": kpi},
            domain={"x": [positions[i], positions[i] + 0.3], "y": [0, 1]},
            gauge={
                "axis": {"range": [0, result["value"] * 1.5]},
                "bar": {"color": result["status"]},
            }
        ))

    fig.update_layout(title="KPI Monitoring Dashboard")

    fig.write_html("output/kpi_monitor.html")


# -----------------------------
# OPTIONAL: Filters (Dropdowns)
# -----------------------------
def create_filtered_dashboard(df):
    cities = df["city"].unique()
    categories = df["category"].unique()

    fig = go.Figure()

    for city in cities:
        filtered = df[df["city"] == city]

        fig.add_trace(go.Bar(
            x=filtered["category"],
            y=filtered["revenue"],
            name=city,
            visible=(city == cities[0])
        ))

    # Dropdown menu
    buttons = []
    for i, city in enumerate(cities):
        visible = [False] * len(cities)
        visible[i] = True

        buttons.append(dict(
            label=city,
            method="update",
            args=[{"visible": visible}]
        ))

    fig.update_layout(
        updatemenus=[{
            "buttons": buttons,
            "direction": "down"
        }],
        title="Revenue by Category (Filtered by City)"
    )

    fig.write_html("output/kpi_filtered_dashboard.html")


# -----------------------------
# MAIN
# -----------------------------
def main():
    engine = connect_db()

    data = extract_data(engine)
    kpis = compute_kpis(data)

    config = load_config()
    results = evaluate_kpis(kpis, config)

    print("\n=== KPI STATUS ===")
    for k, v in results.items():
        print(f"{k}: {v}")

    create_kpi_dashboard(results)
    create_filtered_dashboard(kpis["df"])


if __name__ == "__main__":
    main()