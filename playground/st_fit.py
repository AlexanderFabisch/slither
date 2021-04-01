# pip install streamlit
# run with: streamlit run playground/st_fit.py filename
import sys
import streamlit as st
from fitparse import FitFile


assert len(sys.argv) == 2
fitfile = FitFile(sys.argv[-1])

message_names = list(set([message.name for message in fitfile.messages]))
message_name = st.selectbox("Select message:", options=message_names)
messages = fitfile.get_messages(message_name)

for i, record in enumerate(messages):
    st.write(i)
    for field in record:
        st.write(f"{field.name}: {field.value} {field.units}")
