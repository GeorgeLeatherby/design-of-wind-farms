r E 

## **Praktikum** Praktikum **Design of Wind Farms** Design of Wind Farms 

**Lecture 2:** Lecture 2 **Development of a Wind Farm Project** Development of a Wind Farm Project **Hadi Hoghooghi** Hadi Hoghoog? **Technische Universität München** Technische Universitat Munchen 

**2026** 

## Syllabus 

|No. <br>~~|~~|Week <br>~~|~~|Date (Wed)<br>|9.30-10.15<br>~~Li~~|10.30-11.15<br>~~Li~~|10.30-11.15<br>~~Li~~|11.30-12.15|
|---|---|---|---|---|---|---|
|1<br>~~|~~|14<br>~~| ~~|15/04/26<br>|Overview of Course<br>Lecture 1: Background and<br>Motivations<br> ~~Li~~|Lecture 2: Development of a Wind Farm<br>Project<br>~~Li~~||Lecture 3: Wake Behavior, Wind Farm<br>Control<br>Assignment 1: Basics and Recapitulation|
|2|15|22/04/26|Lecture 4: Wake Models, FLORIS|Assignment 1: Solution<br>Assignment 2:Jensen’s Wake Model<br>and Wake Superposition in Wind Farms||Tutorial 1:FLORIS Installation and Setup|
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

# • **Development of a Wind Farm Project** 

## • **Offshore Wind Farms** 

## **Main Elements of The Development of A Wind Farm Project** 

   - Technical and commercial issues 

   - Environmental considerations 

   - Dialogue and consultation 

- **Wind farm development phases:** 

- **Initial site selection** 

- **Project feasibility assessment** 

- **Preparation and submission of the planning (permitting) application** 

- **Construction** 

- **Operation** 

- **Decommissioning and land reinstatement** 

# **Initial Site Selection** Initial Site Selection 

## Wind Measurement Equipment 

• **For site assessment:** site assessment - **Meteorological masts (cup anemometers and wind** - Meteorological masts **vanes, sensors for pressure, temperature, humidity, …)** - **SODAR (Sonic Detecting And Ranging)** = - SODAR - is - **LiDAR** LIDAR **(Light Detection And Ranging)** • **Wind Atlas for greater region** Bil: Wind atlas **(not for detailed site examination)** • **Wind measurements also used in operation and** Ss **performance** performance **evaluation** evaluation operation Met mast (80m) Wind vane >». lie 

**==> picture [171 x 76] intentionally omitted <==**

**----- Start of picture text -----**<br>
LiDAR<br>||<br>(source: www.offshorewind.biz)<br>**----- End of picture text -----**<br>


Cup anemometer 

(source: www.sgurrenergy.com) 

(source: www.wind-pgc.com) 

## **Wind Direction Distribution** Wind Direction Distributi 

• + **Wind rose** Wind rose **diagram (speed, direction and frequency)** 

- **Important for farm siting and layout optimization** 

