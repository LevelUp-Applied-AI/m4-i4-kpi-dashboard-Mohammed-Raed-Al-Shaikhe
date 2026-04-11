import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

from analysis import connect_db, extract_data, compute_kpis


# -----------------------------
# Load data once
# -----------------------------
engine = connect_db()
data = extract_data(engine)
kpis = compute_kpis(data)
df = kpis["df"]


# -----------------------------
# App setup
# -----------------------------
app = dash.Dash(__name__)
app.title = "KPI Dashboard"


# -----------------------------
# Layout
# -----------------------------
app.layout = html.Div([
    html.H1("KPI Dashboard"),

    # Global Filter
    dcc.Dropdown(
        id="city-filter",
        options=[{"label": c, "value": c} for c in df["city"].unique()],
        value=df["city"].unique()[0],
        clearable=False
    ),

    dcc.Tabs(id="tabs", value="tab-1", children=[
        dcc.Tab(label="KPI Overview", value="tab-1"),
        dcc.Tab(label="Time Series", value="tab-2"),
        dcc.Tab(label="Cohort Analysis", value="tab-3"),
    ]),

    html.Div(id="tab-content")
])


# -----------------------------
# Render Tabs
# -----------------------------
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    Input("city-filter", "value")
)
def render_tab(tab, city):
    filtered = df[df["city"] == city]

    # -----------------------------
    # PAGE 1: KPI Overview
    # -----------------------------
    if tab == "tab-1":
        total_revenue = filtered["revenue"].sum()
        avg_order = filtered.groupby("order_id")["revenue"].sum().mean()

        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=total_revenue,
            title={"text": "Total Revenue"},
            domain={"x": [0, 0.5], "y": [0, 1]}
        ))

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=avg_order,
            title={"text": "Avg Order Value"},
            domain={"x": [0.5, 1], "y": [0, 1]}
        ))

        return dcc.Graph(figure=fig)

    # -----------------------------
    # PAGE 2: Time Series
    # -----------------------------
    elif tab == "tab-2":
        monthly = (
            filtered.groupby(filtered["order_date"].dt.to_period("M"))["revenue"]
            .sum()
            .reset_index()
        )

        monthly["order_date"] = monthly["order_date"].astype(str)

        fig = px.line(
            monthly,
            x="order_date",
            y="revenue",
            title="Monthly Revenue"
        )

        return html.Div([
            dcc.Graph(figure=fig)
        ])

    # -----------------------------
    # PAGE 3: Cohort Analysis
    # -----------------------------
    elif tab == "tab-3":
        filtered["first_order_date"] = filtered.groupby("customer_id")["order_date"].transform("min")
        filtered["cohort"] = filtered["first_order_date"].dt.to_period("M")

        cohort = (
            filtered.groupby("cohort")["revenue"]
            .sum()
            .reset_index()
        )

        cohort["cohort"] = cohort["cohort"].astype(str)

        fig = px.bar(
            cohort,
            x="cohort",
            y="revenue",
            title="Cohort Revenue"
        )

        return dcc.Graph(figure=fig)


# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)