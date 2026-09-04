# LandGuard: NER Landslide Early Warning System

A college-project MVP for AI-assisted landslide risk monitoring in Northeast India (NER). It includes an explainable risk engine, simulated IoT sensor data, regional dashboard, risk explanations, map view, and prioritized response queue.

## Run on Windows PowerShell

```powershell
cd C:\LandGuard
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If the virtual environment does not exist, create it with:

```powershell
py -m venv venv
```

Then open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Project structure

- `app.py`: Streamlit user interface and pages.
- `risk_engine.py`: weighted, explainable risk scoring logic.
- `sample_data.py`: simulated NER sensor telemetry.
- `requirements.txt`: Python dependencies.

## System design

```text
[Rain / Moisture / Tilt / Vibration Sensors]
		      |
	   [ESP32 + LoRa / Wi-Fi Gateway]
		      |
	      [Monitoring API]
		      |
	[Validation + Risk Scoring Engine]
		      |
	[Database + Trend and Alert Service]
	      /                     \
 [NER Dashboard and Map]       [SMS / Control Room]
		      |
	[Verified Safe Place Guidance]
```

The field layer measures environmental and ground-movement signals. The processing layer validates readings and calculates an explainable score. The alert layer classifies locations as Safe, Warning, Danger, or Emergency and provides the nearest verified safe place. The current application simulates the field and database layers so the full workflow can be demonstrated without hardware.

## Academic presentation points

- Inputs: rainfall, soil moisture, slope, displacement, and micro-seismic activity.
- Output: Low, Moderate, High, or Critical risk level with reasons.
- Users: district disaster management authorities, road agencies, field engineers, and communities.
- Future scope: ESP32/LoRa integration, IMD/weather API, satellite rainfall, GIS layers, PostgreSQL, SMS alerts, verified district shelters, and model training with historical landslide events.

The current sensor data and safe places are simulated demonstration data and must not be used for real emergency decisions. Replace the demo points in `sample_data.py` with verified shelters from district authorities before any field use. A real alert system should also send SMS/calls through an approved disaster-management channel and provide route guidance from official GIS data.
