# design-of-wind-farms
Repo for the course work of the Technical University Munich (TUM) course: Design of wind farms in summer semester of 26.

# Design of Wind Farms: Assignment 1

## Overview
This repository contains the Python calculation script for Assignment 1: Basics and Recapitulation. The objective is to calculate the Annual Energy Production (AEP) and the Capacity Factor (CF) for the IEA 3.4MW Reference wind turbine, specifically evaluating the 240° (SW) wind direction sector.

## Files
* `main.py`: The primary Python script containing the calculation logic.
* `IEA_Reference_3.4MW_130.csv`: The provided operational data for the wind turbine. 
* `README.md`: This documentation file.

## Methodology
The script applies the standard continuous integral formulation to calculate the expected power output:
1.  **Weibull PDF**: Calculated for the specific sector using shape parameter `k = 2.72` and scale parameter `C = 7.5 m/s`.
2.  **Numerical Integration**: Because the provided wind speed bins are non-uniform, the script utilizes the Trapezoidal rule (`numpy.trapz`) to accurately integrate the product of the Power Curve and the Weibull PDF between the cut-in (3 m/s) and cut-out (25 m/s) wind speeds.
3.  **AEP and CF**: The integrated mean power is multiplied by the specific working hours for the 240° direction (1270 hrs) to yield the sector AEP. The CF is subsequently derived using the 3370 kW rated power.

## Execution
To run the script, ensure you have `pandas` and `numpy` installed in your environment, and that the CSV data file is located in the same directory as the script.

You should receive a terminal output reading:
--- Assignment 1 Results (Direction: 240 deg) ---
Mean Expected Power: 1,345.21 kW
Sector AEP:          1,708,411.54 kWh
Capacity Factor:     0.3992 (39.92%)
