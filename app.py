import numpy as np 
import pandas as pd 
import os 
import sys 
import time 
import streamlit as st
from datetime import datetime, timezone, timedelta
from sklearn.ensemble import RandomForestRegressor 
# from IPython.display import clear_output 
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


# ===================================================================== 
# 1. CORE PIPELINE INITIALIZATION (MULTI-MODAL ML TRAINING) 
# ===================================================================== 
print("Initializing Enhanced Multi-Tiered Asset Intelligence Environment...") 
np.random.seed(42) 
h_records = 2500 

# Multi-Modal Feature Synthesis: Telemetry, Drone Imagery Analytics, and Weather Sensors
h_temps = np.random.uniform(35.0, 115.0, h_records) 
h_loads = np.random.uniform(40.0, 125.0, h_records) 
h_health = np.random.uniform(15.0, 100.0, h_records) 
h_veg_dist = np.random.uniform(0.2, 15.0, h_records)       # Drone Anomaly Detection (m)
h_sag_cm = np.random.uniform(0.0, 60.0, h_records)          # Drone Physical Anomaly (cm)
h_ambient_c = np.random.uniform(22.0, 45.0, h_records)      # IoT Environmental Condition

# Degradation Formula updated to account for Drone + Weather factors
t_rul = (h_health * 0.50) - (h_temps * 0.20) - (h_loads * 0.10) - (h_sag_cm * 0.15) + (h_veg_dist * 0.4) + 35
t_rul = np.clip(t_rul, 1, 90) + np.random.normal(0, 1.0, h_records) 

# Train Multi-Modal Asset Health Regressor Model
ml_features = ['temp_C', 'load_pct', 'insulation_health', 'veg_distance_m', 'conductor_sag_cm', 'ambient_temp_C']
X_train = pd.DataFrame({
    'temp_C': h_temps, 'load_pct': h_loads, 'insulation_health': h_health,
    'veg_distance_m': h_veg_dist, 'conductor_sag_cm': h_sag_cm, 'ambient_temp_C': h_ambient_c
})
ml_model = RandomForestRegressor(n_estimators=60, random_state=42, n_jobs=-1) 
ml_model.fit(X_train, t_rul) 

# Core Operational Safety Boundaries
SAFE_BASE = 70.0 
ALERT_THRESHOLD = 30.0 

# Dynamic Line Rating (DLR) Logic: Optimizes lines based on cooling wind vs ambient heat
def calculate_dynamic_ceiling(ambient_temp, wind_speed):
    base_ceiling = 86.0
    thermal_cooling_effect = (wind_speed * 0.75) - ((ambient_temp - 30.0) * 0.2)
    return float(np.clip(base_ceiling + thermal_cooling_effect, 76.0, 96.0))

# Financial System Parameters (INR ₹) 
COST_REPLACEMENT_GEN = 45000000
COST_REPLACEMENT_TX = 14000000 
COST_LINE_REPAIR = 2200000 
REGULATORY_FINE = 18000000 
EMERGENCY_LABOR_RATE = 16000 
PLANNED_LABOR_RATE = 4200 
AI_SOFTWARE_OVERHEAD = 88000 

CSV_FILE_PATH = "ap_grid_unified_intelligence.csv" 

# ===================================================================== 
# 2. TIME-SYNCED INGESTION LOOP & DYNAMIC BALANCING ENGINE 
# ===================================================================== 
print(f"Live Multi-Modal Ingestion Engine Active. Destination Database: {CSV_FILE_PATH}") 
time.sleep(1.5) 

