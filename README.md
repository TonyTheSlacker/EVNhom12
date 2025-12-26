# EV Route Planner (Python)

![Language](https://img.shields.io/badge/Language-Python_3.x-3776AB?logo=python&logoColor=white)
![UI Engine](https://img.shields.io/badge/UI-Tkinter-2C3E50)
![Maps](https://img.shields.io/badge/Maps-Folium-77B829)
![Algorithm](https://img.shields.io/badge/Algorithm-A*-red)

An intelligent routing simulation for Electric Vehicles (EVs) that calculates the optimal path between cities while accounting for **battery constraints**, **charging station availability**, and **toll costs (BOT)**.

Unlike standard GPS apps, this system allows users to compare different pathfinding strategies (**A*** vs **Uniform Cost Search**) and visualize the results on an interactive map.

---

## ⚡ Key Features

* **Algorithmic Pathfinding:** Implements **A*** (using Haversine distance heuristics) and **UCS** to find the most efficient route.
* **Constraint Management:** Automatically routes the vehicle through charging stations when battery levels drop below the safety threshold.
* **Cost Optimization:** Optional routing logic to avoid toll stations (BOT) to minimize travel costs.
* **Interactive Visualization:** Generates dynamic HTML maps using **Folium** to display the route, charging stops, and POIs.
* **Data Export:** Generates detailed PDF reports of the itinerary, including charging times and energy consumption stats.

## 🛠️ Technical Architecture

### Core Algorithms
The system treats the map as a weighted graph where nodes are coordinates/stations and edges are road segments.
* **Heuristic Function:** Uses the **Haversine formula** to calculate the great-circle distance between coordinates for the A* heuristic.
* **Energy Model:** Calculates energy consumption (kWh) based on specific vehicle models (e.g., VinFast, Tesla) and distance traveled.

### System Components
* **`main.py`:** The GUI layer built with **Tkinter**, handling user inputs and async algorithm execution.
* **`file.py`:** The logic core containing the A* and UCS graph traversal implementations.
* **`models.py`:** Object-oriented definitions for EV specifications (Battery Capacity, Range, Consumption).
* **`pdf_utils.py`:** A report generation engine using FPDF.

```python
# Snippet: Map Generation Logic (main.py)
def create_route_map(route_points, df_charge, bot_stations):
    """
    Generates an interactive Folium map with markers for:
    - Start/End points
    - Charging stops (Orange bolts)
    - Toll stations (Pink circles)
    """
    m = folium.Map(location=[start_lat, start_lng], zoom_start=6)
    folium.PolyLine(locations=route_points, color="blue", weight=5).add_to(m)
    # ... marker logic ...
```

## 🚀 Installation & Usage
### Prerequisites
      Python 3.8+
      pandas, numpy, geopy, folium, fpdf

### Quick Start
1. Clone the repository:
```bash
  git clone https://github.com/TonyTheSlacker/EVNhom12.git
  cd EVNhom12
```
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Run the application:
```bash
   python main.py
```
## 📊 Supported Vehicles
### The system includes pre-configured models for major EV manufacturers:
    VinFast: VF e34, VF8, VF9, VF5, VF6
    Tesla: Model S, Model 3, Model X, Model Y
    Others: Mercedes EQS, Porsche Taycan, Hyundai Ioniq 5
--------------------------------------------------------------------------------------------------------------------------
***Disclaimer: This project uses static datasets for charging stations/tolls and is intended for simulation/academic purposes.***
