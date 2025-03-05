import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from streamlit_folium import folium_static

# Load dataset
df = pd.read_csv("European_Ski_Resorts.csv")

# Streamlit App Title
st.title("🏔️ Ski Resort Finder")
st.markdown("### Find your perfect ski resort based on your preferences")

# Sidebar Filters
st.sidebar.header("Filter Resorts")
selected_country = st.sidebar.selectbox("Select Country", ['All'] + sorted(df['Country'].dropna().unique()))
selected_level = st.sidebar.selectbox("Ski Level", ['All', 'Beginner', 'Intermediate', 'Advanced'])
max_budget = st.sidebar.slider("Max Budget (Day Pass in €)", int(df['DayPassPriceAdult'].min()), int(df['DayPassPriceAdult'].max()), int(df['DayPassPriceAdult'].max()))
altitude_range = st.sidebar.slider("Altitude Range (meters)", int(df['LowestPoint'].min()), int(df['HighestPoint'].max()), (int(df['LowestPoint'].min()), int(df['HighestPoint'].max())))
domain_size = st.sidebar.slider("Min Total Slope (km)", int(df['TotalSlope'].min()), int(df['TotalSlope'].max()), int(df['TotalSlope'].min()))

# Filtering Data
filtered_df = df.copy()
if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['Country'] == selected_country]
if selected_level != 'All':
    if selected_level == 'Beginner':
        filtered_df = filtered_df[filtered_df['BeginnerSlope'] > 10]
    elif selected_level == 'Intermediate':
        filtered_df = filtered_df[filtered_df['IntermediateSlope'] > 20]
    else:
        filtered_df = filtered_df[filtered_df['DifficultSlope'] > 10]
filtered_df = filtered_df[(filtered_df['DayPassPriceAdult'] <= max_budget) &
                          (filtered_df['LowestPoint'] >= altitude_range[0]) &
                          (filtered_df['HighestPoint'] <= altitude_range[1]) &
                          (filtered_df['TotalSlope'] >= domain_size)]

# Display Filtered Resorts
st.write(f"### Resorts matching your criteria: {len(filtered_df)} results")
st.dataframe(filtered_df[['Resort', 'Country', 'TotalSlope', 'HighestPoint', 'LowestPoint', 'DayPassPriceAdult']])

# Visualizations
st.subheader("Ski Resort Comparison")

# Scatter plot: Altitude vs Domain Size
fig1 = px.scatter(filtered_df, x="TotalSlope", y="HighestPoint", size="DayPassPriceAdult", color="Country", hover_name="Resort",
                   title="Resort Altitude vs. Ski Domain Size", labels={"TotalSlope": "Total Slope (km)", "HighestPoint": "Highest Altitude (m)"})
st.plotly_chart(fig1)

# Bar Chart: Lift Capacities
fig2 = px.bar(filtered_df.sort_values('LiftCapacity', ascending=False), x='Resort', y='LiftCapacity', color='Country',
              title='Lift Capacity by Resort', labels={'LiftCapacity': 'Lift Capacity per Hour'})
st.plotly_chart(fig2)

# Pie Chart: Slope Type Distribution
st.subheader("Ski Slope Distribution")
selected_resort = st.selectbox("Select Resort for Slope Breakdown", filtered_df['Resort'])
resort_data = df[df['Resort'] == selected_resort].iloc[0]
slope_data = pd.DataFrame({
    'Slope Type': ['Beginner', 'Intermediate', 'Difficult'],
    'Length (km)': [resort_data['BeginnerSlope'], resort_data['IntermediateSlope'], resort_data['DifficultSlope']]
})
fig3 = px.pie(slope_data, values='Length (km)', names='Slope Type', title=f'Slope Breakdown for {selected_resort}')
st.plotly_chart(fig3)

# Interactive Map
st.subheader("🏔️ Recommended Resorts Map")
map_center = [filtered_df['LowestPoint'].mean(), filtered_df['HighestPoint'].mean()]
map_ = folium.Map(location=map_center, zoom_start=6)

for _, row in filtered_df.iterrows():
    folium.Marker(
        location=[row['LowestPoint'], row['HighestPoint']],
        popup=f"{row['Resort']}\nAltitude: {row['HighestPoint']}m\nSlope: {row['TotalSlope']}km\nPrice: {row['DayPassPriceAdult']}€",
        tooltip=row['Resort']
    ).add_to(map_)

folium_static(map_)

st.success("🎿 Enjoy your ski trip!")
