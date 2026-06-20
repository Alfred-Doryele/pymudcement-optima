\# Step 9: Validation Against Benchmark Well Data



\## PyMudCement-Optima — Comparative Analysis



\*\*Course:\*\* PENG 258 — Drilling Engineering 1 Capstone Project

\*\*Purpose:\*\* Validate the software's cementing volumetric calculations against a published, industry-style worked example, per the syllabus requirement:



> \*"Run a real-world validation test using benchmark data from tier-1 cementing service companies"\* and \*"A formal evaluation comparing the software's slurry and spacer volume estimates against standard cementing company recommendations."\*



\---



\## 1. Benchmark Source



\*\*Title:\*\* Example Calculation 9 5/8″ Casing Cementation

\*\*Source:\*\* Drilling For Gas — Cementing / Casing reference library

\*\*URL:\*\* https://drillingforgas.com/en/cementing/casing/example-calculation-958in-casing-cementation



This is a complete, fully worked field example (cement volumes, displacement volumes, spacer design, and plug bumping pressure prediction) of the type used in real cementing job design and engineering training. It was selected because it documents every intermediate value, which makes it possible to validate each individual calculation stage of PyMudCement-Optima rather than only a single final answer.



\## 2. Benchmark Well Data



| Parameter | Value (Field Units) | Value (SI) |

|---|---|---|

| Previous casing (13⅜ in) shoe depth | 3,724 ft | 1,135.3 m |

| Open hole size | 12¼ in | 0.31115 m |

| 9⅝ in casing shoe depth | 5,053 ft | 1,540.2 m |

| 9⅝ in casing, 47 lb/ft — standard ID | 8.681 in | 0.22049 m |

| 9⅝ in casing OD | 9.625 in | 0.24448 m |

| Float collar depth (shoetrack length) | 4,954 ft (99 ft shoetrack) | 1,510.2 m |

| Cemented interval length | 1,329 ft | 405.08 m |

| Slurry gradient | 0.822 psi/ft | ≈1,896 kg/m³ |

| Mud in use (CMS, CMC/Bentonite) | 10.4 ppg | ≈1,246 kg/m³ |



\## 3. Validation Results



\### 3.1 Annular Cement Volume — `calculate\_annular\_volume()`



| Case | Benchmark | PyMudCement-Optima | Difference |

|---|---|---|---|

| Gauge hole (0% excess) | 74 bbl = 11.765 m³ | \*\*11.786 m³\*\* | +0.18% |

| Actual field volume (calliper log) | 89 bbl = 14.150 m³ | 14.175 m³ (at implied 20.27% excess) | +0.18% |



\*\*Analysis:\*\* The gauge-hole result matches the benchmark to within 0.18%. This small residual is attributable to the benchmark's use of a rounded industry capacity-factor table (0.0558 bbl/ft) rather than a raw geometric πr² calculation — PyMudCement-Optima computes the exact geometric value directly from the formula in the syllabus, so a sub-1% deviation against a rounded lookup table is expected and acceptable.



The benchmark's real field volume (from an actual calliper log run in the well) implies an excess/washout factor of approximately \*\*20.3%\*\* existed in this particular open-hole section. This is consistent with — and close to — the \*\*15% default excess factor\*\* used as the standard assumption in PyMudCement-Optima (per the syllabus's own example value), confirming that the software's default is a realistic, industry-representative assumption rather than an arbitrary placeholder.



\### 3.2 Displacement Volume — `calculate\_displacement\_volume()`



| Benchmark | PyMudCement-Optima | Difference |

|---|---|---|

| 363 bbl = 57.712 m³ | \*\*57.659 m³\*\* | −0.09% |



\*\*Analysis:\*\* Near-exact agreement (within 0.1%). This confirms the displacement volume formula (`V = (π/4) × D\_ID² × L`) is implemented correctly and matches real casing-capacity-table values used industrially.



\### 3.3 Density Cross-Check (Plug Bumping Pressure Inputs)



The benchmark's reported slurry and mud gradients (0.822 psi/ft cement, \~0.539 psi/ft mud) convert to approximately \*\*1,896 kg/m³\*\* and \*\*1,243 kg/m³\*\* respectively. These values are strikingly close to the \*\*1,900 kg/m³ and 1,250 kg/m³\*\* default values used throughout PyMudCement-Optima's Plug \& P\&A Design and Job Procedure Report pages — an independent confirmation that the default test values chosen during development reflect realistic, industry-typical fluid densities rather than arbitrary numbers.



\## 4. Summary



| Calculation | Validation Result |

|---|---|

| Annular Cement Volume | ✅ Matches within 0.18% |

| Displacement Volume | ✅ Matches within 0.1% |

| Default excess factor (15%) | ✅ Consistent with implied real-world washout (\~20%) |

| Default density assumptions | ✅ Consistent with benchmark's actual field densities |



All validated calculations in PyMudCement-Optima agree with the published benchmark to within approximately \*\*0.2%\*\*, which is well within the precision expected given that the benchmark itself uses rounded industry capacity-factor tables rather than raw geometric formulas. This provides strong evidence that the software's core volumetric engine is mathematically correct and produces results consistent with real-world tier-1-style cementing job design practice.



\## 5. Limitations of This Validation



\- The benchmark example does not report a directly comparable annular \*pressure drop\* or \*ECD\* value (it uses field-measured pump pressures rather than a Bingham-Plastic hydraulics model), so Step 4's hydraulics engine could not be cross-validated against this particular source. This is noted as a limitation; a separate hydraulics-specific benchmark would be needed to validate `hydraulics.py` independently.

\- The benchmark's plug bumping pressure calculation uses a multi-fluid-column method (cement + multiple spacer fluids + mud, each with its own gradient and length) rather than PyMudCement-Optima's simplified two-fluid model. A direct numerical comparison was therefore not performed for plug bumping pressure; instead, the underlying density assumptions were cross-checked and found to be consistent (Section 3.3).ss

