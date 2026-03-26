from src.collector.flow import fetch_flow_data
from src.database.repository import save_flow_tracker

try:
    print("Fetching ADRO...")
    data = fetch_flow_data("ADRO")
    print("Data metrics accdist status:", data.get("metrics", {}).get("accdist_status"))
    print("Saving...")
    save_flow_tracker("ADRO", data)
    print("Saved!")
except Exception as e:
    import traceback
    traceback.print_exc()
