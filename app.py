import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Jwsetier Sample Dashboard", layout="wide")

# ==================== DESIGN OPTIONS ====================

PALETTES = {
    "Dark Ops (Charcoal & Amber)": {
        "bg": "#1C1F22", "card": "#F7F5F0", "text": "#F7F5F0",
        "accent": "#E8963C", "chart": ["#E8963C", "#2F7A72", "#D64545", "#F7F5F0", "#7A9E9F", "#C97B3D"],
    },
    "Clean Corporate (White & Navy)": {
        "bg": "#FFFFFF", "card": "#F0F3F7", "text": "#1E293B",
        "accent": "#1E3A5F", "chart": ["#1E3A5F", "#3B6EA5", "#7DA3C4", "#B0C4DE", "#4A5568", "#2C4A6E"],
    },
    "Fresh Retail (Gray & Green)": {
        "bg": "#F5F5F5", "card": "#FFFFFF", "text": "#1B1B1B",
        "accent": "#2E7D32", "chart": ["#2E7D32", "#66BB6A", "#A5D6A7", "#1B5E20", "#81C784", "#43A047"],
    },
    "Bold Modern (Navy & Cyan)": {
        "bg": "#0D1B2A", "card": "#1B2A3D", "text": "#E0F7FA",
        "accent": "#00B4D8", "chart": ["#00B4D8", "#0077B6", "#90E0EF", "#CAF0F8", "#023E8A", "#48CAE4"],
    },
    "Warm Minimal (Cream & Terracotta)": {
        "bg": "#FAF6F0", "card": "#FFFFFF", "text": "#3D2B1F",
        "accent": "#C1502E", "chart": ["#C1502E", "#E08E45", "#7A9E7E", "#3D2B1F", "#D4A373", "#9C6644"],
    },
}

FONTS = {
    "Modern Sans (Inter)": "'Inter', sans-serif",
    "Condensed Bold (Barlow Condensed)": "'Barlow Condensed', sans-serif",
    "Classic Sans (System Default)": "sans-serif",
    "Monospace (IBM Plex Mono)": "'IBM Plex Mono', monospace",
}

CARD_STYLES = {
    "Left border accent": "border-left: 4px solid {accent}; border-radius: 4px;",
    "Plain / flat": "border-radius: 8px;",
    "Full border": "border: 1px solid {accent}; border-radius: 8px;",
}

CHART_TEMPLATES = {
    "Bars": "bar",
    "Lines only": "line",
    "Mixed (bar + line)": "mixed",
}

# ==================== SIDEBAR: DESIGN SETTINGS ====================

st.sidebar.header(" Design Settings")

with st.sidebar.expander("Customize Appearance", expanded=False):
    palette_name = st.selectbox("Color Palette", list(PALETTES.keys()))
    font_name = st.selectbox("Font Style", list(FONTS.keys()))
    header_size = st.select_slider("Header Size", options=["Small", "Medium", "Large"], value="Medium")
    card_style_name = st.selectbox("KPI Card Style", list(CARD_STYLES.keys()))
    chart_style = st.selectbox("Chart Type Preference", list(CHART_TEMPLATES.keys()))

st.sidebar.divider()

palette = PALETTES[palette_name]
font_family = FONTS[font_name]
card_css = CARD_STYLES[card_style_name].format(accent=palette["accent"])
header_px = {"Small": "28px", "Medium": "36px", "Large": "48px"}[header_size]

