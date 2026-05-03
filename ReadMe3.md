## Assignment3

### Task 1
Added IEA 3.4 MW file to turbine library called: IEA3_4_MW.yaml
Copied IEA 10MW file, used available info from assignment sheet and csv file. Did not change info that wasnt directly given such as: controller_dependent_turbine_parameters or some scalars like cosine_loss_exponent_tilt in the power table. Added extra variable in .yaml file for cp (power coefficient) readings from csv file, as this is requested in task 2.

### Task 2
Ct, Cp, Power and power vs. yaw for 1,150 and 1,225 air densities and 7,5 m/s wind speed for -30 to +30 yaw angles.

Resulting graphs:
![Cp and Ct values for 2 air densities](images\assignment3_cp_ct_curves_task2.png)
There seem to be no differences of the thrust or power coefficients regarding the air density.

![left: Power curve right: power vs yaw angle](images\assignment3_power_power_vs_yaw_angle_task2.png)
The power curve for IEA 3.4 MW. On the right side the power curves for different air densities for various yaw angles. 