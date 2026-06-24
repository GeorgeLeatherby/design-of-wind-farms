r E 

## **Praktikum** Praktikum **Design of Wind Farms** Design of Wind Farms 

**Lecture 6:** Lecture 6 **Layout Optimization** Layout Optimization 

**Samuel Kainz** Samuel Kainz **Technische Universität München** Technische Universitat Munchen 

**2026** 

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



## **Agenda** Agenda 

# • **Introduction to optimization problems** 

- **Optimization problem classification** 

- **Optimization algorithms** 

- **Challenges in wind farm design** 

- **Wind farm layout design optimization** 

# **Introduction to optimization problems** Introduction to optimization problems 

## **Introduction to optimization problems** 

## **Basics** 

- **idea:** find best possible solution for a mathematical function by changing variables that can be controlled, often subject to constraints 

- **approach:** analytical vs. numerical approaches (simple vs. complex) 

- **interdisciplinarity:** Engineering systems rarely isolated but linked to other systems → _multidisciplinary design optimization (MDO)_ 

## _Example_ 

**==> picture [22 x 10] intentionally omitted <==**

**----- Start of picture text -----**<br>
y (m)<br>**----- End of picture text -----**<br>


_Position 6 turbines within the defined boundary to maximize the economic performance._ 

→ _How to measure economic performance?_ 

- → _How to set up a model to calculate a representative metric?_ 

**==> picture [22 x 9] intentionally omitted <==**

**----- Start of picture text -----**<br>
x (m)<br>**----- End of picture text -----**<br>


- → _Once set up, which parameters can we optimize in which range under which constraints in order to minimize LCOE? Which algorithm do we use?_ 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

E ti, 5S 

## **Introduction to optimization problems** 

## **Basics** 

- **idea:** find best possible solution for a mathematical function by changing variables that can be controlled, often subject to constraints 

- **approach:** analytical vs. numerical approaches (simple vs. complex) 

- **interdisciplinarity:** Engineering systems rarely isolated but linked to other systems → _multidisciplinary design optimization (MDO)_ 

## **Optimization problem formulation** 

**Optimization problem:** mathematical statement that can be solved by an optimization algorithm; requires methodical formulation to avoid any weaknesses: 

3. Define the 1. Describe 2. Gather 4. Define the 5. Define the design the problem information objective constraints variables 

## **1. Problem description** 

- system description, goals, requirements 

- typically vague 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

> **-6-** * 

• » collect data and information about the problem (raw data, data processing, - **analysis procedure and models** , input and output mapping, computational time a) for analysis, etc.) ™ • **iterative process** throughout problem formulation g **3. Design variables definition** • 5S Variables that describe the system • Number → **problem dimensionality** • = **Must not depend on each other** or any other parameter • : May vary within bounds = **design space** (limited by physical considerations) • = **Continuous or discrete** • Functional form of objectives and constraints • Often require initial guess 5 c 

## **Introduction to optimization problems** 

3. Define the 1. Describe 2. Gather 4. Define the 5. Define the design the problem information objective constraints variables 

## **2. Gather information** 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

> **-7-** * f Wind Energy Institute 

a = rs : i) By ; . 

## **Introduction to optimization problems** 

3. Define the 1. Describe 2. Gather 4. Define the 5. Define the design the problem information objective constraints variables 

## **4. Objective definition** 

- **Objective function** = quantity that determines if a design is better than another 

- **Scalar computable through a model** for given **design variable vector** 

- **Minimized** or **maximized** 

- Note: max 𝑓 𝑥 = −min[−𝑓 𝑥] 

- • Choice crucial for successful design optimization. 

- • Multi-objective optimization → trade-offs between several objectives me) () 

- **definition** 

- • Constraints = restricted functions of design variables computed through model 

- • **Feasible region** = set of points that satisfy all constraints 

- • **Equality constraint** , e.g., ℎ () 𝑥= 0 

## **5. Constraints definition** 

- **Inequality constraint:** e.g., g () 𝑥≤0 

- Equality constraints can be described by two inequality constraints, e.g., ℎ () 𝑥= 0 → h () 𝑥≥0 _and_ g () 𝑥≤0 

- • Over-constraint → no feasible region in design space 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

## **Introduction to optimization problems** 

**General optimization problem statement** (valid for all continuous single-objective problems) 

_“Minimize the objective function by varying the design variables within their bounds subject to the constraints.”_ 