**(La Guardia, NY, source: http://www.breeze-software.com)** 

**(30 year data for April in Fresno, CA, source: http://www.wcc.nrcs.usda.gov/)** 

us) • = **No local data available**  **wind atlases for resource estimate** S ny . • La, **Open-source for Europe: New European Wind Atlas (NEWA),** New European Wind Atlas (NEWA), So **available via** i **https://map.neweuropeanwindatlas.eu/** c _— • **Base: 30 years of mesoscale simulations (resolution: 3 km, 30 min)** • **Downscaling with linearized** Ss alceland / % Norway, **microscale model (50 m grid)** • **Available information: wind resource,** 5 ie Denmark **site suitability, wind variability,** 4 Oe United N= Lithuania = **wind power predictability, etc.** \, oeq ve2|: Belgium Poland v ¥ France Switzerland Austria **at different heights** San Marino Serbia 3 Romans 4 Andorra) Republic of North Gibraltar, = 2 Portugal Spain tr hen **Sources: https://map.neweuropeanwindatlas.eu/;** -8* | b | Wind Energy Institute 

**U (m/s) @ 100m** 

## **New European Wind Atlas** New European Wind Atlas 

- **-** 

- **Wind roses are created using time** time-series **series (long-term records) of anemometer data (wind speed and direction)** 

**Sources: https://map.neweuropeanwindatlas.eu/; https://www.neweuropeanwindatlas.eu** —_—_—_————— 

## **New European Wind Atlas** New European Wind Atlas 

- **MESO time-series can be downloaded for period 2005 – 2018** 

- **NetCDF-File (.** NC **nc) can be easily processed with MATLAB functions** _**ncinfo**_ **and** _**ncread**_ 

- **Processing with FLORIS easiest by creating .csv** .CSV **file with wind resource information** 

• **Example .nc to .csv conversion using MATLAB:** _WS10 = ncread("Kastrup.nc","WS10"); WD10 = ncread("Kastrup.nc","WD10"); KastrupTS = table(WS10,WD10); writetable(KastrupTS,“KastrupTimeSeries.csv");_ 

- **Shear exponent can be calculated using data from different heights** 

- **Turbulent Kinetic Energy (TKE) and Turbulence Intensity (TI):** 

**==> picture [164 x 34] intentionally omitted <==**

## Influence of Wind Data Binning on Simulation Results Simulation Results 

- **Discretization effects on wind rose and simulation results:** 

   - **The resolution of wind speed and wind direction bins affects the shape of the wind rose.** 

   - **When reading data with software like FLORIS, coarse discretization can alter predicted flow patterns and power output.** 

   - **Typical practice:** 

      - **Wind direction: bins of up to 5°** 

      - **Wind speed: bins of up to 1 m/s** 

      - **Finer discretization improves accuracy but increases computational cost.** 

## **Weibull Distribution to Compute AEP** Weibull Distribution to Compute AEP 

> **Annual energy production:** Annual energy production: 𝑉𝑜𝑢𝑡 𝐴𝐸𝑃 = 𝑌 𝑃 𝑉 𝑑𝑉 ( )𝑓W AEP = y| න𝑉 " 𝑖𝑛 P(V) fy dV **with turbine power curve** P 𝑉 **and** 𝑌 = **8760 h/year** Y= P(V) 

**==> picture [350 x 314] intentionally omitted <==**

**----- Start of picture text -----**<br>
Weibull<br>Power curve<br>distribution ( 𝑓W [)]<br>P ( )<br>fw P(V)<br>P<br>r _ ——<br>|<br>V<br>V V V<br>cut in r cut out<br>—_—— or”<br>Region I Region II - constant  Region III - constant<br>TSR strategy power strategy<br>**----- End of picture text -----**<br>


## Weibull Distribution Weibull Distribution 

Probability distribution function, used to describe the probability of occurrence of a certain wind speed 

• * Cumulative Cumulative probability function (i.e. probability that V V<VY < 𝑉0[): ] 𝑉 Vo 0 𝑘 𝑉 ′ 0 𝐹 𝑉 = 𝑉 𝑑𝑉′ = 1 − − FwlVo) 𝑊 0 𝑓𝑊 ’ ’ exp ~~Vo~~ “ න 𝐶 = | fw(V dV" = 1 - exo( ~~-()~~ ) 0 0 • Probability density density function: 𝑘−1 𝑘 𝑉 𝑉 0 0 𝑉 = 𝑘 − 𝑓 f(Vo) 𝑊 0 ~~vi?~~ 𝐶𝑘 exp ~~Vo~~ 𝐶 k = ~~“t~~ el ~~(=)~~ with 𝑘 k shape shape parameter of the Weibull function, 𝑉𝑎𝑣𝑒 𝐶 C = ~~=—*—~~ scale scale parameter of the Weibull function [m/s], 𝛤 r(1+1/k) (1+1/𝑘) 𝑉 Vo 0 wind speed [m/s], 𝑉ave average wind speed [m/s] and Vave Γ r'(-) (∙) gamma function ( 𝛤 r'(z) 𝑧 = = ׬ J, 0∞ 𝑥 x?-1e*dx 𝑧−1𝑒−𝑥𝑑𝑥 ) • For 𝑘 k =2 (typical value for many locations): Rayleigh Distribution Rayleigh Distribution 

## **Capacity Factor** 

## **Power plants do not work at full power at all times Wind turbines:** 

- **Environmental variability (wind and air density)** 

- **Availability (fraction of time WT is able to produce electricity, i.e. not down for scheduled or unscheduled maintenance) (typically > 95%)** 

> . **: Capacity factor** Capacity factor **(produced energy in given period) = (capacity factor)** (capacity. factor) *** (theoretical max energy) (theoretical max energy) =  (nameplate power) * (period length) ▼Wind (source: IEA)** 100% 

> **Capacity factor:** Capacity factor: 1 * i" °° | a 𝐴𝐸𝑃 𝐶𝐹 = CF = —— 𝑌 — ∙ 𝑃𝑟 T an +s———— Y-P, som Ce ) 0 0.2 .2 < 𝐶𝐹 < 0.6 Po jennfoowman[to]| a) < CE < 0.6 .wots th coma |of 

> **Capacity factors for** :a **various technologies** 5 a es ▶ ee @ @ tH fe GaN og H @ BS 8 82 SQ Be GN a 5 0 | **(source: en.openei.org)** 2° © g & 8 § go 2 3 § & § 8 B 22 aE ye Es § as 

## Specific Power Specific Power 

𝟏 𝟑 3) 𝑷 Pr/ 𝒓ൗ𝑨 Rated power: 𝑷𝒓 = ~~=~~ Rated wind speed 𝑽 V.= 𝒓 = ~~i~~ 𝟏 𝟐[𝝔𝑨𝑽][𝒓𝟑][𝑪][𝑷][𝐦𝐚𝐱] 𝟐 𝝔 𝑪𝑷𝐦𝐚𝐱 • > 𝑪 Cp, 𝑷𝐦𝐚𝐱 limited by physics limited by physics E 3 0 CPmax • 𝑷𝒓 * To decrease To decrease 𝑽 V, 𝒓 ⇒ reduce specific power (power loading) => reduce specific power (power loading) *"/, ൗ𝑨 𝑃 p 𝑃 𝑟 Increasing A yor 𝑉 , Decreasing 𝑽𝒓 G— 𝑉 | 𝑟 More time spent in region III at full power, increased capacity factorincreased capacity factor increased capacity 

More time spent in region III at full power, increased capacity factorincreased capacity factor increased capacity factor 

- Correlation between Capacity Factor and Correlation between Capacity Factor and * . 

- Specific Power Specific Power 

(Source: M. Bolinger et al., 2019) 

- Levelized Cost of Electricity (LCOE) Levelized Cost of Electricity (LCOE) 

Levelized cost of electricity (LCOE) is defined as the price at which the generated electricity should be sold for the system to break even at the end of its lifetime. 

A simple formulation for called sLCOE can be written as follows: 

> 𝒔𝑳𝑪𝑶𝑬 SLCOE = __= (Rated 𝑹𝒂𝒕𝒆𝒅 Capacity 𝑪𝒂𝒑𝒂𝒄𝒊𝒕𝒚 × x 𝑰𝒏𝒗𝒆𝒔𝒕𝒎𝒆𝒏𝒕 Investment Cost 𝑪𝒐𝒔𝒕 xCRF)+(O&M ×𝑪𝑹𝑭 +(𝑶&𝑴 𝑪𝒐𝒔𝒕 Cost XAEP ×𝑨𝑬𝑷 + + … ... ) ) 

> 𝑹𝒂𝒕𝒆𝒅 Rated 𝑪𝒂𝒑𝒂𝒄𝒊𝒕𝒚 Capacity × x 𝑪𝒂𝒑𝒂𝒄𝒊𝒕𝒚 Capacity Factor 𝑭𝒂𝒄𝒕𝒐𝒓 × x 𝟖𝟕𝟔𝟎 8760h 𝒉 Capital Recovery Factor: A capital recovery factor is the ratio of a constant annuity to the present value of receiving that annuity for a given length of time. 

𝒊 𝟏 + 𝒊 𝒏 𝑪𝑹𝑭 CRE = ~~(1 + i)"~~ 𝒏 − 𝟏 + 𝒊 𝟏 ~~Gap~~ i = discount rate,  n = project lifetime (e.g. 20 years) 

## **Vertical Wind Profile (Shear)** 

**Wind speed increase with height within the atmospheric boundary layer Strong effect on power** power **production** production **and fatigue** fatigue **loading** loading w **Profile models:** In(z/20) e • ° ; : U(z) = U(z,) ~~——~~~ **Logarithmic (derived from BL theory):** - Logarithmic (z) (z,) In(z,./20) (a4 • **Power law (flat plate, but also empirical):** M * Power law U(z) = U(z;,) ~~(=)~~ zr 𝒛𝒓 **= reference height** 𝒛𝟎 **= surface roughness length (crops, trees, buildings, waves, …) Low** 𝜶 **= wind shear (power law) exponent, depends on stability, terrain features, wind speed, … (typically 0.2 on-shore, 0.14 off-shore) Normal Wind Profile (NWP):** 𝒛𝒓 = 𝒛𝐡𝐮𝐛; 𝜶= 𝟎. 𝟐 **High** • **Actual wind can be seen as superposition of vertical shear and** superposition of vertical shear and 7 / V1 /; _ — bse **turbulent fluctuations** turbulent fluctuations ely | | 

## **IEC Wind Classes** 

**Wind model used for design and** design and **certification of wind turbines** w **IEC 61400-1 defines:** - ; **Annual average wind speed (Vhub)** - **Reference wind speed or 10 min. mean with 50-year return period (Vref)** - : - Reference wind speed - **Turbulence intensity** Turbulence intensity **(Iref at hub height and 15 m/s)** 3 - **Extreme 50-year gust (1.4 Vref)** - **… IEC 61400** IEC **: International Standard** 61400 **published by the International Electrotechnical Commission For turbine certification, a large number of design load cases** design[load][cases] **(DLCs) for different wind conditions are simulated** 

**(turbulence models, source: Wind Energy Handbook, 2[nd] Ed.)** 

Class I II III S ~~Sees a~~ Vhub (m/s) 10 8.5 7.5 ~~Saas~~ Vref (m/s) 50 42.5 37.5 Values ~~SSS oaoas,~~ A Iref 0.16 specified by ~~ee ee~~ designer B Iref 0.14 ~~Ss~~ C Iref 0.12 ~~a~~ 

## **Initial Site Selection** Initial Site Selection 

**Typical separation distances for medium sized wind turbines** 

wa § 3 

## **Project Feasibility Assessment** Project Feasibility Assessment 

**Once a potential site has been identified then more detailed, and expensive, investigations are required in order to confirm the feasibility of the project.** 

**It is not generally considered acceptable in complex terrain to rely on the estimates of - wind speed made during the initial site selection but to use the Measure** Measure **Correlate** Correlate- **Predict** Predict **(MCP)** (MCP) **technique to establish a prediction of the long-term wind resource.** 

**MCP requires the installation of a mast** mast **at the wind farm site on which are mounted anemometers and a wind vane.** 

- **If possible one anemometer is mounted at the hub** hub **height** height **with others lower to allow wind** wind **shear** shear **to be measured.** 

- **-** 

- **Measurements are made over at least a six** six-month **month period.** 

## **Micrositing and Site Investigations** Micrositing and Site Investigations 

**In addition to MCP, design** design **software** software **package** package **to investigate the performance of a number of potential turbine layouts.** 

- **Two common models:** • - **Wind** Wind **Atlas** Atlas **Analysis** Analysis **and** at • **Application Program (WAsP) and MSMicro/3** 

- * Application Program (WAsP) and MSMicro/3 ray • **Calculate wind** wind flows **flows over a site** ay of MN 

- • **Other constraints such as turbine** turbine **separation,** YS Pea: **terrain** terrain **slope, wind turbine noise, radar** separation **and land** J - aoe ISDE slope wind turbine noise radar and land (gsMZeH, 

- **ownership** ownership **boundaries** boundaries **may also be applied** . PE © 0.00- 300.00 Wim’2 @ 900.00 -1200.00 Wim’2 

- • * **3** 3D **D virtual** virtual **reality** reality techniques **techniques** © 600.00 900.00 Win? 1500.00 1800.00 Wine 

Source: Wind Energy Handbook 

**Investigation:** 

- **Careful assessment of existing land use** 

- **Ground conditions (turbine foundations, access roads and construction areas)** 

## **Public Consultation and Preparation;** Public Consultation and Preparation; **Submission of the Planning Application** Submission of the Planning Application **Informal public consultation: local** local **community,** community, **organisations,** organisations, **environmental** environmental **societies** societies **and** and **wildlife** wildlife **trusts** trusts 

**The purpose of a wind farm Environmental Statement may be summarised as to:** 

- **Physical characteristics of the wind turbines and their land-use requirements** 

- **Environmental character of the proposed site and the surrounding area** 

- **Environmental impact of the wind farm** 

- **Measures which will be taken to mitigates any adverse impact** 

- **The need for the wind farm and provide details to allow the planning** 

**Topics covered in the Environmental Statement:** 

- **Policy framework** 

- **Site selection** 

- **Designated areas** 

- **Visual and landscape assessment** 

- **Noise assessment** 

- **Ecological assessment** 

- **Archaeological and historical assessment** 

- **Hydrological assessment** 

- **Interference with telecommunication systems** 

   - **Safety** 

   - **Traffic management and access construction** 

   - **Electrical connection** 

   - **Economic effects on the local economy** 

   - **Decommissioning** 

   - **Mitigating measures** 

   - **Non-technical summary** 

- **Aircraft safety and interference with radars** 

: rh E 3 5 

- **Landscape and Visual Impact Assessment** landscape and Visual impact Assessment 

- **Landscape character assessment (including landscape policy and designation)** 

- **Design and mitigation** 

- **Assessment of impacts (including visibility and viewpoint analysis)** 

- **Shadow flicker** 

**Wind farm of six 660 kW turbines in flat terrain** 

Source: Wind Energy Handbook 

> -23- 

## **Landscape Character Assessment** Landscape Character Assessment 

- **The fundamental step in minimising the visual** visual **impact** impact **of a wind farm is to identify an appropriate site and ensure that the proposed development is in harmony** harmony **with** with **the** the 

- 7) **location** location. **.** = S i] 

- i. —, ees Li, ——. > ii} iae 2 ~ | Ss MS **Wind farm of 600 kW turbines, Tarifa, Spain. Wind farm of 700 kW wind turbines located along coast.** Source: Wind 

