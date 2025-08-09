import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Judul Aplikasi ---
st.set_page_config(page_title="Statistik Mohamed Salah - Premier League", layout="wide")
st.title("📊 Statistik Mohamed Salah di Premier League")
st.markdown("""
Aplikasi ini menampilkan statistik Mohamed Salah selama bermain di Premier League.  
Data mencakup **Goals (Gls)**, **Assists (Ast)**, **xG (Expected Goals)**, tembakan, dan lainnya.  
**Catatan:**  
- **xG** = "Expected Goals", peluang terjadinya gol berdasarkan kualitas peluang.  
- **Ast** = Assist, umpan yang menghasilkan gol.  
- **Sh** = Shots, jumlah tembakan.  
""")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("Salah-Stat-PrimerLeague.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# --- Sidebar Filter ---
st.sidebar.header("⚙️ Filter Data")
season_list = sorted(df['Season'].unique())
venue_list = sorted(df['Venue'].unique())

season_filter = st.sidebar.multiselect("Pilih Season", season_list, default=season_list)
venue_filter = st.sidebar.multiselect("Pilih Venue", venue_list, default=venue_list)

df_filtered = df[df['Season'].isin(season_filter) & df['Venue'].isin(venue_filter)]

# --- Visualisasi 1: Tren Goals, Assists, xG ---
st.subheader("📈 Tren Goals, Assists, dan xG")
trend_df = df_filtered.groupby("MatchDay").agg({
    "Gls": "sum",
    "Ast": "sum",
    "xG": "sum"
}).reset_index()

fig_trend = px.line(
    trend_df,
    x="MatchDay",
    y=["Gls", "Ast", "xG"],
    markers=True,
    labels={"value": "Jumlah", "MatchDay": "Pertandingan"},
    title="Tren Goals, Assists, dan xG per Matchday"
)
st.plotly_chart(fig_trend, use_container_width=True)

# --- Visualisasi 2: xG vs Goals ---
st.subheader("⚽ Hubungan xG dengan Goals")
fig_scatter = px.scatter(
    df_filtered,
    x="xG",
    y="Gls",
    size="Sh",
    color="Season",
    hover_data=["Date", "Opponent", "Result"],
    labels={"xG": "Expected Goals", "Gls": "Goals", "Sh": "Shots"},
    title="xG vs Goals (Bubble size = Shots)"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# --- Visualisasi 3: Peta Gol (Jika data koordinat ada) ---
if "GoalLocationX" in df.columns and "GoalLocationY" in df.columns:
    st.subheader("🗺️ Peta Gol Mohamed Salah")
    fig_map = px.scatter(
        df_filtered[df_filtered["Gls"] > 0],
        x="GoalLocationX",
        y="GoalLocationY",
        color="Season",
        size="Gls",
        hover_data=["Date", "Opponent", "Result"],
        title="Lokasi Gol Mohamed Salah"
    )
    fig_map.update_yaxes(autorange="reversed")  # Untuk mencocokkan orientasi lapangan
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Peta gol tidak tersedia karena data koordinat tidak ada di CSV.")

# --- Visualisasi 4: Distribusi Shots ---
st.subheader("📊 Distribusi Jumlah Tembakan")
fig_hist = px.histogram(
    df_filtered,
    x="Sh",
    nbins=10,
    color="Season",
    title="Distribusi Jumlah Tembakan per Pertandingan",
    labels={"Sh": "Shots"}
)
st.plotly_chart(fig_hist, use_container_width=True)

# --- Footer ---
st.markdown("""
---
**Sumber Data:** Salah-Stat-PrimerLeague.csv  
Dibuat dengan ❤️ menggunakan Streamlit & Plotly
""")
