import pandas as pd

# Import data
df = pd.read_csv(r"C:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\dataset\9. Sales-Data-Analysis.csv")

# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

# Generate Revenue column 
df["Revenue"] = df["Quantity"] * df["Price"]

# Clean Manager and City columns (remove extra spaces)
df["Manager"] = df["Manager"].str.strip().str.replace(r"\s+", " ", regex=True)
df["City"] = df["City"].str.strip().str.replace(r"\s+", " ", regex=True)

#Export CSV
df.to_csv(r"C:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\dataset\cleaned_dataset.csv")