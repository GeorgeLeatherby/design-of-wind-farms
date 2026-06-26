r E 

## **Praktikum** Praktikum **Design of Wind Farms** Design of Wind Farms 

**Lecture 5:** Lecture 5 **NREL LandBOSSE / Financial Analysis** NREL LandBOSSE / Financial Analysis 

**Samuel Kainz, Hadi Hoghooghi** Samuel Kainz Hadi Hoghooghi **Technische Universität München** Technische Universitat Munchen 

**2026** 

## **S llabus** Syllabus **y** 

|No. <br>~~|)~~|Week <br>~~|)~~|Date (Wed)<br>~~|)~~|9.30-10.15<br>~~LL~~|10.30-11.15<br>~~LL~~|10.30-11.15<br>~~LL~~|11.30-12.15|
|---|---|---|---|---|---|---|
|1<br>~~|)~~|14<br>~~|)~~|15/04/26<br>~~|)~~|Overview of Course<br>Lecture 1: Background and<br>Motivations<br>~~LL~~|Lecture 2: Development of a Wind Farm<br>Project<br>~~LL~~||Lecture 3: Wake Behavior, Wind Farm<br>Control<br>Assignment 1: Basics and Recapitulation|
|2<br>~~|)~~|15<br>~~|)~~|22/04/26<br>~~|) ~~|Lecture 4: Wake Models, FLORIS<br> ~~LL~~|Assignment 1: Solution<br>Assignment 2:Jensen’s Wake Model<br>and Wake Superposition in Wind Farms<br>~~LL~~||Tutorial 1:FLORIS Installation and Setup|
|3|16|29/04/26|Lecture 5_1: LandBOSSE|Tutorial 2:LANDBOSSE Installation and<br>Setup||Assignment 2: Solution<br>Assignment 3: Wind Farm Analysis Using<br>FLORIS|
|5|17|06/05/26|Lecture 5_2: Financial Analysis|Assignment 3:Solution||Assignment 4: Wind Farm Cost Analysis<br>Using FLORIS + LandBOSSE)|
|6|18|13/05/26|Lecture 6: Layout Optimization|Assignment 4: Solution||Assignment 5:Layout Optimization|
|7|19|20/05/26|Assignment 5: Solution||Final group assignment: Introduction,Finalizing Groups, Q&A||
|8<br>~~Fe~~|20<br>~~Fe~~|27/05/26<br>~~a CE~~|Final group assignment:Design Process, Q&A, Writing Report<br>~~CE~~||||
|9<br>~~Fe~~|21<br>~~Fe~~|03/06/26<br>~~a CE~~|No Class<br>~~CE~~||||
|10<br>~~Fe~~<br>~~ee~~|22<br>~~Fe~~<br>~~ee~~|10/06/26<br>~~a CE~~<br>~~ee~~|Final group assignment:Design Process, Q&A, Writing Report<br>~~CE~~<br>~~ee~~||||
|11<br>~~Fe~~<br>~~ee~~<br>~~a~~|28<br>~~Fe ~~<br>~~ee~~<br>~~a~~|08/07/26<br> ~~a CE~~<br>~~ee~~<br>~~a~~|No Class<br>Deadline:Electronic report submission until<br>Tuesday, 07/07/2026, 23:59h<br>~~CE~~<br>~~ee~~<br>~~cr~~||||
|12<br>~~ee~~<br>~~a~~|29<br>~~ee~~<br>~~a~~|15/07/26<br>~~ee~~<br>~~a~~|Final presentation –<br>8:30h<br>(Room<br>2701M<br>)<br>~~ee~~<br>~~cr~~||||



## **Agenda** Agenda 

# • **NREL’s Land-based Balance of System Systems Engineering (LandBOSSE)** 

- **LandBOSSE Example** 

- **Basics of financial analysis** 

## **NREL’s Land-based Balance of System** NREL’s Land-based Balance of System **Systems Engineering (LandBOSSE)** Systems Engineering (LandBOSSE) 

**LandBOSSE model is a tool for modeling the balance-of-system (BOS) costs of land-based wind plants includes:** 

