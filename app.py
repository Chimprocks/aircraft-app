
import math
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Aircraft App Pro", page_icon="✈️", layout="wide")

st.markdown("""
<style>
.stApp {background: radial-gradient(circle at top,#16213e 0%,#070b12 45%,#05070b 100%); color:#eaf2ff;}
[data-testid="stSidebar"] {background:#0b1220; border-right:1px solid #1f2a44;}
.block-container {padding-top:1rem;}
.hero {position:relative;height:430px;border-radius:22px;overflow:hidden;background:
linear-gradient(rgba(5,10,20,.15),rgba(5,10,20,.6)),
url("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1800&q=80");
background-size:cover;background-position:center;border:1px solid rgba(120,170,255,.35);box-shadow:0 0 40px rgba(32,110,255,.18);}
.plane {position:absolute;left:6%;top:42%;font-size:82px;filter:drop-shadow(0 0 18px rgba(255,255,255,.8));animation:fly 7s ease-in-out infinite;}
@keyframes fly {0%{transform:translateX(0) translateY(15px) rotate(4deg) scale(1);}50%{transform:translateX(430px) translateY(-45px) rotate(-4deg) scale(1.15);}100%{transform:translateX(0) translateY(15px) rotate(4deg) scale(1);}}
.hud {position:absolute;left:24px;right:24px;bottom:18px;background:rgba(5,10,20,.72);border:1px solid rgba(120,170,255,.3);border-radius:18px;padding:16px 20px;backdrop-filter:blur(8px);}
.routebar {height:8px;background:#24324f;border-radius:99px;overflow:hidden;}
.routefill {height:8px;width:58%;background:linear-gradient(90deg,#7dd3fc,#60a5fa,#a7f3d0);animation:route 5s ease-in-out infinite;}
@keyframes route {0%{width:18%;}50%{width:74%;}100%{width:18%;}}
.card {background:rgba(12,20,36,.88);border:1px solid rgba(120,170,255,.18);border-radius:18px;padding:16px;box-shadow:0 10px 30px rgba(0,0,0,.25);}
.metricbig {font-size:28px;font-weight:800;color:#67e8f9;}
.small {color:#9fb4d6;font-size:13px;}
.badge {display:inline-block;padding:4px 10px;border-radius:999px;background:#143d72;border:1px solid #2d73c7;font-size:12px;color:#cfe8ff;}
.logo {font-size:26px;font-weight:900;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_aircraft():
    return pd.read_csv("aircraft_data.csv")

@st.cache_data
def load_runways():
    return pd.read_csv("runways_sample.csv")

aircraft = load_aircraft()
runways = load_runways()

st.markdown('<div class="logo">✈️ AIRCRAFT APP PRO <span class="badge">Animated Simulator UI</span> <span class="badge">Accurate Seat Space</span> <span class="badge">Airline Game</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("🎛️ Control Panel")
    category = st.multiselect("Aircraft type", sorted(aircraft.category.unique()), default=sorted(aircraft.category.unique()))
    maker = st.multiselect("Manufacturer", sorted(aircraft.manufacturer.unique()), default=sorted(aircraft.manufacturer.unique()))
    filtered = aircraft[aircraft.category.isin(category) & aircraft.manufacturer.isin(maker)]
    plane_name = st.selectbox("Aircraft", filtered.model.tolist())
    camera = st.radio("Camera view", ["Chase view", "Cockpit view", "Wing view", "Tower view"])
    sim_speed = st.select_slider("Simulation speed", options=["0.5x","1x","2x","4x"], value="1x")

plane = aircraft[aircraft.model == plane_name].iloc[0]
max_pax = int(plane.max_pax)

left, mid, right = st.columns([1.1,2.8,1.2])
with left:
    st.markdown(f'<div class="card"><div class="small">FLIGHT DETAILS</div><h3>{plane.model}</h3><span class="badge">{plane.category}</span><br><br><div class="small">AIRLINE</div><b>Chinmay Airways</b><br><br><div class="small">REGISTRATION</div><b>VT-CXA</b><br><br><div class="small">STATUS</div><span style="color:#86efac;font-weight:800;">En Route</span></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="small">LIVE FLIGHT INFO</div><br><div>Altitude <span style="float:right;color:#67e8f9;">35,987 ft</span></div><div>Ground speed <span style="float:right;color:#67e8f9;">903 km/h</span></div><div>Heading <span style="float:right;color:#67e8f9;">299°</span></div><div>Outside temp <span style="float:right;color:#67e8f9;">-48°C</span></div></div>', unsafe_allow_html=True)

with mid:
    st.markdown('<div class="hero"><div class="plane">🛫</div><div class="hud"><div style="display:flex;justify-content:space-between;"><div><div class="small">FROM</div><b>PER Perth</b></div><div><div class="small">DISTANCE FLOWN</div><b>3,421 km</b></div><div><div class="small">TIME TO DESTINATION</div><b>06:11</b></div><div><div class="small">TO</div><b>SIN Singapore</b></div></div><br><div class="routebar"><div class="routefill"></div></div></div></div>', unsafe_allow_html=True)

with right:
    st.markdown(f'<div class="card"><div class="small">AIRCRAFT MODEL</div><h3>{plane.model}</h3><div class="metricbig">{int(plane.range_km):,} km</div><div class="small">Range</div><br><div class="metricbig">{int(plane.mtow_kg):,} kg</div><div class="small">MTOW</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="card"><div class="small">SIM CONTROLS</div><h2>Pause {sim_speed}</h2><div class="small">{camera}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs(["🛫 Simulator", "🌍 World Map", "🪑 Interactive Seats + Cargo", "🎮 Airline Game"])

with tab1:
    a,b,c,d = st.columns(4)
    passengers = a.number_input("Passengers", 0, max(max_pax,1), min(int(plane.typical_pax), max_pax), 1)
    cargo_kg = b.number_input("Cargo kg", 0, 300000, min(8000, int(plane.max_payload_kg)), 500)
    distance_km = c.number_input("Distance km", 0, 25000, min(3000, int(plane.range_km)), 100)
    fuel_burn = d.number_input("Fuel burn kg/km", 1.0, 60.0, max(1.0, round(float(plane.max_fuel_kg)/max(float(plane.range_km),1),2)), 0.1)
    payload = passengers*95 + cargo_kg
    fuel = distance_km*fuel_burn*1.1
    empty = float(plane.mtow_kg) - float(plane.max_payload_kg) - float(plane.max_fuel_kg)
    tow = payload + fuel + empty
    x1,x2,x3,x4 = st.columns(4)
    x1.metric("Payload", f"{payload:,.0f} kg")
    x2.metric("Fuel", f"{fuel:,.0f} kg")
    x3.metric("Takeoff weight", f"{tow:,.0f} kg")
    x4.metric("Limit status", "OK" if tow <= plane.mtow_kg else "Heavy")
    profile = pd.DataFrame({"Stage":["Takeoff","Climb","Cruise","Descent","Landing"],"Distance km":[distance_km*.03,distance_km*.12,distance_km*.70,distance_km*.12,distance_km*.03]})
    st.plotly_chart(px.bar(profile, x="Stage", y="Distance km", title="Flight progress"), use_container_width=True)

with tab2:
    st.subheader("Interactive runway map")
    uploaded = st.file_uploader("Upload more runways CSV", type=["csv"])
    runway_df = pd.read_csv(uploaded) if uploaded else runways
    labels = runway_df.airport + " (" + runway_df.iata + ")"
    o_name = st.selectbox("Origin", labels, index=0)
    d_name = st.selectbox("Destination", labels, index=min(1, len(runway_df)-1))
    o = runway_df.iloc[list(labels).index(o_name)]
    d = runway_df.iloc[list(labels).index(d_name)]
    fig = px.line_geo(pd.DataFrame({"lat":[o.lat,d.lat],"lon":[o.lon,d.lon],"name":[o.airport,d.airport]}), lat="lat", lon="lon", text="name", projection="natural earth", title=f"{o.iata} → {d.iata}")
    fig.add_scattergeo(lat=runway_df.lat, lon=runway_df.lon, text=runway_df.airport + " " + runway_df.runway, mode="markers", marker=dict(size=7))
    fig.update_layout(height=560, paper_bgcolor="#070b12", plot_bgcolor="#070b12", font_color="#eaf2ff")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Add pointer")
    p1,p2,p3 = st.columns(3)
    p1.text_input("Pointer name", "My runway")
    lat = p2.number_input("Latitude", -90.0, 90.0, float(o.lat), 0.0001)
    lon = p3.number_input("Longitude", -180.0, 180.0, float(o.lon), 0.0001)
    st.map(pd.DataFrame({"lat":[lat],"lon":[lon]}), latitude="lat", longitude="lon")

with tab3:
    st.subheader("Accurate-ish interactive seat selector")
    if max_pax == 0:
        st.info("Cargo aircraft selected — no passenger seat map.")
    else:
        seats_abreast = int(plane.seats_abreast)
        class_space = {"First":4.0, "Business":2.4, "Premium":1.35, "Economy":1.0}
        c1,c2,c3,c4 = st.columns(4)
        first = c1.number_input("First seats", 0, max_pax, 0)
        business = c2.number_input("Business seats", 0, max_pax, 0)
        premium = c3.number_input("Premium economy seats", 0, max_pax, 0)
        economy = c4.number_input("Economy seats", 0, max_pax, min(int(plane.typical_pax), max_pax))
        pref = st.selectbox("Preferred placement", ["Auto realistic", "Front", "Middle", "Rear", "Window priority", "Aisle priority"])
        used_space = first*class_space["First"] + business*class_space["Business"] + premium*class_space["Premium"] + economy
        total_people = first + business + premium + economy
        st.metric("Cabin space used", f"{used_space:.0f} / {max_pax}")
        if used_space <= max_pax and total_people <= max_pax:
            st.success("This cabin mix fits the aircraft cabin space.")
        else:
            st.error("Too many premium/large seats for this aircraft.")

        def letters_for(n):
            if n <= 3: return ["A","C","D"]
            if n == 4: return ["A","C","D","F"]
            if n == 6: return ["A","B","C","D","E","F"]
            if n == 9: return ["A","B","C","D","E","F","G","H","J"]
            return ["A","B","C","D","E","F","G","H","J","K"]
        letters = letters_for(seats_abreast)
        rows = max(1, math.ceil(max_pax / max(seats_abreast,1)))
        seat_list=[]
        for r in range(1, rows+1):
            for l in letters:
                zone = "Front" if r <= rows/3 else ("Middle" if r <= rows*2/3 else "Rear")
                pos = "Window" if l in [letters[0], letters[-1]] else ("Aisle" if l in [letters[min(2,len(letters)-1)], letters[max(0,len(letters)-3)]] else "Middle")
                seat_list.append({"row":r,"letter":l,"seat":f"{r}{l}","zone":zone,"pos":pos,"class":"Empty","icon":"⚪"})
        def priority(cls):
            if pref == "Front": return ["Front","Middle","Rear"]
            if pref == "Middle": return ["Middle","Front","Rear"]
            if pref == "Rear": return ["Rear","Middle","Front"]
            if cls in ["First","Business"]: return ["Front","Middle","Rear"]
            if cls == "Premium": return ["Middle","Front","Rear"]
            return ["Rear","Middle","Front"]
        def pos_priority():
            if pref == "Window priority": return ["Window","Aisle","Middle"]
            if pref == "Aisle priority": return ["Aisle","Window","Middle"]
            return ["Window","Aisle","Middle"]
        for cls,count,icon in [("First", first, "🟣"), ("Business", business, "🔵"), ("Premium", premium, "🟢"), ("Economy", economy, "🟡")]:
            done=0
            for z in priority(cls):
                for p in pos_priority():
                    for s in seat_list:
                        if done >= count: break
                        if s["class"]=="Empty" and s["zone"]==z and s["pos"]==p:
                            s["class"]=cls; s["icon"]=icon; done+=1
            for s in seat_list:
                if done >= count: break
                if s["class"]=="Empty":
                    s["class"]=cls; s["icon"]=icon; done+=1

        display=[]
        for r in range(1, rows+1):
            row={"Row":r}
            for s in [x for x in seat_list if x["row"]==r]:
                row[s["letter"]] = f'{s["icon"]} {s["seat"]}'
            display.append(row)
        st.dataframe(pd.DataFrame(display), use_container_width=True, height=430)
        st.caption("🟣 First | 🔵 Business | 🟢 Premium | 🟡 Economy | ⚪ Empty")
        summary = pd.DataFrame(seat_list).query("class != 'Empty'").groupby(["class","zone","pos"]).size().reset_index(name="seats")
        st.dataframe(summary, use_container_width=True)

    st.markdown("### Cargo balance")
    fwd, mid, aft = st.columns(3)
    fwdkg = fwd.number_input("Forward cargo kg", 0, 200000, 3000, 250)
    midkg = mid.number_input("Middle cargo kg", 0, 200000, 3000, 250)
    aftkg = aft.number_input("Aft cargo kg", 0, 200000, 2000, 250)
    cg = (fwdkg*20 + midkg*35 + aftkg*50) / max(fwdkg+midkg+aftkg,1)
    st.metric("Simple CG estimate", f"{cg:.1f}% MAC")
    st.success("Balanced") if 16 <= cg <= 38 else st.error("Move cargo")

with tab4:
    st.subheader("Airline Tycoon Mode")
    t1,t2,t3,t4 = st.columns(4)
    ticket = t1.number_input("Ticket AUD", 0, 10000, 650, 50)
    cargo_rate = t2.number_input("Cargo AUD/kg", 0.0, 50.0, 2.5, .1)
    fuel_price = t3.number_input("Fuel AUD/kg", 0.0, 10.0, 1.2, .1)
    fixed = t4.number_input("Fixed cost AUD", 0, 1000000, 45000, 5000)
    revenue = passengers*ticket + cargo_kg*cargo_rate
    cost = fuel*fuel_price + fixed
    profit = revenue - cost
    m1,m2,m3 = st.columns(3)
    m1.metric("Revenue", f"AUD {revenue:,.0f}")
    m2.metric("Cost", f"AUD {cost:,.0f}")
    m3.metric("Profit", f"AUD {profit:,.0f}")
    st.success("Profitable route") if profit > 0 else st.error("Losing money")
    game_df = pd.DataFrame({"Type":["Passenger revenue","Cargo revenue","Fuel cost","Fixed cost","Profit"],"AUD":[passengers*ticket,cargo_kg*cargo_rate,-fuel*fuel_price,-fixed,profit]})
    st.plotly_chart(px.bar(game_df, x="Type", y="AUD", text_auto=".0f"), use_container_width=True)

st.warning("Real dispatch calculations need detailed airline manuals, runway, weather, alternate airport, fuel policy, cargo balance, centre of gravity, and legal reserve rules.")
