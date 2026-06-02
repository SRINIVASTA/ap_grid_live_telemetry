# ⚡ APTRANSCO Smart Grid Unified Intelligence System

An advanced, multi-modal machine learning platform and real-time ingestion pipeline designed for state-level electrical power infrastructure. This system integrates **IoT telemetry, drone imagery analytics, and weather sensor data** to predict Asset Remaining Useful Life (RUL), execute dynamic line rating adjustments, and perform predictive network load balancing.

---

## 🛠️ Core Functional Architecture

### 1. Multi-Modal ML Engine
* **Asset Health Regressor**: Built on a `RandomForestRegressor` ensemble pipeline trained across multiple vectors.
* **Feature Integration**: Synthesizes internal thermal loads (`temp_C`, `load_pct`), structural health degradation indices (`insulation_health`), drone spatial anomalies (`veg_distance_m`, `conductor_sag_cm`), and environmental IoT metrics (`ambient_temp_C`).

### 2. Dynamic Line Rating (DLR) Logic
* **Adaptive Ceilings**: Automatically scales safe operational line thresholds between **76.0% and 96.0%** capacity.
* **Thermal Modeling**: Computes ambient cooling coefficients using real-time local wind velocity measurements weighted against thermal air stresses.

### 3. Predictive Load Balancing Engine
* **Automated Mitigation**: Scans the infrastructure mesh for nodes dropping below critical RUL boundaries (< 30 days).
* **Shedding Optimization**: Isolates available system headroom and smoothly steps down overstressed elements, rerouting power directly into under-utilized grid layers without dropping generation baseloads.

---

## 💻 Tech Stack
* **Language**: Python 3.10+
* **ML Framework**: Scikit-Learn (Random Forest Ensemble)
* **Data Processing**: NumPy, Pandas
* **UI Layer**: Streamlit Web Framework / Interactive Control Room CLI Terminal

---

## ⚙️ Installation & Workspace Setup

### 1. Clone the Project
```bash
git clone https://github.com
cd aptransco-grid-intelligence
```

### 2. Configure Your Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install numpy pandas scikit-learn streamlit
```

---

## 🚀 How to Run

### Option A: Interactive Streamlit Dashboard Engine
To run the high-performance, responsive live tracking interface:
```bash
streamlit run app.py
```

### Option B: Integrated Control Room Console Outflow
To start the standard telemetry streaming loop in a terminal session:
```bash
python grid_monitor.py
```

---

## 📁 System Parameters & Storage Outflow

### Financial Allocation Ledger (INR ₹)
The platform evaluates financial risk exposure and tracks capital preservation values in real time:


| Financial Cost Parameter | Allocated Value (INR) | Description |
| :--- | :--- | :--- |
| **COST_REPLACEMENT_GEN** | ₹4,50,00,000 | Total Generation Asset Unit Fail Capital |
| **COST_REPLACEMENT_TX** | ₹1,40,00,000 | Major Transmission Asset Fail Capital |
| **COST_LINE_REPAIR** | ₹22,00,000 | Local Distribution/Feeder Line Fix |
| **REGULATORY_FINE** | ₹1,80,00,000 | State Environmental & Safety Breach Fine |
| **EMERGENCY_LABOR_RATE** | ₹16,000 / hr | Reactive Breakdown Emergency Crew Rate |
| **PLANNED_LABOR_RATE** | ₹4,200 / hr | Proactive Preventive AI Dispatch Rate |

### Persistence Layer
On every pipeline cycle tick, the engine appends compressed telemetry and optimization logs directly into the centralized historical ledger file:
* **Output Path:** `ap_grid_unified_intelligence.csv`
* **Log Columns:** `timestamp`, `asset_id`, `level`, `temp_C`, `load_pct`, `predicted_rul`, `optimized_load_pct`, `reactive_risk_inr`, `net_saved_capital_inr`.

---

## 📄 License
This grid control system software is proprietary property. Licensed for authorized use inside **APTRANSCO and APSPDCL Power Systems Operations Control Centres (SLDC)**.

---
**Created by:** Srinivasta
