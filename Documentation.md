# ImpulseLabs Documentation

## 1. Combustion model
ImpulseLabs uses RocketCEA, which is based on NASA’s Chemical Equilibrium with Applications (CEA). 
### Inputs to the combustion model

- $F$ - Thrust 
Thrust defines the overall force the engine must produce. Higher thrust typically requires higher mass flow rates and larger engine geometry (throat and chamber size), which increases system weight and propellant consumption.
- $P_c$ - Chamber Pressure
Increasing chamber pressure generally improves thrust and efficiency (higher specific impulse) because exhaust gases expand more effectively. However, this comes at the cost of heavier structures, higher thermal loads, and increased turbopump complexity.
- Mixture ratio
The mixture ratio determines how fuel and oxidizer are balanced. There is an optimal MR that maximizes performance (Isp), but operating slightly fuel-rich is often preferred in practice to reduce combustion temperature and protect engine components. 
- Propellant choice
The choice of fuel and oxidizer combination fundamentally determines engine performance. Different propellants produce different combustion temperatures, molecular weights, and specific heat ratios.
High-energy combinations (e.g., hydrogen-based) give higher efficiency ($I_{sp}$) but may be harder to store, while denser propellants (e.g., kerosene-based) simplify tank design but typically yield lower exhaust velocities.
- Oxidizer temperature(optional parameter)
Higher oxidizer temperatures can improve atomization and combustion efficiency but may increase material stress and reduce propellant density, requiring larger tanks.
- Fuel Temperature(optional parameter)
Fuel temperature affects density and cooling capability. Colder fuel increases density (allowing more compact storage) and improves regenerative cooling, while higher temperatures may reduce system efficiency.
- Contraction Ratio (optional parameter)
The contraction ratio (chamber area to throat area) influences combustion stability and flow uniformity. Higher values improve flow conditioning before the throat but increase chamber size and weight.
- $P_a$ - Ambient Pressure: (optional parameter)
Ambient pressure directly affects nozzle performance. Engines designed for high altitude (low  $P_a$) perform poorly at sea level due to over-expansion, while sea-level optimized engines are less efficient in vacuum.
### Outputs from CEA 
- $T_c$ - Combustion chamber temperature

- $c^*$ - Characteristic velocity
It is a measure of the combustion efficiency of the propellant combination, independent of nozzle geometry. It represents how effectively chemical energy is converted into high-pressure, high-temperature gas in the chamber.
Higher $c^*$ means better propellant performance and more efficient energy release.

- $\gamma$ - Ratio of specific heats 
It controls how the gas expands through the nozzle.
A higher $\gamma$ generally leads to more efficient expansion and higher exhaust velocities, directly influencing thrust and specific impulse.

- $M_w$ - Molecular weight of exhaust gases 
It is the average molecular weight of the exhaust gases and affects how fast the gases can accelerate during expansion.
Lower $M_w$ is desirable because lighter molecules achieve higher exhaust velocities, improving engine performance.

## 2. Isentropic flow calculations
### Solving for Exit Mach Number $M_e$
The exit Mach number $M_e$ is obtained by solving the pressure-ratio equation:

$$\frac{P_e}{P_c}=\left( 1 + \frac{\gamma - 1}{2} M_e^2 \right)^{-\frac{\gamma}{\gamma - 1}}$$

where,

- $P_e$ = exit pressure
- $P_c$ = chamber pressure
- $\gamma$ = ratio of specific heats
- $M_e$ = exit Mach number

ImpusleLabs uses Brent's method on a bounded interval [1.001, 50] to find the root of the equation relating pressure ratio to Mach number. Guarantees convergence for all practical chamber-to-ambient pressure ratios. 

### Expansion Ratio 
The expansion ratio in a rocket nozzle is the ratio of how wide the nozzle is at the bottom (exit) compared to how narrow it is in the middle (throat). It dictates how much the high-pressure, hot gas from the combustion chamber is allowed to "stretch out" and speed up before exiting. It is given by the formula :

$$\frac{A_e}{A_t}=\frac{1}{M_e}\left[\frac{2}{\gamma+1}\left(1+\frac{\gamma-1}{2}M_e^2\right)\right]^{\frac{\gamma+1}{2\cdot(\gamma-1)}}$$

Where:

- $A_e$ = exit area
- $A_t$ = throat area

The Trade-off (Altitude): 

- Low Expansion (Small Bell): Best for sea-level where air pressure is high. If it's too wide at sea level, the outside air pushes in and makes the engine inefficient.
- High Expansion (Large Bell): Best for space. In a vacuum, there is no air pressure to hold the gas together, so you want the nozzle as wide as possible to get every last bit of energy out of the gas.

## 3. Performance($I_{sp}$)
 Specific Impulse ($I_{sp}$) is the fuel efficiency of a rocket engine, often described as "miles per gallon" (MPG) for rockets. It is calculated by CEA using the combustion and nozzle expansion values.

