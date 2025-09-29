import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
import time
import matplotlib.dates as mdates
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import warnings


#Set-Up
warnings.filterwarnings("ignore")

#Import the cleaned file
df = pd.read_csv(r"C:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\dataset\cleaned_dataset.csv")

#Use only the Date and Revenue Columns
df_time_series = df.groupby("Date")["Revenue"].sum().reset_index().sort_values(by="Date", ascending=True)
df_time_series["Date"] = pd.to_datetime(df_time_series["Date"])


# Create a plot to thos the original data
def plot_original_date():
    plt.figure(figsize=(12,6))
    plt.plot(df_time_series["Date"], df_time_series["Revenue"])
    plt.title("Daily Revenue Trend", fontsize=14)
    plt.ylabel("Revenue")

    # Format x-axis ticks
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    plt.show()

#Perform Augmented Dickery-Fuller Test
def stationary_test():
    # Set significance level
    alpha = 0.05  
    max_diff = 5   # safety limit (to avoid infinite loop)

    series = df_time_series["Revenue"]
    diff_count = 0

    while True:
        # Perform ADF test
        result = adfuller(series.dropna())
        p_value = result[1]

        print(f"\n=== Differencing Round: {diff_count} ===")
        print("ADF Statistic:", result[0])
        print("p-value:", p_value)
        print("Critical Values:")
        for key, value in result[4].items():
            print(f"   {key}: {value}")

        # Always state the hypotheses
        print("\nHypotheses of the ADF Test:")
        print("   H0: The time series is NON-STATIONARY (has a unit root)")
        print("   H1: The time series is STATIONARY")

        if p_value < alpha:
            print(f"> p-value = {p_value:.4f} <= {alpha} → Reject H0 → Series is STATIONARY ✅")
            break
        else:
            if diff_count >= max_diff:
                print("> Reached max differencing limit, stopping.")
                break
            
            print(f"> p-value = {p_value:.4f} > {alpha} → Fail to reject H0 → Series is NON-STATIONARY ❌")
            print("> Applying differencing...")
            time.sleep(2)

            # Apply differencing
            series = series.diff().dropna()
            diff_count += 1

    # Final differenced series is stored in `series`
    print(f"\nFinal differencing order used: d = {diff_count}")

    # Store back to dataframe for reference
    df_time_series[f"Diff_{diff_count}"] = series

    # Plot original vs differenced
    plt.figure(figsize=(12,5))
    plt.subplot(1,2,1)
    plt.plot(df_time_series['Date'], df_time_series['Revenue'], label="Original")
    plt.title("Original Revenue Trend")
    plt.subplot(1,2,2)
    plt.plot(df_time_series.loc[series.index, 'Date'], series, 
            label=f"{diff_count} Differences", color="orange")
    plt.title(f"{diff_count} Differences")
    plt.show()

    #Save as CSV
    df_time_series.to_csv(r"C:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\dataset\Augmented-Dickery-Fuller.csv")
    print("CSV's Saved")
  
#Perform ARIMA, SARIMA, and ETS Test
# Rename properly
df_time_series = df_time_series.rename(columns={'Unnamed: 0': 'Day',
                                    'Date': 'ds',
                                    'Revenue': 'y'},
                                    errors='ignore')

# Ensure numeric & datetime
df_time_series['ds'] = pd.to_datetime(df_time_series['ds'], errors='coerce')
df_time_series['y'] = pd.to_numeric(df_time_series['y'], errors='coerce')
df_time_series = df_time_series.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)

# Log transform AFTER cleaning
df_time_series["y_log"] = np.log(df_time_series["y"])

# Add unique_id for StatsForecast
df_sf = df_time_series[['ds', 'y_log']].copy()
df_sf['unique_id'] = '1'
df_sf = df_sf[['unique_id', 'ds', 'y_log']].rename(columns={'y_log': 'y'})

# Forecast Horizon
horizon = 10

# Define Models
models = [
    AutoARIMA(seasonal=True, season_length=7, alias="SARIMA"),
    AutoARIMA(seasonal=False, alias="ARIMA"),
    AutoETS(season_length=7, alias="ETS")
]

# Fit and Forecast
sf = StatsForecast(models=models, freq="D")
sf.fit(df=df_sf)
future_preds_log = sf.predict(h=horizon)

# Invert log transformation
future_preds = future_preds_log.copy()
future_preds['SARIMA'] = np.exp(future_preds_log['SARIMA'])
future_preds['ARIMA'] = np.exp(future_preds_log['ARIMA'])
future_preds["ETS"] = np.exp(future_preds_log['ETS'])

