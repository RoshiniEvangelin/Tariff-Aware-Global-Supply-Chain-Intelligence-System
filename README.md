# 🌐 Tariff-Aware Global Supply Chain Intelligence System

> ML-powered import route optimizer across 185 countries with real-time landed cost analysis, live exchange rates, and delivery forecasting.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?style=flat-square&logo=flask)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-orange?style=flat-square&logo=scikit-learn)
![Leaflet](https://img.shields.io/badge/Leaflet.js-Map-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📌 Overview

This system helps businesses make smarter import decisions by calculating the **total landed cost** of importing goods from any supplier country to any of **185 destination countries worldwide**. It uses a trained machine learning model to predict shipping costs and combines them with real tariff data, live exchange rates, and port congestion factors to recommend the optimal supply route.

---

## ✨ Features

- 🤖 **ML-Powered Predictions** — Trained regression model predicts shipping costs based on distance, fuel price, port congestion, container size, and shipping mode
- 🗺️ **Interactive World Map** — Real-time route visualization with great-circle arcs, pulsing markers, and port-level precision
- 🌍 **185 Destination Countries** — Smart routing through regional hubs (Rotterdam, Singapore, Dubai, Johannesburg, Sydney, Panama City)
- ⚓ **Port-Level Selection** — Choose specific destination ports (e.g. Southampton, New York, Busan) for precise routing
- 💱 **Live Exchange Rates** — Landed costs automatically converted to destination country currency
- 📅 **Delivery Date Forecasting** — Predicts exact arrival date including port processing buffer per region
- 🔔 **Tariff Alert System** — Set email alerts when supplier tariffs exceed a threshold
- 🌙 **Dual Themes** — Light and dark professional UI

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ML Model | Scikit-learn (Random Forest / Linear Regression) |
| Data Processing | Pandas, NumPy |
| Route Optimization | NetworkX (shortest path algorithm) |
| Frontend Map | Leaflet.js + GeoJSON |
| Frontend UI | HTML5, CSS3, Vanilla JavaScript |
| Exchange Rates | open.er-api.com (live API) |
| Fonts | Google Fonts (Space Grotesk, Outfit, Cormorant Garamond) |

---

## 📁 Project Structure

```
webapp/
├── app.py                       # Flask backend + optimization logic
├── requirements.txt             # Python dependencies
├── shipping_model.pkl           # Trained ML model
├── supplier_trade_dataset.csv   # Supplier countries + product costs
├── tariff_dataset.csv           # Tariff rates per supplier country
├── shipping_cost_dataset.csv    # Shipping features dataset
├── destination_ports.json       # Port coordinates for 39 countries
└── templates/
    ├── index.html               # Light theme UI
    └── index_dark.html          # Dark theme UI
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/RoshiniEvangelin/supply-chain-optimizer.git
cd supply-chain-optimizer/webapp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py

# 4. Open in browser
# http://localhost:5000
```

---

## 🧠 How It Works

1. **Select** a destination country and port (e.g. United Kingdom → Southampton)
2. **Select** a commodity (Electronics, Steel, Machinery, Textiles)
3. The system builds a **shipping network graph** using NetworkX
4. For each supplier, it predicts shipping cost using the **ML model** with features:
   - Distance (km)
   - Fuel price
   - Port congestion index
   - Container size
   - Shipping mode (Sea / Air / Truck)
5. **Landed cost** = Product Cost + Predicted Shipping + Tariff + Insurance + Handling
6. The **lowest landed cost** supplier is recommended with full route visualization

### Cost Formula
```
Landed Cost = Product Cost
            + ML Predicted Shipping Cost
            + (Product Cost × Tariff%)
            + Insurance ($5)
            + Handling ($8)
```

---

## 📊 Dataset

| Dataset | Rows | Description |
|---|---|---|
| supplier_trade_dataset.csv | ~500 | Supplier countries, commodities, product costs |
| tariff_dataset.csv | ~185 | Tariff rates per exporting country |
| shipping_cost_dataset.csv | ~1000 | Shipping features and historical costs |

---

## 🗺️ Supported Supplier Countries

Brazil · Canada · China · Germany · India · Indonesia · Japan · Malaysia · Mexico · South Korea · Thailand · Vietnam

---

## 🌐 Routing Hubs

| Region | Hub |
|---|---|
| Europe | Rotterdam |
| Asia | Singapore |
| Middle East | Dubai |
| Africa | Johannesburg |
| South America | Panama City |
| North America | Los Angeles |
| Oceania | Sydney |

---

## 📸 Screenshots

> <img width="3016" height="1722" alt="image" src="https://github.com/user-attachments/assets/d358ff82-5834-43f2-ae00-3ea5785dee9f" />

> <img width="3024" height="1710" alt="image" src="https://github.com/user-attachments/assets/07d11838-90d5-41bc-9551-09a635cc1ff0" />



---

## 🔮 Future Improvements

- [ ] Real-time port congestion API integration (MarineTraffic)
- [ ] Live fuel price feed (EIA API)
- [ ] Historical cost tracking with database (PostgreSQL)
- [ ] Email delivery for tariff alerts (SMTP)
- [ ] Multi-commodity comparison mode
- [ ] Risk score per supplier country

---

## 👩‍💻 Author

**Roshini Evangelin**  
[GitHub](https://github.com/RoshiniEvangelin)

---

## 📄 License

This project is licensed under the MIT License.
