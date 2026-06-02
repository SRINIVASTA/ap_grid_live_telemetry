import numpy as np 
import pandas as pd 
import os 
import sys 
import time 
import streamlit as st 
from datetime import datetime, timezone, timedelta 
from sklearn.ensemble import RandomForestRegressor 
import warnings 

# Silencing layout deprecations 
warnings.filterwarnings("ignore", category=DeprecationWarning) 

# ===================================================================== 
# 0. GLOBAL UTILITY CONFIGURATIONS & FORMATTERS (OS-Independent)
# ===================================================================== 
def format_indian_currency(amount):
    try:
        s = f"{float(amount):.2f}"
        parts = s.split('.')
        num_part = parts[0]
        dec_part = parts[1]
        
        if len(num_part) <= 3:
            return f"{num_part}.{dec_part}"
            
        last_three = num_part[-3:]
        remaining = num_part[:-3]
        
        out = ""
        while len(remaining) > 2:
            out = "," + remaining[-2:] + out
            remaining = remaining[:-2]
        if remaining:
            out = remaining + out
            
        return f"{out},{last_three}.{dec_part}"
    except (ValueError, TypeError):
        return "0.00"

# Initialize persistence containers inside session state to prevent empty drops
if "loop_count" not in st.session_state:
    st.session_state.loop_count = 0
if "r_costs" not in st.session_state:
    st.session_state.r_costs = 0.0
if "p_costs" not in st.session_state:
    st.session_state.p_costs = 0.0
if "net_savings" not in st.session_state:
    st.session_state.net_savings = 0.0

# ===================================================================== 
# 1. CORE PIPELINE INITIALIZATION (MULTI-MODAL ML TRAINING) 
# ===================================================================== 
np.random.seed(42) 
h_records = 2500 

h_temps = np.random.uniform(35.0, 115.0, h_records) 
h_loads = np.random.uniform(40.0, 125.0, h_records) 
h_health = np.random.uniform(15.0, 100.0, h_records) 
h_veg_dist = np.random.uniform(0.2, 15.0, h_records) 
h_sag_cm = np.random.uniform(0.0, 60.0, h_records) 
h_ambient_c = np.random.uniform(22.0, 45.0, h_records) 

t_rul = (h_health * 0.50) - (h_temps * 0.20) - (h_loads * 0.10) - (h_sag_cm * 0.15) + (h_veg_dist * 0.4) + 35 
t_rul = np.clip(t_rul, 1, 90) + np.random.normal(0, 1.0, h_records) 

ml_features = ['temp_C', 'load_pct', 'insulation_health', 'veg_distance_m', 'conductor_sag_cm', 'ambient_temp_C'] 
X_train = pd.DataFrame({ 
    'temp_C': h_temps, 'load_pct': h_loads, 'insulation_health': h_health, 
    'veg_distance_m': h_veg_dist, 'conductor_sag_cm': h_sag_cm, 'ambient_temp_C': h_ambient_c 
}) 
ml_model = RandomForestRegressor(n_estimators=60, random_state=42, n_jobs=-1) 
ml_model.fit(X_train, t_rul) 

SAFE_BASE = 70.0 
ALERT_THRESHOLD = 30.0 

def calculate_dynamic_ceiling(ambient_temp, wind_speed): 
    base_ceiling = 86.0 
    thermal_cooling_effect = (wind_speed * 0.75) - ((ambient_temp - 30.0) * 0.2) 
    return float(np.clip(base_ceiling + thermal_cooling_effect, 76.0, 96.0))

COST_REPLACEMENT_GEN = 45000000 
COST_REPLACEMENT_TX = 14000000 
COST_LINE_REPAIR = 2200000 
REGULATORY_FINE = 18000000 
EMERGENCY_LABOR_RATE = 16000 
PLANNED_LABOR_RATE = 4200 
AI_SOFTWARE_OVERHEAD = 88000 
CSV_FILE_PATH = "ap_grid_unified_intelligence.csv" 

