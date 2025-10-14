# scripts/run_weather.py
import sys, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from kfp import Client
from pipelines.weather_istanbul import istanbul_weather_pipeline

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="http://localhost:8888", help="KFP endpoint")
    p.add_argument("--lat", type=float, default=41.01)
    p.add_argument("--lon", type=float, default=28.97)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--city", default="Istanbul, TR")
    args = p.parse_args()

    client = Client(host=args.host)
    run = client.create_run_from_pipeline_func(
        istanbul_weather_pipeline,
        arguments=dict(latitude=args.lat, longitude=args.lon, days=args.days, city=args.city),
    )
    try:
        print("Run started. run_id=", getattr(run, "run_id", None) or run.run_id)
    except Exception:
        print("Run started:", run)

if __name__ == "__main__":
    main()