## 4. Mass flow rate
 Impulselabs calculates the fuel consumption from the required thrust. The mass flow rate ($\dot m$) in a rocket nozzle is the amount of propellant (fuel and oxidizer) the rocket burns and dumps out of the nozzle every single second. It is calculated using the formula:

 
 $$\dot{m} = \frac{F}{I_{sp} \cdot g_0}$$

 where:
 - $F$ = Thrust
- $I_{sp}$ = Specific impusle
- $g_0$ = standard acceleration due to gravity, approximately 9.80665 ⋅$ms^{−2}$

Higher thrust leads to higher fuel consumption whereas a higher $I_{sp}$, meaning higher efficiency leads to lower fuel consumption.

## 5. Throat sizing
The flow becomes sonic(Mach 1) at the throat, where the area is minimum. The area of the throat $A_t$ is calculated using the formula:

$$A_t = \frac{\dot{m} \cdot c^*}{P_c}$$

where:
- $\dot m$ = Mass flow rate
- $c^*$ = Characteristic velocity
- $P_c$ = chamber pressure

The throat controls how much mass can flow. A higher chamber pressure requires a smaller throat whereas a larger mass flow requires a larger throat.




## 6. Exit and Chamber geometry

The exit section of the nozzle determines how completely the exhaust gases expand before leaving the engine. A properly designed exit maximizes thrust by converting thermal energy into kinetic energy.

### Exit Area

The exit area is calculated using the expansion ratio:

$$
A_e = \epsilon \cdot A_t
$$

where:

- $A_e$ = exit area  
- $A_t$ = throat area  
- $\epsilon$ = expansion ratio  

### Exit Radius

Assuming a circular cross-section:

$$
r_e = \sqrt{\frac{A_e}{\pi}}
$$

where:

- $r_e$ = exit radius  

The exit area determines how much the gas expands before leaving the nozzle.



### Chamber Geometry

The combustion chamber stores and burns propellants before they accelerate through the nozzle.

The total combustion volume is defined using the characteristic length $L^*$:

$$
V_c = L^* \cdot A_t
$$

where:

- $V_c$ = chamber volume  
- $L^*$ = characteristic length  
- $A_t$ = throat area  

Since part of this volume is already occupied by the converging section, we subtract it:

$$
V_{conv} = \frac{\pi L_{conv}}{3} (r_c^2 + r_c r_t + r_t^2)
$$

The remaining volume forms the cylindrical chamber:

$$
L_c = \frac{V_c - V_{conv}}{A_c}
$$

where:

- $L_c$ = chamber length  
- $A_c$ = chamber area  

Higher $L^*$ means more time for combustion, but also increases size and weight.


## 7. Converging Section geometry

The converging section accelerates flow from subsonic to sonic conditions at the throat.

The converging length is calculated using:

$$
L_{conv} = \frac{r_c - r_t}{\tan(\theta_{conv})}
$$

where:

- $\theta_{conv}$ = converging angle (typically $30^\circ$)

In the model, the converging section is shaped smoothly (parabolic profile) to ensure stable flow.

Too steep → flow separation  
Too long → unnecessary weight  


## 8. Throat region geometry

The throat is the most critical part of the nozzle, where the flow reaches Mach 1.

To ensure a smooth transition, the throat region is modeled using two circular arcs.

### Entrant Arc

$$
R_u = 1.5 \cdot r_t
$$

### Exit Arc

$$
R_d = 0.382 \cdot r_t
$$

where:

- $r_t$ = throat radius  

These arcs help smoothly guide the flow into and out of the throat.

Without smooth curvature, shocks and losses can occur.


## 9. Diverging Section (Bell Nozzle)

The diverging section accelerates the flow from sonic to supersonic speeds.

ImpulseLabs uses a **Rao bell nozzle**, which is more efficient than a simple conical nozzle.

The expansion ratio is:

$$
\epsilon = \left(\frac{r_e}{r_t}\right)^2
$$

The bell length is calculated as a percentage of an equivalent conical nozzle:

$$
L_{bell} = \lambda \cdot \frac{r_e - r_t}{\tan(15^\circ)}
$$

where:

- $\lambda$ = length percentage (typically 60–90%)

The nozzle contour is generated using a smooth curve (Bezier curve) to ensure efficient expansion.

A well-designed bell nozzle gives high performance while keeping the engine compact.






## Visualization Explanation

One-dimensional (1D) plots are used to analyze how flow properties evolve along the nozzle axis, helping you understand acceleration and expansion behavior.

- **Mach Number Distribution**  
  The Mach number plot shows how the flow accelerates from subsonic (\(M < 1\)) in the chamber to sonic (\(M = 1\)) at the throat, and then to supersonic (\(M > 1\)) in the nozzle. A smooth increase indicates proper nozzle design, while irregularities may suggest flow instability or incorrect geometry.

- **Temperature Distribution**  
  The temperature plot shows how thermal energy is converted into kinetic energy. Temperature is highest in the combustion chamber and decreases along the nozzle as the gas expands and accelerates. A steady drop in temperature confirms efficient energy conversion.

- **Pressure Distribution**  
  The pressure plot illustrates how pressure energy drives the flow. Pressure starts high in the chamber and rapidly decreases through the throat and nozzle.
