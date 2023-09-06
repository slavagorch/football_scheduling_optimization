import streamlit as st
import pandas as pd
import xlsxwriter

schedule_df = pd.read_excel("bundesliga_schedule.xlsx")

# Streamlit app
st.title("Football Schedule App")

# Display the schedule_results table
st.write("Football Schedule:")
st.dataframe(schedule_df, use_container_width=True)

# Dropdown to select a team
selected_team = str(st.selectbox("Select a Team", schedule_df.columns))

# Filter the schedule for the selected team
filtered_schedule = schedule_df[[selected_team]]
filtered_schedule.index.name = 'Team'
filtered_schedule.reset_index(inplace=True)
st.write(f"Schedule for {selected_team}:")
st.dataframe(filtered_schedule, use_container_width=True)

# Button to export schedule to XLSX
if st.button("Export Schedule to XLSX"):
    # Create an XlsxWriter workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('football_schedule.xlsx')
    worksheet = workbook.add_worksheet()

    # Write the schedule to the XLSX file.
    for i, team in enumerate(filtered_schedule['Team']):
        week = filtered_schedule[selected_team].iloc[i]
        worksheet.write(i, 0, team)
        worksheet.write(i, 1, week)

    # Close the workbook to save the file.
    workbook.close()
    st.success("Schedule exported to football_schedule.xlsx")