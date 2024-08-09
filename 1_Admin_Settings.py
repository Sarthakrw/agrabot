import streamlit as st
import subprocess
import time

st.set_page_config(page_title="Admin Settings", layout="centered")

st.title("Admin Settings")

st.text("Run an database update script")

selected_script = st.selectbox("Select a script to run:", ["Update Daily Weather Data", "Update Weekly Weather Data", "Update Monthly Weather Data", "Update Market Data"])

if "update_time" not in st.session_state:
    st.session_state.update_time = None

if st.button("Run Script"):
    if selected_script != "None":
        with st.spinner(f"Running {selected_script}..."):
            start_time = time.time()
            
            if selected_script == "Update Weekly Weather Data":
                subprocess.run(["python", "update_scripts/update_weather_week.py"])
            elif selected_script == "Update Monthly Weather Data":
                subprocess.run(["python", "update_scripts/update_weather_month.py"])
            elif selected_script == "Update Market Data":
                subprocess.run(["python", "update_scripts/update_market_data.py"])
            elif selected_script == "Update Daily Weather Data":
                subprocess.run(["python", "update_scripts/update_weather_day.py"])
            
            end_time = time.time()
            st.session_state.update_time = end_time - start_time
        
        st.success(f"{selected_script} executed successfully.")
        st.info(f"Update time: {st.session_state.update_time:.2f} seconds")
    else:
        st.warning("Please select a script to run.")
