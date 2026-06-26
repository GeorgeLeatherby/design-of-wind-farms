r? E 

## **Praktikum** Praktikum **Design of Wind Farms** Design of Wind Farms 

**Lecture 4:** Lecture 4 **Wake Models, FLORIS** Wake Models, FLORIS 

**Hadi Hoghooghi** Hadi Hoghooghi **Technische Universität München** Technische Universitat Munchen 

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
|10<br>~~Fe~~<br>~~ee~~|22<br>~~Fe~~<br>~~ee~~|10/06/26<br>~~a CE~~<br>~~ee a~~|Final group assignment:Design Process, Q&A, Writing Report<br>~~CE~~<br>~~a~~<br>~~ee~~||||
|11<br>~~Fe~~<br>~~ee~~<br>~~Pt~~|28<br>~~Fe ~~<br>~~ee~~<br>~~PtPF~~|08/07/26<br> ~~a CE~~<br>~~ee a~~<br>~~PF~~|No Class<br>Deadline:Electronic report submission until<br>Tuesday, 07/07/2026, 23:59h<br>~~CE~~<br>~~a~~<br>~~ee~~<br>~~PF~~<br>~~s30mRoomaro~~||||
|12<br>~~ee~~<br>~~Pt~~|29<br>~~ee~~<br>~~PtPF~~|15/07/26<br>~~ee a~~<br>~~PF~~|Final presentation –<br>8:30h<br>(Room<br>2701M<br>)<br>~~a~~<br>~~ee~~<br>~~PF~~<br>~~s30mRoomaro~~||||



## **Agenda** Agenda 

- **Wake Models** 

- **Wake Superposition Models** 

- **Overview on FLORIS Wake Models** 

- **FLORIS Examples** 

## **Wake Model Components** 

, 2 rt ii, ‘c = a 3SCc ‘ c S c **-4-** . 

**Ref: [1]** 

## **Velocity Deficit Models** 

- **Based on Gaussian wake** Gaussian wake **model, the velocity deficit in each model is represented:** 

**Hub height streamwise spanwise vertical velocity deficit standard deviation of the distribution Thrust coeff.** (=Uso **)** max = C(x) =1—,/1-—4>=8(k*x/D+—.,€) **Decays moving downstream** 

## **Velocity Deficit Models** 

## • **: Niayifar and Porte-Agel** 

**local turbulence intensity** 

**==> picture [83 x 14] intentionally omitted <==**

**The Gaussian model in FLORIS is only considered to be applicable in the far wake, which satisfies the condition, where kα and kβ are parameters tuned empirically.** 

**==> picture [366 x 13] intentionally omitted <==**

**==> picture [465 x 64] intentionally omitted <==**

- **Ishihara and Qian: an alternative correction** 

## **Wake-added Turbulence Models** 

- **Purely empirical wake-added turbulence model that relies on:** 

   - **The thrust coefficient alone in the near wake (defined as x/D < 3 for that case)** 

   - **The thrust coefficient and the ambient turbulence in the far wake** 

**Wake-added Turbulence** 

- **where the constant coefficients cc, ca, ci, and cd modulate the dependence on the scale (constant), axial induction factor, ambient turbulence intensity, and downstream distance, respectively.** 

tuning coefficients, k4, k5, and k6 

## **Wake Superposition Models** 

- **Lissaman: combining velocity deficits linearly** 

- **Superposition of energy deficits, rather than velocity or momentum, leading to a root-sum-squares formulation:** 

- **Maximum velocity deficit:** 

## **Jensen Wake Model** 

- **Formulated in the early 1980s, simple, very fast and easy to implement** 

- **where Ct is the thrust coefficient, rr is the rotor radius and k is the wake w** 

- **decay coefficient (kw = 0.1)** 

- **Suggested values for kw = 0.07 5 for on-shore and 0.04/0.05 for offshore** 

- **within a wind farm, the speed deficit at the n[th] turbine** 

- **The speed at the nth turbine, un, is then given as:** 

