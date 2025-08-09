import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Statistik Mohamed Salah", layout="wide")

# ---------------------------
# 1. Load Data
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Salah-Stat-PrimerLeague.csv")
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
    df["MatchDate"] = pd.to_datetime(df["MatchDate"])
    df["HomeAway"] = df["Venue"].apply(lambda x: "Home" if x.lower() == "home" else "Away")
    return df

df = load_data()

# ---------------------------
# 2. Sidebar Filter
# ---------------------------
st.sidebar.header("⚙️ Filter Data")
seasons = st.sidebar.multiselect("Pilih Musim", df["Season"].unique(), default=df["Season"].unique())
venues = st.sidebar.multiselect("Pilih Venue (Home/Away)", df["HomeAway"].unique(), default=df["HomeAway"].unique())

df_filtered = df[(df["Season"].isin(seasons)) & (df["HomeAway"].isin(venues))]

# ---------------------------
# 3. Penjelasan Statistik
# ---------------------------
with st.expander("📖 Penjelasan Istilah Statistik"):
    st.markdown("""
    - **Goals (Gls)** → Jumlah gol yang dicetak.
    - **Assists (Ast)** → Umpan yang langsung menghasilkan gol.
    - **xG (Expected Goals)** → Perkiraan peluang menjadi gol berdasarkan kualitas peluang (lokasi, tipe tembakan, dll).
    - **xAG (Expected Assisted Goals)** → Perkiraan peluang menjadi gol dari umpan yang diberikan.
    - **Shots (Sh)** → Jumlah tembakan ke gawang.
    - **Passing Accuracy (Cmp%)** → Persentase keberhasilan umpan.
    - **Dribbling** → Upaya melewati lawan sambil membawa bola.
    """)

# ---------------------------
# 4. Ringkasan Statistik
# ---------------------------
st.subheader("📊 Ringkasan Statistik Mohamed Salah")

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
col1.metric("⚽ Goals", df_filtered["Goals"].sum())
col2.metric("🎯 Assists", df_filtered["Assists"].sum())
col3.metric("📈 xG", round(df_filtered["xG"].sum(), 2))
col4.metric("📊 xAG", round(df_filtered["xAG"].sum(), 2))
col5.metric("🔫 Shots", df_filtered["Shots"].sum())
col6.metric("🎯 Passing Acc (%)", round(df_filtered["PassAccuracy"].mean(), 2))
col7.metric("💨 Dribbles", df_filtered["DribblesCompleted"].sum())

# ---------------------------
# 5. Line Chart (Tren Statistik)
# ---------------------------
st.subheader("📈 Tren Statistik per Pertandingan")
fig_line = px.line(
    df_filtered.sort_values("MatchDate"),
    x="MatchDate",
    y=["Goals", "Assists", "xG", "xAG", "Shots"],
    markers=True,
    title="Tren Goals, Assists, xG, xAG, Shots"
)
st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------
# 6. Scatter Plot (xG vs Goals)
# ---------------------------
st.subheader("⚽ xG vs Goals")
fig_scatter = px.scatter(
    df_filtered,
    x="xG",
    y="Goals",
    size="Shots",
    color="Season",
    hover_data=["Opponent", "MatchDate"],
    title="xG vs Goals (Bubble size = Shots)"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------
# 7. Heatmap Statistik vs Lawan
# ---------------------------
st.subheader("🔥 Heatmap Statistik vs Lawan")
heatmap_df = df_filtered.groupby("Opponent")[["Goals", "Assists", "xG", "xAG", "Shots"]].sum()
heatmap_df["TotalImpact"] = heatmap_df["Goals"] + heatmap_df["xG"]
heatmap_df = heatmap_df.sort_values("TotalImpact", ascending=False)

fig_heatmap = px.imshow(
    heatmap_df.drop(columns=["TotalImpact"]),
    text_auto=".1f",
    color_continuous_scale=["#1a9850", "#fee08b", "#d73027"],
    title="Heatmap Statistik vs Lawan"
)
fig_heatmap.update_layout(
    xaxis_title="Statistik",
    yaxis_title="Lawan",
    font=dict(size=12)
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# ---------------------------
# 8. Radar Chart (Perbandingan Kemampuan)
# ---------------------------
st.subheader("🕹️ Radar Chart Statistik Rata-rata")
avg_stats = {
    "Goals": df_filtered["Goals"].mean(),
    "Assists": df_filtered["Assists"].mean(),
    "Shots": df_filtered["Shots"].mean(),
    "Passing Accuracy": df_filtered["PassAccuracy"].mean(),
    "Dribbling Success": (df_filtered["DribblesCompleted"].sum() / max(df_filtered["DribblesAttempted"].sum(), 1)) * 100
}

radar_df = pd.DataFrame({
    "Stat": list(avg_stats.keys()),
    "Value": list(avg_stats.values())
})

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=radar_df["Value"],
    theta=radar_df["Stat"],
    fill="toself",
    name="Rata-rata"
))
fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, max(radar_df["Value"]) + 5])
    ),
    showlegend=False
)
st.plotly_chart(fig_radar, use_container_width=True)

# ---------------------------
# 9. Dataframe
# ---------------------------
st.subheader("📋 Detail Pertandingan")
st.dataframe(df_filtered.sort_values(by="MatchDate", ascending=False))
