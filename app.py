
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ----------------------------------
# 1. PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="Malaysia Crime Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Malaysia Crime Analytics Dashboard")
st.caption("Scientific Visualisation | JIE42403")

# ----------------------------------
# 2. LOAD DATASET
# ----------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("crime_district.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    return df

df = load_data()

# ----------------------------------
# 3. PREPARE DATA
# ----------------------------------

# National aggregate data
national = df[
    (df["state"] == "Malaysia") &
    (df["district"] == "All")
].copy()

# National annual totals
annual = (
    national[national["type"] == "all"]
    .groupby("year", as_index=False)["crimes"]
    .sum()
    .sort_values("year")
)

# National crime categories
category_trend = (
    national[national["type"] == "all"]
    .groupby(["year", "category"], as_index=False)["crimes"]
    .sum()
)

# Detailed crime types (exclude aggregate rows)
crime_types = national[
    national["type"] != "all"
].copy()

# District-level data (exclude national aggregates)
district_data = df[
    (df["state"] != "Malaysia") &
    (df["district"] != "All") &
    (df["type"] == "all")
].copy()

# ----------------------------------
# 4. SIDEBAR NAVIGATION
# ----------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Analysis",
    [
        "1. Crime Trends",
        "2. Crime Categories",
        "3. Geographical Distribution"
    ]
)

# ----------------------------------
# PAGE 1: CRIME TRENDS
# ----------------------------------

