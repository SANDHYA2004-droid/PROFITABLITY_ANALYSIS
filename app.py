# ==============================
# IMPORT LIBRARIES
# ==============================
import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Nassau Candy Dashboard", layout="wide")

st.title("🍬 Nassau Candy Distributor - Profitability Dashboard")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_nassau_data.csv")   # ✅ use cleaned file
    
    # FIX DATE FORMAT
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')

    # REMOVE INVALID DATES
    df = df.dropna(subset=['Order Date', 'Ship Date'])

    return df

df = load_data()

# ==============================
# KPI CALCULATIONS
# ==============================
df['Gross Margin %'] = (df['Gross Profit'] / df['Sales']) * 100
df['Profit per Unit'] = df['Gross Profit'] / df['Units']

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔍 Filters")

# Date filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['Order Date'].min(), df['Order Date'].max()]
)

# Division filter
division = st.sidebar.multiselect(
    "Select Division",
    options=df['Division'].unique(),
    default=df['Division'].unique()
)

# Margin filter
margin_filter = st.sidebar.slider(
    "Minimum Margin %",
    min_value=0,
    max_value=100,
    value=0
)

# Product search
product_search = st.sidebar.text_input("Search Product")

# ==============================
# APPLY FILTERS
# ==============================
filtered_df = df[
    (df['Division'].isin(division)) &
    (df['Gross Margin %'] >= margin_filter)
]

# Date filter
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Order Date'] >= pd.to_datetime(date_range[0])) &
        (filtered_df['Order Date'] <= pd.to_datetime(date_range[1]))
    ]

# Product search
if product_search:
    filtered_df = filtered_df[
        filtered_df['Product Name'].str.contains(product_search, case=False)
    ]

# ==============================
# KPI METRICS
# ==============================
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Gross Profit'].sum()
avg_margin = filtered_df['Gross Margin %'].mean()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📈 Total Profit", f"${total_profit:,.0f}")
col3.metric("📊 Avg Margin %", f"{avg_margin:.2f}%")

# ==============================
# PRODUCT ANALYSIS
# ==============================
st.subheader("📦 Product Profitability")

product_analysis = filtered_df.groupby('Product Name').agg({
    'Sales':'sum',
    'Gross Profit':'sum',
    'Gross Margin %':'mean'
}).reset_index()

top_products = product_analysis.sort_values(by='Gross Profit', ascending=False).head(10)

fig1 = px.bar(top_products, x='Product Name', y='Gross Profit',
              title="Top 10 Products by Profit")
st.plotly_chart(fig1, use_container_width=True)

# ==============================
# DIVISION ANALYSIS
# ==============================
st.subheader("🏭 Division Performance")

division_analysis = filtered_df.groupby('Division').agg({
    'Sales':'sum',
    'Gross Profit':'sum',
    'Gross Margin %':'mean'
}).reset_index()

fig2 = px.bar(division_analysis, x='Division', y='Gross Profit',
              title="Profit by Division")
st.plotly_chart(fig2, use_container_width=True)

# ==============================
# COST VS SALES
# ==============================
st.subheader("💸 Cost vs Sales Analysis")

fig3 = px.scatter(filtered_df,
                  x='Cost',
                  y='Sales',
                  color='Division',
                  size='Gross Profit',
                  title="Cost vs Sales")
st.plotly_chart(fig3, use_container_width=True)

# ==============================
# PARETO ANALYSIS
# ==============================
st.subheader("📊 Pareto Analysis (80/20 Rule)")

pareto = product_analysis.sort_values(by='Sales', ascending=False)
pareto['Cumulative %'] = pareto['Sales'].cumsum() / pareto['Sales'].sum() * 100

fig4 = px.line(pareto, y='Cumulative %', title="Cumulative Sales %")
st.plotly_chart(fig4, use_container_width=True)

# ==============================
# PROFIT CONTRIBUTION
# ==============================
st.subheader("🥧 Profit Contribution")

top_profit = product_analysis.sort_values(by='Gross Profit', ascending=False).head(10)

fig5 = px.pie(top_profit, names='Product Name', values='Gross Profit')
st.plotly_chart(fig5, use_container_width=True)

# ==============================
# DATA TABLE
# ==============================
st.subheader("📄 Data Table")
st.dataframe(filtered_df)
