import numpy as np 
import pandas as pd 
import os 
import time 
from datetime import datetime, timedelta 
from sklearn.ensemble import RandomForestRegressor 
import streamlit as st

# Set up Streamlit Page Configurations
st.set_page_config(page_title="APSPDLC Grid Control", layout="wide", page_icon="⚡")

# ===================================================================== 
# 1. CORE PIPELINE INITIALIZATION (ML TRAINING - CACHED FOR SPEED) 
# ===================================================================== 
@st.cache_resource
def initialize_ml_model():
    np.random.seed(42) 
    h_records = 2000 
    h_temps = np.random.uniform(35.0, 115.0, h_records) 
    h_loads = np.random.uniform(40.0, 125.0, h_records) 
    h_health = np.random.uniform(15.0, 100.0, h_records) 
    
    t_rul = (h_health * 0.55) - (h_temps * 0.25) - (h_loads * 0.12) + 38 
    t_rul = np.clip(t_rul, 1, 90) + np.random.normal(0, 1.2, h_records) 
    
    model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1) 
    model.fit(pd.DataFrame({'temp_C': h_temps, 'load_pct': h_loads, 'insulation_health': h_health}), t_rul) 
    return model

ml_model = initialize_ml_model()

# Financial Parameters (INR ₹) 
COST_REPLACEMENT_TX = 14000000 
COST_LINE_REPAIR = 2200000 
REGULATORY_FINE = 18000000 
EMERGENCY_LABOR_RATE = 16000 
PLANNED_LABOR_RATE = 4200 
AI_SOFTWARE_OVERHEAD = 88000 
CSV_FILE_PATH = "ap_grid_live_telemetry.csv" 

# ===================================================================== 
# STREAMLIT UI LAYOUT STRUCTURE & SIDEBAR CONTROLS
# ===================================================================== 
st.title("⚡ APSPLDC Power Grid Control Room Monitor")
st.markdown("Real-time automated analytics pipeline with automated ML asset wear tracking and load balancing optimization.")

# Sidebar Settings Controls
st.sidebar.header("🕹️ System Loop Controls")
run_pipeline = st.sidebar.toggle("Activate Live Ingestion Engine", value=True)
refresh_speed = st.sidebar.slider("Refresh Interval (Seconds)", 1.0, 5.0, 2.0)

st.sidebar.markdown("---")
st.sidebar.header("🎛️ Dynamic Grid Thresholds")

ALERT_THRESHOLD = st.sidebar.slider(
    "Critical RUL Alert Threshold (Days)", 
    min_value=10.0, max_value=50.0, value=30.0, step=1.0,
    help="Assets with an ML-predicted Remaining Useful Life below this value trigger shedding routines."
)

SAFE_BASE = st.sidebar.slider(
    "Target Safe Base Load (%)", 
    min_value=50.0, max_value=80.0, value=70.0, step=1.0,
    help="The target load limit that a stressed asset will be forced down to during a shed event."
)

SAFE_CEILING = st.sidebar.slider(
    "Maximum Safety Ceiling Load (%)", 
    min_value=81.0, max_value=100.0, value=88.0, step=1.0,
    help="The maximum load percentage any healthy backup asset is allowed to accept during routing."
)

# ===================================================================== 
# LIVE DATA EXPORT & PURGE MANAGEMENT
# ===================================================================== 
st.sidebar.markdown("---")
st.sidebar.header("💾 Data Operations")

# Check if the telemetry log file exists and has data to offer
if os.path.exists(CSV_FILE_PATH):
    try:
        # Load a quick static snapshot of the database file for downloading
        export_df = pd.read_csv(CSV_FILE_PATH)
        csv_data = export_df.to_csv(index=False).encode('utf-8')
        
        st.sidebar.download_button(
            label="📥 Export Telemetry Log (CSV)",
            data=csv_data,
            file_name=f"ap_grid_telemetry_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Downloads the complete time-series database up to the current snapshot tick."
        )
    except Exception:
        st.sidebar.warning("Export engine preparing log buffers...")
else:
    st.sidebar.info("Waiting for data ingestion loop to generate logs...")

if st.sidebar.button("Wipe Telemetry History Log (CSV)"):
    if os.path.exists(CSV_FILE_PATH):
        os.remove(CSV_FILE_PATH)
        st.sidebar.success("CSV log file wiped successfully!")
        st.rerun()