- | Energy Handbook 

Source: Wind Energy Handbook 

## **Design and Mitigation** Design and Mitigation 

- **Lower speed** speed **of** of **rotation** rotation **is more relaxing to the eye** 

- * **Tower** Tower **heights** heights **and tower** tower **martials** martials • **Turbine color** 

- * Turbine color 

- **The layout** layout **and design of the wind farm** 

- **Associated ancillary** ancillary **structures** structures **required (substation)** 

- * **Roads** Roads 

• 

**…** 

## **Cameron Ridge in California, USA** 

Source: Wind Energy Handbook 

= e i. 

## **Assessment of Impact** Assessment of Impact 

- **A major part of the Environmental Statement is the assessment** assessment **of** of **landscape** landscape **and visual** visual **impact** impact 

- **Viewpoint analysis** • 

- * Viewpoint analysis 

   - **Sensitivity of the viewpoint (residential/industrial)** 

   - **Magnitude of the change of view** 

**Example of wire-frame showing visibility of three wind farms.** 

E aa : 

Source: Wind Energy Handbook OO https://www.windenergie-hofoldinger-forst.de/informieren/ 

## **Shadow Flicker** Shadow Flicker 

- * **Shadow** Shadow **flicker** flicker **is the term used to describe the stroboscopic effect of the shadows cast by rotating blades of wind turbines when the sun is behind them.** • **– The frequencies that can cause disturbance are between 2.5 20 Hz** 

