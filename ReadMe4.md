## Asignment 4
Working with Floris and Landbosse.


### Task 1
![Windrose Assignment 1](images/assignment4_task1_windrose.png) \
5° discretizations steps for wind direction.


### Task 2
For task 2 I defined a second windrose object with a 1° discretizatino step for the wind directions and changed all requested parameters in the project_list.xlsx. One value I calculated by hand was the rated thrust.

$$T = 0.5 \cdot \rho \cdot A \cdot V^2 \cdot C_t$$
$$T = 0.5 \cdot 1.225 kg/m³ \cdot 13,273.23 m² \cdot 96.04 m²/s² \cdot 0.8068$$

Result: The rated thrust is approximately $630\text{ kN}$.

I choose a cable setup with a single cable running from the substation to the middle turbine and then a cable each to the northern and southern turbine.

AEP: 57012.82 kWh \
AEP no wake: 57814.68 kWh \
Cp wind farm: 0.6437 \
Efficiency: 0.9861 % 


### Task 3

When executing landbosse with the given data I received:
- project_id: foundation_validation_iea36_120
- project data: input\project_data\iea36_120_project_data.xlsx
- Annual AEP: 57,012,816 kWh
- Total BOP Cost: $8,540,274
- Total Investment (CapEx): $21,683,274
- Total Annual O&M (OpEx): $1,114,405

LCOE: $0.0475 / kWh

### Task 4
LCOE Comparison:
- My Calculated LCOE:    $0.0475 / kWh
- IRENA (2023 Avg):        $0.0330 / kWh
- Lazard (2024) Range:      $0.027 - $0.075 / kWh

IRENA stands for International Renewable Energy Agency. The cited value is an industry average and stems from their published report in 2023: https://www.irena.org/Publications/2024/Sep/Renewable-Power-Generation-Costs-in-2023 , last accessed on 12.05.2026.

Lazard is a firm active in asset management and financial advisory. They issued a report about renewable energy in 2024 defining a typical range of LCOE: https://www.lazard.com/media/xemfey0k/lazards-lcoeplus-june-2024-_vf.pdf , last accessed on 12.05.2026.

Pie chart breakdown of types of costs when building a wind farm.
![Pie chart breakdown of types of costs](images\assignment4_task4_piechart.png)

### Task 5

I re-ran floris and landbosse for 8D spacing. Because of OOP code architecture I could reuse the functions task2 and task3. With introducing a verbosity param I could silence their terminal prints for recalculations.

- AEP 5D: 57.0128 GWh | AEP 8D: 57.4287 GWh
- Relative AEP Change: +0.73%
- LCOE 5D: $0.0475/kWh | LCOE 8D: $0.0474/kWh
- Relative LCOE Change: -0.34%
- Observation: Increasing spacing reduced wake losses, increasing AEP.
- Observation: AEP gains from reduced wakes outweighed higher cabling costs, decreasing LCOE.


### Task 6
A dropping discount rate means  future revenues are discounted less heavily, while intial costs are not affected, therefore reducing the LCOE.

- Original Discount Rate: 4.0%
- New Discount Rate:      3.6%
- LCOE (Baseline):        $0.0475/kWh
- LCOE (New Rate):        $0.0465/kWh
- Relative LCOE Change:   -2.07%


### Task 7
This simulation is built around a small farm of only 3 turbines. In reality wind farms are often much larger (often 10+ turbines) and distribute the upfront Balance of Plant (BoP) costs—such as the substation, primary grid connection, and access roads—across a much larger energy output, significantly driving down the LCOE. Other reasons not accounted for are fluctuating energy prices and government subsidies.

### Task 8
For task 8 it is necessary to calculate the cash flows for each year. 
- Electricity price (averaged): $0.0418/kWh (41.8 $/MWh)
- Initial investment: $21,683,274.29
- Annual revenue: $2,383,135.72
- Annual O&M: $1,114,405.06
- Annual net cash flow: $1,268,730.66
- IRR (numerical): 1.55%
- PI (at 4.0% discount rate): 0.7952

Economic assessment: Project is not attractive (PI < 1).


### Task 9
N= 3 | LCOE=$0.0475/kWh | PI=0.7952