- **All costs associated with installing a wind plant, such as permitting, labor, material, and equipment costs associated with site preparation, foundation construction, electrical infrastructure, and tower installation.** 

- **LandBOSSE, however, was designed to help users explore tradeoffs between innovative design scenarios while balancing the level of detail and speed required for model execution.** 

**Ref: [1]** 

”) = = = > s <i= ’ c 

# **Wind Plant Integrated Systems Design and Engineering Model (WISDEM)** 

**However, LandBOSSE is a part of other software called WISDEM** 

**Ref: NREL** 

> **-5-** * 

## **LandBOSSE: Open-source on GitHub** 

**Original code and documentation available at: https://github.com/WISDEM/LandBOSSE** 

**It can execute on macOS and Windows.** 

- **Original version does not allow for irregular layouts and writes outputs to EXCEL** 

- 

- => **In this** In this **Praktikum** Praktikum **we will work with an in** we will work with an in-house **house further developed version of** further developed version of **LandBOSSE** LandBOSSE! **!** 

- => **Available here:** Available here: **https://github.com/WindfarmDesigner/LandBOSSE Original documentation and more details available at: https://www.nrel.gov/docs/fy19osti/72201.pdf** 

**Ref: NREL** 

## **LandBOSSE:** LandBOSSE: **Installation and Operation Folder** Installation and Operation Folder 

- **Download the source code and copy it in a folder of desire (or clone it).** 

- **Open terminal, navigate to folder (using “cd”), type “pip install -e .”** _Note: “-e” only installs a pointer and the source code remains in the original folder. If you prefer a copy to your environment, leave out “-e”._ 

- **You might have to additionally install the** _**pytest**_ **package (“pip install pytest”)** 

- **Please use python version 3.10 – 3.12 (not tested above)** 

- **In the terminal / your IDE, import and execute the function** _**run_landbosse**_ **from** _**landbosse.main_function**_ **.** 

## **Example:** 

import os 

import numpy as np 

from landbosse.main_function import run_landbosse 

## # Inputs 

Turbine_coordinates = np.array([[0,0],[0,400],[0,800]]) # in [m] Substation_coordinate = np.array([[200,400]]) # in [m] Cable_Voltage = 30 # in [kV]. Available: 10,20,30,45,60 kV WriteExcel = False # set to ‘True’ if you additionally want EXCEL files as output Display = True # set to ‘False’ if you don’t want landbosse prints 

## # Run 

landbosse_results = run_landbosse(Turbine_coordinates, Substation_coordinate, Cable_Voltage, WriteExcel, Display) 

## **LandBOSSE Input and Output** _andBOSSE Input and Output 

- **The input is comprised of three parts:** 

   **1. Array voltage level, and turbine and substation coordinates specified when calling run_landbosse in landbosse.main_function. Additionally, you need to specify if you want to write EXCEL output files and see prints.** landbosse_results = run_landbosse( **Turbine_coordinates, Substation_coordinate, Cable_Voltage, WriteExcel, Display** ) 

   **2. Project data, which are .xlsx spreadsheets that contain sheets of data about components, equipment, crews and so on. There is always at least one, and maybe more, files of project data.** 

   **3. A project list which combines parameters that define projects with reference to the project data those projects use. There is only one file that has the project list.** 

**Turbine cost data** 

**Main input parameters** 

## **LandBOSSE Input Parameters** 

## • **Project list input** 

## **Focus on:** 

- **Total project construction time (months)** 

- **Turbine rating MW** 

- **Hub height m** 

- **Rotor diameter m** 

- **Fuel cost USD per gal** 

- **Wind shear exponent** 

## **Ignore (no impact):** 

   - **Number of turbines** 

   - **Turbine spacing** 

   - **Row spacing** 

   - **Road length adder** 

   - **Flag for user-defined home run trench length** 

- **Rated Thrust (N)** 

- **Line Frequency (Hz)** 

   - **Combined Homerun Trench Length to Substation (km)** 

- **Distance to interconnect (miles)** 

- **Interconnect Voltage (kV)** 

**Others: default values are good general guesses** 

