import streamlit as st

# Set up page configuration
st.set_page_config(page_title="SkillScape", layout="wide")

# Use an iframe to load your Flask app
st.markdown(
    """
    <style>
    iframe {
        border: none;
        width: 100vw;
        height: 100vh;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<iframe src="http://localhost:5000" frameborder="0"></iframe>',
    unsafe_allow_html=True,
)
