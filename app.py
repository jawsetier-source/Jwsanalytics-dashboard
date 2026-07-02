import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Page setup ----------
st.set_page_config(page_title="Jwsetier Sample Dashboard", layout="wide")

# ---------- Custom styling ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1 {
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #F7F5F0;
    }

    h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #F7F5F0;
    }

    /* KPI metric cards */
    div[data-testid="stMetric"] {
        background-color: #F7F5F0;
        border-radius: 4px;
        padding: 16px 18px;
        border-left: 4px solid #E8963C;
    }
    div[data-testid="stMetric"] label {
        color: #1C1F22 !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace;
        color: #1C1F22 !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 13px;
        letter-spacing: 0.5px;
    }

    /* Caption / accent text */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #E8963C !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 11px !important;
    }

    hr {
        border-color: rgba(247,245,240,0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Sample Dashboard")
st.caption("Sales · Inventory · Rider Delivery Analytics — Portfolio Project by Julie Ann Wabe-Setier")

# ---------- Load raw data ----------
sales = pd.read_csv("sales_data.csv", parse_dates=["date"])
inventory = pd.read_csv("inventory_data.csv", parse_dates=["date"])
riders = pd.read_csv("rider_deliveries.csv", parse_dates=["date"])

# ---------- Sidebar filter ----------
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

# ---------- KPI row ----------
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

# ---------- Plotly chart theme helper ----------
def style_fig(fig):
    fig.update_layout(
        plot_bgcolor="#1C1F22",
        paper_bgcolor="#1C1F22",
        font_color="#F7F5F0",
        title_font_family="Inter",
        margin=dict(t=50, l=10, r=10, b=10),
    )
    return fig

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📈 Sales", "📦 Inventory", "🛵 Rider Delivery"])

with tab1:
    st.subheader("Daily Sales Trend")
    daily_sales = sales_f.groupby("date")["gross_sales_php"].sum().reset_index()
    fig = px.line(daily_sales, x="date", y="gross_sales_php", title="Gross Sales Over Time")
    fig.update_traces(line_color="#2F7A72", line_width=2.5)
    st.plotly_chart(style_fig(fig), use_container_width=True)

    st.subheader("Sales by Store")
    store_totals = sales.groupby("store_code")["gross_sales_php"].sum().reset_index()
    fig2 = px.bar(store_totals, x="store_code", y="gross_sales_php", color="store_code",
                  title="Total Sales per Store",
                  color_discrete_sequence=["#E8963C", "#2F7A72", "#D64545", "#F7F5F0", "#7A9E9F", "#C97B3D"])
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
                  color_discrete_map={"Critical": "#D64545", "Low": "#E8963C", "Healthy": "#2F7A72"},
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
                  color_continuous_scale=["#D64545", "#E8963C", "#2F7A72"],
                  title="On-Time Delivery Rate (%)")
    st.plotly_chart(style_fig(fig4), use_container_width=True)

    st.dataframe(rider_summary, use_container_width=True)

st.divider()
st.caption("Built with Streamlit, Pandas & Plotly — demonstrating multi-unit F&B operations reporting: "
           "sales monitoring, inventory compliance, and field/rider deployment analytics.")