## **LandBOSSE Input Parameters Specific Layout Designs** _ 4 i | 1 > a 

- **Original LandBOSSE does not accommodate specific layout designs.** 

- **Internally developed code allowing for individual layouts**  **turbines and substation coordinates are model inputs** 

- **Before executing “run_landbosse”, update coordinates and specify array voltage** 

- **For now: Cabling optimization based on minimum-span-tree hence minimized total cable length (not cost)** 

- **Care needs to be taken wrt substation! Must be considerately placed.** 

**==> picture [77 x 27] intentionally omitted <==**

**----- Start of picture text -----**<br>
Almost double<br>cabling costs!<br>**----- End of picture text -----**<br>


• **Originally, landbosse only wrote EXCEL** *) # **output files. You can still use this** rc 4 **option by setting “WriteExcel = True”,** i4 **although it is not recommended. Then, an output folder is created with a file** ci ff Cc **structure comprised of two parts:** — • s **The actual data output from the** — **model in the form of an .xlsx** ©) : **spreadsheet.** CG ©) • **All the input files that created the** i) **output data.** { Project 1D with serial Number of turbines Turbine rating MW Rotor diameter m Module Operation 1D c foundation_validation_1ea36foundation_validation_iea36 a3 3.37337 130120 FoundationCostFoundationCost FoundationFoundation foundation_validation_iea36 3 337 130 FoundationCost Foundation —_ foundation_validation_1ea36 3 3.37 130 SitePreparationCost Roads _ foundation_validation_iea36 a 3.37 130 SitePreparationCost Roads + foundation_validation_iea36 3 3.37 130 SitePreparationCost Roads m foundation _validation_iea36 3 3.37 130 SubstationCost Substation ‘ toundation_validationea36foundationfoundation_validation_iea36 _validation_lea36 333 3.37337337 130120130 collectoncostGridConnectionCostCollectionCost CollectionTransmissionCollection and ate **foundation_validation_iea** 3636 a3 3.14 **37 1** 23 **0 CollectionCost Collection** +) foundation_validation_iea36foundation _validation_iea36 33 3.373.37 130130 DevelopmentCostDevelopmentCost DevelopmentDevelopment foundation_validation_iea36 3 3.37 130 DevelopmentCost Development foundation_validation_iea36 3 2.37 130 DevelopmentCost Development C |foundation_vatidation_lea36foundation_validation_iea36 33 3.373.37 130130 ErectionCostErectionCost ErectionErection foundation_validation_iea36 3 137 120 ErectionCost Erection 

## **LandBOSSE Input and Output** 

- **Output in python is a dataframe listing all BoP costs of the analysed project.** 

## **LandBOSSE Output Parameters** 

## • **The output (dataframe and optional file in folder “output”)** 

## • **Foundation Cost** 

## • **Project Management** 

## • **Bonding** 

## • **Engineering Foundation and Collections System (includes met mast)** 

## • **Site Facility** 

## • **Construction Permitting** 

## • **Insurance** 

) a. • **Site Preparation Cost** : • **Sub station Cost** 1 <4 i i ‘ • **Grid Connection Cost** ©) a • **Collection Cost** C , . • < **Development Cost** • — **Erection Cost** c) • **Management Cost** a ©) a “s) • **Equipment rental** ao • A **Labor** <_ • **Materials** Ss =) • **Mobilization** rs • **Fuel** a t • **Construction Permitting** el, **-12-** , | | | | Wind Energy Institute 

**Note: The cost of turbines themselves and the cost of land should be added to your analyses.** 

## **Syllabus** Syllabus 

