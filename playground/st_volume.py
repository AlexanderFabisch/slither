import streamlit as st
from slither.service import Service
from slither.core.config import config
import pandas as pd
import altair as alt


@st.cache
def load_df():
    s = Service()
    sql = "select sport, start_time, distance, time from activities order by start_time"
    df = pd.read_sql(sql, s.database.engine)
    df["time"] = df["time"].div(3600.0)  # seconds to hours
    df["start_time"] = pd.to_datetime(df["start_time"])
    return df


df = load_df()

y_axis = st.sidebar.radio(
    "Y axis",
    ("Number", "Time", "Distance")
)
excluded_sports = st.sidebar.multiselect("Exclude sport", config["sports"])
min_start_time = df.start_time.min()
max_start_time = df.start_time.max()
start_date = pd.to_datetime(
    st.sidebar.date_input("Start date", min_start_time,
                          min_value=min_start_time, max_value=max_start_time))
end_date = pd.to_datetime(
    st.sidebar.date_input("End date", max_start_time,
                          min_value=start_date, max_value=max_start_time))
selected_df = df[start_date <= df["start_time"]].copy()
selected_df = selected_df[selected_df["start_time"] <= end_date]

for sport in excluded_sports:
    selected_df.drop(selected_df[selected_df.sport == sport].index, inplace=True)

if y_axis == "Number":
    Y = alt.Y("count()", type="ordinal", axis=alt.Axis(title="Number of activities"))
elif y_axis == "Time":
    Y = alt.Y("time", type="quantitative", aggregate="sum", axis=alt.Axis(title="Accumulated duration [h]"))
else:
    Y = alt.Y("distance", type="quantitative", aggregate="sum", axis=alt.Axis(title="Accumulated distance [km]"))
st.write(
    alt.Chart(selected_df).mark_bar().encode(
        # https://altair-viz.github.io/user_guide/transform/timeunit.html#timeunit-transform
        alt.X("yearmonth(start_time)", bin=alt.Bin(), type="temporal",
              axis=alt.Axis(title=None), scale=alt.Scale(domain=(start_date, end_date))),
        Y,
        color="sport",
        order=alt.Order("sport")
    )
)
