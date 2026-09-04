# LandGuard

## AI-Based Early Warning and Landslide Risk Monitoring System for Northeast India

LandGuard is an academic prototype designed to support early detection, risk assessment, and emergency response for landslide-prone areas in the North Eastern Region (NER) of India.

The system combines environmental and ground-movement indicators to produce an explainable landslide risk score. It presents monitoring results through a Streamlit dashboard with maps, graphs, district-level status, early warnings, predicted danger notifications, and suggested evacuation points.

> **Academic prototype:** The current sensor readings and safe places are simulated for demonstration. This application must not be used as an official emergency-warning system without field validation and approval from the responsible authorities.

## Project Objectives

- Monitor rainfall, soil moisture, slope, ground displacement, and micro-seismic activity.
- Identify areas with Low, Moderate, High, or Critical landslide risk.
- Provide early-warning information before conditions become dangerous.
- Display affected locations clearly on a regional map.
- Suggest a nearby evacuation point for high-risk conditions.
- Support disaster-management teams with understandable risk explanations.
- Provide NER state-wise charts for analysis and academic reporting.

## Main Features

- **Regional monitoring dashboard:** Overview of monitored NER districts.
- **Risk classification:** Safe, Warning, Danger, and Emergency status levels.
- **Explainable risk engine:** Shows which environmental factors contribute to the score.
- **Live Monitoring page:** Displays recent sensor telemetry and trends.
- **Advance warnings:** Highlights Moderate-risk areas for early preparation.
- **Predicted danger alerts:** Projects possible High/Critical risk for the next hour using recent trends.
- **Emergency guidance:** Displays the affected district and nearest demo evacuation point.
- **Interactive map:** Uses green, yellow, orange, and red points for risk levels.
- **NER state graphs:** Compares average risk scores and risk categories by state.
- **Report downloads:** Exports state summaries as CSV and interactive graphs as HTML.
- **IST timestamps:** Displays India Standard Time for dashboard and sensor updates.

## Risk Levels

| Colour | Status | Meaning | Suggested response |
|---|---|---|---|
| Green | Safe | Low risk | Continue normal monitoring. |
| Yellow | Warning | Moderate risk | Prepare transport and monitor conditions. |
| Orange | Danger | High risk | Begin response planning and protect vulnerable people. |
| Red | Emergency | Critical risk | Move people away from unstable slopes and follow official instructions. |

## System Architecture

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
             /                     \\
 [NER Dashboard and Map]       [SMS / Control Room]
                    |
       [Verified Safe Place Guidance]
```

### Processing Workflow

1. Sensors collect environmental and ground-movement observations.
2. The system validates and normalizes incoming readings.
3. The risk engine calculates a weighted score from 0 to 100.
4. Each location receives a risk category and explanation.
5. Recent trends are used for a simple one-hour early-warning projection.
6. The dashboard displays alerts, maps, graphs, and response guidance.

## Technology Stack

- **Language:** Python
- **Dashboard:** Streamlit
- **Data processing:** pandas and NumPy
- **Visualizations:** Plotly
- **Machine-learning foundation:** scikit-learn
- **Current data source:** Simulated sensor telemetry
- **Future storage:** PostgreSQL or TimescaleDB
- **Future communication:** ESP32, LoRa, Wi-Fi, 4G, SMS, and control-room integrations

## Project Structure

- `app.py`: Streamlit dashboard, monitoring pages, maps, alerts, and graphs.
- `risk_engine.py`: Explainable weighted landslide risk-scoring logic.
- `sample_data.py`: Simulated NER telemetry and demonstration evacuation points.
- `requirements.txt`: Python dependencies.
- `.streamlit/config.toml`: Dashboard theme configuration.

## Installation on Windows

Open PowerShell in the project folder:

```powershell
cd C:\LandGuard
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks environment activation, run the application directly:

```powershell
C:\LandGuard\venv\Scripts\python.exe -m streamlit run app.py
```

## Run the Application

```powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

Open the local address shown in the terminal, normally:

**http://localhost:8501**

Use the left sidebar to open Overview, Live Monitoring, Risk Assessment, Alerts & Response, or Project Notes & Graphs.

## Future Enhancements

- Connect real ESP32 and LoRa sensor nodes.
- Integrate verified rainfall and weather data.
- Add satellite rainfall, elevation, slope, soil, and geological GIS layers.
- Train and validate a machine-learning model using historical landslide records.
- Store long-term observations in PostgreSQL or TimescaleDB.
- Add SMS, voice-call, siren, and official control-room notifications.
- Replace demo evacuation points with verified shelters and official route guidance.
- Add user authentication, audit logs, offline buffering, and model monitoring.

## Safety and Deployment Notice

The current readings, risk thresholds, predictions, and evacuation points are for academic demonstration only. Real deployment requires calibrated thresholds, redundant field sensors, historical validation, official shelter information, reliable communications, human review, and approval from district disaster-management authorities. Always follow official emergency instructions.

## Author

**MAKAM DHEERAJ NADH**

GitHub: [dheerajmakam06-web/LandGuard](https://github.com/dheerajmakam06-web/LandGuard)