|No. <br>~~TT)~~|Week <br>~~TT)~~|Date (Wed)<br>~~TT)~~|9.30-10.15|10.30-11.15|10.30-11.15|11.30-12.15|
|---|---|---|---|---|---|---|
|1<br>~~TT)~~|14<br>~~TT)~~|15/04/26<br>~~TT)~~|Overview of Course<br>Lecture 1: Background and<br>Motivations|Lecture 2: Development of a Wind Farm<br>Project||Lecture 3: Wake Behavior, Wind Farm<br>Control<br>Assignment 1: Basics and Recapitulation|
|2<br>~~TT)~~|15<br>~~TT)~~|22/04/26<br>~~TT)~~|Lecture 4: Wake Models, FLORIS|Assignment 1: Solution<br>Assignment 2:Jensen’s Wake Model<br>and Wake Superposition in Wind Farms||Tutorial 1:FLORIS Installation and Setup|
|3|16|29/04/26|Lecture 5_1: LandBOSSE|Tutorial 2:LANDBOSSE Installation and<br>Setup||Assignment 2: Solution<br>Assignment 3: Wind Farm Analysis Using<br>FLORIS|
|5|17|06/05/26|Lecture 5_2: Financial Analysis|Assignment 3:Solution||Assignment 4: Wind Farm Cost Analysis<br>Using FLORIS + LandBOSSE)|
|6|18|13/05/26|Lecture 6: Layout Optimization|Assignment 4: Solution||Assignment 5:Layout Optimization|
|7|19|20/05/26|Assignment 5: Solution||Final group assignment: Introduction,Finalizing Groups, Q&A||
|8<br>~~Fe~~|20<br>~~Fe~~|27/05/26<br>~~a CE~~|Final group assignment:Design Process, Q&A, Writing Report<br>~~CE~~||||
|9<br>~~Fe~~|21<br>~~Fe~~|03/06/26<br>~~a CE~~|No Class<br>~~CE~~||||
|10<br>~~Fe~~<br>~~ee~~|22<br>~~Fe~~<br>~~ee~~|10/06/26<br>~~a CE~~<br>~~ee~~|Final group assignment:Design Process, Q&A, Writing Report<br>~~CE~~<br>~~ee~~||||
|11<br>~~Fe~~<br>~~ee~~<br>~~Po}~~|28<br>~~Fe ~~<br>~~ee~~<br>~~Po}tT~~|08/07/26<br> ~~a CE~~<br>~~ee~~<br>~~tT~~|No Class<br>Deadline:Electronic report submission until<br>Tuesday, 07/07/2026, 23:59h<br>~~CE~~<br>~~ee~~<br>~~tT~~<br>~~30hRoomarom~~||||
|12<br>~~ee~~<br>~~Po}~~|29<br>~~ee~~<br>~~Po}tT~~|15/07/26<br>~~ee~~<br>~~tT~~|Final presentation –<br>8:30h<br>(Room<br>2701M<br>)<br>~~ee~~<br>~~tT~~<br>~~30hRoomarom~~||||



# **Project Financial Analysis** Project Financial Analysis 

## **Basic Terms** Basic Terms 

## **Cash Flow (Rt).** 

- **Net balance of cash** moving into and out of a business at specific point in time. 

- Three types: operating, investing, and financing. 

- Problem: timing of costs and benefits in a cash flow series  discounting **!** 

## **Inflation Rates (i).** 

- Rise in price levels through increase in available currency and credit without proportionate increase in available goods and services of equal quality 

   - value of money changes over time 

- Cost and revenue can be expressed in 

   **1. “current” dollar** : actual CF in year it incurs, changes over time due to inflation **2. “constant” dollar:** would have been required if cost was paid in base year 

   - Difference: inflation (base year: cash flows are the same) 

## **Time Point / Periods.** 

- Base year (year to which all cash flows are converted) 

- Dollar Year (year to which base year results are converted and reported) 

- Analysis period vs. investment’s life span (often equal) 

Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Basic Terms** Basic Terms 

## **Discount Rates.** 

_“Time value is the price put on the time that an investor waits for a return on an investment. A dollar received today is worth more than a dollar received tomorrow because the dollar today can be invested to earn interest immediately. Conversely, a dollar received tomorrow is worth less than a dollar received today because the opportunity to earn interest on the dollar is lost.”_ 

- Discount rate = **measure of time value** , essential to calculate present value 

• Either includes effects of inflation (= **nominal discount rate** dn, current dollar analysis) or excludes it (= **real discount rate** dr, constant dollar analysis) Consistency throughout analysis! 

      - 𝟏+ 𝒅𝒏 ) = ¢ 𝟏+ 𝒅𝒓 ) ∙(𝟏+ 𝒊) 

