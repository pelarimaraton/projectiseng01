# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -------------------------
# Config
# -------------------------
st.set_page_config(page_title="Mohamed Salah — Premier League Dashboard", layout="wide")
HEADER = """
# ⚽ Mohamed Salah — Premier League Comprehensive Dashboard
**Catatan:** Data sumber: Kaggle dataset *Mohamed Salah Premier League All Seasons Stats* (diambil dari repo user).\
Dashboard ini menampilkan rangkuman: total, tren per musim, efisiensi finishing, per-90 metrics, home vs away, radar chart, heatmap, dan peta gol (jika koordinat tidak ada, dibuat simulasi).
"""
st.markdown(HEADER)

# -------------------------
# Load & Prepare Data
# -------------------------
@st.cache_data(ttl=3600)
def load_data(url=None):
    if url is None:
        url = "https://raw.githubusercontent.com/pelarimaraton/projectiseng01/main/Salah-Stat-PrimerLeague.csv"
    df = pd.read_csv(url)

    # Standardize columns: lower/strip names optional - we keep original but ensure existence
    # Parse date
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    else:
        df["Date"] = pd.NaT

    # Derive Season if missing
    def season_from_date(d):
        if pd.isna(d):
            return "Unknown"
        y = d.year
        # season usually runs Aug-May -> treat July+ as start new season
        if d.month >= 7:
            return f"{y}-{str(y+1)[-2:]}"
        else:
            return f"{y-1}-{str(y)[-2:]}"
    df["Season"] = df["Date"].apply(season_from_date)

    # Try to extract MatchDay from an "Index" column if available
    idx_cols = [c for c in df.columns if "Index" in c or "MatchDay" in c or "matchday" in c]
    if idx_cols:
        try:
            import re
            s = df[idx_cols[0]].astype(str)
            df["MatchDay"] = s.str.extract(r'([0-9]{1,2})').astype(float)
        except Exception:
            df["MatchDay"] = np.nan
    else:
        # if MatchDay column exists use it, else NaN
        df["MatchDay"] = df["MatchDay"] if "MatchDay" in df.columns else np.nan

    # Numeric columns to coerce
    numeric_cols = ["Gls","Ast","PK","PKatt","Sh","SoT","xG","npxG","xAG","SCA","GCA",
                    "Cmp","Att","Cmp%","PrgP","Carries","PrgC","Att.1","Succ","Touches","Min","Tkl","Int","Blocks","CrdY","CrdR"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = np.nan

    # Replace NaN numeric with 0 where appropriate for aggregations (but keep NaT for date)
    fill_zero_cols = ["Gls","Ast","Sh","SoT","xG","npxG","xAG","SCA","GCA","Min"]
    for c in fill_zero_cols:
        if c in df.columns:
            df[c] = df[c].fillna(0)

    # Derived metrics
    # Shot accuracy (SoT / Sh)
    df["ShotAcc"] = np.where(df["Sh"] > 0, df["SoT"] / df["Sh"], np.nan)
    # Conversion rate = Gls / Sh
    df["ConvRate"] = np.where(df["Sh"] > 0, df["Gls"] / df["Sh"], np.nan)
    # Goals per 90 = Gls / Min * 90
    df["G_per90"] = np.where(df["Min"] > 0, df["Gls"] / df["Min"] * 90, np.nan)
    df["A_per90"] = np.where(df["Min"] > 0, df["Ast"] / df["Min"] * 90, np.nan)
    # Over/Under xG
    df["xG_diff"] = df["Gls"] - df["xG"]

    return df

df = load_data()

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.header("Filters & Settings")
season_options = ["All"] + sorted(df["Season"].dropna().unique().tolist())
sel_season = st.sidebar.selectbox("Season", season_options, index=0)
venues = df["Venue"].dropna().unique().tolist() if "Venue" in df.columns else []
sel_venues = st.sidebar.multiselect("Venue (Home/Away)", options=venues, default=venues)
min_match = int(np.nanmin(df["MatchDay"]) if df["MatchDay"].notna().any() else 1)
max_match = int(np.nanmax(df["MatchDay"]) if df["MatchDay"].notna().any() else 38)
md_range = st.sidebar.slider("MatchDay range", min_value=min_match, max_value=max_match, value=(min_match, max_match))

# Apply filters
df_filtered = df.copy()
if sel_season != "All":
    df_filtered = df_filtered[df_filtered["Season"] == sel_season]
if sel_venues:
    df_filtered = df_filtered[df_filtered["Venue"].isin(sel_venues)]
if "MatchDay" in df_filtered.columns and not df_filtered["MatchDay"].isna().all():
    df_filtered = df_filtered[(df_filtered["MatchDay"] >= md_range[0]) & (df_filtered["MatchDay"] <= md_range[1])]

# -------------------------
# Top summary cards
# -------------------------
total_matches = len(df_filtered)
total_goals = int(df_filtered["Gls"].sum()) if not df_filtered.empty else 0
total_assists = int(df_filtered["Ast"].sum()) if not df_filtered.empty else 0
total_xg = round(float(df_filtered["xG"].sum()),2) if not df_filtered.empty else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Matches", total_matches)
c2.metric("Goals", total_goals)
c3.metric("Assists", total_assists)
c4.metric("xG (total)", total_xg)

# Quick "story" highlight
with st.container():
    st.markdown("**Highlight:**")
    # Best season by goals
    per_season_goals = df.groupby("Season")["Gls"].sum()
    if not per_season_goals.empty:
        best_season = per_season_goals.idxmax()
        best_goals = int(per_season_goals.max())
        st.markdown(f"- Musim terbaik (total gol): **{best_season}** — **{best_goals}** gol")
    else:
        st.markdown("- Data season tidak lengkap.")

st.markdown("---")

# -------------------------
# Tabs for multiple views
# -------------------------
tab_overview, tab_shotmap, tab_heatmap, tab_radar, tab_table = st.tabs(
    ["Overview & Trends", "Goal Map (Shot Map)", "Heatmap & Efficiency", "Radar & Per-90", "Data Table"]
)

# -------------------------
# Tab 1: Overview & Trends
# -------------------------
with tab_overview:
    st.subheader("Tren Musiman: Goals, Assists, xG")
    trends = df.groupby("Season").agg({
        "Gls":"sum","Ast":"sum","xG":"sum","Sh":"sum","SoT":"sum"
    }).reset_index().sort_values("Season")
    if trends.empty:
        st.info("Tidak ada data tren untuk ditampilkan.")
    else:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(x=trends["Season"], y=trends["Gls"], name="Goals"))
        fig_trend.add_trace(go.Bar(x=trends["Season"], y=trends["Ast"], name="Assists"))
        fig_trend.add_trace(go.Line(x=trends["Season"], y=trends["xG"], name="xG", yaxis="y2"))
        fig_trend.update_layout(
            title="Goals & Assists (Bar) + xG (Line)",
            yaxis=dict(title="Count"),
            yaxis2=dict(title="xG", overlaying="y", side="right"),
            barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    st.subheader("Cumulative Goals Through Time")
    if df_filtered.empty:
        st.info("No data after filters")
    else:
        cum = df_filtered.copy().sort_values("Date")
        cum["cum_goals"] = cum["Gls"].cumsum()
        fig_cum = px.line(cum, x="Date", y="cum_goals", markers=True, title="Cumulative Goals")
        st.plotly_chart(fig_cum, use_container_width=True)

    st.subheader("xG vs Actual Goals (Efficiency)")
    if df_filtered.empty:
        st.info("No data after filters")
    else:
        # aggregate per match row
        fig_scatter = px.scatter(
            df_filtered,
            x="xG",
            y="Gls",
            size=np.where(df_filtered["Sh"].fillna(0) > 0, df_filtered["Sh"].abs(), 1),
            color="Season",
            hover_data=["Date","Opponent","Venue"],
            title="xG vs Goals (bubble size = shots)"
        )
        # add line y=x for reference
        fig_scatter.add_shape(type="line", x0=0, y0=0, x1=max(df_filtered["xG"].max(), df_filtered["Gls"].max())+0.5,
                              y1=max(df_filtered["xG"].max(), df_filtered["Gls"].max())+0.5,
                              line=dict(dash="dash", color="gray"))
        st.plotly_chart(fig_scatter, use_container_width=True)

# -------------------------
# Tab 2: Shot Map / Goal Map
# -------------------------
with tab_shotmap:
    st.subheader("Peta Gol / Shot Map")
    st.markdown(
        "**Catatan:** Dataset ini tidak menyediakan koordinat tembakan. " +
        "Jika Anda memiliki data koordinat (x,y) per shot, unggah CSV tersebut di sidebar untuk peta yang *presisi*. " +
        "Sebagai gantinya, saya membuat peta simulasi untuk memberikan gambaran visual."
    )

    # Optional: support user-uploaded shot coords
    uploaded = st.file_uploader("Upload CSV shot coords (opsional, columns: Date,x,y,Outcome[Gls/Shots])", type=["csv"])
    if uploaded is not None:
        sh_df = pd.read_csv(uploaded)
        if {"x","y"}.issubset(set(sh_df.columns)):
            sh_df["x"] = pd.to_numeric(sh_df["x"], errors="coerce")
            sh_df["y"] = pd.to_numeric(sh_df["y"], errors="coerce")
            fig_map = px.scatter(sh_df, x="x", y="y", color=sh_df.get("Outcome", None),
                                 size=sh_df.get("Gls", None).fillna(5),
                                 title="Shot Map (from uploaded data)")
            fig_map.update_yaxes(autorange="reversed")  # optional to mirror pitch orientation
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.error("CSV tidak memiliki kolom x,y yang diperlukan.")
    else:
        # Create simulated coordinates inside a half-pitch (0-100)
        sim = df_filtered.copy()
        if sim.empty:
            st.info("Tidak ada data untuk simulasi (filter pilih).")
        else:
            np.random.seed(42)
            sim["sx"] = np.random.normal(loc=80, scale=12, size=len(sim))  # bias ke area depan
            sim["sy"] = np.random.uniform(10, 90, size=len(sim))
            sim["is_goal"] = sim["Gls"] > 0
            fig_sim = px.scatter(
                sim, x="sx", y="sy",
                color=sim["is_goal"].map({True:"Goal", False:"No Goal"}),
                size=np.where(sim["Gls"]>0, sim["Gls"]*6, 6),
                hover_data=["Date","Opponent","Gls","Sh"],
                title="Simulated Shot / Goal Map"
            )
            fig_sim.update_xaxes(range=[0,100], showgrid=False, zeroline=False)
            fig_sim.update_yaxes(range=[0,100], showgrid=False, zeroline=False, autorange="reversed")
            st.plotly_chart(fig_sim, use_container_width=True)

# -------------------------
# Tab 3: Heatmap & Efficiency
# -------------------------
with tab_heatmap:
    st.subheader("Heatmap: Goals by Season & MatchDay")
    # pivot by Season x MatchDay if MatchDay exists
    if df["MatchDay"].notna().any():
        pivot = df.pivot_table(index="Season", columns="MatchDay", values="Gls", aggfunc="sum", fill_value=0)
        # sort seasons
        pivot = pivot.sort_index(ascending=False)
        fig_h = px.imshow(pivot.values, x=pivot.columns, y=pivot.index,
                          labels=dict(x="MatchDay", y="Season", color="Goals"),
                          aspect="auto", title="Goals per MatchDay x Season")
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.info("Tidak ada kolom MatchDay untuk heatmap season vs matchday.")

    st.subheader("Efisiensi: Shot Accuracy & Conversion Rate per Season")
    eff = df.groupby("Season").agg({"ShotAcc":"mean","ConvRate":"mean"}).reset_index()
    if eff.empty:
        st.info("Data efisiensi tidak cukup.")
    else:
        fig_eff = go.Figure()
        fig_eff.add_trace(go.Bar(x=eff["Season"], y=eff["ShotAcc"], name="Shot Accuracy (SoT/Sh)"))
        fig_eff.add_trace(go.Bar(x=eff["Season"], y=eff["ConvRate"], name="Conversion Rate (Gls/Sh)"))
        fig_eff.update_layout(barmode="group", title="Shot Accuracy & Conversion Rate per Season")
        st.plotly_chart(fig_eff, use_container_width=True)

    st.subheader("Home vs Away Performance")
    if "Venue" in df.columns:
        ha = df.groupby("Venue").agg({"Gls":"sum","Ast":"sum","xG":"sum"}).reset_index()
        fig_ha = px.bar(ha, x="Venue", y=["Gls","Ast","xG"], title="Home vs Away (sum)")
        st.plotly_chart(fig_ha, use_container_width=True)
    else:
        st.info("Kolom 'Venue' tidak tersedia di dataset.")

# -------------------------
# Tab 4: Radar & Per-90
# -------------------------
with tab_radar:
    st.subheader("Radar Chart — Perbandingan Atribut Menyerang per Season (sum)")
    radar_cols = [c for c in ["Gls","Ast","Sh","SoT","xG","xAG","SCA","GCA"] if c in df.columns]
    if len(radar_cols) < 3:
        st.info("Tidak cukup kolom untuk radar chart.")
    else:
        radar_data = df.groupby("Season")[radar_cols].sum().reset_index()
        season_select = st.selectbox("Pilih Season untuk radar", radar_data["Season"].unique())
        row = radar_data[radar_data["Season"]==season_select]
        if not row.empty:
            vals = row.iloc[0,1:].values.tolist()
            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(r=vals, theta=radar_cols, fill='toself', name=season_select))
            fig_r.update_layout(title=f"Radar — {season_select}", polar=dict(radialaxis=dict(visible=True)))
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            st.info("Season tidak ditemukan.")

    st.subheader("Per-90 Metrics (Goals/Assists per 90 minutes) — trend per season")
    per90 = df.groupby("Season").agg(G_per90=("G_per90","mean"), A_per90=("A_per90","mean")).reset_index()
    if per90.empty:
        st.info("Tidak ada data per-90.")
    else:
        fig_per90 = px.line(per90, x="Season", y=["G_per90","A_per90"], markers=True, title="Per-90 Trends")
        st.plotly_chart(fig_per90, use_container_width=True)

