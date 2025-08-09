import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==========================
# Judul Aplikasi
# ==========================
st.set_page_config(page_title="Statistik Mohamed Salah - Premier League", layout="wide")
st.title("⚽ Statistik Mohamed Salah di Premier League")
st.markdown("""
Dashboard ini menampilkan performa Mohamed Salah selama bermain di Premier League.  
Termasuk **Goals, Assists, xG (Expected Goals)**, dan peta tembakan (shot map).  
**xG (Expected Goals)** adalah metrik yang memperkirakan peluang gol berdasarkan kualitas tembakan.  
""")

# ==========================
# Load Data
# ==========================
url = "https://raw.githubusercontent.com/pelarimaraton/projectiseng01/main/Salah-Stat-PrimerLeague.csv"
df = pd.read_csv(url)

# Pastikan kolom numerik dibaca benar
num_cols = ["Gls", "Ast", "PK", "PKatt", "Sh", "SoT", "xG", "npxG", "xAG", "SCA", "GCA", "Cmp", "Att", "Cmp%", "PrgP", "Carries", "PrgC", "Succ"]
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Tambahkan kolom Season jika belum ada
if "Season" not in df.columns:
    df["Season"] = df.index.get_level_values(1) if isinstance(df.index, pd.MultiIndex) else "Unknown"

# ==========================
# Sidebar Filter
# ==========================
st.sidebar.header("🔍 Filter Data")
season_list = df["Season"].dropna().unique().tolist()
season_selected = st.sidebar.multiselect("Pilih Musim", options=season_list, default=season_list)

venue_list = df["Venue"].dropna().unique().tolist()
venue_selected = st.sidebar.multiselect("Pilih Venue", options=venue_list, default=venue_list)

# Filter data
df_filtered = df[
    (df["Season"].isin(season_selected)) &
    (df["Venue"].isin(venue_selected))
]

# ==========================
# Statistik Ringkas
# ==========================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Gol", int(df_filtered["Gls"].sum()))
col2.metric("Total Assist", int(df_filtered["Ast"].sum()))
col3.metric("Total xG", round(df_filtered["xG"].sum(), 2))
col4.metric("Shot On Target %", f"{round((df_filtered['SoT'].sum()/df_filtered['Sh'].sum())*100,2)}%")

# ==========================
# Tren Goals, Assists, xG per Season
# ==========================
st.subheader("📈 Tren Musiman: Goals, Assists, xG")
trend_data = df_filtered.groupby("Season")[["Gls", "Ast", "xG"]].sum().reset_index()
fig_trend = px.line(trend_data, x="Season", y=["Gls", "Ast", "xG"], markers=True)
fig_trend.update_layout(title="Performa Musiman", yaxis_title="Jumlah", legend_title="Statistik")
st.plotly_chart(fig_trend, use_container_width=True)

# ==========================
# Scatter Plot: xG vs Goals
# ==========================
st.subheader("🎯 xG vs Goals")
fig_scatter = px.scatter(
    df_filtered,
    x="xG", y="Gls",
    size="Sh",
    color="Season",
    hover_data=["Date", "Opponent", "Venue"],
    title="xG vs Goals (Bubble size = Shots)"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================
# Peta Gol (Shot Map)
# ==========================
st.subheader("📍 Peta Gol & Tembakan")

# Jika dataset tidak punya koordinat, kita buat random untuk contoh
if "x" not in df_filtered.columns or "y" not in df_filtered.columns:
    np.random.seed(42)
    df_filtered["x"] = np.random.uniform(0, 100, len(df_filtered))
    df_filtered["y"] = np.random.uniform(0, 100, len(df_filtered))

# Buat half-pitch
fig_pitch = go.Figure()

# Outline setengah lapangan
fig_pitch.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(color="white", width=2))
fig_pitch.add_shape(type="rect", x0=0, y0=30, x1=18, y1=70, line=dict(color="white", width=2))  # Kotak penalti
fig_pitch.add_shape(type="circle", x0=88, y0=40, x1=98, y1=60, line=dict(color="white", width=2))  # Lingkaran penalti

# Titik tembakan
fig_pitch.add_trace(go.Scatter(
    x=df_filtered["x"], y=df_filtered["y"],
    mode="markers",
    marker=dict(
        size=df_filtered["Sh"]*2,
        color=df_filtered["Gls"].apply(lambda g: "red" if g > 0 else "blue"),
        opacity=0.7,
        line=dict(width=1, color="white")
    ),
    text=df_filtered["Opponent"],
    hovertemplate="Lawan: %{text}<br>Gol: %{marker.color}<extra></extra>",
    name="Shots"
))

fig_pitch.update_layout(
    title="Shot Map Mohamed Salah",
    xaxis=dict(showgrid=False, zeroline=False, visible=False),
    yaxis=dict(showgrid=False, zeroline=False, visible=False),
    plot_bgcolor="green",
    height=500
)

st.plotly_chart(fig_pitch, use_container_width=True)

# ==========================
# Penutup
# ==========================
st.markdown("""
---
ℹ️ **Catatan**: Data diambil dari statistik Mohamed Salah di Premier League.  
- **xG (Expected Goals)** = Prediksi peluang gol berdasarkan kualitas peluang.  
- **SCA (Shot-Creating Actions)** = Aksi yang menghasilkan tembakan.  
- **GCA (Goal-Creating Actions)** = Aksi yang menghasilkan gol.  
""")
