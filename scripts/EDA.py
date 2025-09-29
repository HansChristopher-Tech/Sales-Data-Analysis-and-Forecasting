import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Import data
df = pd.read_csv(
    r"C:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\dataset\9. Sales-Data-Analysis.csv"
)

# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

# Generate Revenue column 
df["Revenue"] = df["Quantity"] * df["Price"]

# Clean Manager and City columns (remove extra spaces)
df["Manager"] = df["Manager"].str.strip().str.replace(r"\s+", " ", regex=True)
df["City"] = df["City"].str.strip().str.replace(r"\s+", " ", regex=True)

# ------------------------------
# 1. Most preferred payment method
# ------------------------------
def payment():
    df_pay = df.groupby("Payment Method").size()
    max_value = df_pay.idxmax()
    max_count = df_pay.max()
    print(f"> Over {max_count} transactions out of {len(df)} were done using {max_value}")


# ------------------------------
# 2. Top-selling products (by quantity and revenue)
# ------------------------------
def products():
    df_products = df.groupby("Product")[["Quantity", "Revenue"]].sum()
    
    df_prod_qty = df_products["Quantity"].sort_values(ascending=False)
    df_prod_rev = df_products["Revenue"].sort_values(ascending=False)
    
    print("Top Selling in terms of Quantity:")
    print(df_prod_qty)
    print("-" * 50)
    print("Top Selling in terms of Revenue:")
    print(df_prod_rev)
    print("-" * 50)


# ------------------------------
# 3. City and manager generating maximum revenue
# ------------------------------
def manager():
    df_manager = (
        df.groupby(["City", "Manager"])["Revenue"]
          .sum()
          .reset_index()
          .sort_values(by="Revenue", ascending=False)
    )
    print(df_manager)


# ------------------------------
# 4. Daily revenue trend (lineplot)
# ------------------------------
def trends():
    df_revenue_trend = (
        df.groupby("Date")["Revenue"]
          .sum()
          .reset_index()
          .sort_values(by="Date", ascending=True)
    )
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_revenue_trend, x="Date", y="Revenue")
    plt.title("Daily Revenue Trend", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Revenue")
    plt.show()

# ------------------------------
# 5. Summary statistics
# ------------------------------
def stats():
    # Average Revenue
    average_revenue = df["Revenue"].mean()
    print(f"Across {len(df['Date'])} days, the company generated "
          f"an average revenue of ${average_revenue:.2f}")
    
    # November vs December revenue
    df["Month"] = df["Date"].dt.month_name()
    df_months_trend = df.groupby("Month")["Revenue"].sum()
    nov, dec = round(df_months_trend["November"], 2), round(df_months_trend["December"], 2)
    
    if nov > dec:
        print(f"November had higher revenue: ${nov} vs ${dec} in December "
              f"(difference: ${nov - dec:.2f})")
    else:
        print(f"December had higher revenue: ${dec} vs ${nov} in November "
              f"(difference: ${dec - nov:.2f})")
    
    # Std and variance
    std_revenue = round(np.std(df["Revenue"]), 2)
    std_qty = round(np.std(df["Quantity"]), 2)
    var_revenue = round(np.var(df["Revenue"]), 2)
    var_qty = round(np.var(df["Quantity"]), 2)
    
    print(f"Standard Deviations → Revenue: {std_revenue}, Quantity: {std_qty}")
    print(f"Variances → Revenue: {var_revenue}, Quantity: {var_qty}")


# ------------------------------
# 6. Check revenue trend (Nov vs Dec)
# ------------------------------
def checker():
    df["Month"] = df["Date"].dt.month_name()
    df_months_trend = df.groupby("Month")["Revenue"].sum()
    nov, dec = round(df_months_trend["November"], 2), round(df_months_trend["December"], 2)

    if dec > nov:
        print(f"Revenue increased in December by ${dec - nov:.2f}")
    else:
        print(f"Revenue decreased in December by ${nov - dec:.2f}")


# ------------------------------
# 7. Compare average quantity & revenue per product
# ------------------------------
def avg_product_stats():
    df_product = (
        df.groupby("Product")[["Quantity", "Revenue"]]
          .mean()
          .reset_index()
    )
    print(df_product)

payment()
products()
manager()
trends()
stats()
checker()
avg_product_stats()