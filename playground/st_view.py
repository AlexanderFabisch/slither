# pip install streamlit streamlit_folium
# run with: streamlit run playground/st_view.py
import streamlit as st
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from slither.core.visualization import make_map, plot_speed_heartrate, plot_velocity_histogram
from slither.service import Service
from slither.core.ui_text import d


s = Service(base_path="tmp/data_import")
activities = s.list_activities()

page = st.sidebar.selectbox(
    "Select page",
    ("Overview", "Activity")
)

n = st.sidebar.slider("Show first", 0, len(activities) - 1)
view_activity = st.sidebar.selectbox(
    "Select view",
    ("Map", "Speed and Heartrate", "Velocities")
)

if page == "Overview":
    header = f"""
| ID | Start | Sport | Distance | Duration | Calories | Heartrate |
| -- | ----- | ----- | -------- | -------- | -------- | --------- |"""
    rows = [
        f"| {i + 1} | {d.display_datetime(a.start_time)} | {d.display_sport(a.sport)} | {d.display_distance(a.distance)} | {d.display_time(a.time)} | {d.display_calories(a.calories)} | {d.display_heartrate(a.heartrate)} |"
        for i, a in enumerate(activities)]
    st.write("\n".join([header] + rows))
if page == "Activity":
    a = activities[n]

    st.write(f"""
    | Start | Sport | Distance | Duration | Calories | Heartrate |
    | ----- | ----- | -------- | -------- | -------- | --------- |
    | {d.display_datetime(a.start_time)} | {d.display_sport(a.sport)} | {d.display_distance(a.distance)} | {d.display_time(a.time)} | {d.display_calories(a.calories)} | {d.display_heartrate(a.heartrate)} |

    ---
    """)

    if view_activity == "Map":
        if a.has_path:
            m = make_map(a.get_path())
            folium_static(m)
    elif view_activity == "Speed and Heartrate":
        fig = plt.figure()
        ax = plt.subplot(111)
        twin_ax = ax.twinx()
        if a.has_path:
            lines, labels = plot_speed_heartrate(ax, twin_ax, a.get_path())
            fig.legend(handles=lines, labels=labels, loc="upper center")
            st.write(fig)
    elif view_activity == "Velocities":
        fig = plt.figure()
        ax = plt.subplot(111)
        if a.has_path:
            plot_velocity_histogram(a.get_path(), ax)
            st.write(fig)