# Choose only necessary columns
df_time_series = df_time_series[["ds", "y"]]
future_preds = future_preds[["ds", "ARIMA", "SARIMA", "ETS"]]

# SARIMA
df_sarima = future_preds[["ds", "SARIMA"]].rename(columns={"SARIMA": "y"})
df_sarima_final = pd.concat([df_time_series, df_sarima], axis=0).reset_index(drop=True)

# ARIMA
df_arima = future_preds[["ds", "ARIMA"]].rename(columns={"ARIMA": "y"})
df_arima_final = pd.concat([df_time_series, df_arima], axis=0).reset_index(drop=True)

# ETS
df_ets = future_preds[["ds", "ETS"]].rename(columns={"ETS": "y"})
df_ets_final = pd.concat([df_time_series, df_ets], axis=0).reset_index(drop=True)

#Save as CSV's
df_arima_final.to_csv(r"c:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\dataset\arima_predictions.csv")
df_sarima_final.to_csv(r"c:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\dataset\sarima_predictions.csv")
df_ets_final.to_csv(r"c:\Users\Hans Christopher\Documents\DATA ANALYST TOOLS\PYTHON\Sales\dataset\ets_predictions.csv")
print("CSV's Saved")

# Make sure time series is sorted
df_time_series = df_time_series.sort_values("ds")
df_arima_final = df_arima_final.sort_values("ds")
df_sarima_final = df_sarima_final.sort_values("ds")
df_ets_final = df_sarima_final.sort_values("ds")

def save_time_series_plots():
    plt.figure(figsize=(12, 10))

    # --- SARIMA subplot (top) ---
    plt.subplot(3, 1, 1)
    plt.plot(df_sarima_final["ds"], df_sarima_final["y"], label="SARIMA Forecast", color="orange")
    plt.plot(df_time_series["ds"], df_time_series["y"], label="Original", color="blue")
    plt.ylabel("SARIMA")
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))  
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))    

    plt.legend()

    # --- ARIMA subplot (middle) ---
    plt.subplot(3, 1, 2)
    plt.plot(df_arima_final["ds"], df_arima_final["y"], label="ARIMA Forecast", color="green")
    plt.plot(df_time_series["ds"], df_time_series["y"], label="Original", color="blue")
    plt.ylabel("ARIMA")
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    plt.legend()
    
    # --- ETS subplot (bottom) ---
    plt.subplot(3, 1, 3)
    plt.plot(df_ets_final["ds"], df_ets_final["y"], label="ETS Forecast", color="red")
    plt.plot(df_time_series["ds"], df_time_series["y"], label="Original", color="blue")
    plt.ylabel("ETS")
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    plt.legend()
    
    plt.tight_layout()
    plt.show()




#Validation
def compute_metrics(y_true, y_pred):
    # Basic errors
    mae_val = mean_absolute_error(y_true, y_pred)
    rmse_val = np.sqrt(mean_squared_error(y_true, y_pred))
    mape_val = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    # Symmetric MAPE
    smape_val = 100 * np.mean(
        2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred))
    )
    
    # Bias (mean forecast error)
    bias_val = np.mean(y_pred - y_true)
    
    # R² (optional, useful for regression-like forecasting)
    r2_val = r2_score(y_true, y_pred)

    return {
        'MAE': mae_val,
        'RMSE': rmse_val,
        'MAPE (%)': mape_val,
        'SMAPE (%)': smape_val,
        'Bias': bias_val,
        'R²': r2_val
    }

def cross_validation_metrics(sf, df, horizon=30, n_windows=8, step_size=7):
    # Run cross-validation
    cv_df = sf.cross_validation(
        df=df,
        h=horizon,
        n_windows=n_windows,
        step_size=step_size,
        refit=True
    )

    # Prepare a table
    metrics_table = []

    for model in ['SARIMA', 'ARIMA', "ETS"]:
        # Extract predictions
        y_true_all = cv_df['y'].values
        y_pred_all = cv_df[model].values

        # Compute all metrics
        metrics = compute_metrics(y_true_all, y_pred_all)
        metrics['Model'] = model
        metrics_table.append(metrics)

    return pd.DataFrame(metrics_table)

# Usage
cv_results = cross_validation_metrics(sf, df_sf, horizon=10, n_windows=5, step_size=5)
print(cv_results)