- Values of objective and constraint functions computed through the analysis 

- • Typically: analysis = numerical model(s) 

- Objective and constraint functions must depend on design variables 

- Analysis must be fully automatic 

- Initial design x0 typically required 

- Iterative queries analysis until optimum design x* is found 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

. , C) C c ) “a zy <' y cl, 

## **Introduction to optimization problems** 

**==> picture [21 x 9] intentionally omitted <==**

**----- Start of picture text -----**<br>
y (m)<br>**----- End of picture text -----**<br>


_Example Position 6 turbines within the_ ~~—~~ _defined boundary to maximize the economic performance._ 

**==> picture [218 x 195] intentionally omitted <==**

**----- Start of picture text -----**<br>
x (m)<br>gi,j = (xᵢ − xⱼ)² + (yᵢ − yⱼ)²<br>x,y g<br>x 0, y 0 scipy.optimize x *, y *<br>x,y LCOE<br>calc_lcoe( x , y )<br>**----- End of picture text -----**<br>


_minimize LCOE (xi,yi) x by varying l ≤xi ≤xu yl ≤yi ≤yu subject to (xᵢ−xⱼ)² + (yᵢ−yⱼ)² ≥(NDD)²_ ∀ i ≠j _N D … minimum allowable spacing [D] D … Rotor diameter [m]_ 

- E.g. E.g. python function python function • ¢ Input: Input: x x,y , y • * Calls Floris and Calls Floris and Landbosse Landbosse 

- • ¢- Postprocesses results Postprocesses results • * Returns LCOE Returns LCOE 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

## **Convergence and stopping criteria** 

## Convergence 

**Goal of optimization:** iteratively improve objective value to approach optimal solution **Typically** : fast initial improvement, slow refinement near optimum 

**Factors** affecting convergence: 

- Step size / learning rate 

- Conditioning of the problem 

**==> picture [239 x 95] intentionally omitted <==**

**----- Start of picture text -----**<br>
PN | ft [tt]<br>pA<br>Pt ™<br>1 2 3 4 5 6 7 8 9<br>Iteration<br>f(x)<br>**----- End of picture text -----**<br>


## Approximation of optimum 

- Choice of algorithm and initialization 

→ **Monitor convergence!** Track objective value, gradient norm, parameter updates, … 

**==> picture [239 x 102] intentionally omitted <==**

**----- Start of picture text -----**<br>
PNY<br>nnn eee<br>x<br>f(x) Iterations<br>f(x)<br>**----- End of picture text -----**<br>


## **Convergence and stopping criteria** 

_Stop when the solution is both optimal enough and feasible enough!_ **Stopping criteria** (combinations possible): • Objective improvement below threshold ∆𝑓≤𝜀 • Small gradient norm (near stationary point): ae) ∇𝑓 𝑥𝑘 < 𝜀 • Small parameter update: 𝑥𝑘+1 −𝑥𝑘 < 𝜀 

- Constraint violation below tolerance 

• … 

- Maximum iterations reached 

- Time or resource budget exceeded 

- Early stopping to avoid overfitting (ML) 

## Convergence 

**==> picture [285 x 289] intentionally omitted <==**

**----- Start of picture text -----**<br>
PN T | tT Tt TT<br>i e e ∆𝑓≤𝜀<br>1 2 3 4 5 6 7 8 9<br>Iteration C) 𝑖> 𝑖𝑚𝑎𝑥<br>Approximation of optimum<br>en ee<br>MN O\<br>∆𝑥< 𝜀<br>i eeee<br>∆𝑓<br>aney,<br>∆𝑥 [≤𝜀]<br>R R ∆𝑓≤𝜀<br>x<br>f(x) Iterations<br>f(x)<br>f(x)<br>**----- End of picture text -----**<br>


# **Optimization problem classification** Optimization problem classification 

## **Optimization problem classification** 

... required for choice of most appropriate optimization algorithm, because **no optimization algorithm is efficient or appropriate for all types of problems** ! 

**1. Problem formulation** (discussed previously) 

**==> picture [573 x 226] intentionally omitted <==**

**----- Start of picture text -----**<br>
Problem<br>formulation<br>Design<br>Objective Constraints<br>variables<br>Multi- Un-<br>Continuous Discrete Mixed Single Constrained<br>objective constrained<br>ee<br>Note:<br>•<br>Design variables are  discrete  or  continuous . Both included:  mixed problem<br>•<br>Unconstrained problems are rare in engineering design optimization<br>**----- End of picture text -----**<br>


Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

