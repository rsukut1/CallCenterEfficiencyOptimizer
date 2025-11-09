import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- Parameters ---
num_reps = 10
num_days = 7
avg_calls_per_day = 100  # average number of calls per day
call_variation = 10  # ± range

# --- Static Rep Names ---
rep_names = [
    "Ava S", "Liam T", "Noah R", "Emma J", "Olivia K",
    "Ethan M", "Sophia L", "Mason B", "Isabella C", "Lucas D"
]

# Make sure length matches num_reps
if len(rep_names) != num_reps:
    raise ValueError("Number of rep names must match num_reps")

call_types = ["Support", "Sales", "Billing"]
outcomes = ["Resolved", "Escalated", "Dropped"]

# --- Generate Shift Data ---
shift_data = []
for rep in rep_names:
    shift_start = datetime(2025, 11, 8, 8, 0)  # 8 AM
    shift_end = datetime(2025, 11, 8, 16, 0)  # 4 PM
    shift_data.append({
        "rep_name": rep,
        "shift_start": shift_start,
        "shift_end": shift_end,
        "max_calls_per_shift": random.randint(10, 20)
    })

df_shifts = pd.DataFrame(shift_data)

# --- Generate Call Data ---
call_data = []
start_date = datetime(2025, 11, 1)

for day in range(num_days):
    date = start_date + timedelta(days=day)

    # Randomize calls per day within ±call_variation
    calls_today = random.randint(avg_calls_per_day - call_variation, avg_calls_per_day + call_variation)

    for _ in range(calls_today):
        rep = random.choice(rep_names)
        call_time = date + timedelta(minutes=random.randint(8 * 60, 16 * 60))
        handle_time = max(1, round(np.random.normal(5, 2), 2))  # min 1 min
        wait_time = round(np.random.exponential(2), 2)
        call_type = random.choice(call_types)
        outcome = random.choice(outcomes)

        call_data.append({
            "call_id": len(call_data) + 1,
            "timestamp": call_time,
            "rep_name": rep,
            "handle_time": handle_time,
            "wait_time": wait_time,
            "call_type": call_type,
            "outcome": outcome
        })

df_calls = pd.DataFrame(call_data)

# --- Save datasets ---
df_shifts.to_csv("shift_data.csv", index=False)
df_calls.to_csv("call_data.csv", index=False)

print("Sample datasets created:")
print(df_shifts.head())
print(df_calls.head())
