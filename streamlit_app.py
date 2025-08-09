import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Statistik Mohamed Salah - Premier League", layout="wide")

# =======================
# LOAD DATA
# =======================
@st.cache_data
def load_data():
    try:
        return pd.read_csv("Salah-Stat-PrimerLeague.csv")
    except FileNotFoundError:
        # fallback kalau file diambil dari repo GitHub
        url = "https://raw.githubusercontent.com/USERNAME/REPO/main/Salah-Stat-PrimerLeague.csv"
        return pd.read_csv(url)

df = load_data()

# Pastikan kolom yang dibutuhkan ada
expected_cols = ["Season", "HomeAway", "Goals", "Assists", "xG", "Shots", "MatchDate", "Opponent", "xA", "Touches", "Passes", "GoalLocationX", "GoalLocationY"]
missing_cols = [c for c in expected_cols if c not in df.columns]
if missing_cols:
    st.error(f"Kolom berikut hilang dari data: {missing_cols}")
    st.stop()

# Konversi tanggal
df["MatchDate"] = pd.to_datetime(df["MatchDate"])

# =======================
# SIDEBAR FILTER
# =======================
st.sidebar.header("Filter Data")
season_filter = st.sidebar.multiselect("Pilih Musim", sorted(df["Season"].unique()), default=sorted(df["Season"].unique()))
homeaway_filter = st.sidebar.multiselect("Home / Away", df["HomeAway"].unique(), default=df["HomeAway"].unique())

df_filtered = df[(df["Season"].isin(season_filter)) & (df["HomeAway"].isin(homeaway_filter))]

# =======================
# HEADER
# =======================
st.title("📊 Statistik Mohamed Salah - Premier League")
st.markdown("""
Aplikasi ini menampilkan statistik performa **Mohamed Salah** selama bermain di Premier League.
Data meliputi **Goals**, **Assists**, **xG (Expected Goals)**, **xA (Expected Assists)**, jumlah tembakan, sentuhan bola, hingga lokasi gol.
""")

# =======================
# KPI CARD
# =======================
total_goals = df_filtered["Goals"].sum()
total_assists = df_filtered["Assists"].sum()
avg_xg = df_filtered["xG"].mean()
avg_xa = df_filtered["xA"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("⚽ Total Goals", total_goals)
col2.metric("🎯 Total Assists", total_assists)
col3.metric("📈 Rata-rata xG", f"{avg_xg:.2f}")
col4.metric("🅰️ Rata-rata xA", f"{avg_xa:.2f}")

# =======================
# TREN MUSIMAN
# =======================
st.subheader("📅 Tren Musiman: Goals, Assists, xG")
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=df_filtered["MatchDate"], y=df_filtered["Goals"], mode="lines+markers", name="Goals"))
fig_trend.add_trace(go.Scatter(x=df_filtered["MatchDate"], y=df_filtered["Assists"], mode="lines+markers", name="Assists"))
fig_trend.add_trace(go.Scatter(x=df_filtered["MatchDate"], y=df_filtered["xG"], mode="lines+markers", name="xG"))

fig_trend.update_layout(title="Perkembangan Goals, Assists, dan xG per Pertandingan", xaxis_title="Tanggal", yaxis_title="Jumlah / Nilai", hovermode="x unified")
st.plotly_chart(fig_trend, use_container_width=True)

# =======================
# SCATTER xG vs GOALS
# =======================
st.subheader("📊 Hubungan xG vs Goals")
st.markdown("""
**xG (Expected Goals)** adalah metrik yang mengukur seberapa besar kemungkinan sebuah tembakan menjadi gol.
Semakin tinggi xG, semakin besar peluangnya menjadi gol. 
Grafik ini membandingkan jumlah gol aktual dengan nilai xG.
""")

fig_scatter = px.scatter(
    df_filtered,
    x="xG",
    y="Goals",
    size="Shots",
    color="Season",
    hover_data=["MatchDate", "Opponent", "Assists", "xA"],
    title="xG vs Goals (Ukuran bubble = jumlah tembakan)"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# =======================
# PETA GOL
# =======================
st.subheader("🗺️ Peta Lokasi Gol")
st.markdown("Visualisasi posisi di mana Mohamed Salah mencetak gol (koordinat lapangan).")
fig_pitch = px.scatter(
    df_filtered[df_filtered["Goals"] > 0],
    x="GoalLocationX",
    y="GoalLocationY",
    color="Season",
    hover_data=["MatchDate", "Opponent", "Goals"],
    title="Lokasi Gol Mohamed Salah",
    size="Goals"
)
fig_pitch.update_yaxes(scaleanchor="x", scaleratio=0.7)
st.plotly_chart(fig_pitch, use_container_width=True)

# =======================
# DISTRIBUSI TEMBAKAN
# =======================
st.subheader("📍 Distribusi Tembakan per Musim")
fig_shots = px.box(
    df_filtered,
    x="Season",
    y="Shots",
    color="Season",
    title="Distribusi Jumlah Tembakan per Musim"
)
st.plotly_chart(fig_shots, use_container_width=True)

# =======================
# TABEL DATA
# =======================
st.subheader("📋 Data Pertandingan")
st.dataframe(df_filtered.sort_values("MatchDate", ascending=False))

