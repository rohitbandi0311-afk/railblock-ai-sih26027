"""Load deterministic demonstration data."""
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_demo_data(data_dir: Path = DATA_DIR) -> dict[str, pd.DataFrame]:
    """Return synthetic demo inputs; none are official railway records."""
    files = {"assets":"assets.csv", "requests":"maintenance_requests.csv", "trains":"trains.csv", "windows":"candidate_windows.csv", "resources":"resources.csv"}
    return {name: pd.read_csv(data_dir / filename) for name, filename in files.items()}

def hhmm(minutes: int) -> str:
    minutes = int(minutes) % 1440
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
