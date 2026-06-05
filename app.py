from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import random
import os
import json
from datetime import datetime, timedelta
import urllib.request

app = Flask(__name__)
BASE = os.path.dirname(__file__)

supplier_df = pd.read_csv(os.path.join(BASE, "supplier_trade_dataset.csv"), encoding="latin1")
tariff_df   = pd.read_csv(os.path.join(BASE, "tariff_dataset.csv"),         encoding="latin1")
shipping_df = pd.read_csv(os.path.join(BASE, "shipping_cost_dataset.csv"),  encoding="latin1")

supplier_df["supplier_country"] = supplier_df["supplier_country"].str.strip()
tariff_df["supplier_country"]   = tariff_df["supplier_country"].str.strip()
shipping_df["supplier_country"] = shipping_df["supplier_country"].str.strip()

model = joblib.load(os.path.join(BASE, "shipping_model.pkl"))
shipping_df["shipping_mode"] = shipping_df["shipping_mode"].map({"Sea":0,"Air":1,"Truck":2})

# ── Alerts storage (in-memory, replace with DB for production) ──
ALERTS = []

# ── Currency codes per country ──
COUNTRY_CURRENCY = {
    "United Kingdom":"GBP","European Union":"EUR","Germany":"EUR","France":"EUR",
    "Italy":"EUR","Spain":"EUR","Netherlands":"EUR","Australia":"AUD","Japan":"JPY",
    "South Korea":"KRW","China":"CNY","India":"INR","Brazil":"BRL","Canada":"CAD",
    "Mexico":"MXN","Switzerland":"CHF","Norway":"NOK","Sweden":"SEK","Denmark":"DKK",
    "Singapore":"SGD","United Arab Emirates":"AED","Saudi Arabia":"SAR","Qatar":"QAR",
    "Turkey":"TRY","South Africa":"ZAR","Nigeria":"NGN","Egypt":"EGP",
    "New Zealand":"NZD","Thailand":"THB","Malaysia":"MYR","Indonesia":"IDR",
    "Philippines":"PHP","Vietnam":"VND","Pakistan":"PKR","Bangladesh":"BDT",
    "Argentina":"ARS","Chile":"CLP","Colombia":"COP","Peru":"PEN",
    "Israel":"ILS","Morocco":"MAD","Kenya":"KES","Ghana":"GHS",
}

REGION_HUBS = {
    "europe":"Rotterdam","asia":"Singapore","middle_east":"Dubai",
    "africa":"Johannesburg","south_america":"Panama City",
    "north_america":"Los Angeles","oceania":"Sydney",
}

SUPPLIER_TO_HUB_DIST = {
    "China":      {"Singapore":3300,"Rotterdam":19000,"Dubai":6500,"Johannesburg":12000,"Panama City":14000,"Los Angeles":11500,"Sydney":8800},
    "India":      {"Singapore":3600,"Rotterdam":19500,"Dubai":2200,"Johannesburg":8500,"Panama City":16000,"Los Angeles":14000,"Sydney":10000},
    "Germany":    {"Singapore":17000,"Rotterdam":500,"Dubai":5500,"Johannesburg":9000,"Panama City":9000,"Los Angeles":9200,"Sydney":16500},
    "Japan":      {"Singapore":5300,"Rotterdam":20000,"Dubai":7800,"Johannesburg":13500,"Panama City":12000,"Los Angeles":8800,"Sydney":7800},
    "South Korea":{"Singapore":4700,"Rotterdam":20500,"Dubai":7300,"Johannesburg":13000,"Panama City":12500,"Los Angeles":9200,"Sydney":8300},
    "Vietnam":    {"Singapore":1500,"Rotterdam":18500,"Dubai":5500,"Johannesburg":11000,"Panama City":16000,"Los Angeles":12000,"Sydney":7500},
    "Thailand":   {"Singapore":1600,"Rotterdam":18500,"Dubai":5200,"Johannesburg":10800,"Panama City":16500,"Los Angeles":12500,"Sydney":8000},
    "Indonesia":  {"Singapore":1200,"Rotterdam":19000,"Dubai":6000,"Johannesburg":10000,"Panama City":17000,"Los Angeles":13000,"Sydney":6000},
    "Malaysia":   {"Singapore":350,"Rotterdam":18500,"Dubai":5800,"Johannesburg":10500,"Panama City":16500,"Los Angeles":12800,"Sydney":6700},
    "Brazil":     {"Singapore":17000,"Rotterdam":9500,"Dubai":10500,"Johannesburg":7500,"Panama City":4500,"Los Angeles":9000,"Sydney":14000},
    "Canada":     {"Singapore":14000,"Rotterdam":6500,"Dubai":11000,"Johannesburg":14000,"Panama City":4000,"Los Angeles":2500,"Sydney":14500},
    "Mexico":     {"Singapore":14500,"Rotterdam":9000,"Dubai":13000,"Johannesburg":14500,"Panama City":3000,"Los Angeles":2200,"Sydney":14000},
}

