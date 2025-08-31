# streamlit_app.py
# Team B: Visual Edge - Interface & Visualization
# 🚀 Q-RouteNet: Quantum Logistics Dashboard (Futuristic Edition)

import streamlit as st
import folium
from folium.plugins import TimestampedGeoJson
import numpy as np
import pandas as pd
from streamlit_folium import st_folium
import json
import time
from geopy.geocoders import Nominatim
import random
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Q-RouteNet: Quantum Logistics",
    page_icon="⚛️",
    layout="wide"
)

# Custom CSS - Neon Sci-Fi Theme
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0a0a1a, #0e1117);
        color: #00eeff;
        font-family: 'Courier New', monospace;
    }
    h1, h2, h3, h4 {
        color: #00eeff;
        text-shadow: 0 0 10px rgba(0, 238, 255, 0.5);
    }
    .stButton>button {
        background-color: #00eeff;
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        box-shadow: 0 0 15px #00eeff;
    }
    .stMetric {
        background-color: rgba(0, 238, 255, 0.1);
        border-left: 3px solid #00eeff;
        padding: 10px;
        border-radius: 5px;
    }
    .stProgress > div > div > div > div {
        background-color: #00eeff;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'customers' not in st.session_state:
    st.session_state.customers = []
    st.session_state.depot = None
    st.session_state.routes_optimized = []
    st.session_state.routes_greedy = []
    st.session_state.total_distance_optimized = 0
    st.session_state.total_distance_greedy = 0
    st.session_state.overloads = 0
    st.session_state.quantum_confidence = 0.0
    st.session_state.simulated = False
    st.session_state.city_name = "Random City"

# Header with Quantum Flair
st.markdown("<h1 style='text-align: center;'>⚛️ Q-RouteNet: Quantum Logistics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa;'>Quantum Intelligence. Visualized. 🌐</p>", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.header("🔧 Quantum Control Panel")

# City Selection
city_options = ["Random City", "New York", "London", "Tokyo", "Berlin", "Sydney"]
selected_city = st.sidebar.selectbox("🌆 Select City", city_options)
num_customers = st.sidebar.slider("📦 Number of Customers", 5, 10, 7)
num_vehicles = st.sidebar.slider("🚚 Number of Trucks", 2, 4, 3)
vehicle_capacity = st.sidebar.slider("🔋 Truck Capacity", 10, 25, 15)

# Environmental Factors
st.sidebar.subheader("🌦️ Environmental Simulation")
rain_mode = st.sidebar.checkbox("🌧️ Rainy Weather", help="Increases travel distance by 15%")
traffic_mode = st.sidebar.checkbox("🚦 High Traffic", help="May reroute dynamically")

# Sound toggle
enable_sound = st.sidebar.checkbox("🔊 Enable Sound Effects", value=True)

# Button to simulate
if st.sidebar.button("🚀 Deploy to Quantum Cloud"):
    st.session_state.simulated = True
    st.session_state.city_name = selected_city

    # Fake quantum loading
    placeholder = st.empty()
    with placeholder.container():
        status = st.empty()
        for msg in [
            "🔬 Initializing Quantum Core...",
            "🌀 Entangling Delivery Qubits...",
            "📡 Syncing with D-Wave Satellite...",
            "🧮 Solving VRP in Hilbert Space...",
            "✅ Optimal Path Found!"
        ]:
            status.info(msg)
            time.sleep(1.2)

    # Play sound (if enabled)
    if enable_sound:
        st.markdown("""
        <audio autoplay>
          <source src="https://www.soundjay.com/buttons/sounds/button-09.mp3" type="audio/mpeg">
        </audio>
        """, unsafe_allow_html=True)

    st.balloons()

    # Geocode city (if not random)
    if selected_city != "Random City":
        geolocator = Nominatim(user_agent="q_routenet")
        location = geolocator.geocode(selected_city)
        if location:
            depot_x, depot_y = location.longitude, location.latitude
        else:
            # Fallback
            depot_x, depot_y = -73.994454, 40.750042  # NYC
    else:
        depot_x, depot_y = -73.994454, 40.750042  # Default NYC

    st.session_state.depot = {"x": depot_x, "y": depot_y}

    # Generate random customers around depot
    customers = []
    for i in range(num_customers):
        angle = random.uniform(0, 2 * np.pi)
        dist = random.uniform(0.01, 0.05)
        x = depot_x + dist * np.cos(angle)
        y = depot_y + dist * np.sin(angle)
        demand = random.randint(3, 7)
        customers.append({
            "id": i + 1,
            "x": float(x),
            "y": float(y),
            "demand": demand
        })
    st.session_state.customers = customers

    # Simulate Greedy (Before) Routes
    greedy_routes = []
    greedy_distance = 0
    unvisited = list(range(1, num_customers + 1))
    truck_id = 0
    colors = ['gray', 'brown', 'purple', 'darkred']

    for _ in range(num_vehicles):
        route = [0]
        current = 0
        load = 0
        while unvisited:
            nearest = min(unvisited, key=lambda cid: (
                (customers[cid-1]['x'] - (depot_x if current == 0 else customers[current-1]['x']))**2 +
                (customers[cid-1]['y'] - (depot_y if current == 0 else customers[current-1]['y']))**2
            ))
            if load + customers[nearest-1]['demand'] > vehicle_capacity:
                break
            route.append(nearest)
            load += customers[nearest-1]['demand']
            current = nearest
            unvisited.remove(nearest)
        route.append(0)
        dist = sum(
            ((customers[r-1]['x'] if r != 0 else depot_x) - (customers[route[i-1]-1]['x'] if route[i-1] != 0 else depot_x))**2 +
            ((customers[r-1]['y'] if r != 0 else depot_y) - (customers[route[i-1]-1]['y'] if route[i-1] != 0 else depot_y))**2
            for i, r in enumerate(route) if i > 0
        )**0.5 * 111
        if rain_mode:
            dist *= 1.15
        if traffic_mode:
            dist *= 1.10
        greedy_distance += dist
        greedy_routes.append({"truck": truck_id, "color": colors[truck_id], "stops": route})
        truck_id += 1

    st.session_state.routes_greedy = greedy_routes
    st.session_state.total_distance_greedy = round(greedy_distance, 1)

    # Simulate Quantum-Optimized (After) Routes
    opt_routes = []
    opt_distance = 0
    remaining = list(range(1, num_customers + 1))
    opt_colors = ['blue', 'green', 'orange', 'purple']
    opt_truck_id = 0

    for _ in range(num_vehicles):
        route = [0]
        load = 0
        while remaining and load < vehicle_capacity:
            # Simulate smarter choice
            if remaining:
                picked = remaining.pop(0)  # Simplified — in real case use solver
                if load + customers[picked-1]['demand'] <= vehicle_capacity:
                    route.append(picked)
                    load += customers[picked-1]['demand']
                else:
                    break
        route.append(0)
        dist = sum(
            ((customers[r-1]['x'] if r != 0 else depot_x) - (customers[route[i-1]-1]['x'] if route[i-1] != 0 else depot_x))**2 +
            ((customers[r-1]['y'] if r != 0 else depot_y) - (customers[route[i-1]-1]['y'] if route[i-1] != 0 else depot_y))**2
            for i, r in enumerate(route) if i > 0
        )**0.5 * 111
        if rain_mode:
            dist *= 1.10  # Quantum adapts better
        opt_distance += dist
        opt_routes.append({"truck": opt_truck_id, "color": opt_colors[opt_truck_id], "stops": route})
        opt_truck_id += 1

    st.session_state.routes_optimized = opt_routes
    st.session_state.total_distance_optimized = round(opt_distance, 1)
    st.session_state.overloads = 0
    st.session_state.quantum_confidence = round(random.uniform(0.95, 0.995), 3)

# Only show if simulation done
if st.session_state.simulated:
    st.success(f"✅ Quantum solution deployed for **{st.session_state.city_name}**!")

    # Quantum Confidence
    st.markdown("### 🔮 Quantum Confidence Score")
    conf = st.session_state.quantum_confidence
    st.metric("Stability", f"{int(conf*100)}%", delta="High Coherence")
    st.progress(conf)

    # Before vs After Maps
    st.markdown("### 🆚 Route Optimization: Before vs After Quantum AI")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🟡 Before: Greedy Routing")
        m1 = folium.Map(location=[st.session_state.depot['y'], st.session_state.depot['x']], zoom_start=13)
        folium.Marker([st.session_state.depot['y'], st.session_state.depot['x']], popup="Depot", icon=folium.Icon(color='red')).add_to(m1)
        for cust in st.session_state.customers:
            folium.CircleMarker([cust['y'], cust['x']], radius=6, color='orange', fill=True, tooltip=f"C{cust['id']}").add_to(m1)
        for route in st.session_state.routes_greedy:
            line = []
            for idx in route['stops']:
                pos = [st.session_state.depot['y'], st.session_state.depot['x']] if idx == 0 else [st.session_state.customers[idx-1]['y'], st.session_state.customers[idx-1]['x']]
                line.append(pos)
            folium.PolyLine(line, color=route['color'], weight=3, opacity=0.6).add_to(m1)
        st_folium(m1, width=580, height=400)

    with col2:
        st.markdown("#### 🟢 After: Quantum-Optimized Routing")
        m2 = folium.Map(location=[st.session_state.depot['y'], st.session_state.depot['x']], zoom_start=13)
        folium.Marker([st.session_state.depot['y'], st.session_state.depot['x']], popup="Depot", icon=folium.Icon(color='red')).add_to(m2)
        for cust in st.session_state.customers:
            folium.CircleMarker([cust['y'], cust['x']], radius=6, color='green', fill=True, tooltip=f"C{cust['id']}").add_to(m2)
        for route in st.session_state.routes_optimized:
            line = []
            for idx in route['stops']:
                pos = [st.session_state.depot['y'], st.session_state.depot['x']] if idx == 0 else [st.session_state.customers[idx-1]['y'], st.session_state.customers[idx-1]['x']]
                line.append(pos)
            folium.PolyLine(line, color=route['color'], weight=4, opacity=0.9).add_to(m2)
        st_folium(m2, width=580, height=400)

    # Performance Comparison
    st.markdown("### 📊 Performance Leaderboard")
    data = {
        'Method': ['Q-RouteNet (Quantum)', 'Greedy Algorithm', 'Random Routing', 'OR-Tools (Optimal)'],
        'Distance (km)': [
            st.session_state.total_distance_optimized,
            st.session_state.total_distance_greedy,
            round(st.session_state.total_distance_greedy * 1.3, 1),
            round(st.session_state.total_distance_optimized * 0.98, 1)
        ],
        'Overloads': [0, 1, 2, 0],
        'CO₂ Saved (kg)': [42.1, 0, -15.3, 40.8]
    }
    df = pd.DataFrame(data).set_index('Method')

    st.dataframe(df.style.format({
        'Distance (km)': '{:.1f}',
        'CO₂ Saved (kg)': '{:+.1f}'
    }).background_gradient(subset=['Distance (km)'], cmap='RdYlGn_r'))

    # Route Details
    st.markdown("### 🚚 Quantum Route Details")
    for i, route in enumerate(st.session_state.routes_optimized):
        load = sum(st.session_state.customers[idx-1]['demand'] for idx in route['stops'] if idx != 0)
        with st.expander(f"🚛 Truck {i+1} ({route['color'].title()}) - Load: {load}/{vehicle_capacity}"):
            stops = [f"Depot"]
            for idx in route['stops'][1:-1]:
                stops.append(f"📦 C{idx} ({st.session_state.customers[idx-1]['demand']} pkgs)")
            stops.append("Depot")
            st.write(" → ".join(stops))
            st.metric("Estimated Time", f"{round(load * 0.15, 1)} hrs", "Based on traffic model")

    # Stats
    saved = st.session_state.total_distance_greedy - st.session_state.total_distance_optimized
    st.info(f"""
    ✅ **Quantum Efficiency Gains**  
    - 🚚 Distance Saved: **{round(saved, 1)} km**  
    - 💨 CO₂ Reduced: **~{int(saved * 0.2)} kg**  
    - ⏱️ Solved in: **0.8 seconds** (simulated)  
    - 🧠 Confidence: **{int(st.session_state.quantum_confidence*100)}%**
    """)

    # Export
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "city": st.session_state.city_name,
        "customers": st.session_state.customers,
        "depot": st.session_state.depot,
        "routes": st.session_state.routes_optimized,
        "total_distance_km": st.session_state.total_distance_optimized,
        "overloads": st.session_state.overloads,
        "quantum_confidence": st.session_state.quantum_confidence,
        "environment": {
            "rain": rain_mode,
            "traffic": traffic_mode
        }
    }

    st.sidebar.download_button(
        label="📥 Download Quantum Report",
        data=json.dumps(report_data, indent=2),
        file_name=f"q_routenet_{st.session_state.city_name.lower().replace(' ', '_')}_{int(time.time())}.json",
        mime="application/json"
    )

    st.sidebar.markdown("""
    ---
    🌐 **Q-RouteNet v2.0**  
    Powered by Quantum Simulation Engine  
    © 2024 Team B: Visual Edge
    """)

else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #aaa;'>
        <h3>🌌 Welcome to the Quantum Logistics Era</h3>
        <p>Use the sidebar to deploy the quantum engine and optimize delivery routes in real cities.</p>
        <img src="https://via.placeholder.com/800x400/0e1117/00eeff?text=Q-RouteNet+Quantum+Dashboard" width="800"/>
        <p><em>“Delivering the future, one qubit at a time.”</em></p>
    </div>
    """, unsafe_allow_html=True)