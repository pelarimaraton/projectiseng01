# Mohamed Salah Premier League — Colab & Streamlit
# File contains: 1) Colab-friendly data processing / EDA sections (as functions)
# 2) Streamlit app code (at bottom) — save as streamlit_app.py and run with `streamlit run streamlit_app.py`

# -------------------------
# 1) Install dependencies (run in Colab once)
# -------------------------
# !pip install -q pandas numpy plotly streamlit seaborn matplotlib kaleido

# -------------------------
# 2) Imports
# -------------------------
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# -------------------------
# 3) Helper: load data from GitHub raw
# -------------------------
GITHUB_RAW = "https://raw.githubusercontent.com/pelarimaraton/projectiseng01/main/Salah-Stat-PrimerLeague.csv"


def load_and_prepare(url=GITHUB_RAW):
    # Load
    df = pd.read_csv(url)

    # Make a copy
    df = df.copy()

    # If multi-index column present as single column called like 'Index (MatchDay, Season)'
    # try to extract MatchDay and Season
    idx_col_candidates = [c for c in df.columns if 'Index' in c or 'MatchDay' in c or 'Season' in c]
    if idx_col_candidates:
        idx_col = idx_col_candidates[0]
    else:
        idx_col = None

    # Parse Date
    if 'Date' in df.columns:
        try:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        except Exception:
            df['Date'] = pd.to_datetime(df['Date'].str.strip(), errors='coerce', dayfirst=False)
    else:
        df['Date'] = pd.NaT

    # Extract Season and MatchDay from index column if available
    if idx_col is not None:
        # typical format: "(MatchDay 1, 2024–25)" or "MatchDay 1 of 2024-25" or "MatchDay 1, 2024/25"
        def parse_idx(x):
            if pd.isna(x):
                return pd.NA, pd.NA
            s = str(x)
            # try numbers for matchday
            import re
            md = re.search(r'MatchDay\s*([0-9]+)', s, re.IGNORECASE)
            season = re.search(r'(\d{4}[–\-\/]?\d{2,4})|(\d{4}–\d{2})', s)
            mdv = int(md.group(1)) if md else pd.NA
            sv = season.group(0) if season else s.split(',')[-1].strip()
            return mdv, sv

        parsed = df[idx_col].apply(parse_idx)
        df['MatchDay'] = parsed.apply(lambda t: t[0])
        df['Season'] = parsed.apply(lambda t: t[1])

    # If MatchDay not present but there's a column named 'Min' or 'Gls', try to infer Season by Date
    if 'Season' not in df.columns or df['Season'].isnull().all():
        # season calculation: if date known, season = {year}-{year+1} if month >=7 then that season
        def season_from_date(d):
            if pd.isna(d):
                return pd.NA
            y = d.year
            if d.month >= 7:
                return f"{y}-{str(y+1)[-2:]}"
            else:
                return f"{y-1}-{str(y)[-2:]}"

        df['Season'] = df['Date'].apply(season_from_date)

    # Clean numeric columns
    num_cols = ['Min','Gls','Ast','PK','PKatt','Sh','SoT','CrdY','CrdR','Touches','Tkl','Int','Blocks',
                'xG','npxG','xAG','SCA','GCA','Cmp','Att','Cmp%','PrgP','Carries','PrgC','Att.1','Succ']

    for c in num_cols:
        if c in df.columns:
            # remove non-numeric characters
            df[c] = pd.to_numeric(df[c], errors='coerce')

    # Create convenient columns
    if 'Result' in df.columns:
        # parse result to get goals for Salah's team and opponent
        def parse_result(r):
            # examples: 'W 2–0' or 'L 0–1' or 'D 1–1'
            try:
                parts = str(r).split()
                if len(parts) >= 2:
                    score = parts[1]
                    score = score.replace('–','-').replace('—','-')
                    a,b = score.split('-')
                    return int(a), int(b), parts[0]
            except Exception:
                return pd.NA, pd.NA, pd.NA
            return pd.NA, pd.NA, pd.NA

        parsed = df['Result'].apply(parse_result)
        df['TeamGoals'] = parsed.apply(lambda t: t[0])
        df['OppGoals'] = parsed.apply(lambda t: t[1])
        df['ResultType'] = parsed.apply(lambda t: t[2])

    # Fill small things
    df['Venue'] = df['Venue'].fillna('Unknown')
    df['Pos'] = df['Pos'].fillna('NA')

    # Sort by date
    if 'Date' in df.columns:
        df = df.sort_values('Date').reset_index(drop=True)

    return df


