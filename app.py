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
    """
    Formats large financial values into highly scannable, condensed 
    Indian shortcodes (Cr. for Crores, L. for Lakhs) matching Power BI visual standards.
    """
    try:
        val = float(amount)
        if val >= 10000000: # 1 Crore or more
            return f"{val / 10000000:.2f} Cr"
        elif val >= 100000: # 1 Lakh or more
            return f"{val / 100000:.2f} L"
        else:
            # Standard formatting for smaller overheads/labor numbers
            s = f"{val:.2f}"
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
    except (ValueError, TypeError, IndexError):
        return "0.00"

def format_indian_currency(amount):
    """
    Pure-Python OS-Independent Formatter for Indian Standard Currency Notation.
    Groupings: Thousands base digit split followed by Lakhs and Crores pairs.
    """
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
    except (ValueError, TypeError, IndexError):
        return "0.00"

# Initialize persistence containers inside session state to prevent empty drops across reruns
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

# Multi-Modal Feature Synthesis: Telemetry, Drone Imagery Analytics, and Weather Sensors 
h_temps = np.random.uniform(35.0, 115.0, h_records) 
h_loads = np.random.uniform(40.0, 125.0, h_records) 
h_health = np.random.uniform(15.0, 100.0, h_records) 
h_veg_dist = np.random.uniform(0.2, 15.0, h_records) # Drone Anomaly Detection (m) 
h_sag_cm = np.random.uniform(0.0, 60.0, h_records) # Drone Physical Anomaly (cm) 
h_ambient_c = np.random.uniform(22.0, 45.0, h_records) # IoT Environmental Condition 

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

# Initialize Streamlit Layout Configuration
st.set_page_config(page_title="APTRANSCO Power BI Control Analytics", layout="wide")

# ─── POWER BI SIDEBAR PANEL SLICER ───
with st.sidebar:
    st.image("https://icons8.com", width=50)
    st.title("Report Slicers")
    st.markdown("---")
    
    # Interactive multi-select grid filtering slicer
    selected_tier = st.multiselect(
        "Grid Operational Layer Selection",
        options=["Generation", "Transmission", "Distribution"],
        default=["Generation", "Transmission", "Distribution"]
    )
    
    st.markdown("---")
    pause_feed = st.toggle("⏸️ Pause Live Ingestion Stream", value=False)
    
    # Administrative Actions Data Purge
    if st.button("🗑️ Clear Historic Ledger Storage", use_container_width=True):
        if os.path.exists(CSV_FILE_PATH):
            os.remove(CSV_FILE_PATH)
            st.success("Ledger database successfully reset!")
            time.sleep(1)
            st.rerun()

# Build Persistent Empty App Display Canvas Layout Areas
header_area = st.empty()
kpi_cards_area = st.empty()
main_layout_area = st.empty()