- Not the same for all investors! Depend on rate of return, risk premium, planning horizon, interest rates, … 

   - varies from state to state, industry to industry, and company to company. 

- Cost of capital must be recovered by investor to warrant his investment. 

Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Basic Terms** Basic Terms 

## **Present Value.** 

• measure of **today’s value of revenues or costs in the future** 

**==> picture [456 x 63] intentionally omitted <==**

## **Annuity.** 

• When future cash flows are fixed in size and regularly occur over a specific number of periods 

**==> picture [414 x 66] intentionally omitted <==**

**==> picture [128 x 41] intentionally omitted <==**

Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Economic Measures** Economic Measures 

## **Net Present Value.** 

- One way to examine costs (cash outflows) and revenues (cash inflows) together 

- Evaluate investment features / decision 

- Form of streams (current or constant dollars) must be known to apply correct discount rate 

**==> picture [451 x 79] intentionally omitted <==**

## **Total Life-Cycle Cost.** 

- Costs incurred through ownership of an asset over its life span / period of interest 

- Considers all significant costs over life of the project discounted to base year 

**==> picture [627 x 99] intentionally omitted <==**

Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Economic Measures** 

**Total Life-Cycle Cost (cont.).** Simple example with nominal discount rate = 12% Project investment = $10,000 O&M cost in year zero = $1,300, inflating with i = 3% per year thereafter No salvage value, investment is not replaced, no taxes **Current Dollar** TLCC Evaluation Discounted Current Dollar Discounted Year Investment Investment O&M Costs O&M Costs 0 $ 10,000 $ 10,000 $ 0 $ 0 1 0 0 1,339 1,196 **nominal** 2 0 0 1,379 1,100 **discount rate** 3 0 0 1,421 1,011 4 0 0 1,463 930 5 0 0 1,507 855 NPV $ 10,000 $ 5,091 TLCC = $ 15,091 Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency **-19-** and Renewable Energy Technologies”, NREL/TP-462-5173 7] Wind Energy Institute 

Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Economic Measures** 

## **Total Life-Cycle Cost (cont.).** 

Simple example with nominal discount rate = 12% Project investment = $10,000 

O&M cost in year zero = $1,300, inflating with i = 3% per year thereafter No salvage value, investment is not replaced, no taxes 

recall: 

||||||(<br>)|¢<br>)|¢<br>)|
|---|---|---|---|---|---|---|---|
||**Constant Dollar**TLCC Evaluation||||1 + 𝑑𝑛=<br>(<br>)|1 + 𝑑𝑟∙(1 + 𝑖)<br>¢<br>)||
|||||||||
|Year|Investment|Discounted<br>Investment|Constant Dollar<br>O&M Costs|Discounted<br>O&M Costs|d𝑟=|1 + 𝑑𝑛<br>1 + 𝑖−1||
|0|$ 10,000|$ 10,000|$ 0|$ 0||||
|1|0|0|1,300|1,196|d𝑟= 8.74%|||
|2|0|0|1,300|1,100|**real discount rate**||**real discount rate**|
|3|0|0|1,300|1,011||||
|4|0|0|1,300|930||||
|5|0|0|1,300|855||||
|NPV||$ 10,000||$ 5,091||||
|TLCC = $ 15,091||||||||



Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Economic Measures** Economic Measures 

## **Levelized Cost of Energy.** 

_“The LCOE is that cost hat, if assigned to every unit of energy produced by the system over the analysis period, will equal the TLCC when discounted back to the base year.”_ 

**==> picture [159 x 53] intentionally omitted <==**

**==> picture [17 x 7] intentionally omitted <==**

**==> picture [161 x 55] intentionally omitted <==**

with Qn…energy output in year n, N…analysis period 

If the system output Q remains constant over time and considering one year as time period hence Q = AEP (Annual Energy Production), the equation reduces to 

𝑻𝑳𝑪𝑪 𝑳𝑪𝑶𝑬= 𝑨𝑬𝑷∙𝑨 

