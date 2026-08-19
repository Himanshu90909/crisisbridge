from pathlib import Path

import pandas as pd


def load_data(data_dir: Path):
    requests = pd.read_csv(data_dir / "emergency_requests.csv", parse_dates=["reported_at"])
    shelters = pd.read_csv(data_dir / "shelters.csv")
    hospitals = pd.read_csv(data_dir / "hospitals.csv")
    resources = pd.read_csv(data_dir / "resources.csv")
    return requests, shelters, hospitals, resources


def calculate_priority(row) -> float:
    score = 0.0
    score += min(float(row["people_affected"]) / 20.0, 30.0)
    score += {"Critical": 35, "High": 25, "Medium": 14, "Low": 5}.get(row["priority"], 0)
    score += {"Medical": 22, "Rescue": 20, "Water": 16, "Food": 12, "Shelter": 10, "Transport": 8}.get(row["need_type"], 0)
    score += {"Unverified": 0, "Verified": 6, "Assigned": 9, "Completed": -30}.get(row["status"], 0)
    return max(0.0, min(score, 100.0))


def get_filtered_requests(df, statuses, needs, zones):
    result = df[df["status"].isin(statuses) & df["need_type"].isin(needs) & df["zone"].isin(zones)].copy()
    return result.sort_values("priority_score", ascending=False)


def build_resource_recommendations(requests: pd.DataFrame, resources: pd.DataFrame) -> pd.DataFrame:
    open_requests = requests[requests["status"] != "Completed"].copy()
    if open_requests.empty:
        return pd.DataFrame()

    available = resources[resources["available_units"] > 0].copy()
    rows = []
    for need_type, group in open_requests.groupby("need_type"):
        stock = available[available["resource_type"].str.lower() == need_type.lower()]
        if stock.empty:
            continue
        destination = group.sort_values("priority_score", ascending=False).iloc[0]
        supply = stock.sort_values("available_units", ascending=False).iloc[0]
        units = min(int(destination["requested_units"]), int(supply["available_units"]))
        rows.append({
            "Need": need_type,
            "Priority location": destination["location"],
            "Recommended units": units,
            "Dispatch from": supply["warehouse"],
            "Reason": f"{destination['priority']} priority; {int(destination['people_affected'])} people affected",
        })
    return pd.DataFrame(rows)
