import streamlit as st
from validation import validation_page
from chatbot import chatbot_page

st.set_page_config(page_title="Invoice and PO Extraction Bot", layout="wide")

# Sidebar Branding
#st.sidebar.image("logo.png", use_column_width=True)  # Optional: Add a logo
st.sidebar.markdown("## 🌟 **Welcome!**")
st.sidebar.markdown("---")

# Initialize session state for active selection
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Validation"  # Default page

# Sidebar Navigation with Buttons
def nav_button(label, key):
    """Creates a styled button with active highlighting"""
    is_active = st.session_state.selected_page == label
    button_style = "background-color: #4CAF50; color: white;" if is_active else ""

    if st.sidebar.button(label, key=key, help=f"Go to {label}", use_container_width=True):
        st.session_state.selected_page = label
        st.rerun()  # Refresh page when button is clicked

# Navigation Buttons
nav_button("Validation", "validation")
nav_button("Chatbot", "chatbot")

st.sidebar.markdown("---")
st.sidebar.markdown("🔗 **Resources & Support:**")
st.sidebar.markdown("[📖 Documentation](https://docs.example.com)")
st.sidebar.markdown("[💡 Report an Issue](https://github.com/example/issues)")
st.sidebar.markdown("📞 **Contact:** support@example.com")

# Load the selected page
if st.session_state.selected_page == "Validation":
    validation_page()
elif st.session_state.selected_page == "Chatbot":
    chatbot_page()