## **Optimization problem classification** 

## **2. Objective and constraint function characteristics** 

**==> picture [643 x 325] intentionally omitted <==**

**----- Start of picture text -----**<br>
Objective and constraint<br>function characteristics<br>Smooth- Stochas-<br>Linearity Modality Convexity<br>ness ticity<br>Dis- Deter-<br>Continuous Linear Nonlinear Unimodal Multimodal Convex Nonconvex Stochastic<br>continuous ministic<br>•<br>Degree of function  smoothness<br>→ continuity of function (C [0] continuous) (a.)<br>→ continuity of derivatives (C [1] , C [2] ,… continuous) discontinuous<br>•<br>Discontinuities limit optimization algorithm types<br>• Linear optimization problem if objective / constraint (b.)<br>C [0] continuous<br>functions are linear → many methods available f(x) aan<br>• =<br>Most engineering problems are nonlinear typically<br>harder to solve (c.)<br>C [1] continuous<br>**----- End of picture text -----**<br>


oe c’ © a) €o q C = rh c **-15-** - 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

— c’ = wy ™ Continuous 9 Cc • = = « • 5 • S £ rj • $ • • : z c \) **-16-** - Ye 

## **Optimization problem classification** 

## **2. Objective and constraint function characteristics** 

**==> picture [676 x 125] intentionally omitted <==**

**----- Start of picture text -----**<br>
Objective and constraint<br>function characteristics<br>Smooth- Stochas-<br>— Linearity Modality Convexity<br>c’ ness ticity<br>z= “ssa = =e<br>wy<br>Dis- Deter-<br>Continuous Linear Nonlinear Unimodal Multimodal Convex Nonconvex Stochastic<br>continuous ministic<br>**----- End of picture text -----**<br>


- **Unimodal functions** : single minimum 

- **Multimodal functions** : several minima 

- **Local minimum:** better than points in neighbourhood 

- • **Global minimum:** best in whole domain 

- • **Weak minimum:** function around minimum is flat 

- **Convex** function: all line segments connecting any two points in function lie above the function and never intersect. Always unimodal. All multimodal functions are nonconvex. 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

## **Optimization problem classification** 

## **2. Objective and constraint function characteristics** 

**==> picture [684 x 370] intentionally omitted <==**

**----- Start of picture text -----**<br>
Objective and constraint<br>function characteristics<br>2 Smooth- Linearity Modality Convexity Stochas-<br>5 ness ticity<br>i, Continuous Dis- Linear Nonlinear Unimodal Multimodal Convex Nonconvex Deter- Stochastic<br>continuous ministic<br>=<br>< • Stochastic model: yields different function values Deterministic Stochastic<br>‘<br>for repeated evaluations with same input (e.g. roll of<br>5<br>dice)<br>• Deterministic model : always yields the same<br>function values with same input.<br>-<br>•<br>Note: Deterministic models can still be subject to |<br>stochasticity when inputs are subject to uncertainty :<br>(described as probability distributions) that propagate<br>= +»<br>yy through the model x x<br>c<br>Praktikum Design of Wind Farms<br>**----- End of picture text -----**<br>


Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

> **-17-** ” 

# **Optimization algorithms** 

**-18-** 

| 

## **Optimization algorithms** 

No optimization algorithm is effective (solve problem reliably and efficiently) or appropriate for all types of problems. 

## **Attributes to classify optimization algorithms:** 

**==> picture [641 x 122] intentionally omitted <==**

**----- Start of picture text -----**<br>
Optimization algorithm<br>classification<br>Function  Stochas- Time<br>Order Search Algorithm<br>evaluation ticity dependence<br>Mathe- Surrogate  Deter- Stoch-<br>Zeroth First Second Local Global Heuristic Direct Static Dynamic<br>matical model ministic astic<br>**----- End of picture text -----**<br>


- Attributes are **independent** 

- Any **combination** possible 

- Combination is crucial for choice of best algorithm 

