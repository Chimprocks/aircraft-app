
import math
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Aircraft World Dispatch Simulator", page_icon="✈️", layout="wide")
st.title("✈️ Aircraft World Dispatch Simulator")
st.caption("3D aircraft + real-map style runway picker + seat map + cargo/military + airline game + dispatch checks. Educational only.")

@st.cache_data
def load_aircraft():
    return pd.read_csv("aircraft_data.csv")

@st.cache_data
def load_runways():
    return pd.read_csv("runways_sample.csv")

df = load_aircraft()
runways_default = load_runways()

with st.sidebar:
    st.header("Aircraft filter")
    cat = st.multiselect("Category", sorted(df.category.unique()), default=sorted(df.category.unique()))
    maker = st.multiselect("Manufacturer", sorted(df.manufacturer.unique()), default=sorted(df.manufacturer.unique()))
    year = st.slider("Entry year", int(df.entry_year.min()), int(df.entry_year.max()), (2000, int(df.entry_year.max())))

filtered = df[df.category.isin(cat) & df.manufacturer.isin(maker) & df.entry_year.between(year[0], year[1])].copy()
if filtered.empty:
    st.warning("No aircraft found.")
    st.stop()

plane_name = st.selectbox("Choose aircraft", filtered.model.tolist())
plane = filtered[filtered.model == plane_name].iloc[0]
max_pax = int(plane.max_pax)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✈️ Aircraft + 3D",
    "🪑 Seat + cargo balance",
    "🌍 Runway map",
    "🧭 Dispatch checks",
    "🎮 Airline game"
])

# Shared route/runway data
uploaded = None
runway_df = runways_default.copy()

with tab1:
    st.subheader("Aircraft overview")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Category", plane.category)
    c2.metric("Max pax", f"{max_pax:,}")
    c3.metric("Range", f"{int(plane.range_km):,} km")
    c4.metric("MTOW", f"{int(plane.mtow_kg):,} kg")
    c5.metric("Payload", f"{int(plane.max_payload_kg):,} kg")
    c6.metric("Cargo volume", f"{float(plane.cargo_volume_m3):,.1f} m³")

    st.markdown("### 3D-style aircraft visual")
    fig_plane = go.Figure()
    fig_plane.add_trace(go.Scatter3d(x=[-8, 8], y=[0,0], z=[0,0], mode="lines", line=dict(width=14), name="Fuselage"))
    fig_plane.add_trace(go.Scatter3d(x=[-1,0,1], y=[0,-7,0], z=[0,0,0], mode="lines", line=dict(width=9), name="Left wing"))
    fig_plane.add_trace(go.Scatter3d(x=[-1,0,1], y=[0,7,0], z=[0,0,0], mode="lines", line=dict(width=9), name="Right wing"))
    fig_plane.add_trace(go.Scatter3d(x=[-7,-8,-7], y=[0,-2,0], z=[0,0,1.8], mode="lines", line=dict(width=7), name="Tail"))
    fig_plane.add_trace(go.Scatter3d(x=[7.7], y=[0], z=[0], mode="markers", marker=dict(size=10), name="Nose"))
    fig_plane.update_layout(height=430, margin=dict(l=0,r=0,t=0,b=0), scene=dict(xaxis_title="", yaxis_title="", zaxis_title=""))
    st.plotly_chart(fig_plane, use_container_width=True)

    st.markdown("### Basic flight loading")
    a,b,c = st.columns(3)
    with a:
        passengers = st.number_input("Total passengers", 0, max(max_pax, 1), min(int(plane.typical_pax), max_pax), 1)
        avg_pax_weight = st.number_input("Avg passenger + cabin bag kg", 40, 140, 95, 1)
    with b:
        cargo_kg_basic = st.number_input("Cargo / baggage kg", 0, 300000, min(8000, int(plane.max_payload_kg)), 500)
        distance_km = st.number_input("Route distance km", 0, 25000, min(3000, int(plane.range_km)), 100)
    with c:
        reserve_percent = st.slider("Fuel reserve %", 0, 45, 10)
        fuel_burn = st.number_input("Fuel burn kg/km", 1.0, 60.0, max(1.0, round(float(plane.max_fuel_kg)/max(float(plane.range_km),1),2)), 0.1)

    payload = passengers*avg_pax_weight + cargo_kg_basic
    trip_fuel = distance_km*fuel_burn
    reserve_fuel = trip_fuel*reserve_percent/100
    fuel_total = trip_fuel + reserve_fuel
    empty_weight = float(plane.mtow_kg)-float(plane.max_payload_kg)-float(plane.max_fuel_kg)
    takeoff_weight = empty_weight + payload + fuel_total

    checks = pd.DataFrame([
        ["Passengers", passengers, max_pax, passengers <= max_pax],
        ["Payload", payload, plane.max_payload_kg, payload <= plane.max_payload_kg],
        ["Fuel", fuel_total, plane.max_fuel_kg, fuel_total <= plane.max_fuel_kg],
        ["Takeoff weight", takeoff_weight, plane.mtow_kg, takeoff_weight <= plane.mtow_kg],
        ["Distance", distance_km, plane.range_km, distance_km <= plane.range_km],
    ], columns=["Check","Your value","Limit","Pass"])
    st.dataframe(checks, use_container_width=True)
    st.success("✅ Feasible in simple sim") if all(checks.Pass) else st.error("⚠️ Limit broken")

    weight_df = pd.DataFrame({"Component":["Passengers","Cargo","Trip fuel","Reserve fuel","Empty/operating"],"Weight kg":[passengers*avg_pax_weight,cargo_kg_basic,trip_fuel,reserve_fuel,empty_weight]})
    st.plotly_chart(px.bar(weight_df, x="Component", y="Weight kg", text_auto=".0f"), use_container_width=True)

