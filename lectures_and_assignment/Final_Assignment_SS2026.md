Wind Energy Institute Prof. Dr. **Carlo L. Bottasso** 

Technische Universität München 

## **Praktikum Design of Wind Farms** 

Dr. sc. Hadi Hoghooghi – hadi.hoghooghi@tum.de MSc. Samuel Kainz – samuel.kainz@tum.de 

## **Final Assignment (60%): Wind Farm Design** 

The final assignment of the Praktikum aims at _designing_ **two** wind farms with nominal capacities ranging from **45MW to 60MW** situated in advantageous locations - one in **Denmark** and one in **Bayern** - accounting for both medium and low wind speed conditions and _optimizing_ the layout of the wind farms to maximize the **Profitability Index (PI)** of the project. Students are expected to use _FLORIS_ and _LandBOSSE_ and are welcome to explore different ways to achieve the goal. 

Students will be organized into groups, with each group responsible for delivering a 12-minute presentation outlining their approach to the problem and presenting their corresponding results. It is expected that every group member will actively contribute to the presentation. Additionally, a report summarizing the main findings of the study should be submitted on Moodle by _23:59h on Tuesday, July 07, 2026_ . The report should not exceed 25 pages in length. 

Table 1: Specifications of the two selected areas for building wind farms. 

|**Item**|**Site 1**|**Site 2**|
|---|---|---|
|Location|Denmark|Bayern|
||55°15'48.06"N  9° 0'48.68"E; 55°15'41.73"N||
|Site coordinates|9° 4'4.78"E;<br>55°14'53.82"N  9° 3'30.66"E; 55°14'39.19"N|To be specified|
||9° 0'41.31"E||
|Area size|~ 5 km2|~ 5 km2|
|Nominal Capacity|To be specified|To be specified|
|Wind Speed Condition|Medium/High|Low|
|Wind Shear Exponent|0.17|0.20|
|Turbulence Intensity|12%|18%|
|Fuel Cost|9.5 USD/gal|7.5 USD/gal|
|Line Frequency|50Hz|50Hz|
|Standard Voltage|220 - 240 V|230 V|
|Interconnect Voltage|>100 kV|>100 kV|
|Distance to Interconnect*<br>(from the substations)|estimated based on grid maps|estimated based on grid maps|
|Road length adder|4 km|5 km|
|Recommended Hub Height|120 m|120 m|
|Rental Payment for Land|$15,000/MW-yr|$20,000/MW-yr|
|O&M Cost|0.012 $/kWh|0.012 $/kWh|
|Real Discount Rate|3.6%|2.5%|
|Design Lifetime of the Farm|20 years|20 years|
|Project Construction Time|12 months|12 months|
||At least 4 times of turbine tip|At least 1000m|
||(distance to residential areas)|(distance to residential areas)|
||Turbines can be installed only close to|Turbines can be installed only close to the|
|Installation Regulations**|the borders of green fields|side roads in the forest|
||Minimum distance to roads: rotor radius|Minimum distance to roads: rotor radius|
||plus the following buffer distances —|plus the following buffer distances —|
||Autobahn: 30m, Bundesstraße: 15m,|Autobahn: 30m, Bundesstraße: 15m,|
||Staatsstraße: 15m,Kreisstraße: 10m|Staatsstraße: 15m,Kreisstraße: 10m|



- Be careful about the units in LandBOSSE 

** The remaining regulations were discussed in the lectures. Additionally, it is advisable to research further regulations on the Internet to make reasonable assumptions. It is important to note that the chosen sites should not have any restrictions on installing wind farms. 

Wind Energy Institute Prof. Dr. **Carlo L. Bottasso** 

Technische Universität München 