- • **The effect on the human** human **eye** eye-brain **brain is the same as that caused by changes in intensity of an incandescent electric light due to variations in network voltage** 2.5—20 Hz 

- **from a wind turbine** 

   - **–** 

   - **Main concern is variations in light at frequencies of 2** 2.5—3 **.5 3 Hz** Hz 

   - **Large modern three-bladed wind turbines will rotate at less than 30–35 rpm, –** 

   - **giving blade** blade **passing** passing **frequencies** frequencies **of** of **1** 1.5-1.75 **.5 1.75 Hz** Hz **, which is below the critical frequency of 2.5 Hz.** 

**Example of shadow flicker prediction – continuous line shows time of sunset** 

E 

Source: Wind Energy Handbook 

## **Noise** Noise 

- **Wind farm Environmental Statement should include:** 

   - **Predicted noise** noise **levels** levels **at specific properties close to the wind farm over the most critical range of wind speeds** 

   - **Measured background** background **noise** noise **levels** levels **at the properties at these wind speeds** 

   - **A scale** scale **map** map **showing the proposed wind turbines, the prevailing wind conditions and nearby existing developments** 

   - **Results of independent measurements of noise** noise **emission** emission **from the proposed wind turbines including the sound** sound **power** power and **and narrow** narrow **band** band **frequency** frequency **spectrum** spectrum 