with tab2:
    st.subheader("Seat map + cargo balance + centre of gravity")
    if max_pax == 0:
        st.info("Cargo aircraft: passenger seating disabled, but cargo balance still works.")
        economy = premium = business = first = 0
    else:
        x1,x2,x3 = st.columns(3)
        with x1:
            economy = st.number_input("Economy", 0, max_pax, min(int(plane.typical_pax), max_pax), 1, key="eco")
            premium = st.number_input("Premium economy", 0, max_pax, 0, 1, key="prem")
        with x2:
            business = st.number_input("Business", 0, max_pax, 0, 1, key="bus")
            first = st.number_input("First", 0, max_pax, 0, 1, key="first")
        with x3:
            pref_zone = st.selectbox("Preferred cabin zone", ["Auto mix","Front","Middle","Rear"])
            pref_pos = st.selectbox("Preferred seat position", ["Auto mix","Window","Aisle","Middle"])

        def letters_for(max_pax, typ):
            if max_pax <= 150: return ["A","C","D","F"]
            if "Narrow" in typ or max_pax <= 244: return ["A","B","C","D","E","F"]
            if max_pax <= 380: return ["A","B","C","D","E","F","G","H","J"]
            return ["A","B","C","D","E","F","G","H","J","K"]
        def pos(letter, letters):
            if letter in [letters[0], letters[-1]]: return "Window"
            if len(letters) <= 4 and letter in [letters[1], letters[-2]]: return "Aisle"
            if len(letters) > 4 and letter in [letters[2], letters[-3]]: return "Aisle"
            return "Middle"
        def zone(row, rows):
            if row <= rows/3: return "Front"
            if row <= rows*2/3: return "Middle"
            return "Rear"
        def make_map():
            letters = letters_for(max_pax, str(plane.type))
            rows = math.ceil(max_pax/len(letters))
            seats=[]
            for r in range(1,rows+1):
                for l in letters:
                    if len(seats) >= max_pax: break
                    seats.append({"Row":r,"Letter":l,"Seat":f"{r}{l}","Position":pos(l,letters),"Zone":zone(r,rows),"Class":"Empty"})
            for cls,count in [("First",first),("Business",business),("Premium",premium),("Economy",economy)]:
                assigned=0
                zones=[pref_zone] if pref_zone!="Auto mix" else (["Front","Middle","Rear"] if cls in ["First","Business"] else ["Rear","Middle","Front"])
                positions=[pref_pos] if pref_pos!="Auto mix" else ["Window","Aisle","Middle"]
                for z in zones:
                    for p in positions:
                        for s in seats:
                            if assigned>=count: break
                            if s["Class"]=="Empty" and s["Zone"]==z and s["Position"]==p:
                                s["Class"]=cls; assigned+=1
                for s in seats:
                    if assigned>=count: break
                    if s["Class"]=="Empty":
                        s["Class"]=cls; assigned+=1
            return pd.DataFrame(seats)
        seatmap=make_map()
        display=[]
        for r,g in seatmap.groupby("Row"):
            row={"Row":r}
            for _,s in g.iterrows():
                row[s.Letter]={"First":"🟣","Business":"🔵","Premium":"🟢","Economy":"🟡","Empty":"⚪"}[s.Class]+" "+s.Seat
            display.append(row)
        st.dataframe(pd.DataFrame(display), use_container_width=True, height=420)
        st.caption("🟣 First | 🔵 Business | 🟢 Premium | 🟡 Economy | ⚪ Empty")
        st.dataframe(seatmap[seatmap.Class!="Empty"].groupby(["Class","Zone","Position"]).size().reset_index(name="Seats"), use_container_width=True)

    st.markdown("### Cargo hold balance")
    z1,z2,z3 = st.columns(3)
    forward_cargo = z1.number_input("Forward cargo hold kg", 0, 200000, min(3000, int(plane.max_payload_kg)), 250)
    mid_cargo = z2.number_input("Middle cargo hold kg", 0, 200000, min(3000, int(plane.max_payload_kg)), 250)
    aft_cargo = z3.number_input("Aft cargo hold kg", 0, 200000, min(2000, int(plane.max_payload_kg)), 250)

    cargo_total = forward_cargo + mid_cargo + aft_cargo
    total_people = economy + premium + business + first
    people_weight = total_people * 95
    # Simple CG estimate: forward = 20% MAC, middle = 35%, aft = 50%
    empty_cg = float(plane.empty_cg_percent_mac)
    cg_numerator = empty_weight*empty_cg + forward_cargo*20 + mid_cargo*35 + aft_cargo*50 + people_weight*35
    cg_denominator = max(empty_weight + cargo_total + people_weight, 1)
    cg = cg_numerator / cg_denominator

    cg_ok = float(plane.cg_min_percent_mac) <= cg <= float(plane.cg_max_percent_mac)
    st.metric("Estimated centre of gravity", f"{cg:.1f}% MAC")
    st.success("✅ CG inside simplified safe range") if cg_ok else st.error("⚠️ CG outside simplified safe range. Move cargo/passengers.")

    cg_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=cg,
        title={"text":"CG % MAC"},
        gauge={"axis":{"range":[0,60]}, "threshold":{"line":{"width":4},"value":cg}}
    ))
    st.plotly_chart(cg_fig, use_container_width=True)