# Set dynamic placeholders that persist through loop iterations
placeholder_meta = st.empty()
st.markdown("---")
st.subheader("📊 Real-Time Grid Node Status Matrix")
placeholder_table = st.empty()
st.markdown("---")

# Layout columns for interactive trending telemetry charts
st.subheader("📈 Historical Telemetry Performance Trends")
chart_col1, chart_col2 = st.columns(2)
placeholder_load_chart = chart_col1.empty()
placeholder_rul_chart = chart_col2.empty()

st.markdown("---")
st.subheader("💰 State Power Infrastructure Capital Ledger (INR ₹)")
col1, col2, col3 = st.columns(3)
metric_risk = col1.empty()
metric_cost = col2.empty()
metric_savings = col3.empty()

# ===================================================================== 
# 2. TIME-SYNCED MONITORING STREAM LOOP
# ===================================================================== 
if run_pipeline:
    if SAFE_BASE >= SAFE_CEILING:
        st.error("Configuration Error: Safe Base Load cannot be equal to or greater than the Maximum Safety Ceiling.")
        st.stop()

    loop_count = 0 
    while True: 
        loop_count += 1 
        
        # Sync with Indian Standard Time (IST) 
        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30) 
        timestamp = ist_time.strftime("%Y-%m-%d %H:%M:%S") 
        
        # Simulating live mid-day telemetry load volatility profiles 
        peak_hour_multiplier = 1.08 
        fluctuation = np.sin(loop_count * 0.4) * 5.0 
        random_noise = np.random.uniform(-2.0, 2.0) 
        
        # Real-Time Telemetry Data Matrix Array from AP Grid Nodes 
        ap_grid_nodes = [ 
            {"asset_id": "Simhadri_STPS_Transformer", "type": "wire", "temp_C": 101.0 + fluctuation + random_noise, "load_pct": (104.0 * peak_hour_multiplier) + fluctuation, "insulation_health": 42.10}, 
            {"asset_id": "Vizag_Industrial_Feeder", "type": "wire", "temp_C": 98.0 - fluctuation + random_noise, "load_pct": (102.5 * peak_hour_multiplier) - fluctuation, "insulation_health": 32.50}, 
            {"asset_id": "Vijayawada_Thermal_Link", "type": "wire", "temp_C": 103.0 + (fluctuation * 0.5), "load_pct": (107.0 * peak_hour_multiplier) + (fluctuation * 0.6), "insulation_health": 24.80}, 
            {"asset_id": "Kurnool_Solar_Interconnect", "type": "wire", "temp_C": 44.0 + random_noise, "load_pct": 58.0 + fluctuation, "insulation_health": 93.00}, 
            {"asset_id": "Rayalaseema_STPP_Line", "type": "wire", "temp_C": 46.0, "load_pct": 52.0, "insulation_health": 89.00}, 
            {"asset_id": "Amaravati_Storage_BESS", "type": "bess", "temp_C": 27.5, "load_pct": 15.0, "insulation_health": 99.0} 
        ] 
        
        live_grid_df = pd.DataFrame(ap_grid_nodes) 
        live_grid_df["timestamp"] = timestamp 
        
        # Compute ML Wear Lifecycle Model Predictions over streaming variables 
        live_grid_df["predicted_rul"] = ml_model.predict(live_grid_df[['temp_C', 'load_pct', 'insulation_health']]) 
        
        # Execute Network Control Load Balancing Algorithms
        balanced_grid_df = live_grid_df.copy() 
        stressed = balanced_grid_df[(balanced_grid_df["predicted_rul"] < ALERT_THRESHOLD) & (balanced_grid_df["type"] == "wire")] 
        
        for idx, row in stressed.iterrows(): 
            load_to_shed = row["load_pct"] - SAFE_BASE 
            while load_to_shed > 0.01: 
                balanced_grid_df['headroom'] = SAFE_CEILING - balanced_grid_df['load_pct'] 
                targets = balanced_grid_df[(balanced_grid_df["load_pct"] < SAFE_CEILING) & (balanced_grid_df["asset_id"] != row['asset_id'])] 
                if targets.empty: 
                    break 
                best_idx = targets['headroom'].idxmax() 
                transfer = min(load_to_shed, balanced_grid_df.loc[best_idx, 'headroom']) 
                balanced_grid_df.loc[idx, "load_pct"] -= transfer 
                balanced_grid_df.loc[best_idx, "load_pct"] += transfer 
                load_to_shed -= transfer 
                
        # Process Live Financial Protection Variables 
        r_costs, p_costs = 0, 0 
        for _, node in live_grid_df[(live_grid_df["predicted_rul"] < ALERT_THRESHOLD) & (live_grid_df["type"] == "wire")].iterrows(): 
            eq_loss = COST_REPLACEMENT_TX if "STPS" in node["asset_id"] or "Thermal" in node["asset_id"] else COST_LINE_REPAIR 
            r_costs += eq_loss + REGULATORY_FINE + (24 * EMERGENCY_LABOR_RATE) 
            p_costs += (8 * PLANNED_LABOR_RATE) + AI_SOFTWARE_OVERHEAD 
        net_savings = r_costs - p_costs 
        
        # ===================================================================== 
        # DATA STORAGE EXTRACTION SYSTEM (APPENDING TO CSV LOG) 
        # ===================================================================== 
        log_df = live_grid_df.copy() 
        log_df["optimized_load_pct"] = balanced_grid_df["load_pct"] 
        log_df["reactive_risk_inr"] = r_costs 
        log_df["predictive_cost_inr"] = p_costs 
        log_df["net_saved_capital_inr"] = net_savings 
        
        log_columns = [ 
            "timestamp", "asset_id", "type", "temp_C", "load_pct", 
            "insulation_health", "predicted_rul", "optimized_load_pct", 
            "reactive_risk_inr", "predictive_cost_inr", "net_saved_capital_inr" 
        ] 
        log_df = log_df[log_columns] 
        
        if not os.path.isfile(CSV_FILE_PATH): 
            log_df.to_csv(CSV_FILE_PATH, index=False, mode='w') 
        else: 
            log_df.to_csv(CSV_FILE_PATH, index=False, mode='a', header=False) 
            
        # ===================================================================== 
        # UPDATE LIVE STREAMLIT UI COMPONENTS 
        # ===================================================================== 
        placeholder_meta.markdown(f"⏱️ **SNAPSHOT TICK:** #{loop_count} &nbsp;|&nbsp; 🕒 **INDIAN STANDARD TIME (IST):** `{timestamp}` &nbsp;|&nbsp; ⚠️ **SAFE CEILING LIMIT:** `{SAFE_CEILING}% Load` &nbsp;|&nbsp; 🛑 **ALERT BOUNDARY:** `< {ALERT_THRESHOLD} Days RUL`")
        
        # Style Dataframe rows conditionally based on dynamically adjusted RUL alert variable
        def style_rows(row):
            if row['predicted_rul'] < ALERT_THRESHOLD and row['type'] == 'wire':
                return ['background-color: #ffcccc'] * len(row)
            return [''] * len(row)
            
        display_df = log_df.copy()
        styled_df = display_df.style.apply(style_rows, axis=1).format({
            'temp_C': '{:.2f}°C',
            'load_pct': '{:.1f}%',
            'optimized_load_pct': '{:.1f}%',
            'predicted_rul': '{:.1f} Days'
        })
        
        placeholder_table.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # ===================================================================== 
        # GENERATE INTERACTIVE TIME-SERIES LINE CHARTS 
        # ===================================================================== 
        try:
            history_df = pd.read_csv(CSV_FILE_PATH)
            load_history = history_df.pivot(index='timestamp', columns='asset_id', values='load_pct')
            rul_history = history_df.pivot(index='timestamp', columns='asset_id', values='predicted_rul')
            
            placeholder_load_chart.markdown("**Live Real-Time Asset Load Percentage History Over Time (%)**")
            placeholder_load_chart.line_chart(load_history.tail(30))
            
            placeholder_rul_chart.markdown("**ML Predicted Asset Remaining Useful Life (RUL - Days)**")
            placeholder_rul_chart.line_chart(rul_history.tail(30))
        except Exception:
            pass 
            
        # Output financial ledger components onto active view layers
        metric_risk.metric(label="Total Unmitigated Exposure Risk", value=f"₹{r_costs:,.2f}")
        metric_cost.metric(label="Managed AI Operations Cost", value=f"₹{p_costs:,.2f}")
        metric_savings.metric(label="NET Protected Public Savings", value=f"₹{net_savings:,.2f}")
        
        time.sleep(refresh_speed)
else:
    st.info("Ingestion Engine Paused. Toggle the switch on the sidebar to resume pipeline streaming loops.")