HUB_TO_DEST = {
    "Rotterdam":   {"europe":500,"north_america":7000,"south_america":9500,"asia":18000,"middle_east":5500,"africa":9000,"oceania":16000},
    "Singapore":   {"asia":3000,"europe":18000,"north_america":12000,"south_america":18000,"middle_east":5500,"africa":10000,"oceania":6300},
    "Dubai":       {"middle_east":500,"europe":5500,"asia":4000,"africa":6000,"north_america":12000,"south_america":14000,"oceania":12000},
    "Johannesburg":{"africa":1500,"europe":9000,"asia":11000,"middle_east":6000,"north_america":14000,"south_america":7500,"oceania":11000},
    "Panama City": {"south_america":2000,"north_america":3000,"europe":9000,"asia":16000,"middle_east":13000,"africa":13000,"oceania":17000},
    "Los Angeles": {"north_america":1500,"south_america":7000,"europe":9200,"asia":11000,"middle_east":13000,"africa":15000,"oceania":11500},
    "Sydney":      {"oceania":1500,"asia":7000,"north_america":12000,"south_america":13000,"europe":17000,"middle_east":12000,"africa":11000},
}

COUNTRY_REGION = {
    "Albania":"europe","Andorra":"europe","Bosnia and Herzegovina":"europe","Gibraltar":"europe",
    "Iceland":"europe","Kosovo":"europe","Liechtenstein":"europe","Moldova":"europe",
    "Monaco":"europe","Montenegro":"europe","North Macedonia":"europe","Norway":"europe",
    "San Marino":"europe","Serbia":"europe","Switzerland":"europe","Ukraine":"europe",
    "United Kingdom":"europe","European Union":"europe","Germany":"europe","France":"europe",
    "Italy":"europe","Spain":"europe","Netherlands":"europe","Belgium":"europe","Austria":"europe",
    "Poland":"europe","Sweden":"europe","Denmark":"europe","Finland":"europe","Portugal":"europe",
    "Czech Republic":"europe","Romania":"europe","Hungary":"europe","Greece":"europe",
    "Bulgaria":"europe","Croatia":"europe","Slovakia":"europe","Slovenia":"europe",
    "Estonia":"europe","Latvia":"europe","Lithuania":"europe","Luxembourg":"europe",
    "Malta":"europe","Cyprus":"europe","Ireland":"europe","Svalbard and Jan Mayen":"europe",
    "China":"asia","Japan":"asia","South Korea":"asia","Taiwan":"asia","Vietnam":"asia",
    "Thailand":"asia","Indonesia":"asia","Malaysia":"asia","Philippines":"asia","Singapore":"asia",
    "Myanmar (Burma)":"asia","Cambodia":"asia","Laos":"asia","Brunei":"asia","Timor-Leste":"asia",
    "Bangladesh":"asia","India":"asia","Pakistan":"asia","Sri Lanka":"asia","Nepal":"asia",
    "Bhutan":"asia","Maldives":"asia","Afghanistan":"asia","Mongolia":"asia",
    "Kazakhstan":"asia","Kyrgyzstan":"asia","Tajikistan":"asia","Turkmenistan":"asia","Uzbekistan":"asia",
    "Georgia":"asia","Armenia":"asia","Azerbaijan":"asia",
    "Saudi Arabia":"middle_east","United Arab Emirates":"middle_east","Qatar":"middle_east",
    "Kuwait":"middle_east","Bahrain":"middle_east","Oman":"middle_east","Jordan":"middle_east",
    "Israel":"middle_east","Lebanon":"middle_east","Syria":"middle_east","Iraq":"middle_east",
    "Iran":"middle_east","Yemen":"middle_east","Turkey":"middle_east",
    "South Africa":"africa","Nigeria":"africa","Kenya":"africa","Ethiopia":"africa",
    "Ghana":"africa","Tanzania":"africa","Uganda":"africa","Angola":"africa","Mozambique":"africa",
    "Zambia":"africa","Zimbabwe":"africa","Cameroon":"africa","Senegal":"africa","Mali":"africa",
    "Niger":"africa","Guinea":"africa","Benin":"africa","Togo":"africa","Rwanda":"africa",
    "Burundi":"africa","South Sudan":"africa","Sudan":"africa","Eritrea":"africa",
    "Djibouti":"africa","Comoros":"africa","Madagascar":"africa","Mauritius":"africa",
    "Cabo Verde":"africa","Sao Tome and Principe":"africa","Equatorial Guinea":"africa",
    "Gabon":"africa","Republic of the Congo":"africa","Democratic Republic of the Congo":"africa",
    "Central African Republic":"africa","Chad":"africa","Libya":"africa","Tunisia":"africa",
    "Algeria":"africa","Morocco":"africa","Egypt":"africa","Mauritania":"africa",
    "Gambia":"africa","Guinea-Bissau":"africa","Sierra Leone":"africa","Liberia":"africa",
    "Lesotho":"africa","Eswatini":"africa","Botswana":"africa","Namibia":"africa",
    "Malawi":"africa","Mayotte":"africa","Reunion":"africa","Saint Helena":"africa",
    "United States":"north_america","USA":"north_america","Canada":"north_america","Mexico":"north_america",
    "Bermuda":"north_america","Cayman Islands":"north_america","Bahamas":"north_america",
    "Barbados":"north_america","Belize":"north_america","Costa Rica":"north_america",
    "Dominica":"north_america","Dominican Republic":"north_america","El Salvador":"north_america",
    "Grenada":"north_america","Guatemala":"north_america","Haiti":"north_america",
    "Honduras":"north_america","Jamaica":"north_america","Nicaragua":"north_america",
    "Panama":"north_america","Trinidad and Tobago":"north_america","Aruba":"north_america",
    "Curacao":"north_america","Anguilla":"north_america","Antigua and Barbuda":"north_america",
    "Brazil":"south_america","Argentina":"south_america","Colombia":"south_america",
    "Chile":"south_america","Peru":"south_america","Venezuela":"south_america",
    "Ecuador":"south_america","Bolivia":"south_america","Paraguay":"south_america",
    "Uruguay":"south_america","Guyana":"south_america","Suriname":"south_america",
    "French Guiana":"south_america","Falkland Islands":"south_america",
    "Australia":"oceania","New Zealand":"oceania","Papua New Guinea":"oceania","Fiji":"oceania",
    "Solomon Islands":"oceania","Vanuatu":"oceania","Samoa":"oceania","Tonga":"oceania",
    "Kiribati":"oceania","Micronesia":"oceania","Marshall Islands":"oceania","Nauru":"oceania",
    "Tuvalu":"oceania","Cook Islands":"oceania","French Polynesia":"oceania",
}