with tab3:
    st.subheader("Interactive runway map")
    st.write("Starter world runway data is included. For all-world runways, upload a larger CSV using the same column names.")
    uploaded = st.file_uploader("Upload runway CSV: airport,iata,country,lat,lon,runway,runway_length_m,elevation_m", type=["csv"])
    runway_df = pd.read_csv(uploaded) if uploaded else runways_default
    runway_df = runway_df.dropna(subset=["lat","lon"])

    labels = runway_df["airport"] + " (" + runway_df["iata"] + ")"
    col1,col2,col3 = st.columns(3)
    origin = col1.selectbox("Origin runway/airport", labels, index=0)
    dest = col2.selectbox("Destination runway/airport", labels, index=min(1, len(runway_df)-1))
    alternate = col3.selectbox("Alternate airport", labels, index=min(2, len(runway_df)-1))

    o = runway_df.iloc[list(labels).index(origin)]
    d = runway_df.iloc[list(labels).index(dest)]
    alt = runway_df.iloc[list(labels).index(alternate)]

    st.map(runway_df.rename(columns={"lat":"latitude","lon":"longitude"}), latitude="latitude", longitude="longitude", size="runway_length_m")

    route_df = pd.DataFrame({"lat":[o.lat,d.lat,alt.lat],"lon":[o.lon,d.lon,alt.lon],"Airport":[o.airport,d.airport,alt.airport],"Role":["Origin","Destination","Alternate"]})
    fig_map = px.line_geo(route_df.iloc[:2], lat="lat", lon="lon", text="Airport", projection="natural earth", title=f"Route: {o.iata} → {d.iata}, alternate {alt.iata}")
    fig_map.add_scattergeo(lat=runway_df.lat, lon=runway_df.lon, text=runway_df.airport + " runway " + runway_df.runway, mode="markers", marker=dict(size=7))
    fig_map.add_scattergeo(lat=[alt.lat], lon=[alt.lon], text=[f"Alternate: {alt.airport}"], mode="markers+text", marker=dict(size=12))
    fig_map.update_layout(height=560)
    st.plotly_chart(fig_map, use_container_width=True)

    st.write("Add your own custom runway pointer")
    p1,p2,p3,p4 = st.columns(4)
    custom_name = p1.text_input("Pointer name", "My runway point")
    custom_lat = p2.number_input("Latitude", -90.0, 90.0, float(o.lat), 0.0001)
    custom_lon = p3.number_input("Longitude", -180.0, 180.0, float(o.lon), 0.0001)
    custom_rwy = p4.text_input("Runway label", "00/00")
    custom_df = pd.DataFrame({"lat":[custom_lat],"lon":[custom_lon],"name":[custom_name + " " + custom_rwy]})
    custom_fig = px.scatter_geo(custom_df, lat="lat", lon="lon", text="name", projection="natural earth", title="Your custom runway pointer")
    custom_fig.update_traces(marker=dict(size=14))
    st.plotly_chart(custom_fig, use_container_width=True)

    st.write("Selected runway details")
    st.dataframe(pd.DataFrame([o,d,alt]), use_container_width=True)

