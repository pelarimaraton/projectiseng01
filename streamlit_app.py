import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Mohamed Salah Premier League Stats", layout="wide")

st.title("📊 Mohamed Salah - Statistik Premier League")
st.markdown("""
Aplikasi ini menampilkan statistik **Mohamed Salah** di Premier League.
### Penjelasan singkat metrik:
- **Goals**: Jumlah gol yang dicetak.
- **Assists**: Umpan yang berujung gol.
- **Shots**: Total tembakan.
- **xG (Expected Goals)**: Prediksi jumlah gol berdasarkan kualitas peluang.
- **xAG (Expected Assisted Goals)**: Prediksi jumlah assist berdasarkan peluang yang diciptakan.
- **Passing Accuracy**: Persentase umpan sukses.
- **Dribbles Completed**: Jumlah dribel berhasil.
""")

@st.cache_data
def load_data():
    df = pd.read_csv("Salah-Stat-PrimerLeague.csv")
    
    # Bersihkan kolom
    df.columns = df.columns.str.strip()
    
    # Rename agar konsisten
    df.rename(columns={
        "Date": "MatchDate",
        "Gls": "Goals",
        "Ast": "Assists",
        "Sh": "Shots",
        "xG": "xG",
        "xAG": "xAG",
        "Cmp%": "PassAccuracy",
        "Succ": "DribblesCompleted",
        "Att.1": "DribblesAttempted"
    }, inplace=True)
    
    # Ubah tipe data
    num_cols = ["Goals", "Assists", "Shots", "xG", "xAG", "PassAccuracy", "DribblesCompleted", "DribblesAttempted"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df["MatchDate"] = pd.to_datetime(df["MatchDate"])
    df["HomeAway"] = df["Venue"].apply(lambda x: "Home" if str(x).lower() == "home" else "Away")
    
    return df

df = load_data()

# Sidebar filter
st.sidebar.header("Filter Data")
season_filter = st.sidebar.multiselect("Pilih Musim", sorted(df["Season"].unique()), default=sorted(df["Season"].unique()))
venue_filter = st.sidebar.multiselect("Pilih Venue", ["Home", "Away"], default=["Home", "Away"])

df_filtered = df[(df["Season"].isin(season_filter)) & (df["HomeAway"].isin(venue_filter))]

# Ringkasan Statistik
st.subheader("📌 Ringkasan Statistik")
col1, col2, col3, col4 = st.columns(4)
col1.metric("⚽ Goals", int(df_filtered["Goals"].sum()))
col2.metric("🎯 Assists", int(df_filtered["Assists"].sum()))
col3.metric("📈 xG", round(df_filtered["xG"].sum(), 2))
col4.metric("📊 xAG", round(df_filtered["xAG"].sum(), 2))

# Line Chart: Tren Musiman
st.subheader("📈 Tren Musiman")
fig_line = px.line(df_filtered, x="MatchDate", y=["Goals", "Assists", "xG", "xAG"], markers=True)
st.plotly_chart(fig_line, use_container_width=True)

# Scatter Plot: xG vs Goals
st.subheader("🎯 xG vs Goals")
fig_scatter = px.scatter(df_filtered, x="xG", y="Goals", size="Shots", color="Season",
                         hover_data=["Opponent", "MatchDate"],
                         title="xG vs Goals (Ukuran bubble = jumlah tembakan)")
st.plotly_chart(fig_scatter, use_container_width=True)

# Heatmap: Distribusi Statistik
st.subheader("🔥 Heatmap Statistik")
heatmap_data = df_filtered.groupby("Season")[["Goals", "Assists", "Shots", "xG", "xAG"]].sum()
fig_heatmap = px.imshow(heatmap_data, text_auto=True, aspect="auto", color_continuous_scale="YlOrRd")
st.plotly_chart(fig_heatmap, use_container_width=True)

# Radar Chart: Perbandingan Statistik
st.subheader("🛡️ Radar Chart")
stats_avg = df_filtered[["Goals", "Assists", "Shots", "xG", "xAG", "PassAccuracy", "DribblesCompleted"]].mean()
categories = list(stats_avg.index)
fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(r=stats_avg.values, theta=categories, fill='toself', name='Rata-rata'))
fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False)
st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("💡 *Data ini diambil dari catatan pertandingan Mohamed Salah di Premier League. Visualisasi interaktif ini memudahkan analisis performa pemain berdasarkan musim dan lokasi pertandingan.*")
