import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# Judul dan Deskripsi
# ===============================
st.set_page_config(page_title="Statistik Mohamed Salah - Premier League", layout="wide")

st.title("📊 Statistik Mohamed Salah di Premier League")
st.markdown("""
Analisis performa **Mohamed Salah** selama bermain di **Premier League**.
Data ini mencakup **Goals**, **Assists**, **Expected Goals (xG)**, tembakan, dan peta posisi gol.

**Apa itu xG (Expected Goals)?**  
xG adalah metrik yang mengukur peluang sebuah tembakan menjadi gol, berdasarkan posisi, sudut tembak, dan tipe assist.
Semakin tinggi xG, semakin besar kemungkinan peluang tersebut berbuah gol.
""")

# ===============================
# Load Data
# ===============================
@st.cache_data
def load_data():
    # Ganti ini dengan path/URL dataset asli Anda
    df = pd.read_csv("mohamed_salah_premier_league.csv")
    return df

df = load_data()

# Pastikan kolom tanggal dalam format datetime
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# ===============================
# Sidebar Filter
# ===============================
st.sidebar.header("🔍 Filter Data")
season_options = sorted(df["Season"].unique())
venue_options = sorted(df["Venue"].unique())

selected_season = st.sidebar.multiselect("Pilih Season", season_options, default=season_options)
selected_venue = st.sidebar.multiselect("Pilih Venue", venue_options, default=venue_options)

# Filter Data
df_filtered = df[(df["Season"].isin(selected_season)) & (df["Venue"].isin(selected_venue))]

# ===============================
# Tren Musiman: Goals, Assists, xG
# ===============================
st.subheader("📈 Tren Musiman")

if df_filtered.empty:
    st.warning("⚠️ Data tidak tersedia untuk filter yang dipilih.")
else:
    trend_data = df_filtered.groupby("Season")[["Gls", "Ast", "xG"]].sum().reset_index()
    fig_trend = px.line(
        trend_data,
        x="Season",
        y=["Gls", "Ast", "xG"],
        markers=True,
        title="Tren Goals, Assists, dan xG per Season"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# ===============================
# Scatter Plot: xG vs Goals
# ===============================
st.subheader("🎯 xG vs Goals")

scatter_data = df_filtered.copy()
scatter_data["xG"] = pd.to_numeric(scatter_data["xG"], errors="coerce")
scatter_data["Gls"] = pd.to_numeric(scatter_data["Gls"], errors="coerce")
scatter_data["Sh"] = pd.to_numeric(scatter_data["Sh"], errors="coerce")
scatter_data = scatter_data.dropna(subset=["xG", "Gls", "Sh"])

if scatter_data.empty:
    st.warning("⚠️ Data tidak tersedia untuk kombinasi filter ini.")
else:
    fig_scatter = px.scatter(
        scatter_data,
        x="xG",
        y="Gls",
        size="Sh",
        color="Season",
        hover_data=["Date", "Opponent", "Venue"],
        title="xG vs Goals (Bubble size = Shots)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ===============================
# Heatmap Gol (Goal Map)
# ===============================
st.subheader("🗺️ Peta Gol Mohamed Salah")

if {"x", "y"}.issubset(df_filtered.columns):
    heatmap_data = df_filtered.dropna(subset=["x", "y"])
    if heatmap_data.empty:
        st.warning("⚠️ Data posisi gol tidak tersedia untuk filter ini.")
    else:
        fig_heatmap = px.density_heatmap(
            heatmap_data,
            x="x",
            y="y",
            nbinsx=20,
            nbinsy=20,
            color_continuous_scale="Reds",
            title="Peta Kepadatan Gol/Tembakan"
        )
        fig_heatmap.update_yaxes(autorange="reversed")  # agar sesuai tampilan lapangan
        st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.info("ℹ️ Data tidak memiliki koordinat posisi gol (kolom x, y).")

# ===============================
# Ringkasan Statistik
# ===============================
st.subheader("📋 Ringkasan Statistik")
if not df_filtered.empty:
    total_goals = df_filtered["Gls"].sum()
    total_assists = df_filtered["Ast"].sum()
    total_xg = df_filtered["xG"].sum()
    total_shots = df_filtered["Sh"].sum()

    st.metric("Total Goals", total_goals)
    st.metric("Total Assists", total_assists)
    st.metric("Total xG", round(total_xg, 2))
    st.metric("Total Shots", total_shots)
else:
    st.warning("Tidak ada data untuk ditampilkan pada ringkasan statistik.")