- **–** 

- * **IEC** IEC **61400** 61400-—11 **11 (** (2006) **2006) describes how tests to determine the noise emissions from a wind turbine may be conducted** 

- **–** 

- * **IEC** IEC **61400** 61400-14 **14 (** (2005) **2005) details how the results of these tests should be declared** 

E 

## **Wind Turbine Noise** Wind Turbine Noise 

- **Wind turbine noise:** 

   - * **Mechanical** Mechanical **(rotating machinery in the nacelle, particularly the gearbox and generator, cooling fans, auxiliary equipment, yaw system)** 

   - • **Aerodynamic (low frequency noise (dominated by 3P), inflow turbulence noise, airfoil self noise)** 

   - * Aerodynamic 

- **Airfoil self noise:** 

   - **Trailing edge noise (750–2000 Hz)** 

   - **Tip noise** 

   - **Stall effects** 

> **sound power level:** sound power level: 

> **LW ≈ (50 to 60) logV** LW = (50 to 60) logV,,, **tip** 

- **Blunt trailing edge noise** 

- **Surface imperfections** 

Source: Wind Energy Handbook 

## **Measurement, Prediction and Assessment** Measurement, Prediction and Assessment **of Wind Farm Noise** of Wind. Farm Noise• **The sound power level of a wind turbine is normally determined by field experiments.** 