iV, Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 (arr 

## **Optimization algorithms** 

**==> picture [687 x 414] intentionally omitted <==**

**----- Start of picture text -----**<br>
Optimization algorithm<br>classification<br>Function  Stochas- Time<br>Order Search Algorithm<br>evaluation ticity dependence<br>2 Mathe- Surrogate  Deter- Stoch-<br>Zeroth First Second Local Global Heuristic Direct Static Dynamic<br>matical model ministic astic<br>-<br>i,<br>7 WN<br>•<br>2 Zeroth order: gradient-free algorithms § 104<br>= → only use function values of objective and constraints =B 3 Gradient free<br>=<br>: → Advantage:  easy to set up  (no additional computation)<br>S &® [2]<br>→ Disadvantage:  expensive for many design variables<br>z<br>i's 5<br>• al<br>First (or second) order: gradient-based  algorithms fo)<br>c: → gradients of objective / constraints wrt design variables 2 Gradient based<br>→ fast once set up  (efficient convergence to optimum) g 10 20 30<br>Number of design variables<br>→ require functions to be smooth (at least C [1] continuous)<br>→ Gradients analytical or estimated via finite difference<br>c<br>Praktikum Design of Wind Farms<br>**----- End of picture text -----**<br>


> **-20-** - | Wind Energy Institute 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

## **Optimization algorithms** 

Optimization algorithm classification 

**==> picture [687 x 363] intentionally omitted <==**

**----- Start of picture text -----**<br>
Function  Stochas- Time<br>Order Search Algorithm<br>evaluation ticity dependence<br>» Mathe- Surrogate  Deter- Stoch-<br>cS Zeroth First Second Local Global Heuristic Direct Static Dynamic<br>matical model ministic astic<br>iN),<br>a,<br>•<br>Local search  of design space:<br>g → starts from single point<br>5 → hopefully converge to (local) optimum<br>•<br>c Global search : spans whole design space aiming at finding global optimum<br>•<br>Mathematical solver<br>: : Rigorous search with optimality guarantees<br>=<br>•<br>Heuristic solver : Rule-based search for good-enough solutions.<br>o<br>r<br>.<br>Praktikum Design of Wind Farms<br>**----- End of picture text -----**<br>


Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

> **-21-** - | Wind Energy Institute 

pS < . a) ™ 9 = S q ' Cc a 

## **Optimization algorithms** 

**==> picture [641 x 122] intentionally omitted <==**

**----- Start of picture text -----**<br>
Optimization algorithm<br>classification<br>Function  Stochas- Time<br>Order Search Algorithm<br>evaluation ticity dependence<br>Mathe- Surrogate  Deter- Stoch-<br>Zeroth First Second Local Global Heuristic Direct Static Dynamic<br>matical model ministic astic<br>**----- End of picture text -----**<br>


- **Direct function call:** numerical models solved repeatedly 

- If computationally expensive: can be approximated through **surrogate models** (“metamodels”, interpolation- or projection-based) 

- **Deterministic** algorithm: same result for same initial conditions 

- **Stochastic** algorithm: impact of randomness 

- **Static** problems: numerical model is solved at each optimization iteration 

- **Dynamic** problems solve sequence of optimization problems (different time instances) 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

> **-22-** “ Ye Wind Energy Institute 

## **Optimization algorithms** 

**Selection of optimization algorithm** is problem-specific and requires optimization problem classification and understanding of the algorithm’s characteristics. 

**Various open-source optimization algorithms available** (python packages, Matlab optimization toolbox, etc.) 

often not known but guess is possible 

Hard to solve, avoid if possible 

Model improvements for smoothness possible? 

Intractable for highdimensional problems 

More details in: 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021., **https://mdobook.github.io/** 

Joaquim R. R. A. Martins and Andrew Ning. Engineering Design Optimization. Cambridge University Press, 2021. ISBN: 9781108833417 

# **Challenges in wind farm design** Challenges in wind farm design 

## **Challenges in wind farm design** 

Wind farms are amongst most **complex systems** worldwide: 

- Coupled interactions across subcomponents and disciplines 

- Set of interconnected components, individual behaviour and interactions determine overall performance 

• Performance simultaneously q i i described by technical, economic, environmental, social,… disciplines < > • Uncertain: power output, § costs and other KPIs rely on many stochastic parameters and imperfect models ‘ • Heterogenous: every farm = looks and performs differently, design faces = particular constraints —_ 

Sanchez Perez Moreno, S. (2019): A guideline for selecting MDAO workflows with an application in offshore wind energy. Dissertation, Delft University of Technology. 

> **-25-** a 

## **Challenges in wind farm design** Challenges in wind farm design 

