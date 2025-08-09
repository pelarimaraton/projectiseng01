import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# 1. Konfigurasi Halaman
# ---------------------------
st.set_page_config(
    page_title="Mohamed Salah Premier League Stats",
    layout="wide",
    page_icon="⚽"
)

st.title("📊 Statistik Mohamed Salah - Premier League")
st.markdown("""
Dashboard interaktif ini menampilkan performa **Mohamed Salah** di Premier League.
Termasuk data **Goals**, **Assists**, **Expected Goals (xG)**, dan lain-lain.  
Keterangan:
- **xG** (*Expected Goals*): Probabilitas peluang menjadi gol.
- **xAG** (*Expected Assists*): Probabilitas umpan menjadi assist.
- **Home / Away**: Lokasi pertandingan.
""")

# ---------------------------
# 2. Load Data
# ---------------------------
@st.cache_data
def load_data():
    # Pastikan file ini diunggah ke Streamlit Cloud
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

# Buat kolom Home/Away
df["HomeAway"] = df["Venue"].apply(lambda x: "Home" if x.strip().lower() == "home" else "Away")

# ---------------------------
# 4. Filter Samping
# ---------------------------
seasons = sorted(df["Season"].unique())
home_away_options = ["All", "Home", "Away"]

selected_season = st.sidebar.selectbox("Pilih Season", ["All"] + seasons)
selected_ha = st.sidebar.selectbox("Pilih Home/Away", home_away_options)

df_filtered = df.copy()
if selected_season != "All":
    df_filtered = df_filtered[df_filtered["Season"] == selected_season]
if selected_ha != "All":
    df_filtered = df_filtered[df_filtered["HomeAway"] == selected_ha]

# ---------------------------
# 5. Visualisasi 1 - Tren Musiman
# ---------------------------
st.subheader("📈 Tren Musiman: Goals, Assists, xG")
trend_df = df_filtered.groupby("Season")[["Goals", "Assists", "xG"]].sum().reset_index()
fig_trend = px.line(trend_df, x="Season", y=["Goals", "Assists", "xG"],
                    markers=True, labels={"value": "Jumlah", "variable": "Statistik"},
                    title="Perbandingan Goals, Assists, dan xG per Musim")
st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------
# 6. Visualisasi 2 - xG vs Goals (Bubble Chart)
# ---------------------------
st.subheader("⚽ Hubungan xG dengan Goals")
fig_scatter = px.scatter(
    df_filtered,
    x="xG",
    y="Goals",
    size="Shots",
    color="Season",
    hover_data=["Date", "Opponent", "Result", "Shots"],
    labels={"xG": "Expected Goals", "Goals": "Goals", "Shots": "Shots"},
    title="xG vs Goals (Bubble size = Shots)"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------
# 7. Visualisasi 3 - Peta Gol
# ---------------------------
if "GoalLocationX" in df.columns and "GoalLocationY" in df.columns:
    st.subheader("🗺️ Peta Lokasi Gol")
    fig_pitch = px.scatter(
        df_filtered[df_filtered["Goals"] > 0],
        x="GoalLocationX",
        y="GoalLocationY",
        color="Season",
        hover_data=["Date", "Opponent", "Result"],
        labels={"GoalLocationX": "Lebar Lapangan", "GoalLocationY": "Panjang Lapangan"},
        title="Lokasi Gol Mohamed Salah"
    )
    fig_pitch.update_yaxes(scaleanchor="x", scaleratio=0.7)
    st.plotly_chart(fig_pitch, use_container_width=True)
else:
    st.info("Data lokasi gol tidak tersedia di dataset ini.")

# ---------------------------
# 8. Tabel Data
# ---------------------------
st.subheader("📋 Data Detail")
st.dataframe(df_filtered)

# ---------------------------
# 9. Ringkasan Statistik
# ---------------------------
st.subheader("📊 Ringkasan Statistik")
summary_stats = {
    "Total Goals": df_filtered["Goals"].sum(),
    "Total Assists": df_filtered["Assists"].sum(),
    "Total Shots": df_filtered["Shots"].sum(),
    "Total xG": round(df_filtered["xG"].sum(), 2),
    "Total xAG": round(df_filtered["xAG"].sum(), 2)
}
st.write(summary_stats)