try: 
    loop_count = 0 
    while True: 
        loop_count += 1 
        
        # Indian Standard Time (IST) Synchronization
        ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30) 
        timestamp = ist_time.strftime("%Y-%m-%d %H:%M:%S")

        # Simulating fluctuations, environmental dynamics, and drone anomaly ticks
        fluctuation = np.sin(loop_count * 0.4) * 5.0 
        random_noise = np.random.uniform(-1.5, 1.5) 
        cur_wind = np.random.uniform(2.0, 14.0)          # Live IoT sensor: Wind Speed (m/s)
        cur_ambient = np.random.uniform(32.0, 42.0)       # Live IoT sensor: Ambient Temp (°C)
        
        # Compute Dynamic Safety Limit for this specific timestamp context
        DYNAMIC_SAFE_CEILING = calculate_dynamic_ceiling(cur_ambient, cur_wind)
        peak_hour_multiplier = 1.08 

        # Unified Network Representation: Generation, Transmission, and Distribution Layers
        ap_grid_nodes = [ 
            {"asset_id": "Simhadri_STPS_Gen_Unit1", "level": "Generation", "temp_C": 102.0 + fluctuation, "load_pct": (103.0 * peak_hour_multiplier) + fluctuation, "insulation_health": 41.5, "veg_distance_m": 15.0, "conductor_sag_cm": 0.0, "ambient_temp_C": cur_ambient}, 
            {"asset_id": "Vijayawada_Thermal_Link", "level": "Generation", "temp_C": 104.5 + (fluctuation * 0.5), "load_pct": (106.5 * peak_hour_multiplier) + (fluctuation * 0.4), "insulation_health": 22.1, "veg_distance_m": 12.0, "conductor_sag_cm": 0.0, "ambient_temp_C": cur_ambient}, 
            {"asset_id": "Rayalaseema_STPP_Line", "level": "Transmission", "temp_C": 52.0 + random_noise, "load_pct": 74.0 + fluctuation, "insulation_health": 82.0, "veg_distance_m": 2.1, "conductor_sag_cm": 38.5, "ambient_temp_C": cur_ambient}, 
            {"asset_id": "Kurnool_Solar_Interconnect", "level": "Transmission", "temp_C": 44.0 + random_noise, "load_pct": 58.0 + fluctuation, "insulation_health": 93.0, "veg_distance_m": 8.5, "conductor_sag_cm": 12.0, "ambient_temp_C": cur_ambient}, 
            {"asset_id": "Vizag_Industrial_Feeder", "level": "Distribution", "temp_C": 98.0 - fluctuation + random_noise, "load_pct": (101.5 * peak_hour_multiplier) - fluctuation, "insulation_health": 31.0, "veg_distance_m": 4.5, "conductor_sag_cm": 18.0, "ambient_temp_C": cur_ambient}, 
            {"asset_id": "Amaravati_Storage_BESS", "level": "Distribution", "type": "bess", "temp_C": 26.5, "load_pct": 20.0, "insulation_health": 99.0, "veg_distance_m": 15.0, "conductor_sag_cm": 0.0, "ambient_temp_C": cur_ambient} 
        ] 
        
        live_grid_df = pd.DataFrame(ap_grid_nodes) 
        live_grid_df["timestamp"] = timestamp 
        
        # Execute ML Prediction over Multi-Modal Variables
        live_grid_df["predicted_rul"] = ml_model.predict(live_grid_df[ml_features]) 
        
        # Predictive Network Load Balancing Execution
        balanced_grid_df = live_grid_df.copy() 
        stressed = balanced_grid_df[(balanced_grid_df["predicted_rul"] < ALERT_THRESHOLD) & (balanced_grid_df["level"] != "Generation")] 
        
        for idx, row in stressed.iterrows(): 
            load_to_shed = row["load_pct"] - SAFE_BASE 
            while load_to_shed > 0.01: 
                balanced_grid_df['headroom'] = DYNAMIC_SAFE_CEILING - balanced_grid_df['load_pct'] 
                targets = balanced_grid_df[(balanced_grid_df["load_pct"] < DYNAMIC_SAFE_CEILING) & (balanced_grid_df["asset_id"] != row['asset_id'])] 
                if targets.empty: 
                    break 
                best_idx = targets['headroom'].idxmax() 
                transfer = min(load_to_shed, balanced_grid_df.loc[best_idx, 'headroom']) 
                balanced_grid_df.loc[idx, "load_pct"] -= transfer 
                balanced_grid_df.loc[best_idx, "load_pct"] += transfer 
                load_to_shed -= transfer 
        
        # Calculate Real-Time Ledger Values based on Grid Tier Classifications
        r_costs, p_costs = 0, 0 
        field_dispatches = []
        
        for _, node in live_grid_df[live_grid_df["predicted_rul"] < ALERT_THRESHOLD].iterrows(): 
            if node["level"] == "Generation":
                eq_loss = COST_REPLACEMENT_GEN
            elif "STPP" in node["asset_id"] or "Interconnect" in node["asset_id"]:
                eq_loss = COST_REPLACEMENT_TX
            else:
                eq_loss = COST_LINE_REPAIR
                
            r_costs += eq_loss + REGULATORY_FINE + (24 * EMERGENCY_LABOR_RATE) 
            p_costs += (8 * PLANNED_LABOR_RATE) + AI_SOFTWARE_OVERHEAD 
            
            # Generate Real-Time Machine-to-Field Guideline Objects
            field_dispatches.append({
                "asset_id": node["asset_id"],
                "tier": node["level"],
                "rul": node["predicted_rul"],
                "guidance": "Schedule targeted insulation verification." if node["insulation_health"] < 40 else "Deploy clearance crews for vegetation/sag hazard removal."
            })
            
        net_savings = max(0, r_costs - p_costs) 
        
        # Compile Comprehensive Data Logs for CSV Persistence
        log_df = live_grid_df.copy() 
        log_df["optimized_load_pct"] = balanced_grid_df["load_pct"] 
        log_df["reactive_risk_inr"] = r_costs 
        log_df["predictive_cost_inr"] = p_costs 
        log_df["net_saved_capital_inr"] = net_savings 
        
        log_columns = [ 
            "timestamp", "asset_id", "level", "temp_C", "load_pct", 
            "predicted_rul", "optimized_load_pct", "reactive_risk_inr", "net_saved_capital_inr" 
        ] 
        log_df = log_df[log_columns] 
        if not os.path.isfile(CSV_FILE_PATH): 
            log_df.to_csv(CSV_FILE_PATH, index=False, mode='w') 
        else: 
            log_df.to_csv(CSV_FILE_PATH, index=False, mode='a', header=False) 
            
        # ===================================================================== 
        # 3. UNIFIED OPERATOR VIEW & INTEGRATED CONTROL ROOM OUTFLOW 
        # ===================================================================== 
        # clear_output(wait=True) 
        print("=" * 110) 
        print(f"⚡ APSPDCL/APTRANSCO INTEGRATED CONTROL MONITOR | TICK #{loop_count}") 
        print(f"🕒 TIMESTAMP (IST): {timestamp} | DLR ENVIRONMENT: Wind {cur_wind:.1f} m/s, Amb {cur_ambient:.1f}°C")
        print(f"🔒 ADAPTIVE DYNAMIC SAFETY CEILING LIMIT: {DYNAMIC_SAFE_CEILING:.1f}% Load Capacity")
        print("=" * 110) 
        print(f"{'Asset System ID':<28} | {'Grid Tier':<12} | {'Temp (°C)':<9} | {'Raw Load %':<10} | {'Opt Load %':<10} | {'Est RUL (Days)':<13}") 
        print("-" * 110) 
        
        for _, row in log_df.iterrows(): 
            print(f"{row['asset_id']:<28} | {row['level']:<12} | {row['temp_C']:<9.1f} | {row['load_pct']:<10.1f} | {row['optimized_load_pct']:<10.1f} | {row['predicted_rul']:<13.1f}") 
            
        print("-" * 110) 
        print("🚨 REAL-TIME AI-ASSISTED FIELD DISPATCH & TECHNICIAN ALERTS INTERFACE")
        if not field_dispatches:
            print("  🎉 System Healthy. No active critical degradation vectors detected.")
        else:
            # Pushed to the right inside the else block
            for alert in field_dispatches:
                print(f"  ⚡ [{alert['tier'].upper()} RISK] {alert['asset_id']} -> RUL: {alert['rul']:.1f} Days. Guidance: {alert['guidance']}")
            
        print("-" * 110)
        print(f"💰 STATE POWER INFRASTRUCTURE CAPITAL PROTECTION INTEGRATED LEDGER")
        print(f"  ├─ Total Unmitigated Breakdown Risk Exposure : ₹{r_costs:,.2f}")
        print(f"  ├─ Managed AI Proactive Operations Cost      : ₹{p_costs:,.2f}")
        print(f"  └─ NET CURRENT PROTECTED STATE SAVINGS       : ₹{net_savings:,.2f}")
        print("=" * 110)
        print(" Pipeline executing smoothly. Persistent logs writing to 'ap_grid_unified_intelligence.csv'.")
        
        time.sleep(2.5)
        
except KeyboardInterrupt:
    print(f"\n Unified multi-tier monitoring loop safely paused. All compiled metrics saved inside '{CSV_FILE_PATH}'.")