with tab4:
    st.subheader("Real-dispatch-style checks")
    st.warning("Educational model only. Real dispatch calculations need airline manuals, runway performance charts, weather, alternates, fuel policy, cargo balance, CG, and legal reserve rules.")

    q1,q2,q3,q4 = st.columns(4)
    wind = q1.number_input("Headwind + / tailwind - knots", -100, 100, 0, 5)
    temp = q2.number_input("Temperature °C", -40, 60, 25, 1)
    weather_risk = q3.selectbox("Weather condition", ["Good", "Rain", "Storm", "Fog", "Snow/Ice"])
    legal_reserve_min = q4.number_input("Legal reserve minutes", 0, 180, 45, 5)

    # Simple runway requirement model
    base_required = 1200 + (takeoff_weight / max(float(plane.mtow_kg),1))*1800
    temp_penalty = max(0, temp-15)*15
    tailwind_penalty = max(0, -wind)*20
    weather_penalty = {"Good":0,"Rain":250,"Storm":600,"Fog":400,"Snow/Ice":800}[weather_risk]
    runway_required = base_required + temp_penalty + tailwind_penalty + weather_penalty

    st.metric("Estimated runway required", f"{runway_required:,.0f} m")
    st.caption("Use the Runway Map tab to compare this with selected runway length.")

    legal_reserve_fuel = legal_reserve_min/60 * fuel_burn * 850
    taxi_fuel = st.number_input("Taxi fuel kg", 0, 20000, 1000, 100)
    alternate_distance = st.number_input("Alternate distance km", 0, 5000, 500, 50)
    alternate_fuel = alternate_distance * fuel_burn
    contingency_percent = st.slider("Contingency fuel % of trip fuel", 0, 20, 5)

    total_dispatch_fuel = trip_fuel + trip_fuel*contingency_percent/100 + alternate_fuel + legal_reserve_fuel + taxi_fuel
    st.metric("Total dispatch fuel estimate", f"{total_dispatch_fuel:,.0f} kg")
    st.success("✅ Fuel fits aircraft tank") if total_dispatch_fuel <= float(plane.max_fuel_kg) else st.error("⚠️ Fuel exceeds max fuel capacity")

    dispatch_df = pd.DataFrame({
        "Fuel item":["Trip fuel","Contingency","Alternate","Legal reserve","Taxi"],
        "kg":[trip_fuel, trip_fuel*contingency_percent/100, alternate_fuel, legal_reserve_fuel, taxi_fuel]
    })
    st.plotly_chart(px.bar(dispatch_df, x="Fuel item", y="kg", text_auto=".0f"), use_container_width=True)

with tab5:
    st.subheader("Airline game mode")
    st.write("Try to make the route profitable.")
    g1,g2,g3,g4 = st.columns(4)
    ticket = g1.number_input("Average passenger ticket AUD", 0, 10000, 650, 50)
    cargo_rate = g2.number_input("Cargo revenue AUD per kg", 0.0, 50.0, 2.5, 0.1)
    fuel_price = g3.number_input("Fuel cost AUD per kg", 0.0, 10.0, 1.2, 0.1)
    fixed_cost = g4.number_input("Airport + crew + maintenance AUD", 0, 1000000, 45000, 5000)

    revenue = passengers*ticket + cargo_kg_basic*cargo_rate
    cost = fuel_total*fuel_price + fixed_cost
    profit = revenue - cost

    q1,q2,q3 = st.columns(3)
    q1.metric("Revenue", f"AUD {revenue:,.0f}")
    q2.metric("Cost", f"AUD {cost:,.0f}")
    q3.metric("Profit", f"AUD {profit:,.0f}")

    game_df = pd.DataFrame({"Type":["Passenger revenue","Cargo revenue","Fuel cost","Fixed cost","Profit"],"AUD":[passengers*ticket,cargo_kg_basic*cargo_rate,-fuel_total*fuel_price,-fixed_cost,profit]})
    st.plotly_chart(px.bar(game_df, x="Type", y="AUD", text_auto=".0f"), use_container_width=True)
    if profit > 0:
        st.success("🏆 Profitable route! Airline CEO mode unlocked.")
    else:
        st.error("💸 Losing money. Increase ticket/cargo revenue or reduce cost.")

st.divider()
st.subheader("Aircraft database")
st.dataframe(filtered.sort_values(["category","manufacturer","model"]), use_container_width=True)
