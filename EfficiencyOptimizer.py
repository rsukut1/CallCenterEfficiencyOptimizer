import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# --- Load datasets ---
df_calls = pd.read_csv("call_data.csv", parse_dates=["timestamp"])
df_shifts = pd.read_csv("shift_data.csv", parse_dates=["shift_start", "shift_end"])

# --- Streamlit setup ---
st.set_page_config(page_title="Call Center Efficiency Optimizer", layout="wide")
st.markdown("<h1 style='text-align:center;'>📊 Call Center Efficiency Optimizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Analyze call volume, agent performance, and optimize staffing for efficiency.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar Filters ---
st.sidebar.header("🎚 Filters")
selected_rep = st.sidebar.multiselect(
    "Select Rep(s)", options=df_calls['rep_name'].unique(), default=df_calls['rep_name'].unique()
)
selected_call_type = st.sidebar.multiselect(
    "Call Type", options=df_calls['call_type'].unique(), default=df_calls['call_type'].unique()
)
date_range = st.sidebar.date_input(
    "Select Date Range", [df_calls['timestamp'].min(), df_calls['timestamp'].max()]
)
max_handle_filter = st.sidebar.slider("Filter: Max Handle Time (min)", 1, 15, 10)
max_wait_filter = st.sidebar.slider("Filter: Max Wait Time (min)", 0, 10, 5)

# --- Filter data ---
df_filtered = df_calls[
    (df_calls['rep_name'].isin(selected_rep)) &
    (df_calls['call_type'].isin(selected_call_type)) &
    (df_calls['timestamp'].dt.date.between(date_range[0], date_range[1])) &
    (df_calls['handle_time'] <= max_handle_filter) &
    (df_calls['wait_time'] <= max_wait_filter)
].copy()

# --- KPI Metrics ---
st.subheader("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Calls", df_filtered.shape[0])
col2.metric("Avg Handle Time (min)", round(df_filtered['handle_time'].mean(), 2))
col3.metric("Avg Wait Time (min)", round(df_filtered['wait_time'].mean(), 2))
col4.metric("Resolved %", round((df_filtered['outcome'] == "Resolved").mean()*100, 2))

# --- Call Volume by Hour ---
st.subheader("📞 Call Volume by Hour")
df_filtered['hour'] = df_filtered['timestamp'].dt.hour
call_hour = df_filtered.groupby('hour').size().reset_index(name='calls')
fig_calls_hour = px.bar(
    call_hour, x='hour', y='calls',
    labels={'hour': 'Hour of Day', 'calls': 'Number of Calls'},
    title="Hourly Call Volume"
)
st.plotly_chart(fig_calls_hour, use_container_width=True)

# --- Handle Time by Rep ---
st.subheader("🧠 Average Handle Time per Rep")
handle_rep = df_filtered.groupby('rep_name')['handle_time'].mean().reset_index()
fig_handle = px.bar(handle_rep, x='rep_name', y='handle_time',
                    labels={'rep_name': 'Rep', 'handle_time': 'Avg Handle Time'},
                    title="Avg Handle Time by Rep", color='handle_time', color_continuous_scale='Tealgrn')
st.plotly_chart(fig_handle, use_container_width=True)

# --- Wait Time by Rep ---
st.subheader("⏳ Average Wait Time per Rep")
wait_rep = df_filtered.groupby('rep_name')['wait_time'].mean().reset_index()
fig_wait = px.bar(wait_rep, x='rep_name', y='wait_time',
                  labels={'rep_name': 'Rep', 'wait_time': 'Avg Wait Time'},
                  title="Avg Wait Time by Rep", color='wait_time', color_continuous_scale='Viridis')
st.plotly_chart(fig_wait, use_container_width=True)

# --- Calls Handled by Rep ---
st.subheader("📋 Calls Handled by Rep")
calls_per_rep = df_filtered.groupby('rep_name').size().reset_index(name='calls_handled')
fig_workload = px.pie(calls_per_rep, names='rep_name', values='calls_handled', title="Call Distribution by Rep")
st.plotly_chart(fig_workload, use_container_width=True)

# --- Forecasting: Simple call volume trend ---
st.subheader("🔮 Tomorrow's Call Volume Forecast")
daily_calls = df_calls.groupby(df_calls['timestamp'].dt.date).size().reset_index(name='calls')
daily_calls['day_num'] = np.arange(len(daily_calls))

# Simple linear regression forecast
model = LinearRegression()
model.fit(daily_calls[['day_num']], daily_calls['calls'])
next_day_num = daily_calls['day_num'].max() + 1
forecast_calls = int(model.predict([[next_day_num]])[0])

fig_forecast = px.line(daily_calls, x='timestamp', y='calls', title="Daily Call Volume Trend")
st.plotly_chart(fig_forecast, use_container_width=True)
st.info(f"📅 Predicted calls for tomorrow: **{forecast_calls}** (based on past trend)")

# --- Staffing Recommendation ---
st.subheader("📌 Staffing Recommendation")
df_workload = calls_per_rep.merge(df_shifts[['rep_name','max_calls_per_shift']], on='rep_name')
overloaded_reps = df_workload[df_workload['calls_handled'] > df_workload['max_calls_per_shift']]

if not overloaded_reps.empty:
    st.warning("⚠️ These reps may be overloaded:")
    st.table(overloaded_reps)

    # Optimization suggestion
    avg_calls = df_workload['calls_handled'].mean()
    suggested_reassign = overloaded_reps.sample(1).iloc[0]
    st.markdown(f"""
    ✅ **Suggestion:** Move {suggested_reassign['rep_name']} to a lighter shift or reduce call allocation.
    This could balance workloads and reduce overload by ~{round((suggested_reassign['calls_handled'] / avg_calls - 1)*100, 1)}%.
    """)
else:
    st.success("All reps are within optimal workload range! ✅")

# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align:center; font-size: 0.9em;'>Created by Rena Sukut | Call Center Efficiency Optimizer © 2025</p>", unsafe_allow_html=True)
