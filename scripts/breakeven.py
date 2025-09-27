import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Import Data
df = pd.read_csv(r"C:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\Original Data\9. Sales-Data-Analysis.csv")

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

# Determine when accumulated units reach break-even
df["Accumulated Units"] = df["Quantity"].cumsum()
df_1 = df[["Date", "Accumulated Units"]]

# Find first index where accumulated units >= break_even_units
idx = (df_1["Accumulated Units"] >= break_even_units).idxmax()  

# Get the date and accumulated units at break-even
be_date = df_1["Date"].iloc[idx]
be_units = df_1["Accumulated Units"].iloc[idx-1]

print(f"Break-even reached on {be_date} with {be_units} units sold.")

# Plot lines
plt.figure(figsize=(10,6))
plt.plot(units, total_revenue, label="Revenue", color="blue")
plt.plot(units, total_cost, label="Total Cost", color="red")

# Shade loss area (left of BEP, cost above revenue)
plt.fill_between(units, total_revenue, total_cost, 
                 where=(units <= break_even_units), 
                 interpolate=True, color="red", alpha=0.2, label="Loss Area")

# Shade profit area (right of BEP, revenue above cost)
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