def get_region(c): return COUNTRY_REGION.get(c,"north_america")
def get_hub(dest):  return REGION_HUBS.get(get_region(dest),"Los Angeles")

def get_distance(supplier, destination):
    hub      = get_hub(destination)
    hub_dist = SUPPLIER_TO_HUB_DIST.get(supplier,{}).get(hub, random.randint(3000,15000))
    dest_dist= HUB_TO_DEST.get(hub,{}).get(get_region(destination), random.randint(500,3000))
    return int(hub_dist + dest_dist)

def get_route(supplier, destination):
    hub = get_hub(destination)
    if supplier == destination: return [supplier, destination]
    if hub == supplier:         return [supplier, destination]
    return [supplier, hub, destination]

# ── Feature 1: Live Exchange Rates ──
_fx_cache = {"rates": {}, "timestamp": None}

def get_exchange_rates():
    now = datetime.now()
    # Cache for 1 hour
    if _fx_cache["timestamp"] and (now - _fx_cache["timestamp"]).seconds < 3600 and _fx_cache["rates"]:
        return _fx_cache["rates"]
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
        _fx_cache["rates"] = data.get("rates", {})
        _fx_cache["timestamp"] = now
        return _fx_cache["rates"]
    except:
        return {}

def convert_currency(amount_usd, currency_code):
    rates = get_exchange_rates()
    rate  = rates.get(currency_code, 1.0)
    return round(amount_usd * rate, 2), rate

# ── Feature 3: Delivery Date Predictor ──
def get_estimated_arrival(days_float, destination):
    today      = datetime.now()
    # Add port processing buffer (2-5 days depending on region)
    region     = get_region(destination)
    buffer     = {"europe":3,"asia":2,"middle_east":4,"africa":5,"north_america":2,"south_america":4,"oceania":3}.get(region,3)
    total_days = int(days_float) + buffer
    arrival    = today + timedelta(days=total_days)
    # Skip weekends for final delivery
    while arrival.weekday() >= 5:
        arrival += timedelta(days=1)
    return {
        "departure_date":  today.strftime("%d %b %Y"),
        "arrival_date":    arrival.strftime("%d %b %Y"),
        "transit_days":    int(days_float),
        "buffer_days":     buffer,
        "total_days":      total_days,
        "day_of_week":     arrival.strftime("%A"),
    }

