# PyMudCement-Optima

**Intelligent Mud & Cement Design Suite**
PENG 258 — Drilling Engineering 1 Capstone Project
Department of Petroleum and Natural Gas Engineering, UENR
Submission Date: 8 August 2026

---

## 📖 Overview

PyMudCement-Optima is a Python-based engineering application that automates:

1. **Drilling Fluids & Hydraulics** — mud weight design, PV/YP rheology, annular pressure drop, ECD tracking, hole cleaning.
2. **Cementing Engineering** — slurry/spacer/displacement volumetrics, additive selection, plug bumping pressure, and Plug & Abandonment (P&A) design.

Built with **Python 3.10+**, **NumPy/SciPy**, and a **Streamlit** web interface.

---

## 🗂️ Project Structure
pymudcement-optima/

├── app.py                      # Streamlit GUI entry point

├── requirements.txt            # Python dependencies

├── README.md                   # This file

├── modules/

│   ├── init.py

│   ├── mud_engine.py           # Mud weight, pressure balance, PV/YP rheology

│   ├── hydraulics.py           # Annular pressure drop, ECD

│   ├── cement_engine.py        # Slurry/spacer/displacement volumes

│   ├── cement_db.py            # Additive lookup database

│   └── pa_plugs.py             # Plug bumping pressure, P&A design

├── data/

│   └── cement_additives.json   # Additive lookup table

├── tests/

│   ├── init.py

│   └── test_calculations.py    # Unit tests + hand-calc validation

└── reports/

└── sample_output/          # Generated job procedure sheets
---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Alfred-Doryele/pymudcement-optima.git
cd pymudcement-optima
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

### 5. Run tests
```bash
pytest tests/ -v
```

---

## 👥 Team & Module Ownership

| Module | File | Owner | Status |
|---|---|---|---|
| Mud Weight & Pressure Balance | `modules/mud_engine.py` | TBD | ✅ Implemented |
| Rheology (PV/YP) | `modules/mud_engine.py` | TBD | 🚧 Scaffold |
| Annular Hydraulics & ECD | `modules/hydraulics.py` | TBD | 🚧 Scaffold |
| Cement Volumetrics | `modules/cement_engine.py` | TBD | 🚧 Scaffold |
| Additive Database | `modules/cement_db.py` | TBD | 🚧 Scaffold |
| Plug Bumping & P&A | `modules/pa_plugs.py` | TBD | 🚧 Scaffold |
| GUI Integration | `app.py` | TBD | 🚧 Scaffold |

> Update this table as your group assigns ownership. Each member should work on their own branch and submit pull requests for review.

---

## 🧮 Core Engineering Equations

**Hydrostatic Pressure:**
`P_hyd = ρ_mud × g × TVD`

**Bingham-Plastic Rheology:**
`τ = YP + PV × γ`

**Annular Volume (Cementing):**
`V_ann = (π/4) × (D_hole² − D_casing_OD²) × L × (1 + W_e)`

---

## 🛣️ Development Roadmap

- [x] **Step 1:** Project scaffold, GitHub repo, environment setup
- [x] **Step 2:** Mud weight & safe window calculator
- [ ] **Step 3:** Mud report parser & PV/YP rheology
- [ ] **Step 4:** Annular hydraulics & ECD engine
- [ ] **Step 5:** Cement volumetrics
- [ ] **Step 6:** Additive database & slurry design
- [ ] **Step 7:** Plug bumping pressure & P&A module
- [ ] **Step 8:** Streamlit GUI integration
- [ ] **Step 9:** Validation against benchmark data
- [ ] **Step 10:** Final testing, demo prep, technical report

---

## 📋 Assessment Alignment (PENG 258)

| Component | Weight |
|---|---|
| Source Code Repository | 40% |
| Technical Report | 40% |
| Software Viva & Demo | 20% |

---

## 📄 License

Academic project for PENG 258, UENR — for educational use only.