# Setup layout parameters
st.set_page_config(page_title="APTRANSCO Control Monitor", layout="wide")
header_area = st.empty()
alert_area = st.empty()
table_area = st.empty()
ledger_area = st.empty()

# ===================================================================== 
# 2. TIME-SYNCED INGESTION LOOP & DYNAMIC BALANCING ENGINE 
# ===================================================================== 
try: 
    st.session_state.loop_count += 1 
    
    ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30) 
    timestamp = ist_time.strftime("%Y-%m-%d %H:%M:%S") 
    
    fluctuation = np.sin(st.session_state.loop_count * 0.4) * 5.0 
    random_noise = np.random.uniform(-1.5, 1.5) 
    cur_wind = np.random.uniform(2.0, 14.0) 
    cur_ambient = np.random.uniform(32.0, 42.0) 
    
    DYNAMIC_SAFE_CEILING = calculate_dynamic_ceiling(cur_ambient, cur_wind) 
    peak_hour_multiplier = 1.08 
    
    ap_grid_nodes = [ 
        {"asset_id": "Simhadri_STPS_Gen_Unit1", "level": "Generation", "temp_C": 102.0 + fluctuation, 
         "load_pct": (103.0 * peak_hour_multiplier) + fluctuation, "insulation_health": 41.5, 
         "veg_distance_m": 15.0, "conductor_sag_cm": 0.0, "ambient_temp_C": cur_ambient}, 
        {"asset_id": "Vijayawada_Thermal_Link", "level": "Generation", "temp_C": 104.5 + (fluctuation * 0.5), 
         "load_pct": (106.5 * peak_hour_multiplier) + (fluctuation * 0.4), "insulation_health": 22.1, 
         "veg_distance_m": 12.0, "conductor_sag_cm": 0.0, "ambient_temp_C": cur_ambient}, 
        {"asset_id": "Rayalaseema_STPP_Line", "level": "Transmission", "temp_C": 52.0 + random_noise, 
         "load_pct": 74.0 + fluctuation, "insulation_health": 82.0, "veg_distance_m": 2.1, 
         "conductor_sag_cm": 38.5, "ambient_temp_C": cur_ambient}, 
        {"asset_id": "Kurnool_Solar_Interconnect", "level": "Transmission", "temp_C": 44.0 + random_noise, 
         "load_pct": 58.0 + fluctuation, "insulation_health": 93.0, "veg_distance_m": 8.5, 
         "conductor_sag_cm": 12.0, "ambient_temp_C": cur_ambient}, 
        {"asset_id": "Vizag_Industrial_Feeder", "level": "Distribution", "temp_C": 98.0 - fluctuation + random_noise, 
         "load_pct": (101.5 * peak_hour_multiplier) - fluctuation, "insulation_health": 31.0, 
         "veg_distance_m": 4.5, "conductor_sag_cm": 18.0, "ambient_temp_C": cur_ambient}, 
        {"asset_id": "Amaravati_Storage_BESS", "level": "Distribution", "type": "bess", "temp_C": 26.5, 
         "load_pct": 20.0, "insulation_health": 99.0, "veg_distance_m": 15.0, "conductor_sag_cm": 0.0, 
         "ambient_temp_C": cur_ambient} 
    ] 
    
    live_grid_df = pd.DataFrame(ap_grid_nodes) 
    live_grid_df["timestamp"] = timestamp 
    live_grid_df["predicted_rul"] = ml_model.predict(live_grid_df[ml_features]) 
    
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
    
    local_r_costs = 0
    local_p_costs = 0
    field_dispatches = []
    
    for _, node in live_grid_df[live_grid_df["predicted_rul"] < ALERT_THRESHOLD].iterrows(): 
        if node["level"] == "Generation": 
            eq_loss = COST_REPLACEMENT_GEN 
        elif "STPP" in node["asset_id"] or "Interconnect" in node["asset_id"]: 
            eq_loss = COST_REPLACEMENT_TX 
        else: 
            eq_loss = COST_LINE_REPAIR 
        
        local_r_costs += eq_loss + REGULATORY_FINE + (24 * EMERGENCY_LABOR_RATE) 
        local_p_costs += (8 * PLANNED_LABOR_RATE) + AI_SOFTWARE_OVERHEAD 

        field_dispatches.append({ 
            "asset_id": node["asset_id"], 
            "tier": node["level"], 
            "rul": node["predicted_rul"], 
            "guidance": "Schedule targeted insulation verification." if node["insulation_health"] < 40 else "Deploy clearance crews for vegetation/sag hazard removal." 
        })
    
    st.session_state.r_costs = local_r_costs
    st.session_state.p_costs = local_p_costs
    st.session_state.net_savings = max(0, local_r_costs - local_p_costs)

    # ===================================================================== 
    # 3. UNIFIED OPERATOR VIEW & INTEGRATED CONTROL ROOM OUTFLOW 
    # ===================================================================== 
    r_costs_str = format_indian_currency(st.session_state.r_costs)
    p_costs_str = format_indian_currency(st.session_state.p_costs)
    net_savings_str = format_indian_currency(st.session_state.net_savings)

    with header_area.container():
        st.title("⚡ APTRANSCO Smart Grid Control Monitor")
        st.caption(f"**Tick Sequence ID:** #{st.session_state.loop_count} | **Timestamp (IST):** {timestamp}")
        st.info(f"🎯 **Adaptive Dynamic Safety Ceiling Limit:** {DYNAMIC_SAFE_CEILING:.1f}% Load Capacity")

    with alert_area.container():
        if field_dispatches:
            st.error(f"🚨 **CRITICAL EMERGENCY ALERT**: {len(field_dispatches)} Anomalies Found!")
            for alert in field_dispatches:
                st.warning(f"⚠️ **[{alert['tier'].upper()} RISK]** {alert['asset_id']} ➜ RUL: {alert['rul']:.1f} Days. *Guidance:* {alert['guidance']}")
        else:
            st.success("✅ All state grid infrastructure metrics currently operating within normal engineering metrics.")

    with table_area.container():
        st.subheader("📊 Live Mesh Node Status Telemetry")
        display_df = pd.DataFrame({
            "Asset Identification": live_grid_df["asset_id"],
            "Layer Tier": live_grid_df["level"],
            "Telemetry Temp (°C)": live_grid_df["temp_C"].round(1),
            "Unmanaged Load %": live_grid_df["load_pct"].round(2),
            "AI Balanced Load %": balanced_grid_df["load_pct"].round(2),
            "Predicted RUL (Days)": live_grid_df["predicted_rul"].round(1)
        })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    with ledger_area.container():
        st.markdown("### 💰 STATE POWER INFRASTRUCTURE CAPITAL PROTECTION INTEGRATED LEDGER")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(label="Total Unmitigated Breakdown Risk Exposure", value=f"₹ {r_costs_str}")
        with m_col2:
            st.metric(label="Managed AI Proactive Operations Cost", value=f"₹ {p_costs_str}")
        with m_col3:
            st.metric(label="NET CURRENT PROTECTED STATE SAVINGS", value=f"₹ {net_savings_str}")

        st.code(
            f"STATE POWER INFRASTRUCTURE CAPITAL PROTECTION INTEGRATED LEDGER\n"
            f" ├─ Total Unmitigated Breakdown Risk Exposure : ₹{r_costs_str}\n"
            f" ├─ Managed AI Proactive Operations Cost      : ₹{p_costs_str}\n"
            f" └─ NET CURRENT PROTECTED STATE SAVINGS       : ₹{net_savings_str}",
            language="text"
        )

    # Log values to persistent local disk file
    summary_data = live_grid_df.copy()
    summary_data["ai_balanced_load_pct"] = balanced_grid_df["load_pct"]
    summary_data["net_savings_inr"] = st.session_state.net_savings
    
    file_exists = os.path.isfile(CSV_FILE_PATH)
    summary_data.to_csv(CSV_FILE_PATH, mode='a', header=not file_exists, index=False)

    time.sleep(2.5) 
    st.rerun()

except Exception as pipeline_error:
    st.error(f"Operational pipeline runtime tracking paused: {pipeline_error}")
