# Ion Thruster Preliminary Design Tool

## Principle

This software is designed to conduct a Ion thruster design, given a set of design parameters specified by the user in an [input file](#input-file). It produces two main results:
- a [plain text output](#output-file) containing the best design, optimized for given design target
- a [sensitivity analysis](#optional-sensivity-analysis) on all mission parameters for given design target

The program calculates these results by sweeping a value space for ion beam voltage (denoted V_b) and beam intensity (denoted I_b). These two parameters are indeed the main scaling factors of the thruster, as described in the report.

## Usage

### Input file

The program is designed to process input test file *(usually in txt format)* and minimize the command line interactions to make the use as fluid as possible. Input files must have this structure:
```
parameter1: value
paramater2: value
...
```
where parameters are references by name with colons, and value is a floating point using python format. Scientific notation *(eg 2.13e3)* is supported.

Parameters are separated into two categories:
- Necessary parameters : these are the parameters that must be provided for the program to run
- Filters : these are optional parameters that can be used to refine the design further. If not specified, default value will be used

Please refer to the [parameter reference](#parameters-reference) for the description of all available parameters and look at the [examples](#examples-input-file).

To allow for more readable inputs, comments *(python format)* and empty lines are allowed in input files, like so:
```
#Comment line describing following parameter 
parameter1: value

#Other comment line, following an empty line
parameter2: value
```

The input file reader has a built-in error detection system that will report any anomaly with provided input file to allow the user to quickly find problems with their input.

### Output file

The program writes results to a plain text file with three sections:

**Optimal operating point** — the best (V_b, I_b) pair found,
with all computed performance parameters.

**Mass budget** — thruster mass, propellant mass, and total
system mass.

**Mission** — trip time in hours and days.

**Throttle table** — all feasible operating points sorted by
thrust level, formatted like a flight throttle table.

**Full sweep** — every evaluated (V_b, I_b) point for plotting
trade-off curves.

### Optional Sensivity Analysis

If desired, an optional local sensitivy analysis can be requested.
Using Local Derivative + One-Factor-at-a-Time method, both missions parameters and restrictions are evaluated regarding its variation and impact over the mission objective. For initial paramenters, alternative propellant solutions are also evaluated.

The measurement of the parameter change impact is given by [S] - normalized sensitivity index:

        % Variation in Objective
  S = ----------------------------- 
        % Variation in Parameter

To ensure compliance with non-linear nature of problem, the sensivity index is computed at 4 symetric locations: for +-1% and +- 5% variations, assuming OAT method variation for the parameters.
By reviewing  results, the user can get a simplified picture of the non-linear evolution of the objetive for differente degrees of variation.

Current implementation doesn't consider simultaneous multi-parameter variation impact.

Results are displayed on the terminal window. 
As an optional, they can be exported into table format, displayed in floating window plot and exported as .PNG

**The matplotlib is required to plot and display the results. If not installed, plot functions are disabled.**

**Plot 1** - Plot figure displaying the objective evolution inside a full range of +- 20% parameter variation: Allows for quick understanding of the non linearity evolution and possible boundaries of the problem.

**Plot 2** - tornado diagram showing the influence on objetive for a +- 5% parameter variation;

**NOTE: Ensure the sweep parameters in the parameters file are fine enought to allow qualitative sweep analysis. Large steps, diminuish the granularity of results, thus reducing the quality of sensitivity analysis!**
**Total computation time is sensible to step size. Smaller steps result in larger computation times**


Indicative ranges for sweep parameters for under 30s computation times in modern hardware: 

| beam_voltage_step  | Step size of V_b sweep        | V    | 5      |
| beam_current_step  | Step size of I_b sweep        | A    | 0.01   |


## Parameters reference

### Necessary parameters

These must be provided or the program will not run.

| Parameter    | Description                                        | Unit |
|--------------|----------------------------------------------------|------|
| deltav       | Total delta-v the thruster must deliver            | km/s |
| payload_mass | Satellite dry mass, excluding thruster/propellant  | kg   |

### Filters

Optional. If not specified, default values are used.

#### Mission constraints

| Parameter    | Description                                        | Unit    | Default  |
|--------------|----------------------------------------------------|---------|----------|
| max_power    | Maximum electrical power available for propulsion  | W       | infinity |
| min_thrust   | Minimum acceptable thrust                          | mN      | 0        |
| max_duration | Maximum acceptable mission duration                | h       | infinity |

#### Propellant

| Parameter  | Description                          | Unit | Default |
|------------|--------------------------------------|------|---------|
| propellant | 0 = Xenon, 1 = Krypton, 2 = Iodine   | -    | 0       |

#### Thruster efficiency parameters

These depend on the thruster technology and operating regime.
Typical flight values are given as defaults.

| Parameter | Description                                              | Unit | Default |
|-----------|----------------------------------------------------------|------|---------|
| eta_m     | Mass utilization efficiency (fraction ionized)           | -    | 0.90    |
| eta_e     | Electrical efficiency (beam power / total input power)   | -    | 0.85    |
| xi        | Thrust correction (beam divergence + multiply charged ions) | - | 0.97    |

#### Beam voltage sweep (design variable)

V_b is the primary design variable. The tool sweeps over this
range and finds the optimal value for the chosen objective.

| Parameter          | Description                   | Unit | Default |
|--------------------|-------------------------------|------|---------|
| beam_voltage_min   | Lower bound of V_b sweep      | V    | 800     |
| beam_voltage_max   | Upper bound of V_b sweep      | V    | 2000    |
| beam_voltage_step  | Step size of V_b sweep        | V    | 10      |

#### Beam current sweep (throttle range)

I_b is the throttle variable. It is bounded above by the power
budget: I_b_max = eta_e * max_power / V_b.

| Parameter          | Description                   | Unit | Default |
|--------------------|-------------------------------|------|---------|
| beam_current_min   | Lower bound of I_b sweep      | A    | 0.5     |
| beam_current_max   | Upper bound of I_b sweep      | A    | 3.0     |
| beam_current_step  | Step size of I_b sweep        | A    | 0.1     |

#### Objective function

| Parameter | Description                                          | Unit | Default |
|-----------|------------------------------------------------------|------|---------|
| objective | 0 = minimize total mass, 1 = minimize trip time, 2 = maximize Isp | - | 0 |

## Examples input file

Here are some examples of valid input files. You can find these in the example folder

Minimalist input file:
```
deltav: 5.0
payload_mass: 100
```

A more flesh out design file, with all parameters:
```
# Mission
deltav: 5.0
payload_mass: 100

# Constraints
max_power: 3000
max_duration: 4000

# Propellant (Xenon)
propellant: 0

# Efficiency assumptions
eta_m: 0.90
eta_e: 0.85
xi: 0.97

# Design sweep
beam_voltage_min: 800
beam_voltage_max: 2000
beam_voltage_step: 100
beam_current_min: 0.5
beam_current_max: 3.0
beam_current_step: 0.25

# Objective: minimise total mass
objective: 0
```