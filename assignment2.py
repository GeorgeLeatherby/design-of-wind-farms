import pandas as pd
import numpy as np

# =============================================================================
# MODELS AND FORMULAS
# =============================================================================

def jensen_velocity_deficit(x: float, r_0: float, ct: float, k: float) -> float:
    """
    Calculates the fractional velocity deficit using Jensen's Wake Model
    
    Formula: delta_V = (1 - sqrt(1 - C_t)) / (1 + (k * x) / r_0)^2
    """
    if x <= 0:
        return 0.0  # No wake effects if the turbine is not downstream
    
    numerator = 1.0 - np.sqrt(1.0 - ct)
    denominator = (1.0 + (k * x) / r_0) ** 2
    return numerator / denominator

def root_sum_square_superposition(deficits: list) -> float:
    """
    Calculates the total velocity deficit from multiple upstream wakes
    
    Formula: delta_V_tot = sqrt(sum(delta_V_i^2))
    """
    if not deficits:
        return 0.0
    return np.sqrt(np.sum(np.square(deficits)))

def main():
    # =========================================================================
    # 1. ASSIGNMENT PARAMETERS
    # =========================================================================
    V_0 = 7.5           # Freestream wind speed [m/s] 
    k_w = 0.075         # Wake decay constant [-] 
    D = 130.0           # Rotor diameter [m] 
    r_0 = D / 2.0       # Rotor radius [m]
    separation = 5 * D  # 5D Separation = 650m 
    
    # Wind Directions to evaluate
    wind_directions = [0, 270]  # Degrees 

    # Turbine Coordinates (X: West->East, Y: North->South)
    # Turbines installed in a row (North to South)
    turbines = [
        {'id': 'T1', 'x': 0.0, 'y': 0.0},
        {'id': 'T2', 'x': 0.0, 'y': 1.0 * separation},
        {'id': 'T3', 'x': 0.0, 'y': 2.0 * separation}
    ]

    # =========================================================================
    # 2. DATA LOADING
    # =========================================================================
    try:
        df = pd.read_csv('IEA_Reference_3.4MW_130.csv')
    except FileNotFoundError:
        print("Error: 'IEA_Reference_3.4MW_130.csv' not found.")
        return

    # Extract data for interpolation
    V_curve = df['Wind Speed [m/s]'].values
    P_curve = df['Power [kW]'].values
    Ct_curve = df['Ct [-]'].values

    print(f"--- Assignment 2 Results ---")
    print(f"Turbine Type: IEA 3.4MW Reference | Hub Height: 120m")
    print(f"Freestream Wind Speed (V0): {V_0} m/s | k_w: {k_w}\n")

    # =========================================================================
    # 3. CALCULATION LOOP
    # =========================================================================
    for wd in wind_directions:
        print(f"--- Wind Direction: {wd}° ---")
        
        # Determine the flow direction vector based on your coordinate system
        # 0 deg (North) blows in +Y direction. 270 deg (West) blows in +X direction.
        if wd == 0:
            dx_func = lambda target, up: target['y'] - up['y']
        elif wd == 270:
            dx_func = lambda target, up: target['x'] - up['x']
        else:
            dx_func = lambda target, up: 0.0 # Simplified for these two directions

        results = []
        p1_power = 0.0

        for i, target in enumerate(turbines):
            deficits = []
            
            # Find deficits from all other turbines
            for j, other in enumerate(turbines):
                if i == j: continue
                
                # Distance downstream relative to the wind direction
                dist_downstream = dx_func(target, other)
                
                if dist_downstream > 0:
                    # In a real wind farm, we'd use the Ct at V_eff of the upstream turbine.
                    # For this assignment's "by hand" context, we use the provided Ct.
                    ct_val = 0.766  # Example Ct value for 7.5 m/s from the curve (you can interpolate if needed)
                    
                    deficit = jensen_velocity_deficit(dist_downstream, r_0, ct_val, k_w)
                    deficits.append(deficit)
            
            # Superposition and effective conditions
            total_deficit = root_sum_square_superposition(deficits)
            v_eff = V_0 * (1.0 - total_deficit)
            p_eff = np.interp(v_eff, V_curve, P_curve)
            
            if i == 0: p1_power = p_eff
            relative_p = p_eff / p1_power if p1_power > 0 else 0
            
            results.append({
                'id': target['id'],
                'v_eff': v_eff,
                'p_eff': p_eff,
                'rel_p': relative_p
            })
            
            print(f"Turbine {target['id']}: V_eff = {v_eff:.2f} m/s | Power = {p_eff:7.2f} kW | Pn/P1 = {relative_p:.4f}")
        
        total_p = sum(r['p_eff'] for r in results)
        efficiency = (total_p / (p1_power * len(turbines))) * 100
        print(f"Farm Summary: Total Power = {total_p:,.2f} kW | Efficiency = {efficiency:.2f}%\n")

if __name__ == "__main__":
    main()