if page == "1. Crime Trends":

    st.header("Crime Trends in Malaysia")

    st.write(
        "Objective: To analyse changes in recorded crime "
        "cases in Malaysia between 2016 and 2023."
    )

    # Summary boxes
    total = annual["crimes"].sum()
    highest = annual.loc[
        annual["crimes"].idxmax()
    ]

    lowest = annual.loc[
        annual["crimes"].idxmin()
    ]

    change = (
        (annual.iloc[-1]["crimes"] /
         annual.iloc[0]["crimes"]) - 1
    ) * 100

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Recorded Cases", f"{total:,.0f}")
    c2.metric("Highest Year", int(highest["year"]))
    c3.metric("Lowest Year", int(lowest["year"]))
    c4.metric("2016–2023 Change", f"{change:.1f}%")

    st.divider()

    # Visualization 1: Annual crime trend
    st.subheader("1. Annual Crime Trend")

    fig1 = px.line(
        annual,
        x="year",
        y="crimes",
        markers=True,
        title="Total Recorded Crimes (2016–2023)"
    )

    fig1.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Crimes"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Visualization 2: Category trend
    st.subheader("2. Assault vs Property Crime")

    fig2 = px.line(
        category_trend,
        x="year",
        y="crimes",
        color="category",
        markers=True,
        title="Crime Trends by Category"
    )

    fig2.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Crimes"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Visualization 3: Year-on-year change
    st.subheader("3. Year-on-Year Percentage Change")

    annual["percentage_change"] = (
        annual["crimes"].pct_change() * 100
    )

    yoy = annual.dropna()

    fig3 = px.bar(
        yoy,
        x="year",
        y="percentage_change",
        title="Annual Percentage Change in Recorded Crimes"
    )

    fig3.add_hline(y=0, line_dash="dash")

    fig3.update_layout(
        xaxis_title="Year",
        yaxis_title="Percentage Change (%)"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Interpretation")

    st.write(
        "Recorded crimes declined considerably between "
        "2016 and 2022, before increasing slightly in 2023. "
        "The overall decrease indicates a long-term downward "
        "trend in recorded cases during the observation period."
    )

# ----------------------------------
# PAGE 2: CRIME CATEGORIES
# ----------------------------------

elif page == "2. Crime Categories":

    st.header("Crime Category and Type Analysis")

    st.write(
        "Objective: To examine the distribution of crime "
        "categories and identify frequently recorded crime types."
    )

    selected_year = st.selectbox(
        "Select Year",
        sorted(crime_types["year"].unique(), reverse=True),
        index=0
    )

    selected_types = crime_types[
        crime_types["year"] == selected_year
    ]

    # Summary calculations
    type_totals = (
        selected_types.groupby("type")["crimes"]
        .sum()
        .sort_values(ascending=False)
    )

    category_totals = (
        national[
            (national["type"] == "all") &
            (national["year"] == selected_year)
        ]
        .groupby("category")["crimes"]
        .sum()
    )

    total_cases = category_totals.sum()
    top_type = type_totals.idxmax()
    dominant_category = category_totals.idxmax()

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Cases", f"{total_cases:,.0f}")
    c2.metric("Most Frequent Type", top_type.replace("_", " ").title())
    c3.metric("Dominant Category", dominant_category.title())

    st.divider()

    # Visualization 4: Crime type bar chart
    st.subheader("4. Recorded Crimes by Type")

    fig4 = px.bar(
        type_totals.reset_index(),
        x="crimes",
        y="type",
        orientation="h",
        title=f"Crime Types in {selected_year}"
    )

    fig4.update_layout(
        xaxis_title="Number of Crimes",
        yaxis_title="Crime Type",
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig4, use_container_width=True)

    # Visualization 5: Category donut chart
    st.subheader("5. Crime Category Distribution")

    fig5 = px.pie(
        category_totals.reset_index(),
        names="category",
        values="crimes",
        hole=0.45,
        title=f"Assault vs Property Crimes ({selected_year})"
    )

    st.plotly_chart(fig5, use_container_width=True)

    # Visualization 6: Crime type heatmap
    st.subheader("6. Crime Type Heatmap")

    heatmap_data = (
        crime_types.pivot_table(
            index="type",
            columns="year",
            values="crimes",
            aggfunc="sum"
        ).fillna(0)
    )

    heatmap_data = heatmap_data.loc[
        heatmap_data.sum(axis=1).sort_values(
            ascending=False
        ).index
    ]

    fig6 = px.imshow(
        heatmap_data,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels={
            "x": "Year",
            "y": "Crime Type",
            "color": "Cases"
        },
        title="Crime Type Distribution Across Years"
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Interpretation")

    st.write(
        f"In {selected_year}, {dominant_category} was the "
        f"dominant crime category. The most frequently "
        f"recorded individual crime type was {top_type.replace('_', ' ')}. "
        "The heatmap allows comparisons of crime types across "
        "the observation period."
    )

# ----------------------------------
# PAGE 3: GEOGRAPHICAL DISTRIBUTION
# ----------------------------------

elif page == "3. Geographical Distribution":

    st.header("Geographical Crime Distribution")

    st.write(
        "Objective: To investigate recorded crime distribution "
        "across Malaysian states and districts."
    )

    selected_year = st.selectbox(
        "Select Year",
        sorted(district_data["year"].unique(), reverse=True),
        index=0
    )

    yearly_district = district_data[
        district_data["year"] == selected_year
    ]

    # Aggregate district counts by state and district
    district_summary = (
        yearly_district.groupby(
            ["state", "district"], as_index=False
        )["crimes"].sum()
    )

    state_summary = (
        district_summary.groupby(
            "state", as_index=False
        )["crimes"].sum()
        .sort_values("crimes", ascending=False)
    )

    top_districts = district_summary.nlargest(
        10, "crimes"
    )

    highest_state = state_summary.iloc[0]
    highest_district = top_districts.iloc[0]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Highest State",
        highest_state["state"]
    )

    c2.metric(
        "Highest District",
        highest_district["district"]
    )

    c3.metric(
        "Total District Cases",
        f"{district_summary['crimes'].sum():,.0f}"
    )

    st.divider()

    # Visualization 7: State ranking
    st.subheader("7. Recorded Crimes by State")

    fig7 = px.bar(
        state_summary,
        x="state",
        y="crimes",
        title=f"Crime Distribution by State ({selected_year})"
    )

    fig7.update_layout(
        xaxis_title="State",
        yaxis_title="Number of Crimes",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig7, use_container_width=True)

    # Visualization 8: Top 10 districts
    st.subheader("8. Top 10 Districts")

    fig8 = px.bar(
        top_districts.sort_values("crimes"),
        x="crimes",
        y="district",
        color="state",
        orientation="h",
        title=f"Top 10 Districts with Highest Crimes ({selected_year})"
    )

    st.plotly_chart(fig8, use_container_width=True)

    # Visualization 9: Assault vs property
    st.subheader("9. Assault vs Property Crime Relationship")

    scatter_data = yearly_district.pivot_table(
        index=["state", "district"],
        columns="category",
        values="crimes",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    fig9 = px.scatter(
        scatter_data,
        x="assault",
        y="property",
        hover_data=["state", "district"],
        title="Relationship Between Assault and Property Crimes"
    )

    fig9.update_layout(
        xaxis_title="Assault Crimes",
        yaxis_title="Property Crimes"
    )

    st.plotly_chart(fig9, use_container_width=True)

    st.subheader("Interpretation")

    st.write(
        f"In {selected_year}, {highest_state['state']} "
        f"recorded the highest district-level total, while "
        f"{highest_district['district']} had the highest "
        "individual district count. The scatter plot compares "
        "assault and property crime counts across districts."
    )

# ----------------------------------
# FOOTER
# ----------------------------------

st.sidebar.divider()
st.sidebar.caption("JIE42403 Scientific Visualisation")
st.sidebar.caption("Malaysia Crime Analytics | 2016–2023")
