import pandas as pd
import numpy as np

def weibull_pdf(v: np.ndarray, c: float, k: float) -> np.ndarray:
    """
    Calculates the Weibull probability density function.
    """
    return (k / c) * ((v / c) ** (k - 1)) * np.exp(- (v / c) ** k)

def main():
    # ---------------------------------------------------------
    # 1. Assignment Parameters (Direction: 240 deg)
    # ---------------------------------------------------------
    C = 7.5          # Scale parameter [m/s]
    k = 2.72         # Shape parameter [-]
    hours = 1270.0   # Turbine working hours in this condition [hrs]
    P_rated = 3370.0 # Rated power of the IEA 3.4MW turbine [kW]

    # ---------------------------------------------------------
    # 2. Data Loading & Validation
    # ---------------------------------------------------------
    # Load the turbine performance data
    df = pd.read_csv('IEA_Reference_3.4MW_130.csv')
    
    # Extract arrays for Wind Speed (V) and Power (P)
    V = df['Wind Speed [m/s]'].values
    P = df['Power [kW]'].values
    
    # Perform assertion checks based on turbine specs
    assert np.isclose(V[0], 3.0), f"Expected V_in of 3 m/s, but got {V[0]} m/s"
    assert np.isclose(V[-1], 25.0), f"Expected V_out of 25 m/s, but got {V[-1]} m/s"

    # ---------------------------------------------------------
    # 3. Core Calculations
    # ---------------------------------------------------------
    # Calculate the Weibull probability density for each wind speed bin
    f_V = weibull_pdf(V, C, k)
    
    # Calculate the expected power integrand: P(V) * f(V)
    integrand = P * f_V
    
    # Numerically integrate over the wind speeds using the Trapezoidal rule
    mean_power = np.trapezoid(y=integrand, x=V)
    
    # Calculate Sector AEP [kWh] and Capacity Factor [-]
    aep_sector = mean_power * hours
    cf_sector = aep_sector / (P_rated * hours)

    # ---------------------------------------------------------
    # 4. Output Results
    # ---------------------------------------------------------
    print("--- Assignment 1 Results (Direction: 240 deg) ---")
    print(f"Mean Expected Power: {mean_power:,.2f} kW")
    print(f"Sector AEP:          {aep_sector:,.2f} kWh")
    print(f"Capacity Factor:     {cf_sector:.4f} ({cf_sector * 100:.2f}%)")

if __name__ == "__main__":
    main()