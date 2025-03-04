import streamlit as st
import pandas as pd
import copy
import numpy as np
import nbimporter
import io
import sys
from scoreCalculation import load_bracket, madness_sim

st.title("🏀 March Madness Simulator")

df = pd.read_csv('ratings.csv')

if st.button("Run Simulation"):
    bracket = load_bracket()

    # ✅ Capture printed output
    output_buffer = io.StringIO()  
    sys.stdout = output_buffer  # Redirect print statements

    madness_sim(bracket, df)  # ✅ Run the simulation (prints rounds)

    sys.stdout = sys.__stdout__  # Reset print redirection

    # ✅ Display the captured output in Streamlit
    st.text_area("📜 Tournament Results:", output_buffer.getvalue(), height=500)