# -------------------------
# 4) Example EDA functions (for Colab use)
# -------------------------

def show_head(df, n=10):
    display(df.head(n))


def season_summary(df):
    # Aggregate per season
    agg = df.groupby('Season').agg(
        Matches=('Date','count'),
        Goals=('Gls','sum'),
        Assists=('Ast','sum'),
        Shots=('Sh','sum'),
        SoT=('SoT','sum'),
        xG=('xG','sum')
    ).reset_index()
    return agg


# -------------------------
# 5) Streamlit app
#    Save the below part into streamlit_app.py when running locally or in Colab with write
# -------------------------

STREAMLIT_APP = r"""
# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

GITHUB_RAW = 'https://raw.githubusercontent.com/pelarimaraton/projectiseng01/main/Salah-Stat-PrimerLeague.csv'

@st.cache_data
def load_data(url=GITHUB_RAW):
    df = pd.read_csv(url)
    # lightweight parsing (reuse helper logic where needed)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    # season derivation
    def season_from_date(d):
        if pd.isna(d):
            return 'Unknown'
        y = d.year
        if d.month >= 7:
            return f"{y}-{str(y+1)[-2:]}"
        else:
            return f"{y-1}-{str(y)[-2:]}"
    df['Season'] = df['Date'].apply(season_from_date)
    # numeric conversions
    for c in ['Gls','Ast','Sh','SoT','xG','Cmp%','Touches','Min']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

# Load
st.set_page_config(layout='wide', page_title='Mohamed Salah — Premier League Visuals')
st.title('⚽ Mohamed Salah — Premier League (All Seasons)')

df = load_data()

# Sidebar filters
st.sidebar.header('Filters')
seasons = ['All'] + sorted(df['Season'].dropna().unique().tolist())
sel_season = st.sidebar.selectbox('Select Season', seasons)
min_matchday = int(df['MatchDay'].min()) if 'MatchDay' in df.columns else 1
max_matchday = int(df['MatchDay'].max()) if 'MatchDay' in df.columns else 38
md_range = st.sidebar.slider('MatchDay range', min_matchday, max_matchday, (min_matchday, max_matchday))
venue = st.sidebar.multiselect('Venue', options=df['Venue'].dropna().unique().tolist(), default=df['Venue'].dropna().unique().tolist())

# apply filters
dd = df.copy()
if sel_season != 'All':
    dd = dd[dd['Season'] == sel_season]
if 'MatchDay' in dd.columns:
    dd = dd[(dd['MatchDay'] >= md_range[0]) & (dd['MatchDay'] <= md_range[1])]
if 'Venue' in dd.columns:
    dd = dd[dd['Venue'].isin(venue)]

# Top metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric('Matches', int(dd.shape[0]))
col2.metric('Goals', int(dd['Gls'].sum()))
col3.metric('Assists', int(dd['Ast'].sum() if 'Ast' in dd.columns else 0))
col4.metric('xG (sum)', round(dd['xG'].sum(),2) if 'xG' in dd.columns else 0)

# Layout: Left (time series + heatmap), Right (scatter + radar)
left, right = st.columns((2,1))

with left:
    st.subheader('Goals over Time')
    if 'Date' in dd.columns:
        fig = px.line(dd, x='Date', y='Gls', markers=True, title='Goals by Match Date')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader('Goals by MatchDay (heatmap)')
    if 'MatchDay' in df.columns:
        # pivot table: seasons x matchday
        heat_df = df.pivot_table(index='Season', columns='MatchDay', values='Gls', aggfunc='sum', fill_value=0)
        # order seasons descending
        heat_df = heat_df.sort_index(ascending=False)
        fig2 = px.imshow(heat_df.values, x=heat_df.columns, y=heat_df.index, aspect='auto', labels=dict(x='MatchDay', y='Season', color='Goals'), title='Goals per MatchDay by Season')
        st.plotly_chart(fig2, use_container_width=True)

with right:
    st.subheader('xG vs Goals (scatter)')
    if 'xG' in dd.columns:
        fig3 = px.scatter(dd, x='xG', y='Gls', size='Sh' if 'Sh' in dd.columns else None, hover_data=['Date','Opponent','Season'], title='xG vs Actual Goals')
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader('Per-Season Performance (radar)')
    # aggregate per season
    per_season = df.groupby('Season').agg(Matches=('Date','count'), Goals=('Gls','sum'), Assists=('Ast','sum'), Shots=('Sh','sum'), xG=('xG','sum')).reset_index()
    if not per_season.empty:
        # choose season to display
        ssel = st.selectbox('Select season for radar', ['All'] + per_season['Season'].tolist())
        if ssel == 'All':
            row = per_season.drop(columns='Season').sum()
            title = 'All Seasons (aggregate)'
        else:
            row = per_season[per_season['Season']==ssel].iloc[0].drop(labels='Season')
            title = f'Season {ssel}'
        categories = row.index.tolist()
        values = row.values.tolist()
        # radar requires looped values
        fig4 = go.Figure()
        fig4.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name=title))
        fig4.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False, title='Season Performance Radar')
        st.plotly_chart(fig4, use_container_width=True)

st.markdown('---')

# Additional: shot accuracy and passing trend
st.header('Detailed Analyses')
cols = st.columns(2)
with cols[0]:
    st.subheader('Shot Accuracy Trend')
    if 'SoT' in df.columns and 'Sh' in df.columns:
        df['ShotAcc'] = df['SoT'] / df['Sh']
        shot_trend = df.groupby('Season').agg(ShotAcc=('ShotAcc','mean')).reset_index()
        fig5 = px.bar(shot_trend, x='Season', y='ShotAcc', title='Average Shot Accuracy per Season')
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.write('Not enough shot data in dataset for this chart.')

with cols[1]:
    st.subheader('Pass Completion Trend')
    if 'Cmp%' in df.columns:
        pass_trend = df.groupby('Season').agg(PassAcc=('Cmp%','mean')).reset_index()
        fig6 = px.line(pass_trend, x='Season', y='PassAcc', markers=True, title='Average Pass Completion by Season')
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.write('No pass completion data available.')

st.markdown('---')
st.write('Tips: Use the sidebar to filter seasons and matchdays. Select different seasons in the radar chart to compare per-season performances.')

"""

# Write streamlit app to file (if running in Colab)

def write_streamlit_app(path='streamlit_app.py'):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(STREAMLIT_APP)
    print(f'Wrote Streamlit app to {path}')


# -------------------------
# 6) Usage notes
# -------------------------
usage = '''
Instructions:
1) In Google Colab:
   - Run `!pip install -q streamlit plotly kaleido` (if you plan to run streamlit there)
   - Run the helper functions in this file to load and inspect data:
        df = load_and_prepare(GITHUB_RAW)
        show_head(df)
        season_summary(df)
   - To write the Streamlit app file: write_streamlit_app('streamlit_app.py')

2) Run Streamlit locally:
   - Save `STREAMLIT_APP` into streamlit_app.py (use write_streamlit_app())
   - Run: `streamlit run streamlit_app.py` in terminal

3) Run Streamlit in Colab (optional, requires ngrok or localtunnel):
   - It's possible but more complex; recommended to run app locally or deploy on Streamlit Cloud.

Enjoy! Customize colors, layout, and add images (player photo) to make the dashboard more appealing.
'''

print(usage)
