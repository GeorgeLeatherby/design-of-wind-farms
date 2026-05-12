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
        self.Display = False # Display the results


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
        self.turbine_capex_3_turbines = total_capacity_mw * self.turbine_cost * 1e6
        self.total_investment = self.turbine_capex_3_turbines + self.bop_cost

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
            self.turbine_capex_3_turbines,     # Initial Turbine Cost
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
        self.capex_5d = copy.deepcopy(self.turbine_capex_3_turbines)
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
        For the case of question 3 (5D baseline), determine the internal rate of return
        (IRR) numerically and calculate the profitability index (PI) for an average
        electricity spot price of 41.8 $/MWh.
        """
        print(f"\nTask 8: IRR and Profitability Index (PI)")

        # Case of task 3 / baseline 5D
        electricity_price = 41.8 / 1000.0  # $/kWh
        aep_kwh = self.aep_5d / 1000.0
        baseline_n_turbines = 3
        baseline_capacity_mw = baseline_n_turbines * (self.rated_power_single_turbine / 1000.0)
        turbine_capex_baseline = baseline_capacity_mw * self.turbine_cost * 1e6
        initial_investment = turbine_capex_baseline + self.bop_cost_5d
        annual_revenue = aep_kwh * electricity_price
        annual_net_cf = annual_revenue - self.total_annual_om_5d

        # Cash flow series: year 0 investment, years 1..N net inflows
        self.cash_flows = [-initial_investment] + [annual_net_cf] * self.design_lifetime

        # NPV function used for numerical IRR search
        def npv(rate):
            total = 0.0
            for year, cf in enumerate(self.cash_flows):
                total += cf / ((1 + rate) ** year)
            return total

        # Numerical IRR (bisection)
        lower = 0.0
        upper = 1.0
        for _ in range(120):
            mid = 0.5 * (lower + upper)
            if npv(mid) > 0.0:
                lower = mid
            else:
                upper = mid
        self.irr = 0.5 * (lower + upper)

        # PI = PV(future net cash inflows) / initial investment
        annuity_factor = (1 - (1 + self.discount_rate) ** (-self.design_lifetime)) / self.discount_rate
        pv_future_inflows = annual_net_cf * annuity_factor
        self.pi = pv_future_inflows / initial_investment

        print(f"Electricity price: ${electricity_price:.4f}/kWh (41.8 $/MWh)")
        print(f"Initial investment: ${initial_investment:,.2f}")
        print(f"Annual revenue: ${annual_revenue:,.2f}")
        print(f"Annual O&M: ${self.total_annual_om_5d:,.2f}")
        print(f"Annual net cash flow: ${annual_net_cf:,.2f}")
        print(f"IRR (numerical): {self.irr*100:.2f}%")
        print(f"PI (at {self.discount_rate*100:.1f}% discount rate): {self.pi:.4f}")

        if self.pi > 1.0:
            print("Economic assessment: Project is attractive (PI > 1).")
        else:
            print("Economic assessment: Project is not attractive (PI < 1).")

    def task9(self):
        """
        Estimate the minimum number of turbines in a straight North-South line with
        5D spacing to achieve PI > 1. Compare LCOE and PI as turbine number grows.
        """
        print(f"\nTask 9: Minimum Turbine Number for PI > 1")

        electricity_price = 41.8 / 1000.0  # $/kWh
        annuity_factor = (1 - (1 + self.discount_rate) ** (-self.design_lifetime)) / self.discount_rate

        self.pi_vs_n = []
        self.lcoe_vs_n = []
        self.n_values = []

        min_n_for_pi_gt_1 = None

        for n_turbines in range(1, 101):
            self.x = [0.0] * n_turbines
            self.y = [i * 5 * self.D for i in range(n_turbines)]
            self.turbine_coordinates = np.array([[0.0, yi] for yi in self.y])
            self.pos_substation = np.array([[500.0, 0.5 * (self.y[0] + self.y[-1])]])

            self.task2(verbose=0)
            self.task3(verbose=0)

            aep_kwh = self.aep / 1000.0
            total_capacity_mw = n_turbines * (self.rated_power_single_turbine / 1000.0)
            turbine_capex_n = total_capacity_mw * self.turbine_cost * 1e6
            initial_investment = turbine_capex_n + self.bop_cost
            annual_revenue = aep_kwh * electricity_price
            annual_net_cf = annual_revenue - self.total_annual_om
            pi_value = (annual_net_cf * annuity_factor) / initial_investment

            self.n_values.append(n_turbines)
            self.lcoe_vs_n.append(self.lcoe)
            self.pi_vs_n.append(pi_value)

            print(f"N={n_turbines:2d} | LCOE=${self.lcoe:.4f}/kWh | PI={pi_value:.4f} | Annual Net CF=${annual_net_cf:,.2f} | AEP={aep_kwh/1e6:.2f} GWh | Investment=${initial_investment:,.2f} | Revenue=${annual_revenue:,.2f}")

            if pi_value > 1.0 and min_n_for_pi_gt_1 is None:
                min_n_for_pi_gt_1 = n_turbines

        if min_n_for_pi_gt_1 is not None:
            print(f"Minimum number of turbines for PI > 1: {min_n_for_pi_gt_1}")
        else:
            print("PI > 1 was not reached in the tested range (1 to 20 turbines).")

    def show_plots(self):
        """Show the plots"""
        plt.show()

assignment4 = assignment4()