- **The measurements are taken at a distance, R0, from the base of the tower:** 

**==> picture [98 x 38] intentionally omitted <==**

- **Sound pressure level of the wind turbine:** 

𝑳𝑷+𝑵 𝑳𝑵 𝐋 𝟎 𝟏𝟎 −𝟏𝟎𝟏𝟎 𝐏 = 𝟏𝟎𝒍𝒐𝒈𝟏𝟎(𝟏 ) 

   - **A-weighted sound power level of the turbine:** 

   - 𝟐 

   - 𝐋 = 𝑳 𝟒𝛑𝑹 −𝟔 𝐖 𝑷𝑨𝒆𝒒 + 𝟏𝟎𝒍𝒐𝒈𝟏𝟎 𝒊 

- **LP is the sound pressure level of the wind turbine.** 

- **LP+N is the sound pressure level of the wind turbine and the background sound.** 

   - **R is the slant distance from the i** 

   - **microphone to the wind turbine hub** 

- **LN is the sound pressure level of the** . 

- **background** 

Source: Wind Energy Handbook 

## **Electromagnetic Interference and Aviation** Electromagnetic Interference and Aviation **Radar** Radar 

- **Wind turbines have the potential to interfere with electromagnetic signals that form part of a wide range of modern communication systems and so their siting requires careful assessment in respect of Electromagnetic Interference (EMI).** 

