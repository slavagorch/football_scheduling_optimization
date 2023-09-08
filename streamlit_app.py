import streamlit as st
import pandas as pd
from main import run_pipeline
import io
from PIL import Image
import base64

schedule_df = pd.read_excel("bundesliga_schedule.xlsx")

# Streamlit app
logo_col, title_col = st.columns([0.2, 0.8])

logo = Image.open("data/bundesliga_logo.jpg")
logo_col.image(logo)

title_col.title("Bundesliga Schedule App")

@st.cache_resource
def run_optimizer():
    return run_pipeline()

schedule = run_optimizer()


# Display teams map
st.header("Bundesliga teams map")
st.plotly_chart(schedule.fig)

# Display the schedule_results table
st.header("Optimized Schedule:")
st.dataframe(schedule_df, use_container_width=True)

# Dropdown to select a team
selected_team = str(st.selectbox("Select a Team", schedule.filtered_schedule_per_team_dict.keys()))

# Filter the schedule for the selected team
st.table(schedule.filtered_schedule_per_team_dict[selected_team]) #, use_container_width=True)

# Button to export schedule to XLSX

# download button 2 to download dataframe as xlsx
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    schedule.league_schedule_table.to_excel(writer, sheet_name='Schedule', index=False)

    download2 = st.download_button(
        label="Download schedule as Excel",
        data=buffer,
        file_name='bundesliga_schedule.xlsx',
        mime='application/vnd.ms-excel'
    )