- **Complex decision-making process** to satisfy requirement of all the multiple stakeholders involved: project developer, operator, OEM, governments, electrical system operators, financial institutions, consumers, … 

- **Design process** : different companies design different components with limited communication 

- Optimization of sub-systems usually not optimum for whole system (dep. on trade-offs elsewhere) 

→ Lack of knowledge about **sub-system design interactions** 

→ **Traditional** industrial design often takes place **sequential** : 

1. Wind turbines designed independent of site location 

2. Layout designers fix positions for wake minimization 

3. Design of support structures for water depths and soil conditions 

4. Topology of power collection system 

→ **Design automation not fully exploited** 

Sanchez Perez Moreno, S. (2019): A guideline for selecting MDAO workflows with an application in offshore wind energy. Dissertation, Delft University of Technology. 

# **Wind farm layout design optimization** 

**-27-** 

**-28-** 

**-29-** 

**-30-** 

**-31-** 

**-32-** 

**-33-** 

**-34-** 

**-35-** 

**-36-** 

**-37-** 

**-38-** 

## **Wind farm layout design optimization** Wind farm layout design optimization 

- Task of wind farm developer 

- Typically for fixed available wind turbine type(s) within predefined zone(s) (boundaries = constraint) 

- **Design variables** : primarily the **turbine positions** , but can also be number of turbines, turbine type, tower height, etc. 

- **Classic objective function** : AEP, LCoE, and/or profitability estimates 

- Ongoing research considers metrics beyond classic objectives (next lecture) and combined layout and wind farm control optimization (“control co-design”) 

- Classic design (and this Praktikum) requires consideration of the wind field including wake losses, turbine performance, plant capacity, land use (rental), balance-of-plant costs (especially cabling), expected profit and risks. In reality: various additional aspects. 

## → **Layout design requires (complex) multi-disciplinary optimization** 

- Hint: Floris comes with a layout optimization tool for AEP or annual value production maximization, but costs are not considered. 

Thomas, J. J. et al (2023): A comparison of eight optimization methods applied to a wind farm layout optimization problem. Wind Energy Science, 8, p.865-891 

## **Wind farm layout design optimization** 

## **Challenges** from optimization perspective: 

- Large design space → we find **good, not globally optimal solutions** with available methods 

• Highly multimodal design space favours gradient-free methods But: potentially high number of design variables and constraints favour gradientbased methods 

ip) e But: potentially high number of design variables and constraints favour gradient= based methods W " • Problems are often discontinuous and continuous at the same time. Qo Cc Example: divide turbines among allowed zones (discontinuous), place turbines in zones (continuous) —_ S ) _ ope N y e)) ono? a.oreSe. iNS **Baseline** : AEP = 2851 GWh 81x Task: ‘4 Place 81 x anee 09°a© Powa.) — 4a) DOD **Option A** : AEP +2.07% IEA-10MW Pa machines to Cie)&aw|ofwy% & ,'Pf§ fee"9° 4Mo §Oo **Option B** : AEP +1.95% = maximize AEP awews ary% **Option C** : AEP +2.05% a= «oe 3 **Source** : 3B & % Thomas et al., 2022 (preprint) | wi x Thomas, J. J. et al (2023): A comparison of eight optimization methods applied to **-40-** = a wind farm layout optimization problem. Wind Energy Science, 8, p.865-891 Ye Wind Energy Institute 

Thomas, J. J. et al (2023): A comparison of eight optimization methods applied to a wind farm layout optimization problem. Wind Energy Science, 8, p.865-891 

## **Wind farm layout design optimization** Wind farm layout design optimization 

## **Challenges** from optimization perspective: 

- Large design space → we find **good, not globally optimal solutions** with available methods 

• Highly multimodal design space favours gradient-free methods But: potentially high number of design variables and constraints favour gradientbased methods 

• Problems are often discontinuous and continuous at the same time. Example: divide turbines among allowed zones (discontinuous), place turbines in zones (continuous) 

## **How to overcome?** 

- Re-parameterize or discretize to reduce number of design variables / constraints 

- Avoid local optima: pair algorithms with global-search techniques (e.g. multi-start approach) 

- Hybrid approach: combine gradient-based and gradient-free methods, global and local-search method, … 

- Choice of appropriate algorithm and search method highly **dependent on problem and situation** , and user experience 

Thomas, J. J. et al (2023): A comparison of eight optimization methods applied to a wind farm layout optimization problem. Wind Energy Science, 8, p.865-891 