- **Electromagnetic properties of wind turbine rotors will be influenced by:** 

   - **Rotor diameter and rotational speed** 

   - **Rotor surface area, planform and blade orientation including yaw angle** 

   - **Hub height** 

   - **Structural blade materials and surface finish** 

   - **Hub construction** 

   - **Surface contamination (including rain and ice)** 

   - **Internal metallic components including lightning protection** 

- **The main impacts of a wind farm on radar are:** 

   - **Masking** 

   - **Radar Clutter** 

   - **Scattering** 

More details: Wind Energy Handbook 

## **Ecological Assessment** Ecological Assessment 

- **Categories of effects:** 

   - **Immediate damage to wildlife habitats during construction** 

   - **Direct effects on individual species during operation** 

   - **Longer term changes to wildlife habitats as a consequence of construction or because of changed land use management practices** 

- **Impact on birds:** 

   - **Collision** 

   - **Displacement due to disturbance** 

   - **Barrier effect** 

   - **Habitat change and loss** 

-_ c) = = c) GS ©) x% if) =j 4 x, -33‘" 

## **Off-Shore Wind** Off-Shore + WineWind 

## **Reasons for going off-shore:** 

- **Huge available resources** 

- **Improved social acceptability** 

- **Lower environmental impacts (e.g. noise)** 

- • **Scale / logistics** 

- **Potential for reduced LCOE** 

## **Off-Shore Wind** 

a LS ion a : £ Cc Se Cc>oo|< 

we) = “s 5 eC = S| e - c)) a c = =3 =4 S) 4 wy x 

## **Off-Shore Wind** 

**More capacity for less cash thanks to:** • **Cost reductions** 

• **Increased competition** 

**Fixed Floating Monopile Jacket Twisted jacket Semisubmersible Tension leg Spar buoy** a Se Se | rd ; > -= | c)) sa _— if) 7} an . UJ = =. he c) r € - SS a : ; ; ) = = Sas . a . - > -_~ **(** _**Illustration by Josh Bauer, NREL)**_ 

## **Off-Shore Foundations** 

## **Offshore Power Collection and** Offshore Power Collection and **Transmission** Transmission 

**multiple HVDC transmission links 30–36 kV 132–150 kV** 

- **Key parameter for layout optimization** 

**==> picture [108 x 9] intentionally omitted <==**

**----- Start of picture text -----**<br>
Offshore sub-station<br>**----- End of picture text -----**<br>


Source: Wind Energy Handbook 

## **More Detailed Information on Wind Farm** More Detailed Information on Wind Farm 

# **1) Tony Burton, Nick Jenkins, David Sharpe, Ervin Bossanyi, GL Garrad Hassan. Wind Energy Handbook, Second Edition, WILEY, 2011.** 

