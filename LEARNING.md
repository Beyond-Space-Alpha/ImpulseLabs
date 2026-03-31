# ImpulseLabs Propulsion Design – Fully Solved Flow

## Input Parameters
- Chamber Pressure (Pc) = 30 bar = 3 × 10^6 Pa  
- Mixture Ratio (O/F) = 2.5  
- Thrust (F) = 1000 N  
- Propellants = LOX + RP-1  
- Contraction Ratio (CR) = 3  

---

## 1. Thermochemical Properties

- Chamber Temperature → Tc ≈ 3500 K  
- Specific Heat Ratio → γ ≈ 1.22  
- Gas Constant → R ≈ 355 J/kg·K  
- Characteristic Velocity → c* ≈ 1650 m/s  

---

## 2. Isentropic Relations

### Pressure
$$
\\frac{P}{P_c} = \\left(1 + \\frac{\\gamma - 1}{2} M^2 \\right)^{-\\frac{\\gamma}{\\gamma - 1}}
$$

### Temperature
$$
\\frac{T}{T_c} = \\left(1 + \\frac{\\gamma - 1}{2} M^2 \\right)^{-1}
$$

---

## 3. Exit Conditions 

### Exit Pressure
$$
P_e ≈ 0.1 \\times P_c = 3 \\text{ bar}
$$

### Exit Temperature
$$
T_e = 3500 \\times (1 + 0.11 \\times 9)^{-1} ≈ 1750 \\text{ K}
$$

---

## 4. Exit Velocity

$$
V_e = \\sqrt{ \\frac{2 \\gamma}{\\gamma - 1} \\cdot R \\cdot T_c \\cdot \\left(1 - \\left(\\frac{P_e}{P_c}\\right)^{\\frac{\\gamma - 1}{\\gamma}} \\right)}
$$

$$
V_e ≈ 2600 \\text{ m/s}
$$

---

## 5. Specific Impulse

$$
I_{sp} = \\frac{V_e}{g_0}
$$

$$
I_{sp} ≈ \\frac{2600}{9.81} ≈ 265 \\text{ s}
$$

---

## 6. Thrust Coefficient

$$
C_f ≈ 1.5
$$

---

## 7. Mass Flow Rate

$$
\\dot{m} = \\frac{F}{C_f \\cdot c^*}
$$

$$
\\dot{m} = \\frac{1000}{1.5 \\times 1650} ≈ 0.404 \\text{ kg/s}
$$

---

## 8. Throat Area

$$
A_t = \\frac{\\dot{m} \\cdot c^*}{P_c}
$$

$$
A_t = \\frac{0.404 \\times 1650}{3 \\times 10^6} ≈ 2.22 \\times 10^{-4} \\text{ m}^2
$$

### Throat Radius
$$
R_t = \\sqrt{\\frac{A_t}{\\pi}} ≈ 8.4 \\text{ mm}
$$

---

## 9. Expansion Ratio

$$
\\epsilon ≈ 6
$$

---

## 10. Exit Area

$$
A_e = \\epsilon \\cdot A_t
$$

$$
A_e ≈ 1.33 \\times 10^{-3} \\text{ m}^2
$$

### Exit Radius
$$
R_e = \\sqrt{\\frac{A_e}{\\pi}} ≈ 20.6 \\text{ mm}
$$

---

## 11. Chamber Geometry

### Chamber Area
$$
A_c = CR \\cdot A_t
$$

$$
A_c ≈ 6.66 \\times 10^{-4} \\text{ m}^2
$$

### Chamber Radius
$$
R_c = \\sqrt{\\frac{A_c}{\\pi}} ≈ 14.6 \\text{ mm}
$$

---

### Characteristic Length (Assume L* ≈ 1 m)

$$
L_c = \\frac{L^* \\cdot A_t}{A_c}
$$

$$
L_c ≈ 0.33 \\text{ m}
$$

---

## 12. Rao Nozzle Geometry

- Entrant Radius = 1.5 Rt ≈ 12.6 mm  
- Throat Radius = 0.382 Rt ≈ 3.2 mm  
- Initial Angle = 15°  
- Exit Angle = 30°  

---

## 13. Final Results

| Parameter | Value |
|----------|------|
| Exit Velocity | 2600 m/s |
| Specific Impulse | 265 s |
| Mass Flow Rate | 0.404 kg/s |
| Throat Radius | 8.4 mm |
| Exit Radius | 20.6 mm |
| Chamber Length | 0.33 m |
| Expansion Ratio | 6 |

---

## Flow Summary

Inputs → Combustion → Expansion → Velocity → Thrust → Geometry → Nozzle

---

## TLDR

- 30 bar LOX/RP1 gives ~2600 m/s exhaust  
- ~0.4 kg/s flow needed for 1000 N thrust  
- Compact engine: ~8 mm throat, ~20 mm exit  
- Solid baseline design for small rocket engine  