# -------------------------
# Tab 5: Data Table & Export
# -------------------------
with tab_table:
    st.subheader("Raw Data (filtered) — preview")
    st.dataframe(df_filtered.reset_index(drop=True).head(200))
    csv = df_filtered.to_csv(index=False)
    st.download_button("Download CSV (filtered)", csv, file_name="salah_filtered.csv", mime="text/csv")

# -------------------------
# Footer: metric explanations
# -------------------------
st.markdown("---")
with st.expander("Penjelasan metrik (sederhana)"):
    st.markdown("""
    - **xG (Expected Goals)**: estimasi probabilitas tiap tembakan berubah jadi gol (0..1), jumlah xG = kualitas peluang.
    - **npxG**: xG tanpa penalti.
    - **xG diff (Gls - xG)**: positif -> lebih tajam/clinical; negatif -> kurang clinical dibanding ekspektasi.
    - **Shot Accuracy**: SoT / Sh (berapa proporsi tembakan yang on target).
    - **Conversion Rate**: Gls / Sh (berapa proporsi tembakan jadi gol).
    - **Per-90**: nilai dinormalkan per 90 menit (G_per90, A_per90).
    """)
st.caption("Dashboard dibuat otomatis — silakan modifikasi warna / layout / gambar profil untuk personalisasi.")