# ==================== APPLY STYLING ====================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

    .stApp {{
        background-color: {palette["bg"]};
    }}

    html, body, [class*="css"] {{
        font-family: {font_family};
        color: {palette["text"]};
    }}

    h1 {{
        font-family: {font_family};
        font-weight: 700;
        font-size: {header_px} !important;
        color: {palette["text"]};
    }}

    h2, h3 {{
        font-family: {font_family};
        color: {palette["text"]};
    }}

    div[data-testid="stMetric"] {{
        background-color: {palette["card"]};
        padding: 16px 18px;
        {card_css}
    }}
    div[data-testid="stMetric"] label {{
        color: {palette["bg"] if palette["card"] != palette["bg"] else palette["text"]} !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: 'IBM Plex Mono', monospace;
        color: {palette["bg"] if palette["card"] != palette["bg"] else palette["text"]} !important;
        opacity: 1 !important;
    }}
    div[data-testid="stMetricValue"] > div {{
        color: {palette["bg"] if palette["card"] != palette["bg"] else palette["text"]} !important;
    }}

    button[data-baseweb="tab"] {{
        font-family: {font_family};
        font-weight: 600;
        text-transform: uppercase;
        font-size: 13px;
    }}

    [data-testid="stCaptionContainer"] {{
        color: {palette["accent"]} !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 11px !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title("Sample Dashboard")
st.caption("Sales · Inventory · Rider Delivery Analytics — Portfolio Project by Julie Ann Wabe-Setier")

# ==================== LOAD DATA ====================

sales = pd.read_csv("sales_data.csv", parse_dates=["date"])
inventory = pd.read_csv("inventory_data.csv", parse_dates=["date"])
riders = pd.read_csv("rider_deliveries.csv", parse_dates=["date"])

store_list = sorted(sales["store_code"].unique())
selected_store = st.sidebar.selectbox("Filter by Store", ["All Stores"] + store_list)

if selected_store != "All Stores":
    sales_f = sales[sales["store_code"] == selected_store]
    inventory_f = inventory[inventory["store_code"] == selected_store]
    riders_f = riders[riders["store_code"] == selected_store]
else:
    sales_f = sales
    inventory_f = inventory
    riders_f = riders

# ==================== KPI ROW ====================

col1, col2, col3, col4 = st.columns(4)

total_sales = sales_f["gross_sales_php"].sum()
avg_basket = sales_f["avg_basket_php"].mean()
critical_items = inventory_f[inventory_f["on_hand_units"] < inventory_f["reorder_point"]].shape[0]
avg_on_time = round((riders_f["deliveries_on_time"].sum() / riders_f["deliveries_assigned"].sum()) * 100, 1)

col1.metric("Total Sales", f"₱{total_sales:,.0f}")
col2.metric("Avg Basket Size", f"₱{avg_basket:,.2f}")
col3.metric("Below Reorder Point", critical_items)
col4.metric("Avg On-Time Delivery", f"{avg_on_time}%")

st.divider()

# ==================== CHART HELPER ====================

def style_fig(fig):
    fig.update_layout(
        plot_bgcolor=palette["bg"],
        paper_bgcolor=palette["bg"],
        font_color=palette["text"],
        margin=dict(t=50, l=10, r=10, b=10),
    )
    return fig

def make_trend_chart(df, x, y, title):
    if CHART_TEMPLATES[chart_style] == "bar":
        fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=[palette["accent"]])
    else:
        fig = px.line(df, x=x, y=y, title=title)
        fig.update_traces(line_color=palette["accent"], line_width=2.5)
    return style_fig(fig)

# ==================== TABS ====================

tab1, tab2, tab3 = st.tabs(["📈 Sales", "📦 Inventory", "🛵 Rider Delivery"])

with tab1:
    st.subheader("Daily Sales Trend")
    daily_sales = sales_f.groupby("date")["gross_sales_php"].sum().reset_index()
    st.plotly_chart(make_trend_chart(daily_sales, "date", "gross_sales_php", "Gross Sales Over Time"),
                     use_container_width=True)

    st.subheader("Sales by Store")
    store_totals = sales.groupby("store_code")["gross_sales_php"].sum().reset_index()
    fig2 = px.bar(store_totals, x="store_code", y="gross_sales_php", color="store_code",
                  title="Total Sales per Store", color_discrete_sequence=palette["chart"])
    st.plotly_chart(style_fig(fig2), use_container_width=True)

with tab2:
    st.subheader("Stock Levels vs Reorder Point (latest count)")
    latest_date = inventory_f["date"].max()
    latest_inv = inventory_f[inventory_f["date"] == latest_date]
    latest_inv = latest_inv.assign(
        status=latest_inv.apply(
            lambda r: "Critical" if r["on_hand_units"] < r["reorder_point"] * 0.5
            else ("Low" if r["on_hand_units"] < r["reorder_point"] else "Healthy"),
            axis=1
        )
    )
    fig3 = px.bar(latest_inv.sort_values("on_hand_units"), x="on_hand_units", y="sku",
                  color="status", orientation="h",
                  color_discrete_map={"Critical": "#D64545", "Low": palette["accent"], "Healthy": "#2F7A72"},
                  title=f"Stock on Hand as of {latest_date.date()}")
    st.plotly_chart(style_fig(fig3), use_container_width=True)

    st.dataframe(latest_inv[["store_code", "sku", "category", "on_hand_units", "reorder_point", "status"]],
                 use_container_width=True)

with tab3:
    st.subheader("On-Time Delivery Rate by Route")
    rider_summary = riders_f.groupby(["rider_name", "route"]).agg(
        assigned=("deliveries_assigned", "sum"),
        on_time=("deliveries_on_time", "sum")
    ).reset_index()
    rider_summary["on_time_rate"] = round((rider_summary["on_time"] / rider_summary["assigned"]) * 100, 1)

    fig4 = px.bar(rider_summary.sort_values("on_time_rate"), x="on_time_rate", y="rider_name",
                  color="on_time_rate", orientation="h",
                  color_continuous_scale=["#D64545", palette["accent"], "#2F7A72"],
                  title="On-Time Delivery Rate (%)")
    st.plotly_chart(style_fig(fig4), use_container_width=True)

    st.dataframe(rider_summary, use_container_width=True)

st.divider()
st.caption("Built with Streamlit, Pandas & Plotly — demonstrating multi-unit F&B operations reporting: "
           "sales monitoring, inventory compliance, and field/rider deployment analytics.")