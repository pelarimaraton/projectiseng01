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
        "xAG": "xAG"
    }, inplace=True)
    df["MatchDate"] = pd.to_datetime(df["MatchDate"])
    return df

df = load_data()

# ---------------------------
# 2. Sidebar Filter
# ---------------------------
st.sidebar.header("⚙️ Filter Data")
seasons = st.sidebar.multiselect("Pilih Musim", df["Season"].unique(), default=df["Season"].unique())
venues = st.sidebar.multiselect("Pilih Venue", df["Venue"].unique(), default=df["Venue"].unique())

df_filtered = df[(df["Season"].isin(seasons)) & (df["Venue"].isin(venues))]

# ---------------------------
# 3. Ringkasan Statistik
# ---------------------------
st.subheader("📊 Ringkasan Statistik Mohamed Salah")

col1, col2, col3, col4, col5 = st.columns(5)
total_goals = df_filtered["Goals"].sum()
total_assists = df_filtered["Assists"].sum()
total_shots = df_filtered["Shots"].sum()
total_xg = df_filtered["xG"].sum()
total_xag = df_filtered["xAG"].sum()

with col1:
    st.metric("⚽ Goals", total_goals)
with col2:
    st.metric("🎯 Assists", total_assists)
with col3:
    st.metric("🔫 Shots", total_shots)
with col4:
    st.metric("📈 xG", round(total_xg, 2))
with col5:
    st.metric("📊 xAG", round(total_xag, 2))

# ---------------------------
# 4. Tren Goals per Musim
# ---------------------------
st.subheader("📈 Tren Goals per Musim")
goals_per_season = df_filtered.groupby("Season")["Goals"].sum().reset_index()
fig_goals = px.bar(goals_per_season, x="Season", y="Goals", text="Goals", color="Goals", 
                   color_continuous_scale="blues")
st.plotly_chart(fig_goals, use_container_width=True)

# ---------------------------
# 5. Scatter Plot xG vs Goals
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
# 6. Heatmap Statistik Upgrade
# ---------------------------
st.subheader("🔥 Heatmap Statistik vs Lawan")
heatmap_df = df_filtered.groupby("Opponent")[["Goals", "Assists", "xG", "xAG", "Shots"]].sum()
heatmap_df["TotalImpact"] = heatmap_df["Goals"] + heatmap_df["xG"]
heatmap_df = heatmap_df.sort_values("TotalImpact", ascending=False)

fig_heatmap = px.imshow(
    heatmap_df.drop(columns=["TotalImpact"]),
    text_auto=".1f",
    color_continuous_scale=["#1a9850", "#fee08b", "#d73027"],  # hijau → kuning → merah
    title="🔥 Heatmap Statistik vs Lawan (Urut Berdasarkan Total Impact)"
)

fig_heatmap.update_layout(
    xaxis_title="Statistik",
    yaxis_title="Lawan",
    coloraxis_colorbar=dict(
        title="Nilai",
        ticks="outside"
    ),
    font=dict(size=12)
)
fig_heatmap.update_traces(textfont_size=12, textfont_color="black")

st.plotly_chart(fig_heatmap, use_container_width=True)

# ---------------------------
# 7. Statistik Per Pertandingan
# ---------------------------
st.subheader("📋 Detail Statistik Pertandingan")
st.dataframe(df_filtered[["MatchDate", "Opponent", "Venue", "Goals", "Assists", "Shots", "xG", "xAG"]]
             .sort_values(by="MatchDate", ascending=False))

st.caption("Data bersumber dari catatan pertandingan Mohamed Salah di Premier League")