recall: A…Annuity 

Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Economic Measures** Economic Measures 

## **Levelized Cost of Energy (Cont.).** 

Neglecting taxes, assuming constant O&M costs per year, no financing, constant inflation rate, constant AEP, and no salvage value, we can write: 

𝑰 𝑶&𝑴 𝑳𝑪𝑶𝑬= 𝑨𝑬𝑷∙𝑨[+] 𝑨𝑬𝑷 with I…Initial Investment 

A = f(d)  discount rate in A can be nominal or real, depending on the analysis purpose. Typically: Short-term studies in current dollars, long-term studies in real dollars 

Cash Flow - Nominal Cash Flow - Real LCOE - Nominal LCOE - Real 

Year 

Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Economic Measures** Economic Measures 

## **Levelized Cost of Energy (Cont.).** 

Coming back to our **example** with TLCC = $ 15,091 Assuming AEP = 1000 units/a d = d n = 12% 

**==> picture [368 x 96] intentionally omitted <==**

Selling energy for $4.19 per unit in current dollars over the next 5 years  **investor recoups initial investment and annual O&M costs, and earns 12%** 

Repeating the exercise for constant dollars  LCOE = $3.85 per unit ( … and earns 8.74%) 

Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Economic Measures** Economic Measures 

So far: cost-based 

Now: **value-based** (considering earnings through selling energy) For a project to be profitable, the total earnings must be higher than the total cost. 

## **Internal Return Rate (IRR).** 

= discount rate that makes the net present value (NPV) of all negative and positive cash flows equal to zero in a discounted cash flow analysis. 

**==> picture [191 x 53] intentionally omitted <==**

**Solutions** : roots of polynomial of n[th] order 

 For higher order: graphically or numerically 

Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Economic Measures** 

## **Internal Return Rate (cont.).** 

|Year|Investment<br>Current Dollar<br>O&M Costs<br>Revenues<br>Cash flow<br>Discounted<br>Cash flow||
|---|---|---|
|0<br>1<br>2<br>3<br>4<br>5|$ 10,000<br>$ 0<br>$ 0<br>$-10,000<br>$-10,000<br>0<br>1,339<br>4,120<br>2,781<br>…<br>0<br>1,379<br>4,244<br>2,865<br>…<br>0<br>1,421<br>4,371<br>2,950<br>…<br>0<br>1,463<br>4,502<br>3,039<br>…<br>0<br>1,507<br>4,637<br>3,130<br>…||



function of d n 

Coming back to our example. 

Energy price: P = $4 per unit in year 0 Inflating at 3% per year 

 Here: graphical solution 

- up to dn = 14.3%, the project is profitable 

**==> picture [337 x 154] intentionally omitted <==**

**----- Start of picture text -----**<br>
4000<br>2000<br>Discounted net CF<br>0<br>IRR = 14.3%<br>-2000<br>0.03 0.06 0.09 0.12 0.15 0.18<br>Discount rate (-)<br>Net CF ($)<br>**----- End of picture text -----**<br>


Short et al., 1995, “A Manual for the Economic Evaluation of Energy Efficiency and Renewable Energy Technologies”, NREL/TP-462-5173 

## **Economic Measures** Economic Measures 

## **Profitability Index (PI).** 

𝑭 σ𝑵𝒏=𝟏 ~~CC)~~ 𝟏+ 𝒅𝒏[𝒏] ~~|~~ 𝑵𝑷𝑽 𝑷𝑰= = 𝟏+ 𝑰 𝑰 

- Compares payoff (PV of future cashflows) with initial investment 

- Measure of a project's or investment's attractiveness 

- To be profitable: PI ≥ 1.0 

In our example with dn = 12%: 

$𝟏𝟎, 𝟓𝟕𝟒 𝑷𝑰= $𝟏𝟎, 𝟎𝟎𝟎[= 𝟏. 𝟎𝟔≥𝟏]  profitable 

|Year|Discounted<br>Cash flow|
|---|---|
|0<br>1<br>2<br>3<br>4<br>5|$-10,000<br>2483<br>2284<br>2100<br>1931<br>1776|



https://www.investopedia.com 