# ===================================================================== 
# 2. TIME-SYNCED INGESTION LOOP & DYNAMIC BALANCING ENGINE 
# ===================================================================== 
try: 
    if not pause_feed:
        st.session_state.loop_count += 1 
    
    # Indian Standard Time (IST) Synchronization
    ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30) 
    timestamp = ist_time.strftime("%Y-%m-%d %H:%M:%S") 
    
    # Simulating fluctuations, environmental dynamics, and drone anomaly ticks 
    fluctuation = np.sin(st.session_state.loop_count * 0.4) * 5.0 
    random_noise = np.random.uniform(-1.5, 1.5) 
    cur_wind = np.random.uniform(2.0, 14.0) # Live IoT sensor: Wind Speed (m/s) 
    cur_ambient = np.random.uniform(32.0, 42.0) # Live IoT sensor: Ambient Temp (°C) 
    
    # Compute Dynamic Safety Limit for this specific timestamp context 
    DYNAMIC_SAFE_CEILING = calculate_dynamic_ceiling(cur_ambient, cur_wind) 
    peak_hour_multiplier = 1.08 
    
    # Unified Network Representation: Generation, Transmission, and Distribution Layers 
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
        
        # Generate Real-Time Machine-to-Field Guideline Objects 
        field_dispatches.append({ 
            "asset_id": node["asset_id"], 
            "tier": node["level"], 
            "rul": node["predicted_rul"],
            "guidance": "Schedule targeted insulation verification." if node["insulation_health"] < 40 else "Deploy clearance crews for vegetation/sag hazard removal."
        })

    # Sync calculations directly to Streamlit memory context to prevent data reset drop
    if not pause_feed:
        st.session_state.r_costs = local_r_costs
        st.session_state.p_costs = local_p_costs
        st.session_state.net_savings = max(0, local_r_costs - local_p_costs)

    # Apply Slicer Filters onto active displayed collections
    filtered_live_df = live_grid_df[live_grid_df["level"].isin(selected_tier)]
    filtered_balanced_df = balanced_grid_df[balanced_grid_df["level"].isin(selected_tier)]

    # Parse formatted localized display currency strings
    r_costs_str = format_indian_currency(st.session_state.r_costs)
    p_costs_str = format_indian_currency(st.session_state.p_costs)
    net_savings_str = format_indian_currency(st.session_state.net_savings)

    # =====================================================================
    # 3. UNIFIED OPERATOR VIEW & INTEGRATED CONTROL ROOM OUTFLOW
    # =====================================================================
    
    # ─── POWER BI BANNER NAVIGATION HEADER & INJECTED STYLES ───
    with header_area.container():
        # FIXED ALL TYPOS: Set explicitly to 'unsafe_allow_html=True' parameters
        st.markdown("""
            <style>
            .stApp { background-color: #F3F4F6; }
            div[data-testid="stMetricBlock"] {
                background-color: #FFFFFF !important;
                border-radius: 6px !important;
                padding: 15px !important;
                box-shadow: 0px 2px 4px rgba(0,0,0,0.05) !important;
                border-left: 5px solid #118DFF !important; /* Power BI Accent Blue */
            }
            div[data-testid="stMetricBlock"] label { font-weight: bold !important; color: #4B5563 !important; }
            .powerbi-card {
                background-color: #FFFFFF;
                border-radius: 6px;
                padding: 20px;
                box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
                margin-bottom: 20px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background-color: #1F2937; padding: 15px; border-radius: 6px; margin-bottom: 20px; color: #FFFFFF;">
                <h2 style='margin: 0; color: #FFFFFF; font-size: 24px;'>⚡ APTRANSCO Smart Grid Executive Report</h2>
                <p style='margin: 5px 0 0 0; font-size: 13px; color: #9CA3AF;'>
                    <b>Report Sync Timestamp:</b> {timestamp} (IST) | <b>Adaptive Dynamic Ceiling Limit:</b> {DYNAMIC_SAFE_CEILING:.1f}% Load Capacity | <b>Active Cycle Tick:</b> #{st.session_state.loop_count}
                </p>
            </div>
        """, unsafe_allow_html=True)

    # ─── POWER BI TOP ROW HIGHLIGHT METRICS ───
    with kpi_cards_area.container():
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Total Breakdown Financial Risk", f"₹ {r_costs_str}")
        m_col2.metric("Managed AI Proactive Fix Cost", f"₹ {p_costs_str}")
        m_col3.metric("NET PROTECTED STATE CAPITAL", f"₹ {net_savings_str}")
        
        # FIXED: Removed the accidental extra space to perfectly align with the metrics layout above
        avg_health = filtered_live_df["predicted_rul"].mean() if not filtered_live_df.empty else 90.0
        m_col4.metric(
            "Grid System Health Index", 
            f"{avg_health:.1f} RUL Days", 
            delta="Healthy" if avg_health > 45 else "Action Needed", 
            delta_color="normal" if avg_health > 45 else "inverse"
        )

    # ─── POWER BI CENTRAL DASHBOARD LAYOUT ───
    with main_layout_area.container():
        left_panel, right_panel = st.columns((5, 3))
        
        with left_panel:
            st.markdown("<div class='powerbi-card'>", unsafe_allow_html=True)
            st.subheader("📊 Live Grid Asset Cross-Tabular Matrix")
            
            display_df = pd.DataFrame({
                "Asset Tracking ID": filtered_live_df["asset_id"],
                "Operational Layer Tier": filtered_live_df["level"],
                "Thermal Telemetry (°C)": filtered_live_df["temp_C"].round(1),
                "Raw Demand Load %": filtered_live_df["load_pct"].round(2),
                "AI Optimized Load %": filtered_balanced_df["load_pct"].round(2),
                "Est. Health RUL (Days)": filtered_live_df["predicted_rul"].round(1)
            })
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # --- INTERACTIVE DATA LEDGER FILE EXPORT LAYER ---
            if os.path.isfile(CSV_FILE_PATH):
                @st.cache_data(ttl=2.0)
                def convert_df_to_bytes(path):
                    with open(path, "rb") as f:
                        return f.read()
                csv_bytes = convert_df_to_bytes(CSV_FILE_PATH)
                st.download_button(
                    label="📥 Export Live Intelligence Ledger Data (.CSV)",
                    data=csv_bytes,
                    file_name=f"ap_grid_bi_ledger_{timestamp.replace(' ', '_').replace(':', '-')}.csv",
                    mime="text/csv",
                    key="bi_ledger_download_trigger",
                    use_container_width=True
                )
            st.markdown("</div>", unsafe_allow_html=True)
            
        with right_panel:
            st.markdown("<div class='powerbi-card'>", unsafe_allow_html=True)
            st.subheader("🚨 Real-Time Action Dispatches")
            
            if field_dispatches:
                for idx, alert in enumerate(field_dispatches):
                    if alert["asset_id"] in filtered_live_df["asset_id"].values:
                        st.markdown(f"""
                            <div style="background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
                                <strong style="color: #991B1B;">⚠️ {alert['asset_id']}</strong><br/>
                                <small style="color: #B91C1C;">Layer: {alert['tier']} | Est. RUL: {alert['rul']:.1f} Days</small><br/>
                                <span style="font-size: 13px; color: #374151;">👉 <b>Guidance:</b> {alert['guidance']}</span>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("✅ All monitored nodes are performing within normal engineering parameters.")
                
            st.markdown("<br/>", unsafe_allow_html=True)
            st.caption("**DAX Consolidated Ledger Log Expression Outflow**")
            st.code(
                f"EVALUATE MEASURE 'Ledger'[ProtectedStateSavings]\n"
                f" ├─ Total Unmitigated Risk Exposure : ₹{r_costs_str}\n"
                f" ├─ Managed Proactive Operations Cost: ₹{p_costs_str}\n"
                f" └─ NET CURRENT PROTECTED SAVINGS    : ₹{net_savings_str}",
                language="text"
            )
            st.markdown("</div>", unsafe_allow_html=True)

    # Persist log records to disk storage asynchronously
    if not pause_feed:
        summary_data = live_grid_df.copy()
        summary_data["ai_balanced_load_pct"] = balanced_grid_df["load_pct"]
        summary_data["net_savings_inr"] = st.session_state.net_savings
        
        file_exists = os.path.isfile(CSV_FILE_PATH)
        summary_data.to_csv(CSV_FILE_PATH, mode='a', header=not file_exists, index=False)

    # Synchronized pipeline loop throttle time match
    time.sleep(2.5)
    st.rerun()

except Exception as pipeline_error:
    st.error(f"Power BI Report engine processing error encountered: {pipeline_error}")