**Note:** From the available array voltages, values can be freely chosen. The location of the substations should be placed reasonably (towards the plant center to minimize costs, but also considering land restrictions). The plant shall feed into the existing high-voltage grid (>100kV), and the distance to the interconnector shall be estimated using open-source grid maps (e.g., https://www.entsoe.eu/data/map/). 

The presentation should include the shapes of the sites' areas. Furthermore, for enhanced precision in location verification and distance measurement, students can create polygon files of the areas using Google Earth software. Portable versions of this software are available for free download and installation, facilitating easy access and utilization. 

The wind rose for Site 1 is provided in Table 2, and its coordinates are given in Table 1. For Site 2, you are required to select a suitable location within eligible areas in Bavaria (Bayern) and obtain its coordinates independently. You should then generate the wind rose for this location using the time series data from the New European Wind Atlas, covering the full available period (01/01/2005 to 31/12/2018). 

Table 2: Denmark (Site 1) windrose data. 

**==> picture [433 x 146] intentionally omitted <==**

**----- Start of picture text -----**<br>
||||||||||||||||
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|WD (bin center)|[º]|Scale (at 120m)|[m/s]|Shape [-]|Rel. Frequency|[%]|Plot with 10º discretization|
|30 0|9.79 8.28|2.31 2.09|14.71 6.09|GEHGN|1>10|E|20|--|2015n/s m/sm/s|ESG|E|-|-|5G10m/sns|
|60|8.72|1.89|6.16|N|0.06.|
|90|9.63|1.94|8.17|NW|NE|
|120|10.11|1.95|9.58|.04|
|150|8.34|1.90|6.05|
|180|8.94|1.91|5.34|
|w|
|210|10.76|1.91|7.27|
|240|11.71|1.97|8.00|
|270|11.36|2.05|14.6|
|300|10.68|2.06|7.78|sw|SE|
|330|8.96|1.93|6.25|Ss|

**----- End of picture text -----**<br>


Three reference turbines are available to buy for these two projects (click on the links to access most of the turbine data and check the attached EXCEL file for the Ct-curves). The key parameters of the turbines and their characteristics are as follows: 

Table 3: Reference turbines are available to buy for these two projects. 

**==> picture [445 x 146] intentionally omitted <==**

**----- Start of picture text -----**<br>
||||||||
|---|---|---|---|---|---|---|
|Item|Turbine 1|Turbine 2|Turbine 3|
|Name|IEA 3.4MW Reference|BAR_BAU- IEA_3.3MW|BAR_BAU_LSP_3.25MW|
|Rated Power|3370 kW|3300 kW|3250 kW|
|Specific Power|256 W/m|[2 ]|173 W/m|[2]|150 W/m|[2]|
|Rated Wind Speed|9.8 m/s|9.0 m/s|8.5 m/s|
|Rated TSR|8.2|8.9|9.4|
|Cut-in Wind Speed|3 m/s|4 m/s|4 m/s|
|Cut-out Wind Speed|25 m/s|25 m/s|25 m/s|
|Rotor Diameter|130 m|156 m|166 m|
|Hub Height|120 m|120 m|120 m|
|Control|Pitch Regulated|Pitch Regulated|Pitch Regulated|
|Cost Model Baseline|[*]|(LandBOSSE)|iea36_120|iea36_120|iea36_120|
|Price|$1.125 million per MW|$1.30 million per MW|$1.40 million per MW|

**----- End of picture text -----**<br>


* Parameters to be updated in LandBOSSE input (the thrust coefficients for the different turbine types are provided in the attached EXCEL table) 

Wind Energy Institute Prof. Dr. **Carlo L. Bottasso** 

Technische Universität München 

The electricity spot price depends on the market zone (Germany, Denmark), wind speed, and the annual average spot price. The latter changes over time due to market effects (geopolitics, regulation, catastrophes, economic growth, etc.) as shown in Figure 1. The dependency on wind speed is derived by linear regression of the annually normalized wind speed time series of each site and the corresponding spot price time series in the respective market zone between 2015 and 2018. Table 3 shows the project timeline, spot price functions, and annual average spot prices. 

Figure 1: Average spot market price over time, distinguished by market zone 

Table 4: Spot price in the electricity market during the lifetime of the projects. 

|||||**Spot price ($/MWh)**|**Spot price ($/MWh)**||||**Average spot price**<br>**A($/MWh)**|**Average spot price**<br>**A($/MWh)**|
|---|---|---|---|---|---|---|---|---|---|---|
|**Year**|**Site 1(Denmark)**|||||**Site 2(Bayern)**|||**Site 1**|**Site 2**|
|2020|||||||||Construction||
|2021|||||||||100.5|110.4|
|2022|||||||||249.8|268.5|
|2023|||||||||154.3|193.7|
|2024|||||||||74.3|96.9|
|2025|𝐬𝐩𝐨𝐭 𝐩𝐫𝐢𝐜𝐞=||||𝐬𝐩𝐨𝐭 𝐩𝐫𝐢𝐜𝐞=||||57.7|71.6|
|2026<br>2027|𝐀× [𝟏. 𝟐𝟑𝟓−𝟎. 𝟎𝟒𝟐𝟗𝟓~~(~~𝟏𝟏𝟎<br>𝐇𝐇<br>~~)~~<br>𝛂𝐬𝐡𝐞𝐚𝐫|||× 𝐖𝐒]|𝐀× [𝟏. 𝟏𝟒𝟓−𝟎. 𝟎𝟑𝟕𝟓𝟓~~(~~𝟏𝟏𝟎<br>𝐇𝐇<br>)<br>𝛂𝐬𝐡𝐞𝐚𝐫|||× 𝐖𝐒]|53.6<br>63.1|63.1<br>67.4|
|2028|||||||||51.2|59.1|
|2029|||||||||38.9|51.7|
|2030|||||||||35.9|47.0|
|2031-<br>2040|||||||||32.6|42.0|



_Note: HH = hub height; WS = wind speed at hub height_ 

Wind Energy Institute Prof. Dr. **Carlo L. Bottasso** 

Technische Universität München 

## **It is desirable:** 

1. The suitable wind turbine for each site. Show your analysis results and explain your reasons. 

2. The number of required turbines and the optimized layout of each site. Visualization of the flow field in the wind farms for your layouts and explaining the situations in the optimization process. 

3. AEP, capacity factor, farm efficiency, LCOE, cost breakdown, total investment cost, internal rate of return (IRR), and profitability index (PI) of the optimized wind farm layouts. Compare the results for all iterations in the optimization process. 

4. Compare LCOE and profitability index (PI) for two sites and explain the comparison. In addition to that, compare the estimated LCOEs with the literature. 

5. Repeat your analysis using the wake steering method for the final layouts, visualize the flow field, and compare all parameters you calculated in question 3 for the case of the final layout with and without wake steering. 

## **Approach guidelines** 

1. Identify suitable areas by taking into account the layout of existing wind farms and any other constraints present at the chosen locations. 

2. Estimate the required (possible) number of turbines based on power requirements and turbine specifications. 

3. Specify eligible areas for turbine installation, considering wind turbine wake behavior derived from the wind rose data. Design a preliminary layout adhering to wind farm design criteria, then optimize the layout by adjusting turbine locations to maximize efficiency. 

4. Conduct FLORIS simulations to optimize turbine placement and analyze wake effects on neighboring turbines. 

5. Utilize LandBOSSE analysis to estimate costs associated with the wind farm project, including installation, operation, and maintenance expenses. 

6. Compare the new optimized design with the previous layout to assess improvements in efficiency and cost-effectiveness. 

7. Iterate on the design until satisfactory results are achieved, refining turbine placement and layout based on simulation outcomes and cost estimates. 

8. Achieve a detailed characterization and understanding of the wind farm design, encompassing all constraints and limitations. This involves documenting the approach, presenting diagrams and tables outlining assumptions, wind farm layouts and rationale, optimization methodologies, capacity factor calculations, Annual Energy Production (AEP), wind farm efficiency metrics, investment costs, cost breakdown analysis, Levelized Cost of Energy (LCOE), Internal Rate of Return (IRR), and Profitability Index (PI). 

Technische Universität München 

Wind Energy Institute Prof. Dr. **Carlo L. Bottasso** 

## **Notes** 

1. Each group is required to work autonomously, devising unique methodologies and approaches to the task. 

2. Prioritize intelligent decision-making to minimize computational expenses while maintaining effective analysis. 

3. Evaluation of the final assignment will consider factors such as project significance and complexity, the sophistication of the approach employed, as well as the clarity, quality, and professionalism of both the presentation and the accompanying report. 

