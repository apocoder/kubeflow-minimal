# pipelines/weather_istanbul.py
# KFP v2 minimal sample: Open-Meteo 7-day forecast for Istanbul → HTML report
# No API key required.

from kfp import dsl
from kfp.dsl import component, Dataset, Output, Input

BASE_IMAGE = "python:3.11-slim"  # tip: bake requests+pandas into your own image for speed

@component(base_image=BASE_IMAGE)
def fetch_forecast(
    latitude: float,
    longitude: float,
    days: int,
    out_csv: Output[Dataset],
):
    """
    Fetch daily weather forecast using Open-Meteo.
    Docs: https://open-meteo.com/en/docs
    """
    # lazy deps
    try:
        import pandas as pd  # noqa
        import requests  # noqa
    except Exception:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pandas", "requests"])
        import pandas as pd, requests

    # Build URL
    base = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": "Europe/Istanbul",
        "forecast_days": days,
    }
    r = requests.get(base, params=params, timeout=30)
    r.raise_for_status()
    js = r.json()
    daily = js.get("daily", {})

    # Normalize to CSV
    import pandas as pd
    df = pd.DataFrame(daily)
    # ensure date column named 'date'
    if "time" in df.columns:
        df = df.rename(columns={"time": "date"})
    df.to_csv(out_csv.path, index=False)

@component(base_image=BASE_IMAGE)
def render_html(city: str, csv_in: Input[Dataset], out_html: Output[Dataset]):
    """Simple HTML table with best/worst day blurb."""
    try:
        import pandas as pd  # noqa
        import numpy as np  # noqa
    except Exception:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pandas", "numpy"])
        import pandas as pd, numpy as np

    import io

    df = pd.read_csv(csv_in.path)

    # Pretty numbers
    def fmt(x):
        try:
            return f"{float(x):.1f}"
        except Exception:
            return x

    # pick best day by max temp, worst by precip
    best_row = df.loc[df["temperature_2m_max"].idxmax()]
    wet_row  = df.loc[df["precipitation_sum"].idxmax()]

    buf = io.StringIO()
    buf.write(f"<h2>{city} — {len(df)}-Day Weather Forecast</h2>")
    buf.write("<p>Source: <a href='https://open-meteo.com/'>Open-Meteo</a> · Timezone: Europe/Istanbul</p>")
    buf.write(df.to_html(index=False, float_format=lambda x: f"{x:.1f}"))  # ← fixed
    buf.write("<hr/>")
    buf.write(f"<p><b>Warmest day:</b> {best_row['date']} (max {fmt(best_row['temperature_2m_max'])}°C)</p>")
    buf.write(f"<p><b>Rainiest day:</b> {wet_row['date']} (precip {fmt(wet_row['precipitation_sum'])} mm)</p>")

    with open(out_html.path, "w") as f:
        f.write(buf.getvalue())

@dsl.pipeline(name="istanbul-weather-forecast")
def istanbul_weather_pipeline(
    # Istanbul coords by default; override if you like.
    latitude: float = 41.01,
    longitude: float = 28.97,
    days: int = 7,
    city: str = "Istanbul, TR",
):
    data = fetch_forecast(latitude=latitude, longitude=longitude, days=days)
    render_html(city=city, csv_in=data.outputs["out_csv"])
