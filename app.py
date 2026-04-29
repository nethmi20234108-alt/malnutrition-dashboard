import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data

st.set_page_config(page_title="Child Malnutrition Dashboard", layout="wide")

@st.cache_data
def get_data():
    return load_data()

df = get_data()

# ── Sidebar filters ──────────────────────────────────────────
st.sidebar.title("Filters")
regions = ["All"] + sorted(df["un_region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("UN Region", regions)

year_min, year_max = int(df["year"].min()), int(df["year"].max())
selected_years = st.sidebar.slider("Year range", year_min, year_max, (2000, 2020))

indicator_map = {
    "Stunting": "stunting",
    "Wasting": "wasting",
    "Severe Wasting": "severe_wasting",
    "Underweight": "underweight",
    "Overweight": "overweight"
}
selected_indicator_label = st.sidebar.selectbox("Indicator", list(indicator_map.keys()))
indicator = indicator_map[selected_indicator_label]

# ── Filter data ───────────────────────────────────────────────
filtered = df[(df["year"] >= selected_years[0]) & (df["year"] <= selected_years[1])]
if selected_region != "All":
    filtered = filtered[filtered["un_region"] == selected_region]

# ── Title ─────────────────────────────────────────────────────
st.title("🌍 Global Child Malnutrition Dashboard")
st.caption("Data: UNICEF/WHO Joint Malnutrition Estimates, March 2020 | Children aged 0–59 months")

# ── KPI cards ────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
latest = filtered[filtered["year"] == filtered["year"].max()]
col1.metric("Countries", filtered["country"].nunique())
col2.metric(f"Avg Stunting %", f"{latest['stunting'].mean():.1f}%")
col3.metric(f"Avg Wasting %", f"{latest['wasting'].mean():.1f}%")
col4.metric(f"Avg Underweight %", f"{latest['underweight'].mean():.1f}%")

st.markdown("---")

# ── Tab layout ───────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ World Map", "📈 Trends", "📊 Regional Compare", "📋 Data Table"])

# Tab 1: Choropleth map
with tab1:
    map_df = filtered.groupby(["iso_code","country"])[indicator].mean().reset_index()
    fig = px.choropleth(
        map_df,
        locations="iso_code",
        color=indicator,
        hover_name="country",
        color_continuous_scale="YlOrRd",
        title=f"Average {selected_indicator_label} by Country ({selected_years[0]}–{selected_years[1]})",
        labels={indicator: f"{selected_indicator_label} (%)"}
    )
    fig.update_layout(margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

# Tab 2: Trend lines
with tab2:
    countries = sorted(filtered["country"].dropna().unique().tolist())
    selected_countries = st.multiselect(
        "Select countries to compare",
        countries,
        default=countries[:5] if len(countries) >= 5 else countries
    )
    trend_df = filtered[filtered["country"].isin(selected_countries)]
    trend_agg = trend_df.groupby(["country","year"])[indicator].mean().reset_index()
    fig2 = px.line(
        trend_agg, x="year", y=indicator, color="country",
        title=f"{selected_indicator_label} over time",
        labels={indicator: f"{selected_indicator_label} (%)", "year": "Year"},
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

# Tab 3: Regional bar chart
with tab3:
    region_agg = filtered.groupby("un_region")[indicator].mean().reset_index().sort_values(indicator, ascending=False)
    fig3 = px.bar(
        region_agg, x="un_region", y=indicator,
        color=indicator, color_continuous_scale="YlOrRd",
        title=f"Average {selected_indicator_label} by UN Region",
        labels={indicator: f"{selected_indicator_label} (%)", "un_region": "UN Region"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Income group breakdown
    income_agg = filtered.groupby("income_group")[indicator].mean().reset_index().dropna()
    fig4 = px.bar(
        income_agg, x="income_group", y=indicator,
        title=f"{selected_indicator_label} by World Bank Income Group",
        labels={indicator: f"{selected_indicator_label} (%)", "income_group": "Income Group"}
    )
    st.plotly_chart(fig4, use_container_width=True)

# Tab 4: Raw data table
with tab4:
    st.dataframe(filtered.sort_values("year", ascending=False), use_container_width=True)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_malnutrition.csv", "text/csv")