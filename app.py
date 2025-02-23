import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from streamlit_option_menu import option_menu

# Load the dataset
@st.cache_data
def load_data():
    file_path = "inventory_performance_dashboard_data.xlsx"
    xls = pd.ExcelFile(file_path)
    df_dim_product = pd.read_excel(xls, sheet_name="DimProduct")
    df_fact_inventory = pd.read_excel(xls, sheet_name="FactInventory")
    df_inventory = df_fact_inventory.merge(df_dim_product, on="ProductID", how="left")
    df_inventory["Date"] = pd.to_datetime(df_inventory["Date"])
    df_inventory["Month"] = df_inventory["Date"].dt.to_period("M")
    return df_inventory

df_inventory = load_data()

# Streamlit Sidebar Navigation
st.sidebar.title("Navigation")
page = option_menu("Main Menu", ["Overview", "Trends Over Time"],
                   icons=["bar-chart", "line-chart"], menu_icon="cast", default_index=0)

if page == "Overview":
    st.title("📊 Inventory Performance Overview")
    
    # KPIs
    avg_inv_turnover = df_inventory["Invt TO"].mean()
    total_stockout_days = df_inventory["StockoutDays"].sum()
    avg_stock_levels = df_inventory[["OpeningStock", "ClosingStock"]].mean().mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Inventory Turnover", f"{avg_inv_turnover:.2f}")
    col2.metric("Total Stockout Days", total_stockout_days)
    col3.metric("Avg Stock Levels", f"{avg_stock_levels:.2f}")

    # Stockout Frequency per Product
    st.subheader("Stockout Frequency per Product")
    stockout_frequency = df_inventory.groupby("ProductName")["StockoutDays"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots()
    stockout_frequency.plot(kind="bar", ax=ax, colormap='tab10')
    ax.set_xlabel("Product Name")
    ax.set_ylabel("Total Stockout Days")
    ax.set_title("Stockout Frequency per Product")
    st.pyplot(fig)

    # Inventory Turnover by Category
    st.subheader("Inventory Turnover by Category")
    fig, ax = plt.subplots()
    sns.boxplot(x="Category", y="Invt TO", data=df_inventory, palette="Set2", ax=ax)
    ax.set_xlabel("Product Category")
    ax.set_ylabel("Inventory Turnover")
    ax.set_title("Distribution of Inventory Turnover by Category")
    ax.grid(axis='y')
    st.pyplot(fig)

elif page == "Trends Over Time":
    st.title("📈 Trends Over Time")
    
    # Stock Levels Over Time
    st.subheader("Stock Levels Over Time")
    stock_trend = df_inventory.groupby("Date")[["OpeningStock", "ClosingStock"]].mean()
    st.line_chart(stock_trend)

    # Stock Used by Product Over Time (Monthly)
    st.subheader("Stock Used by Product Over Time (Monthly)")
    stock_used_trend = df_inventory.groupby(["Month", "ProductName"])["StockUsed"].sum().unstack()
    st.line_chart(stock_used_trend)
    
    # Stockout Days Over Time (Monthly)
    st.subheader("Stockout Days Over Time (Monthly)")
    stockout_trend = df_inventory.groupby("Month")["StockoutDays"].sum()
    st.line_chart(stockout_trend)
    
    # Stock Received Over Time (Monthly)
    st.subheader("Stock Received Over Time (Monthly)")
    stock_received_trend = df_inventory.groupby("Month")["StockReceived"].sum()
    st.line_chart(stock_received_trend)
    
    # OpeningStock and ClosingStock by Month
    st.subheader("OpeningStock and ClosingStock by Month")
    stock_levels_by_date = df_inventory.groupby(df_inventory['Date'].dt.to_period('M'))[['OpeningStock', 'ClosingStock']].mean()
    st.write(stock_levels_by_date)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    stock_levels_by_date.plot(kind='bar', ax=ax, color=['skyblue', 'lightgreen'])
    ax.set_xlabel('Month')
    ax.set_ylabel('Average Stock Levels')
    ax.set_title('OpeningStock and ClosingStock by Month')
    st.pyplot(fig)
