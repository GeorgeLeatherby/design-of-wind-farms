# design-of-wind-farms
Repo for the course work of the Technical University Munich (TUM) course: Design of wind farms in summer semester of 26.

### Design of Wind Farms: Assignment 1 ###
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


### Design of Wind Farms: Assignment 2 ###

## Overview
This assignment implements the estimation of wind farm power production using analytical wake models. The analysis focuses on calculating the velocity deficits and power losses for a row of turbines using **Jensen's wake model** and the **Root-Sum-Square (RSS) superposition model**

You should receive a terminal output reading:

--- Assignment 2 Results ---
Turbine Type: IEA 3.4MW Reference | Hub Height: 120m
Freestream Wind Speed (V0): 7.5 m/s | k_w: 0.075

--- Wind Direction: 0° ---
Turbine T1: V_eff = 7.50 m/s | Power = 1515.15 kW | Pn/P1 = 1.0000
Turbine T2: V_eff = 6.24 m/s | Power =  872.36 kW | Pn/P1 = 0.5758
Turbine T3: V_eff = 6.09 m/s | Power =  812.42 kW | Pn/P1 = 0.5362
Farm Summary: Total Power = 3,199.93 kW | Efficiency = 70.40%

--- Wind Direction: 270° ---
Turbine T1: V_eff = 7.50 m/s | Power = 1515.15 kW | Pn/P1 = 1.0000
Turbine T2: V_eff = 7.50 m/s | Power = 1515.15 kW | Pn/P1 = 1.0000
Turbine T3: V_eff = 7.50 m/s | Power = 1515.15 kW | Pn/P1 = 1.0000
Farm Summary: Total Power = 4,545.45 kW | Efficiency = 100.00%
