import streamlit as st
from slither.service import Service
import pandas as pd
import altair as alt


@st.cache
def load_df():
    s = Service()
    sql = "select sport, start_time, distance, time from activities order by start_time"
    return pd.read_sql(sql, s.database.engine)


df = load_df()
df = df[df["start_time"] > "2015"]

y_axis = st.sidebar.radio(
    "Y axis",
    ("Number", "Time", "Distance")
)
if y_axis == "Number":
    Y = alt.Y("count()", type="ordinal")
elif y_axis == "Time":
    Y = alt.Y("time", type="quantitative", aggregate="sum")
else:
    Y = alt.Y("distance", type="quantitative", aggregate="sum")
st.write(
    alt.Chart(df).mark_bar().encode(
        # https://altair-viz.github.io/user_guide/transform/timeunit.html#timeunit-transform
        alt.X("yearmonth(start_time)", bin=alt.Bin(), type="temporal"),
        Y,
        color="sport",
        order=alt.Order("sport")
    )
)
