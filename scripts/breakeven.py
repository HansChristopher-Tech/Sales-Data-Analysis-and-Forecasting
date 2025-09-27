import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Import Data
df = pd.read_csv(r"C:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\Original Data\9. Sales-Data-Analysis.csv")

# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

# Parameters
profit_margin = 0.30
fixed_cost = 10000

# Calculate Revenue and Cost
df["Revenue"] = df["Price"] * df["Quantity"]
df["Variable_Cost"] = df["Revenue"] * (1 - profit_margin)
df["Cost_Per_Product"] = df["Variable_Cost"] / df["Quantity"]

# Averages
avg_price = df["Price"].mean()
avg_variable_cost = df["Cost_Per_Product"].mean()

# Break-even (Formula method)
break_even_units = fixed_cost / (avg_price - avg_variable_cost)
break_even_revenue = break_even_units * avg_price
print(f"Break-even Units: {break_even_units:.0f}")
print(f"Break-even Revenue: ${break_even_revenue:.0f}")

# Create data for plotting (Revenue vs Cost lines)
units = np.linspace(0, break_even_units * 1.5, 200)
total_revenue = units * avg_price
total_cost = fixed_cost + units * avg_variable_cost

# Track accumulated units by date
df_daily = df.groupby("Date")["Quantity"].sum().reset_index()
df_daily["Accumulated Units"] = df_daily["Quantity"].cumsum()
df_daily["Day"] = df_daily["Day"] = range(1, len(df_daily) + 1)

# Find the first date when accumulated units >= break-even
be_row = df_daily[df_daily["Accumulated Units"] >= break_even_units].iloc[0]
be_date = be_row["Date"]
be_units = be_row["Accumulated Units"]
be_day = be_row["Day"]
print(f"Break-even reached on the {be_day}rd day, at exactly {be_date.date()} with {be_units:.0f} units sold.")

# ----------------- Plot -----------------
plt.figure(figsize=(10,6))
plt.plot(units, total_revenue, label="Revenue", color="blue")
plt.plot(units, total_cost, label="Total Cost", color="red")

# Shade loss area
plt.fill_between(units, total_revenue, total_cost, 
                 where=(units <= break_even_units), 
                 interpolate=True, color="red", alpha=0.2, label="Loss Area")

# Shade profit area
plt.fill_between(units, total_revenue, total_cost, 
                 where=(units >= break_even_units), 
                 interpolate=True, color="green", alpha=0.2, label="Profit Area")

# Mark break-even point
plt.scatter(break_even_units, break_even_revenue, color="black", zorder=5)
plt.text(break_even_units, break_even_revenue,
         f"Break-even\n({break_even_units:.0f} units, ${break_even_revenue:.0f})",
         ha="left", va="top")

plt.title("Break-even Analysis (Formula Method)")
plt.xlabel("Units Sold")
plt.ylabel("Value ($)")
plt.legend()
plt.show()
