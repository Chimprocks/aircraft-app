
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Aircraft Weight & Route Planner", layout="wide")

st.title("✈️ Aircraft Weight, Passenger, Cargo & Distance Planner")
st.caption("Interactive planner for modern passenger aircraft from year 2000 onwards. Edit aircraft_data.csv to add more planes.")

@st.cache_data
def load_data():
    return pd.read_csv("aircraft_data.csv")

df = load_data()

with st.sidebar:
    st.header("Aircraft filter")
    maker = st.multiselect("Manufacturer", sorted(df["manufacturer"].unique()), default=sorted(df["manufacturer"].unique()))
    aircraft_type = st.multiselect("Aircraft type", sorted(df["type"].unique()), default=sorted(df["type"].unique()))
    year_min, year_max = st.slider(
        "Entry year",
        int(df["entry_year"].min()),
        int(df["entry_year"].max()),
        (2000, int(df["entry_year"].max()))
    )

filtered = df[
    df["manufacturer"].isin(maker)
    & df["type"].isin(aircraft_type)
    & df["entry_year"].between(year_min, year_max)
].copy()

if filtered.empty:
    st.warning("No aircraft match your filter.")
    st.stop()

left, right = st.columns([1, 2])

with left:
    plane_name = st.selectbox("Choose aircraft", filtered["model"].tolist())
    plane = filtered[filtered["model"] == plane_name].iloc[0]

    st.subheader("Trip inputs")
    passengers = st.number_input("Passengers", min_value=0, max_value=int(plane["max_pax"])+50, value=int(plane["typical_pax"]), step=1)
    avg_passenger_kg = st.number_input("Average passenger + cabin bag weight (kg)", min_value=40, max_value=140, value=95, step=1)
    cargo_kg = st.number_input("Cargo / checked baggage weight (kg)", min_value=0, max_value=200000, value=8000, step=500)
    distance_km = st.number_input("Route distance (km)", min_value=0, max_value=20000, value=min(3000, int(plane["range_km"])), step=100)

    st.subheader("Fuel assumptions")
    reserve_percent = st.slider("Fuel reserve %", 0, 30, 10)
    fuel_burn_kg_per_km = st.number_input(
        "Estimated fuel burn kg/km",
        min_value=1.0,
        max_value=25.0,
        value=round(float(plane["max_fuel_kg"]) / float(plane["range_km"]), 2),
        step=0.1
    )

payload_kg = passengers * avg_passenger_kg + cargo_kg
trip_fuel_kg = distance_km * fuel_burn_kg_per_km
fuel_with_reserve_kg = trip_fuel_kg * (1 + reserve_percent / 100)
estimated_takeoff_weight_kg = payload_kg + fuel_with_reserve_kg + (plane["mtow_kg"] - plane["max_payload_kg"] - plane["max_fuel_kg"])

payload_ok = payload_kg <= plane["max_payload_kg"]
fuel_ok = fuel_with_reserve_kg <= plane["max_fuel_kg"]
mtow_ok = estimated_takeoff_weight_kg <= plane["mtow_kg"]
range_ok = distance_km <= plane["range_km"]
pax_ok = passengers <= plane["max_pax"]

with right:
    st.subheader(f"{plane_name} summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Max passengers", f"{int(plane['max_pax'])}")
    c2.metric("Range", f"{int(plane['range_km']):,} km")
    c3.metric("MTOW", f"{int(plane['mtow_kg']):,} kg")
    c4.metric("Max payload", f"{int(plane['max_payload_kg']):,} kg")

    st.subheader("Flight feasibility")
    checks = pd.DataFrame([
        ["Passengers within limit", passengers, plane["max_pax"], pax_ok],
        ["Payload within max payload", payload_kg, plane["max_payload_kg"], payload_ok],
        ["Fuel within max fuel", fuel_with_reserve_kg, plane["max_fuel_kg"], fuel_ok],
        ["Takeoff weight within MTOW", estimated_takeoff_weight_kg, plane["mtow_kg"], mtow_ok],
        ["Distance within aircraft range", distance_km, plane["range_km"], range_ok],
    ], columns=["Check", "Your value", "Aircraft limit", "Pass"])

    st.dataframe(
        checks.style.format({"Your value": "{:,.0f}", "Aircraft limit": "{:,.0f}"}).map(
            lambda v: "background-color: #c6f6d5" if v is True else ("background-color: #fed7d7" if v is False else ""),
            subset=["Pass"]
        ),
        use_container_width=True
    )

    if all([payload_ok, fuel_ok, mtow_ok, range_ok, pax_ok]):
        st.success("✅ This configuration looks feasible with the simplified model.")
    else:
        st.error("⚠️ This configuration breaks one or more limits. Try fewer passengers, less cargo, shorter distance, or a larger aircraft.")

    st.subheader("Weight breakdown")
    chart_df = pd.DataFrame({
        "Component": ["Passengers + cabin bags", "Cargo / checked baggage", "Fuel incl. reserve", "Estimated empty + operating weight"],
        "Weight kg": [
            passengers * avg_passenger_kg,
            cargo_kg,
            fuel_with_reserve_kg,
            estimated_takeoff_weight_kg - payload_kg - fuel_with_reserve_kg
        ]
    })
    fig = px.bar(chart_df, x="Component", y="Weight kg", text_auto=".0f")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Compare aircraft database")
compare_cols = ["model","manufacturer","entry_year","type","max_pax","range_km","mtow_kg","max_payload_kg","max_fuel_kg","cargo_volume_m3"]
st.dataframe(filtered[compare_cols].sort_values(["manufacturer","model"]), use_container_width=True)

st.info(
    "Safety note: This is an educational planning model, not a certified aircraft performance tool. "
    "Real dispatch calculations need detailed airline manuals, runway, weather, alternate airport, fuel policy, cargo balance, centre of gravity, and legal reserve rules."
)
