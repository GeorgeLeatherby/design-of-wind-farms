## Assignment 5
Layout Optimization for LCoE using floris and landbosse.

### Task 1
Windrose based on the full available data range from the New European Wind Atlas at Marienplatz in Munich. With 5° discretizations steps for wind direction and 1 m/s discretization steps for wind speeds.
![Windrose Task 1](images\assignment5_windrose_marienplatz_120m.png)

### Task 2
Evaluate AEP, capacity factor, and farm efficiency using the Gauss wake model (default 
parameters) of the baseline wind farm. Then, calculate LCoE and PI. Interpret the results 
based on the knowledge you gained in the previous assignments and lectures of the 
course. 

![Initial Layout](images\assignment5_initial_layout.png)

Found values for initial layout:

- AEP: 77062354807.63 Wh
- Capacity Factor: 0.3263
- Farm Efficiency: 85.45 %
- LCOE: 71.23 $/MWh
- Profitability Index (PI) : 0.9123

The initial layout is not a profitable investment from the investors view, as the PI < 1. The farm efficiency suggests that the turbines influence each other through wake, resulting in a loss of ~ 15%. Looking at the windrose this result is not surprising, as the main wind directions are in east-west direction. This is exactly the direction in which the windturbines have the most wake influences on subsequent turbines in the initial layout.

### Task 3
Since the optimizers are default calibrated to work with normalized input values, I defined the x and y ranges to [0-1]. Import parameters like $rhobeg$ which defines the initial trust region depend on the magnitude of the input values. \
Source: https://docs.scipy.org/doc/scipy/reference/optimize.minimize-cobyla.html


First used initial layout is the suggested starting layout with placement of turbines along the edges of the boundaries with equal distances.

![Solution initial layout 1](images\assignment5_solution_layout1.png)
The first starting layout showed acceptable convergence for $rhobeg = 0.35$. 

Derived from the first found optimized solution I tried to further refine the solution. Following attempts all showed the following final solution below. This particular one was reached with $rhobeg = 0.05$. However the optimization exhibits only very limited change in final solution through changing of the layout. THis particular second solution is even worse then the found solution above. I have re ran this layout with smaller and larger $rhobeg$ but could not derive better results.
![Solution initial layout 2](images\assignment5_solution_layout2.png)



#### Comment on convergence graphs reaching lower LCoE values during optimization and bouncing back up
 During the early iterations, the trust region is relatively large. The algorithm is essentially trying to find a direction that reduces LCoE while respecting the boundary and spacing constraints. It may temporarily move into a region of the design space where the linear approximation looks very promising (the "dip" to a lower value), even if that path later violates a constraint or proves less efficient once the approximation is refined.

COBYLA is a trust-region method that solves linear programming subproblems. If a step leads to a position that violates the minimum turbine distance or boundary constraints, the algorithm will sharply increase the "cost" (penalty) of that position to force the search back into the feasible region. That sharp spike is likely the algorithm "recovering" from an infeasible layout.

Source of comment:
- https://www.damtp.cam.ac.uk/user/na/NA_papers/NA2007_03.pdf
