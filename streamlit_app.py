import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------
# 1. Konfigurasi Halaman
# ---------------------------
st.set_page_config(
    page_title="Mohamed Salah Premier League Stats",
    layout="wide",
    page_icon="⚽"
)

st.title("⚽ Dashboard Statistik Mohamed Salah - Premier League")
st.markdown("""
Dashboard ini menampilkan **statistik detail Mohamed Salah** di Premier League:  
- **Goals, Assists, xG, xAG, Shots, Passing, Dribbling**
- Filter berdasarkan **musim** dan **Home/Away**
- Visualisasi interaktif termasuk **line chart, scatter plot, heatmap, radar chart**
""")

# ---------------------------
# 2. Load Data
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Salah-Stat-PrimerLeague.csv")
    return df

df = load_data()

# ---------------------------
# 3. Bersihkan & Siapkan Data
# ---------------------------
df.columns = df.columns.str.strip()
df.rename(columns={
    "Gls": "Goals",
    "Ast": "Assists",
    "Sh": "Shots"
}, inplace=True)

numeric_cols = ["Goals", "Assists", "Shots", "xG", "npxG", "xAG", "Cmp", "Att", "Cmp%", "PrgP", "Carries", "PrgC"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["HomeAway"] = df["Venue"].apply(lambda x: "Home" if x.strip().lower() == "home" else "Away")

# ---------------------------
# 4. Filter Sidebar
# ---------------------------
seasons = sorted(df["Season"].unique())
home_away_options = ["All", "Home", "Away"]

selected_season = st.sidebar.selectbox("📅 Pilih Season", ["All"] + seasons)
selected_ha = st.sidebar.selectbox("🏟 Pilih Home/Away", home_away_options)

df_filtered = df.copy()
if selected_season != "All":
    df_filtered = df_filtered[df_filtered["Season"] == selected_season]
if selected_ha != "All":
    df_filtered = df_filtered[df_filtered["HomeAway"] == selected_ha]

# ---------------------------
# 5. Ringkasan Statistik Menarik
# ---------------------------
st.subheader("📊 Ringkasan Statistik")

total_goals = int(df_filtered["Goals"].sum())
total_assists = int(df_filtered["Assists"].sum())
total_shots = int(df_filtered["Shots"].sum())
total_xg = round(df_filtered["xG"].sum(), 2)
total_xag = round(df_filtered["xAG"].sum(), 2)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div style="background-color:#ff4b4b;padding:20px;border-radius:10px;text-align:center">
        <h2 style="color:white">{total_goals}</h2>
        <p style="color:white;font-weight:bold">Goals</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background-color:#4bafff;padding:20px;border-radius:10px;text-align:center">
        <h2 style="color:white">{total_assists}</h2>
        <p style="color:white;font-weight:bold">Assists</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="background-color:#4bff88;padding:20px;border-radius:10px;text-align:center">
        <h2 style="color:white">{total_shots}</h2>
        <p style="color:white;font-weight:bold">Shots</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="background-color:#ff884b;padding:20px;border-radius:10px;text-align:center">
        <h2 style="color:white">{total_xg}</h2>
        <p style="color:white;font-weight:bold">Expected Goals (xG)</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div style="background-color:#aa4bff;padding:20px;border-radius:10px;text-align:center">
        <h2 style="color:white">{total_xag}</h2>
        <p style="color:white;font-weight:bold">Expected Assists (xAG)</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# 6. Tren Musiman
# ---------------------------
st.subheader("📈 Tren Goals, Assists, xG per Musim")
trend_df = df_filtered.groupby("Season")[["Goals", "Assists", "xG"]].sum().reset_index()
fig_trend = px.line(
    trend_df, x="Season", y=["Goals", "Assists", "xG"],
    markers=True,
    color_discrete_sequence=["#ff4b4b", "#4bafff", "#4bff88"],
    labels={"value": "Jumlah", "variable": "Statistik"},
    title="Tren Goals, Assists, xG"
)
st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------
# 7. Scatter xG vs Goals
# ---------------------------
st.subheader("⚽ Hubungan xG dengan Goals")
fig_scatter = px.scatter(
    df_filtered,
    x="xG", y="Goals",
    size="Shots", color="Season",
    hover_data=["Date", "Opponent", "Result", "Shots"],
    color_discrete_sequence=px.colors.qualitative.Set2,
    title="xG vs Goals (Bubble = Shots)"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------
# 8. Heatmap Performansi
# ---------------------------
st.subheader("🔥 Heatmap Statistik")
heatmap_df = df_filtered.groupby("Opponent")[["Goals", "Assists", "xG", "xAG", "Shots"]].sum()
fig_heatmap = px.imshow(
    heatmap_df,
    text_auto=True,
    color_continuous_scale="Reds",
    title="Heatmap Performansi Lawan"
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# ---------------------------
# 9. Radar Chart
# ---------------------------
st.subheader("🎯 Radar Chart: Keterampilan")
radar_stats = {
    "Goals": total_goals,
    "Assists": total_assists,
    "xG": total_xg,
    "xAG": total_xag,
    "Shots": total_shots,
    "Progressive Passes": df_filtered["PrgP"].sum(),
    "Progressive Carries": df_filtered["PrgC"].sum()
}
categories = list(radar_stats.keys())
values = list(radar_stats.values())
values += values[:1]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=values,
    theta=categories + [categories[0]],
    fill='toself',
    name='Statistik',
    line_color="#ff4b4b"
))
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True)),
    title="Radar Chart Keterampilan",
    showlegend=False
)
st.plotly_chart(fig_radar, use_container_width=True)

# ---------------------------
# 10. Distribusi Goals
# ---------------------------
st.subheader("📊 Distribusi Goals")
fig_hist = px.histogram(
    df_filtered, x="Goals",
    color="Season",
    marginal="box",
    nbins=5,
    title="Distribusi Goals per Pertandingan"
)
st.plotly_chart(fig_hist, use_container_width=True)

# ---------------------------
# 11. Data Table
# ---------------------------
st.subheader("📋 Data Detail")
st.dataframe(df_filtered)