@app.route("/")
def home():
    commodities = sorted(supplier_df["commodity"].dropna().unique())
    raw_dests   = sorted(tariff_df["supplier_country"].unique())
    destinations= []
    for d in raw_dests:
        try:    destinations.append(d.encode('latin1').decode('utf-8'))
        except: destinations.append(d)
    return render_template("index.html", commodities=commodities, destinations=destinations)

@app.route("/optimize", methods=["POST"])
def optimize():
    commodity   = request.json.get("commodity","")
    destination = request.json.get("destination","United States")

    df = supplier_df[supplier_df["commodity"].str.lower() == commodity.lower()]
    if df.empty:
        return jsonify({"error":"No suppliers found for this commodity"})

    # Get currency for destination
    currency_code = COUNTRY_CURRENCY.get(destination, "USD")
    fx_rates      = get_exchange_rates()
    fx_rate       = fx_rates.get(currency_code, 1.0) if currency_code != "USD" else 1.0

    results=[]
    best_supplier=None; best_route=None; best_time=None; lowest_cost=float("inf")

    for _, row in df.iterrows():
        supplier     = row["supplier_country"]
        product_cost = row["product_cost"]

        distance = get_distance(supplier, destination)
        route    = get_route(supplier, destination)

        sm = shipping_df[shipping_df["supplier_country"]==supplier]
        if sm.empty: continue
        ship_row = sm.iloc[0]

        features = pd.DataFrame([{
            "distance_km":     distance,
            "fuel_price":      ship_row["fuel_price"],
            "port_congestion": ship_row["port_congestion"],
            "container_size":  ship_row["container_size"],
            "shipping_mode":   ship_row["shipping_mode"]
        }])
        pred_ship      = model.predict(features)[0]
        tm             = tariff_df[tariff_df["supplier_country"]==supplier]
        if tm.empty: continue
        tariff_percent = tm.iloc[0]["tariff_percent"]
        tariff_cost    = product_cost * tariff_percent / 100
        landed         = product_cost + pred_ship + tariff_cost + 13
        time           = round(distance/800, 1)

        # Local currency conversion
        landed_local   = round(landed * fx_rate, 2) if fx_rate != 1.0 else None

        results.append({
            "country":        str(supplier),
            "landed_cost":    float(round(landed,2)),
            "landed_local":   landed_local,
            "product_cost":   float(product_cost),
            "tariff":         float(tariff_percent),
            "shipping_cost":  float(round(pred_ship,2)),
            "delivery_time":  float(time),
            "route":          route,
            "distance":       int(distance),
        })

        if landed < lowest_cost:
            lowest_cost=landed; best_supplier=supplier; best_route=route; best_time=time

    if not results:
        return jsonify({"error":"Could not compute results"})

    results.sort(key=lambda x: x["landed_cost"])

    # Delivery date prediction for best supplier
    delivery_info = get_estimated_arrival(best_time, destination)

    return jsonify({
        "best_supplier":  str(best_supplier),
        "best_route":     best_route,
        "delivery_time":  float(round(best_time,1)),
        "landed_cost":    float(round(lowest_cost,2)),
        "destination":    destination,
        "currency_code":  currency_code,
        "fx_rate":        float(round(fx_rate,4)),
        "landed_local":   round(lowest_cost*fx_rate,2) if fx_rate!=1.0 else None,
        "delivery_info":  delivery_info,
        "all_suppliers":  results,
    })

# ── Feature 4: Tariff Alert System ──
@app.route("/alert", methods=["POST"])
def save_alert():
    data      = request.json
    email     = data.get("email","").strip()
    commodity = data.get("commodity","").strip()
    supplier  = data.get("supplier","").strip()
    threshold = float(data.get("threshold", 30))

    if not email or not commodity:
        return jsonify({"error":"Email and commodity are required"})

    alert = {
        "id":        len(ALERTS)+1,
        "email":     email,
        "commodity": commodity,
        "supplier":  supplier,
        "threshold": threshold,
        "created":   datetime.now().strftime("%d %b %Y %H:%M"),
    }
    ALERTS.append(alert)
    return jsonify({"success":True, "message":f"Alert saved! We'll email {email} if {supplier or 'any supplier'} tariff exceeds {threshold}%", "alert": alert})

@app.route("/alerts", methods=["GET"])
def list_alerts():
    return jsonify({"alerts": ALERTS})

@app.route("/fx", methods=["GET"])
def get_fx():
    rates = get_exchange_rates()
    return jsonify({"rates": rates, "source": "open.er-api.com", "base": "USD"})

if __name__ == "__main__":
    app.run(debug=True)
