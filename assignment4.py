# imports
from floris import FlorisModel, TimeSeries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from external.landbosse.landbosse.main_function import run_landbosse
import copy

class assignment4:
    def __init__(self):

        # Load TimeSeries from csv
        self.df = pd.read_csv("inputs/sample_time_series.csv")
        self.ws = np.array(self.df["ws_HH_m/s"])
        self.wd = np.array(self.df["wd_HH_deg"])

        # Init timeseries object
        self.timeseries = None
        self.aep = None

        self.ti = 0.06 # Turbulence intensity
        self.d1_wd = 5 # deg (discretization for wind direction task 1)
        self.d1_ws = 1 # m/s (discretization for wind speed task 1)
        self.d2_wd = 1 # deg (discretization for wind direction task 2)
        self.d2_ws = 1 # m/s (discretization for wind speed task 2)
        self.D = 130 # m (turbine diameter)
        self.x = [0.0, 0.0, 0.0] # m (turbine location)
        self.y = [0.0, 5*self.D, 10*self.D] # m (turbine location)


        self.rated_power_single_turbine = 3370 # (kW)

        self.turbine_coordinates = np.array([[0.0, 0.0], [0.0, 5*self.D], [0.0, 10*self.D]])
        self.pos_substation = np.array([[500.0, 5*self.D]]) # m (substation location)
        self.fuel_cost_per_gallon = 5.19 # $
        self.line_frequency = 50 # (Hz)
        self.Cable_Voltage = 30 # (kV) Available: 10,20,30,45,60 kV
        self.turbine_cost = 1.3 # Million per megawatt (MW)
        self.o_m = 0.016 # $/kWh
        self.rental_payment = 20000 # $/MW-year (MW-year = megawatt year)
        self.discount_rate = 0.04 # 4%
        self.design_lifetime = 20 # year
        self.project_construction_time = 12 # months

        self.WriteExcel = False # Write excel file with results
        self.Display = True # Display the results


        # Execution
        self.task1()
        self.task2()
        self.task3()
        self.task4()
        self.task5()
        self.task6()
        self.task8()
        self.task9()

        self.show_plots()

    def task1(self):
        """Create and plot the windrose"""
        self.timeseries = TimeSeries(wind_speeds=self.ws, wind_directions=self.wd, turbulence_intensities=self.ti)

        wind_rose1 = self.timeseries.to_WindRose(
            wd_edges = np.arange(0, 360, self.d1_wd),
            ws_edges = np.arange(0, 50, self.d1_ws)
        )

        wind_rose1.plot(ws_step = self.d1_ws*2, wd_step=self.d1_wd*2)
        plt.title("Windrose task 1")
        plt.tight_layout()


    def task2(self, verbose = 1):
        """
        Define the wind farm as well as the windrose in FLORIS using the Gauss wake model 
        (default parameters). Then, determine the AEP, the capacity factor of the wind farm as 
        well as the wind farm efficiency (P/Pno_wake). Use a wind rose discretization with a 
        bin size of 1m/s for wind speed and 1° for wind direction.
        """
        if verbose == 1:
            print(f"\nTask 2")

        # Setup FlorisModel
        fmodel = FlorisModel("inputs/gch.yaml")

        # task 2 windrose definition
        wind_rose2 = self.timeseries.to_WindRose(
            wd_edges = np.arange(0, 360, self.d2_wd),
            ws_edges = np.arange(0, 50, self.d2_ws)
        )

        fmodel.assign_hub_height_to_ref_height()
        fmodel.set(
            layout_x=self.x, 
            layout_y=self.y, 
            wind_data=wind_rose2,
            turbine_type=["IEA3_4_MW"]
            )
        
        # Run the model
        fmodel.run()
        fmodel_nowake = copy.deepcopy(fmodel)
        fmodel_nowake.run_no_wake()

        # AEP
        self.aep = fmodel.get_farm_AEP() # This is in Watt-hours!
        aep_nowake = fmodel_nowake.get_farm_AEP()

        if verbose == 1:
            print(f"\nAEP: {(self.aep/1e6):.2f}")
            print(f"AEP no wake: {(aep_nowake/1e6):.2f}")
        
        # Capacity factor full windfarm. Ratio of actual energy produced to theoretically max possible energy
        capacity_factor = self.aep / ((self.rated_power_single_turbine*1000*3) * 8760)

        if verbose == 1:
            print(f"Cp wind farm: {capacity_factor:.4f}")

        # Windfarm efficiency (P/P_nowake)
        efficiency = self.aep / aep_nowake
        
        if verbose == 1:
            print(f"Efficiency: {efficiency:.4f}%")

    def task3(self, verbose = 1):
        """
        Define the wind farm in LandBOSSE. Use “iea36_120_project_data” as the input turbine 
        and update the “Turbine rating MW” as well as the rest of the parameters needed to be 
        updated based on the following criteria. Then, calculate the Balance-of-Plant costs for the 
        project and the LCOE. 
        """

        if verbose == 1:
            print(f"\nTask 3")

        # Using updated project_list.xlsx file in standard landbosse input

        landbosse_results_df = run_landbosse(
            self.turbine_coordinates,
            self.pos_substation,
            self.Cable_Voltage,
            self.WriteExcel,
            self.Display
        )

        # print(f"{landbosse_results_df}")

        # Total BoP costs is sum of entries in cost column from results
        self.bop_cost = landbosse_results_df['Cost per project'].sum()
        # print(f"Sum of Balance of plant costs: {bop_cost}")

        aep_kwh = self.aep / 1000.0

        n_turbines = len(self.x)
        total_capacity_mw = n_turbines * (self.rated_power_single_turbine / 1000.0)

        # Initial investment = Turbine Capex + BOP Costs
        self.turbine_capex = total_capacity_mw * self.turbine_cost * 1e6
        self.total_investment = self.turbine_capex + self.bop_cost

        # Annual O&M = Fixed (Rental Payments) + Variable (Maintenance Rate * AEP)
        annual_fixed_om = total_capacity_mw * self.rental_payment
        annual_variable_om = aep_kwh * self.o_m
        self.total_annual_om = annual_fixed_om + annual_variable_om

        # Annuity factor = (1 - (1 + d)^-N) / d
        d = self.discount_rate
        N = self.design_lifetime
        annuity_factor = (1 - (1 + d)**(-N)) / d

        # LCOE Calculation ($/kWh)
        self.lcoe = (self.total_investment / (aep_kwh * annuity_factor)) + (self.total_annual_om / aep_kwh)

        if verbose == 1:
            # Results Output
            print(f"Annual AEP: {aep_kwh:,.2f} kWh")
            print(f"Total BOP Cost: ${self.bop_cost:,.2f}")
            print(f"Total Investment (CapEx): ${self.total_investment:,.2f}")
            print(f"Total Annual O&M (OpEx): ${self.total_annual_om:,.2f}")
            print(f"---")
            print(f"LCOE: ${self.lcoe:.4f} / kWh")

    def task4(self):
        """
        Compare the estimated LCOE with the literature and plot the cost breakdown of the wind farm by turbine investment,
        balance of plant investment, O&M and land rental in a pie chart
        """
        print(f"\nTask 4")

        # 1. Literature Comparison Sources
        # Source A: IRENA (2023) "Renewable Power Generation Costs in 2023" -> Avg: $0.033/kWh
        # Source B: Lazard (2024) "Levelized Cost of Energy Analysis v17.0" -> Range: $0.027 - $0.075/kWh
        irena_lcoe = 0.033
        lazard_range = [0.027, 0.075]
        
        print(f"LCOE Comparison:")
        print(f"My Calculated LCOE:    ${self.lcoe:.4f} / kWh")
        print(f"IRENA (2023 Avg):        ${irena_lcoe:.4f} / kWh (Diff: {((self.lcoe - irena_lcoe)/irena_lcoe)*100:+.1f}%)")
        print(f"Lazard (2024) Range:      ${lazard_range[0]:.3f} - ${lazard_range[1]:.3f} / kWh")

        # 2. Extract Data for Lifetime Cost Breakdown (assuming 20-year project lifetime)
        n_turbines = len(self.x)
        aep_kwh = self.aep / 1000.0
        total_mw = n_turbines * (self.rated_power_single_turbine / 1000.0)

        # Lifetime Operational Costs
        lifetime_maintenance = (aep_kwh * self.o_m) * self.design_lifetime
        lifetime_rental = (total_mw * self.rental_payment) * self.design_lifetime
        
        # Totals for the Full Wind Park
        full_park_costs = [
            self.turbine_capex,     # Initial Turbine Cost
            self.bop_cost,          # Initial Construction/BOP
            lifetime_maintenance,    # 20-year Maintenance
            lifetime_rental         # 20-year Land Lease
        ]

        # Individual Turbine Breakdown
        per_turbine_costs = [cost / n_turbines for cost in full_park_costs]

        # 3. Plotting
        labels = ['Turbine Investment', 'Balance of Plant', 'O&M (Maintenance)', 'Land Rental']
        colors = ["#3c98da", "#ca9668", "#43bd43", "#9E3333"]
        explode = (0, 0, 0, 0) # no explode

        fig, ax1 = plt.subplots(1, 1, figsize=(8, 7))

        # Chart 1: Full Wind Park
        ax1.pie(full_park_costs, labels=labels, autopct=lambda p: f'{p:.1f}%\n(${p * sum(full_park_costs) / 100:,.0f})', 
                startangle=140, colors=colors, explode=explode, shadow=True)
        ax1.set_title(f"Full Wind Farm Lifetime Cost Breakdown\n(Total: ${sum(full_park_costs)/1e6:.2f}M)")

        plt.tight_layout()

    def task5(self):
        """
        Repeat tasks 2 and 3 with 8D separation distance and compare 
        AEP and LCOE results to the 5D baseline.
        """
        print(f"\nTask 5: Repeat Analysis with 8D Spacing")

        # 1. Store 5D Baseline values (from previous tasks)
        self.aep_5d = copy.deepcopy(self.aep) # Use deepcopy, to create real copy with own memory instead of pointer!
        self.lcoe_5d = copy.deepcopy(self.lcoe)
        self.capex_5d = copy.deepcopy(self.turbine_capex)
        self.total_annual_om_5d = copy.deepcopy(self.total_annual_om)
        self.bop_cost_5d = copy.deepcopy(self.bop_cost)

        # 2. Update spacing to 8D and recalculate coordinates
        # We keep the first turbine at 0.0 and space the others at 8*D
        self.y = [0.0, 8*self.D, 16*self.D]
        self.turbine_coordinates = np.array([[0.0, 0.0], [0.0, 8*self.D], [0.0, 16*self.D]])
        
        # Update substation position to stay "perpendicular to the middle turbine"
        self.pos_substation = np.array([[500.0, 8*self.D]])

        print(f"Re-running FLORIS and LandBOSSE for 8D spacing...")
        
        # 3. Re-run Task 2 (AEP) and Task 3 (Financials/LCOE)
        # Note: These methods update self.aep and self.lcoe with 8D values
        self.task2(verbose = 0)
        self.task3(verbose = 0)

        aep_8d = self.aep
        lcoe_8d = self.lcoe

        # 4. Calculate relative differences (%)
        # Formula: (New - Old) / Old * 100
        aep_diff = ((aep_8d - self.aep_5d) / self.aep_5d) * 100
        lcoe_diff = ((lcoe_8d - self.lcoe_5d) / self.lcoe_5d) * 100

        # 5. Output Comparison
        print(f"AEP 5D: {self.aep_5d/1e9:.4f} GWh | AEP 8D: {aep_8d/1e9:.4f} GWh")
        print(f"Relative AEP Change: {aep_diff:+.2f}%")
        print(f"LCOE 5D: ${self.lcoe_5d:.4f}/kWh | LCOE 8D: ${lcoe_8d:.4f}/kWh")
        print(f"Relative LCOE Change: {lcoe_diff:+.2f}%")
        
        if aep_diff > 0:
            print("Observation: Increasing spacing reduced wake losses, increasing AEP.")
        if lcoe_diff > 0:
            print("Observation: Higher cabling costs from 8D spacing outweighed AEP gains, increasing LCOE.")
        else:
            print("Observation: AEP gains from reduced wakes outweighed higher cabling costs, decreasing LCOE.")
    

    def task6(self):
        """
        Calculates LCOE for 5D spacing with a 10% reduction in discount rate, meaning 3.6%
        Compares it to the baseline LCOE (at 4% discount rate).
        """
        print(f"\nTask 6: Discount Rate Change")
        
        # 1. Baseline Values (Assume these were calculated in Task 3/4)
        lcoe_baseline = self.lcoe_5d  # This is the LCOE at 4% for 5D spacing
        d_baseline = 0.04
        N = 20  # Lifetime in years
        
        # 2. Calculate New Discount Rate
        d_new = d_baseline * (1 - 0.10) # 3.6%
        
        # 3. Recalculate Annuity (A) for the new rate
        # Annuity formula: ((1+d)^N - 1) / (d * (1+d)^N)
        annuity_new = ((1 + d_new)**N - 1) / (d_new * (1 + d_new)**N)
        
        # 4. Recalculate TLCC and LCOE
        # LandBOSSE provides the Initial Investment (I) and O&M. 
        # Total Life-Cycle Cost (TLCC) = I + (O&M * Annuity)
        # Task 3 already provides LCOE, we can use the simplified formula:
        # LCOE = (I / (AEP * A)) + (O&M / AEP)
        
        # Accessing costs from previous LandBOSSE run for 5D. 
        initial_investment = self.capex_5d + self.bop_cost_5d
        annual_om_costs = self.total_annual_om_5d
        aep = (self.aep_5d / 1000.0) # aep is converted from Wh to kWh
        
        lcoe_new = (initial_investment / (aep * annuity_new)) + (annual_om_costs / aep)
        
        # 5. Calculate Relative Difference
        lcoe_diff_pct = ((lcoe_new - lcoe_baseline) / lcoe_baseline) * 100
        
        # 6. Output
        print(f"Original Discount Rate: {d_baseline*100:.1f}%")
        print(f"New Discount Rate:      {d_new*100:.1f}%")
        print(f"LCOE (Baseline):        ${lcoe_baseline:.4f}/kWh")
        print(f"LCOE (New Rate):        ${lcoe_new:.4f}/kWh")
        print(f"Relative LCOE Change:   {lcoe_diff_pct:+.2f}%")


    def task8(self):
        """
        Calculate the Net Present Value (NPV) of the wind farm project.
        Assumes an initial investment in Year 0, and inflating revenues 
        and O&M costs in Years 1-20.
        """
        print(f"\nTask 8: Net Present Value (NPV) Calculation")
        
        # Financial parameters (Adjust energy_price_y0 if specified in your assignment)
        self.energy_price_y0 = 0.04 # Assume $0.04 / kWh --> taken from slide 25 of lecture 5
        self.inflation_rate = 0.03  # 3% annual inflation from lecture slides
        
        # Using 5D baseline values
        self.aep_kwh = self.aep_5d / 1000.0
        self.investment = self.capex_5d + self.bop_cost_5d
        
        # Initialize cash flows list with Year 0 (Negative Initial Investment)
        self.cash_flows = [-self.investment] 
        self.npv = -self.investment
        
        print(f"{'Year':<5} | {'Net Cash Flow ($)':<20} | {'Discounted CF ($)':<20}")
        
        for year in range(1, self.design_lifetime + 1):
            # Calculate inflated revenues and O&M costs for the current year
            revenue = self.aep_kwh * self.energy_price_y0 * ((1 + self.inflation_rate) ** year)
            om_cost = self.total_annual_om_5d * ((1 + self.inflation_rate) ** year)
            
            # Net cash flow
            net_cf = revenue - om_cost
            self.cash_flows.append(net_cf)
            
            # Discount the cash flow back to present value
            discounted_cf = net_cf / ((1 + self.discount_rate) ** year)
            self.npv += discounted_cf
            
            # Print output for the first 5 years and the last year to keep terminal clean
            if year <= self.design_lifetime: 
                print(f"{year:<5} | {net_cf:<20,.2f} | {discounted_cf:<20,.2f}")

                
        print(f"Total Project NPV: ${self.npv:,.2f}")

    def task9(self):
        """
        Calculate the Internal Rate of Return (IRR) numerically.
        IRR is the discount rate that makes the NPV exactly equal to zero.
        """
        print(f"\nTask 9: Internal Rate of Return (IRR) Calculation")
        
        # Helper function to calculate NPV for a given test rate
        def calculate_test_npv(rate):
            test_npv = 0
            for year, cf in enumerate(self.cash_flows):
                test_npv += cf / ((1 + rate) ** year)
            return test_npv
            
        # Check if project even breaks even at a 0% discount rate
        if calculate_test_npv(0.0) < 0:
            print("Project cash flows are entirely negative. IRR cannot be calculated.")
            return

        # Simple Bisection Method to find the root (NPV = 0)
        lower_bound = 0.00
        upper_bound = 1.00 # Assume IRR is below 100%
        tolerance = 1e-5
        
        for _ in range(100): # Limit iterations to prevent infinite loops
            guess_rate = (lower_bound + upper_bound) / 2.0
            current_npv = calculate_test_npv(guess_rate)
            
            if abs(current_npv) < tolerance:
                break # We found the IRR
            
            if current_npv > 0:
                # NPV is positive, meaning the test rate is too low
                lower_bound = guess_rate
            else:
                # NPV is negative, meaning the test rate is too high
                upper_bound = guess_rate
                
        self.irr = guess_rate
        
        print(f"Calculated IRR: {self.irr * 100:.2f}%")
        
        # Compare to baseline discount rate
        if self.irr > self.discount_rate:
            print(f"Conclusion: Project is PROFITABLE. (IRR > {self.discount_rate*100:.1f}%)")
        else:
            print(f"Conclusion: Project is NOT PROFITABLE. (IRR < {self.discount_rate*100:.1f}%)")

    def show_plots(self):
        """Show the plots"""
        plt.show()

assignment4 = assignment4()