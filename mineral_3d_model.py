import streamlit as st
from app_views import render_mineral_view, render_petroleum_view, render_real_data_view, render_sidebar_intro

def main():
    st.set_page_config(page_title="Sims N Stuff", layout="wide", initial_sidebar_state="expanded")

    st.title("Sims N Stuff")
    st.markdown("Visualise realistic 3D deposits of minerals and petroleum using advanced geological modelling.")
    st.caption("Pick a view above, then use the sidebar to adjust only the controls that apply to that mode.")

    render_sidebar_intro()

    deposit_type = st.radio(
        "Select view:",
        ["Mineral Deposits", "Petroleum Deposits", "Real Data"],
        horizontal=False,
        help="Switch between synthetic geology and the real-data overlays.",
    )
    if deposit_type == "Real Data":
        st.caption("Real Data includes EIA trends, USGS mineral statistics, and CSV upload overlays.")

    if deposit_type == "Mineral Deposits":
        render_mineral_view()
    elif deposit_type == "Petroleum Deposits":
        render_petroleum_view()
    elif deposit_type == "Real Data":
        render_real_data_view()

    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("1. Use the sidebar to select deposit types and adjust geological parameters.")
    st.markdown("2. Switch between mineral, petroleum, and real data views using the radio buttons.")
    st.markdown("3. Explore different geological modelling modes for realistic deposit patterns.")
    st.code("streamlit run mineral_3d_model.py", language="bash")

if __name__ == "__main__":
    main()