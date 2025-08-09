import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==== CONFIG ====
st.set_page_config(page_title="Mohamed Salah Premier League Dashboard", layout="wide")

# ==== HEADER ====
st.title("📊 Mohamed Salah Premier League Dashboard")
st.markdown("""
**Statistik komprehensif Mohamed Salah selama bermain di Premier League**.  
Data ini mencakup jumlah gol, assist, expected goals (xG), shot accuracy, dan berbagai metrik lain  
yang membantu memahami kontribusi Salah di setiap musimnya.
""")

# ==== LOAD DATA ====
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pelarimaraton/projectiseng01/main/Salah-Stat-PrimerLeague.csv"
    df = pd.read_csv(url)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    def get_season(date):
        if pd.isna(date):
            return "Unknown"
        y = date.year
        return f"{y}-{str(y+1)[-2:]}" if date.month >= 7 else f"{y-1}-{str(y)[-2:]}"
    df["Season"] = df["Date"].apply(get_season)

    num_cols = ["Gls", "Ast", "PK", "PKatt", "Sh", "SoT", "xG", "npxG", "xAG", "SCA", "GCA", "Cmp%", "Touches", "Min"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

df = load_data()

# ==== SIDEBAR FILTER ====
st.sidebar.header("Filters")
seasons = ["All"] + sorted(df["Season"].unique())
sel_season = st.sidebar.selectbox("Season", seasons)
venues = st.sidebar.multiselect("Venue", df["Venue"].dropna().unique(), default=list(df["Venue"].dropna().unique()))

df_filtered = df.copy()
if sel_season != "All":
    df_filtered = df_filtered[df_filtered["Season"] == sel_season]
if venues:
    df_filtered = df_filtered[df_filtered["Venue"].isin(venues)]

# ==== METRIC EXPLANATION ====
with st.expander("ℹ️ Penjelasan Metrik"):
    st.markdown("""
    - **Goals (Gls)**: Jumlah gol yang dicetak.
    - **Assists (Ast)**: Umpan yang menghasilkan gol.
    - **xG (Expected Goals)**: Perkiraan gol yang seharusnya dicetak berdasarkan kualitas peluang.
    - **npxG (Non-Penalty xG)**: Sama seperti xG tetapi tanpa penalti.
    - **xAG (Expected Assists)**: Perkiraan assist berdasarkan kualitas peluang yang diciptakan.
    - **SCA (Shot Creating Actions)**: Aksi yang berkontribusi menghasilkan tembakan.
    - **GCA (Goal Creating Actions)**: Aksi yang berkontribusi menghasilkan gol.
    - **Shot Accuracy**: Persentase tembakan yang tepat sasaran.
    """)

# ==== TABS ====
tab1, tab2, tab3, tab4 = st.tabs(["📈 Statistik Utama", "🎯 Peta Gol", "📊 Heatmap & Tren", "🛡️ Radar Chart"])

# ==== TAB 1 ====
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Matches", len(df_filtered))
    col2.metric("Goals", int(df_filtered["Gls"].sum()))
    col3.metric("Assists", int(df_filtered["Ast"].sum()))
    col4.metric("xG Total", round(df_filtered["xG"].sum(), 2))

    st.subheader("Goals Over Time")
    fig1 = px.line(df_filtered, x="Date", y="Gls", markers=True, title="Goals by Match Date")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("xG vs Goals")
    fig2 = px.scatter(
        df_filtered,
        x="xG",
        y="Gls",
        size=df_filtered["Sh"].abs(),
        color="Season",
        hover_data=["Date", "Opponent", "Season"],
        title="xG vs Goals"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ==== TAB 2 (GOAL MAP) ====
with tab2:
    st.subheader("Peta Gol Mohamed Salah (Simulasi)")
    np.random.seed(42)
    shots_x = np.random.uniform(0, 100, size=len(df_filtered))
    shots_y = np.random.uniform(0, 100, size=len(df_filtered))
    goals = df_filtered["Gls"].astype(int)

    fig_goalmap = go.Figure()
    fig_goalmap.add_trace(go.Scatter(
        x=shots_x, y=shots_y,
        mode='markers',
        marker=dict(
            size=goals*5 + 5,
            color=np.where(goals > 0, "red", "blue"),
            opacity=0.7,
            line=dict(width=1, color='white')
        ),
        text=df_filtered["Opponent"],
        hovertemplate="Lawan: %{text}<br>X: %{x}<br>Y: %{y}<extra></extra>"
    ))
    fig_goalmap.update_layout(
        title="Goal Map (Simulasi)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=500
    )
    st.plotly_chart(fig_goalmap, use_container_width=True)

# ==== TAB 3 ====
with tab3:
    st.subheader("Heatmap Goals per Season & MatchDay")
    fig_heatmap = px.density_heatmap(
        df, x="Season", y=df.index, z="Gls",
        title="Distribusi Gol Berdasarkan Musim & Matchday"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.subheader("Shot Accuracy per Season")
    df["Shot Accuracy"] = (df["SoT"] / df["Sh"]).replace([float("inf"), -float("inf")], 0).fillna(0)
    acc_season = df.groupby("Season")["Shot Accuracy"].mean().reset_index()
    fig4 = px.bar(acc_season, x="Season", y="Shot Accuracy", title="Shot Accuracy per Season")
    st.plotly_chart(fig4, use_container_width=True)

# ==== TAB 4 ====
with tab4:
    st.subheader("Radar Chart Performa")
    radar_cols = ["Gls", "Ast", "Sh", "SoT", "xG", "xAG", "SCA", "GCA"]
    radar_data = df.groupby("Season")[radar_cols].sum().reset_index()
    season_selected = st.selectbox("Pilih Season untuk Radar Chart", radar_data["Season"].unique())
    season_stats = radar_data[radar_data["Season"] == season_selected].iloc[0, 1:]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=season_stats.values,
        theta=radar_cols,
        fill='toself',
        name=season_selected
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=False,
        title=f"Radar Chart Performa {season_selected}"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")
st.caption("Data Source: Kaggle — Mohamed Salah Premier League All Seasons Stats")
