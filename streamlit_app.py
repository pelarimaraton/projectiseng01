import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==== CONFIG ====
st.set_page_config(
    page_title="Mohamed Salah Premier League Stats",
    layout="wide"
)

# ==== LOAD DATA ====
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/pelarimaraton/projectiseng01/main/Salah-Stat-PrimerLeague.csv"
    df = pd.read_csv(url)

    # Date parsing
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Season derivation
    def get_season(date):
        if pd.isna(date):
            return "Unknown"
        y = date.year
        if date.month >= 7:
            return f"{y}-{str(y+1)[-2:]}"
        else:
            return f"{y-1}-{str(y)[-2:]}"
    df["Season"] = df["Date"].apply(get_season)

    # Numeric columns conversion
    num_cols = ["Gls","Ast","Sh","SoT","xG","Cmp%","Touches","Min"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

df = load_data()

# ==== SIDEBAR ====
st.sidebar.header("Filters")
seasons = ["All"] + sorted(df["Season"].unique())
sel_season = st.sidebar.selectbox("Season", seasons)
venues = st.sidebar.multiselect("Venue", df["Venue"].unique(), default=list(df["Venue"].unique()))

# Apply filters
df_filtered = df.copy()
if sel_season != "All":
    df_filtered = df_filtered[df_filtered["Season"] == sel_season]
if venues:
    df_filtered = df_filtered[df_filtered["Venue"].isin(venues)]

# ==== METRICS ====
col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches", len(df_filtered))
col2.metric("Goals", int(df_filtered["Gls"].sum()))
col3.metric("Assists", int(df_filtered["Ast"].sum()))
col4.metric("xG Sum", round(df_filtered["xG"].sum(), 2))

# ==== VISUALISASI ====
st.subheader("Goals Over Time")
if not df_filtered.empty:
    fig1 = px.line(df_filtered, x="Date", y="Gls", markers=True, title="Goals by Match Date")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("No data available for selected filters.")

st.subheader("xG vs Goals")
if not df_filtered.empty:
    fig2 = px.scatter(df_filtered, x="xG", y="Gls", size="Sh", hover_data=["Date","Opponent","Season"], title="xG vs Goals")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Goals by Season")
goals_season = df.groupby("Season")["Gls"].sum().reset_index()
fig3 = px.bar(goals_season, x="Season", y="Gls", title="Total Goals per Season")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Shot Accuracy by Season")
if "SoT" in df.columns and "Sh" in df.columns:
    df["Shot Accuracy"] = (df["SoT"] / df["Sh"]).fillna(0)
    acc_season = df.groupby("Season")["Shot Accuracy"].mean().reset_index()
    fig4 = px.bar(acc_season, x="Season", y="Shot Accuracy", title="Shot Accuracy per Season")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.caption("Data Source: Kaggle (Mohamed Salah Premier League All Seasons Stats)")