D is,=5) AUUx (- 1 c <= = x eXD 5 g-llevl : 2 /1-G c = 3 • **k* is the wake growth rate that** % 7 c 

## **Bastankhah Analytical Wake Model** 

- **A new analytical wake model; neglecting viscous and pressure terms in the momentum equation** 

   - **y and z are spanwise and vertical coordinates, respectively,** 

   - **z h is the hub height,** 

- **k* is the wake growth rate that need to specify one parameter (value of k*) for each case.** 

# **FLOw Redirection and Induction in Steady State** FLOw Redirection and Induction in Steady State **FLORIS** FLORIS 

ch 

## **Modeling Tools at NREL** 

**Increasing flow physics** 

FLORIS FAST.FARM 

WindSE SOWFA 

- **Control-oriented model** • **New code which overlays** • **Solves the steady/** • **Wind farm simulator DWM) wakes unsteady 2D/3D RANS based on large-eddy** 

- • **Runs in fractions of equations simulation** 

- **Runs in fractions of equations simulation seconds** • **Includes embedded FAST** • • 

- **models of turbines Adjoints included for Allows detailed** 

- • **Can be used to find large-scale optimizations investigation of wake optimal control settings** • **Runs on few cores, near physics, but requires and analyse across wind real time, allowing load** • **Runs in serial or in many cores and time to rose suite analysis parallel, in minutes run simulations** 

**All are (will be) available open source on www.github.com** 

**Ref: NREL** 

ip) = y _ 5, s . >) e YJé A . 3 • - a, | **-13-** . 

## **FLORIS: Controls-oriented Wind Farm Model** 

- **FLORIS (FLOw Redirection and Induction in Steady State) is an open-source framework, developed originally by the National Renewable Energy Laboratory (NREL) and TU Delft, which includes both control-oriented wake models as well as tools used for the design and analysis of wind farm control strategies.** 

- **Computationally inexpensive (<1s for 100 turbines)** 

**==> picture [250 x 104] intentionally omitted <==**

**----- Start of picture text -----**<br>
Models Tools<br>•  Wake models •  Visualization<br>•  Turbulence models •  Optimization<br>•  Turbine models •  Analysis<br>**----- End of picture text -----**<br>


• **FLORIS is open-source and shared freely on github.com at:** ——___— **https://github.com/NREL/floris** 

**Ref: [4]** 

## **Large Array Updates** Large Array Updates 

- **Initial implementation of FLORIS as an expanded multizone version of the Jensen wake deficit model, coupled to the Jimenez model of wake deflection** 

- **Issue: wake expansion was not affected by changes in control or turbulence** 

- **Gaussian wake deficit and velocity models of as options within FLORIS provided thrust and turbulence dependence, and this Gaussian model became the default wake model used within FLORIS** 

## **Counter-rotating Vortices in Wake Steering** Counter-rotating Vortices in Wake Steering 

- **An engineering model of wake steering, including these counter-rotating vortices, called curl model, is implemented into FLORIS in** 

- **Curled wake model is more computationally expensive than analytical models, such as the Gaussian model** 

- **Fast analytical models with low computational costs, which can be computed in fractions of a second, are very important for the suite of engineering processes in wind plant analysis, the design of wake control strategies, and layout optimization** 

- **To implement the flow physics observed in secondary steering without increasing the computational costs of wake modeling, a new Gauss-Curl Hybrid (GCH) model was implemented** 

   - **First modification, called yaw-added recovery** 

   - **Second modification is secondary steering** 

**Ref: [4]** 

— ©) > > c c)) <4 ip) a c ce am —) <¢ = =4 vy, el. **-16-** . 

## **Wake Models in FLORIS** 

- **Jensen (Park) Model – 0.0018 s** 

- **Multi-zone wake model – 0.0019 s** 

- **Gaussian wake model – 0.0025 s** 

- **Curl model – 1.6 s** 

**Ref: NREL** 

c 5 >, 5 = =< > ©) = e)) py ab ce c = : cD 

## **Wake Models – Gaussian** 

- **Analytical solution to the simplified linearized Navier-Stokes equations** 

- **Dependent on physical parameters that can be measured in the field** 

   - **Ambient turbulence intensity** 

   - **Shear** 

   - **Veer** 

- **Only 4 tuning parameters** 

- **Good for normal turbine operation** 

**Ref: NREL** 

: bi c - < = © c c)) C5 = 2— F ao cl, **-18-** . f 

## **Wake Models – Curl** 

- **Solves the linearized Navier-Stokes equations in time marching fashion** 

- **Dependent on physical parameters that can be measured in the field** 

   - **Ambient turbulence intensity** 

   - **Shear** 

   - **Veer** 

- **Only 2 tuning parameters** 

- **Good for wake steering analysis** 

**Ref: NREL** 

• **Wake is offset from** ( **centreline** . ci. =. F =< = • Cc> **Curl model deflection** • Cc=,2 ip) • ao **Wake rotation** Pa • **Secondary steering** cc’ = : 5 * el, **-19-** : | } | Wind Energy Institute 

## **Deflection Model** 

## • **Gaussian model deflection** 

- **Counter-rotating vortices** 

**Ref: NREL** 

i.C - | 8 30 ~>. os 'E 2 - Oo —S— iauw |. 10 Se | ° STE c of = Y -) 2 —" G-10 ‘s) ov DD = ‘2 @ -20 = = =} S =$ 1, al, **-20-** “ | | | 

## **Compare Wake Steering** 

- **Relative power difference 6D downstream of 2[nd] turbine** 

**Ref: NREL** 

) 2 . DD " c) a > — > = c)) n a = — Ss 3 v x 

## **Turbulence Models Turbine Model – Cp/Ct Tables** 

- **Wake expansion dependent on ambient turbulence intensity** 

- **Added turbulence due to turbine operation** 

   - **As Ct increases, wake expansion increases** 

- **Very important for investigating deep array effects (ongoing work)** 

- **Turbine represented as Actuator Disks** 

- **Generate Cp/Ct tables by:** 

   - _**FAST**_ **–Aeroelastic code** 

   - _**CCBlade**_ **– steady/state BEM coupled to FLORIS** 

**Ref: NREL** 

> **-21-** ” 

if) & -_— = re ti, A a; > ‘S FS) b rn Cc : x 

## **Heterogeneous Inflows** 

- **Models the atmospheric in flow as a heterogeneous field with spatially varying wind speed, direction, and turbulence intensity** 

   - **This improvement is now included by default, with homogeneous in flows being a special case of general heterogeneously defined in flows.** 

**SOWFA - yawed** 

**Homogeneous Heterogeneous FLORIS - yawed FLORIS - yawed** 

- **The gains in power from yawing the turbines is much better matched with the inclusion of secondary steering from GCH (Gauss-Curl Hybrid).** 

**Ref: [4]** 

**-22-** “- Y Wind Energy Institute 

## **Optimization** Optimization 

- **The FLORIS framework includes methods for design of wind farm control strategies as well as analysis.** 

- **Current update to FLORIS: robust methods for computing the dynamic optimum, by assuming uncertainty in measurements, as well as accounting for the dynamics of the yaw controller** 

- **The effects of wind direction and yaw position uncertainty resulting from dynamic wind conditions are modeled in FLORIS by including a distribution of wind directions and yaw off sets centered on the intended wind direction/yaw offset combination when calculating wind farm power** 

- **FLORIS users can provide their own probability distributions for wind direction and yaw uncertainty or rely on the default Gaussian distributions** 

**collaboration on analysis in a similar** (t) roof} a 800 **c** 4 600 0.95, Ss 400 z 0.90 —_ < 08s mo 200 F N c) 0.80 ; S : - | -200 0.75 i) —— Baseline ao 0 500 1000 1500 2000 0.70 + —*— Controlled= 5 e <= 1.054 S| 1.00 —— c 0.954 S 3 ~ 0.90} \ \ =. 5 50.85) a ° 5 9.20 [i ey **Ref: [4]** “ 0.754 \ yf 

## **Field Validation** 

- **The FLORIS framework includes methods for design of wind farm control strategies as well as analysis.** 

- **Often, FLORIS and field results are compared using a method called the energy ratio. The energy ratio function is included in FLORIS to facilitate open collaboration on analysis in a similar way as the open wake models.** 

**-24-** po 

Ls S 

## - » e . ; | Dm os **FLORIS Framework Modularization** 

**Ref: [4]** 

## in gm - a _ _ a 4 oe |_| a _ — _ 4 a _ =——_ Ve ig ai — a - 4 re —_ ee Ge i od **FLORIS: Open-source and Collaborative** 

**Available at:** SS) **https://github.com/NREL/floris** 

**Divided into two packages:** 

- **Simulation:** 

   - **Contains code for FLORIS models** 

- **Tools:** 

   - **Modules for interacting with FLORIS models and data** 

**Documentation and examples available at:** sss **https://floris.readthedocs.io/_/dow** CCccCcCcCcCcCccccccccCcCcCcCCCCCccss~ sss **nloads/en/latest/pdf/** 

- ee **http://floris.readthedocs.io/** SSSEEE **https://nrel.github.io/floris** 

**Ref: NREL** 

**,,,\floris-main\examples** 2 examples_control_optimization c: examples_emgaussexamples_control_types ) samples floating ii examples_get_flow — examples_heterogeneous ©) examples_layout_optimization = examples_multidim =<— examples_turbine -_ examples_uncertain _ rs) examples_visualizatperts examples_wied_data . inputs 2 inputs_floating 4 [= _convert_examples_to_notebooks Fs [= 001_opening_floris_computing_power - [= 002_visualizations - R: 005eesetting power 3a [B[@ 006.007_sweeping_variables getfarm_aep | [@ 008_uncertain_models RY [= 009_compare_farm_power_with_neighbor **-27-** ” Ye Wind Energy Institute 

## **FLORIS Installation Folder** 

**In the FLORIS installation folder, there are a couple of useful examples which are the main codes we use in this praktikum.** 

**\floris-main\floris\turbine_library** 

**You can add new turbine by having Power-Ct-Speed data** 

## **Example_1: Open and Calculate Power in** 4 , | gm i | _ 5 a as — q y | **FLORIS Tools module allows for easy and intuitive interaction with FLORIS models.** 

**All in python using open-source python modules.** 

## **001_opening_floris_computing_power.py** 

- **Line 17: import the FLORIS module** 

- **Line 22: create FLORIS interface** 

- **Line 25: define farm layout** 

- **Line 30: define wind directions and wind speeds** 

- **Line 55: calculate turbine power** 

- • **Line 56: calculate farm power** 

## _a1‘|—a **FLORIS Interface** |fo “Se oe —_ | i = wn “Ss —_ 

## **Many important input files should be defined in the interface file (.yaml)** 

## • **It should be noted that some of these parameters can be also defined in the code** 

**In the example the Annual Energy Production (AEP) of a wind farm using wind rose information stored in a .csv file can be calculated.** 4ay **006_get_farm_aep.py** ¢ Cc=• **Line 25: create FLORIS interface** D 4 ia • —_ **Line 29-31: define farm layout** ci ff • **Line 41: import time series** = • =< **Line 62: import the wind rose (.csv)** a ° a 21 |ws 0lwd 0 ‘<= 3 0 5 _— • + **Line 88: calculate AEP** cc)—_s 456 || 000 101520| ») 87 | **0** 2530 i) • **Wind rose defined** 90 | 00 4035 o 1 0 45 = **by three parameters:** 2|3 00 5055 = • **ws (wind speed)** 4|5 **0 6** 50 = 6| 0 = } • **wd (wind direction)** 7| 0 75 =. 8 0 80 i 9) 0 85 • **freq_val (frequency)** PO 0 90 x by | 0 95 v Total number of wind direction and wind speed combination: 1872 p2 | 0 100 Number of @ frequency bins: 545 B3 | 0 105 n_findex: 1327 b4 0 110 C AEP from- wind rose: 59.076 (GWh) b 0 

## **Example_2: Calculate Wind Farm AEP** 

**-30-** - 

**002_visualizations.py** if) Turbine Points c 1400 c 200 = q») woe@0 Li 600 400 200 Cc ° ° m0 x00 x00 1400 Turbine Points, Labels, and——_—Waking Directions7 1200 3re — a90—26007 ir4 . 2000 d i oy Cc 3 é _\yos B00 t / eo 00 : N,“e wt| 400 : *e,tee ? A c 200 3 on 4 ° S00 1000 1500 - - ‘ Horizontal Flow with 2000 1500 =, ~~. _ 1000 = 3% a 500 =. - — = = we -500 ct -1000 

| | | **Example_3: Visualizations** 17 import matplotlib.pyplot as plt 18 **This example initializes the FLORIS** 19 import floris.layout_visualization as 20 from floris import FlorisModel **software, and then uses internal** 21 from floris.flow_visualization import 22 23 **functions to run a simulation and** 24 fmodel = FlorisModel ("inputs/gch.yaml") 25 **plot the results.** 26 # Set the farm layout to have 8 turbines 

<= = > ') : j « = =f “4 4») 

## **Example_4: Optimization** 

**Perform yaw optimizations to investigate wake steering power gains.** 

## **004_optimize_yaw_aep.py** 

- **Line 54-60: create optimization object with min. and max. yaw angles** 

- **Line 62: perform yaw optimization** 

**Ref: NREL** 

## **References** References 

- **1) Nicholas Hamilton, Christopher J. Bay, Paul Fleming, et al. Comparison of modular analytical wake models to the Lillgrund wind plant, J. Renewable Sustainable Energy 12, 053311 (2020)** 

- **2) Alfredo Peña, Pierre-Elouan Réthoré and M. Paul van der Laan, On the application of the Jensen wake model using a turbulence-dependent wake decay coefficient: the Sexbierum case, Wind Energ. 2016; 19:763–776.** 

- **3) Majid Bastankhah, Fernando Porté-Agel, A new analytical model for wind-turbine wakes, Renewable Energy 70 (2014) 116-123.** 

- **4) Paul Fleming, Jennifer King, Christopher J. Bay, Eric Simley, Rafael Mudafort, Nicholas Hamilton, Alayna Farrell, and Luis Martinez-Tossas, Overview of FLORIS updates, Journal of Physics: Conference Series 1618 (2020), 022028.** 

