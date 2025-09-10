import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ---------- Custom CSS ----------
st.markdown("""
    <style>
    input[data-testid="stTextInput"][aria-label="Number"],
    input[data-testid="stTextInput"][aria-label="IMEI"],
    input[data-testid="stTextInput"][aria-label="Handset"],
    input[data-testid="stTextInput"][aria-label="First Cell"],
    input[data-testid="stTextInput"][aria-label="Last Cell"],
    input[data-testid="stTextInput"][aria-label="IMSI"],
    input[data-testid="stTextInput"][aria-label="Address"] {
        max-width: 160px !important;
    }
    div[data-baseweb="select"]:has(div[aria-label="Circle"]),
    div[data-baseweb="select"]:has(div[aria-label="Condition"]) {
        max-width: 160px !important;
    }
    .stFileUploader {
        max-width: 160px !important;
    }
    .summary-box {
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 10px;
    }
    .summary-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Advanced Search Dialog ----------
def show_search_panel():
    with st.dialog("Advanced Search"):
        st.markdown("## 🔍 Advanced Search")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("Number")
        with col2:
            st.button("From File", key="number_file")

        col1, col2, col3, col4 = st.columns([2, 2, 1, 3])
        with col1:
            st.selectbox("Circle", ["", "Circle 1", "Circle 2", "Circle 3"])
        with col2:
            st.selectbox("Condition", ["Contains", "Equals", "Starts With", "Ends With"], key="circle_condition")
        with col3:
            st.checkbox("Not", key="circle_not")
        with col4:
            st.radio("Party Type", ["A Party", "B Party", "Both"], horizontal=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("IMEI")
        with col2:
            st.button("From File", key="imei_file")

        def input_with_condition(label):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.text_input(label)
            with c2:
                st.selectbox("Condition", ["Contains", "Equals", "Starts With", "Ends With"], key=f"{label}_cond")
            with c3:
                st.checkbox("Not", key=f"{label}_not")

        for field in ["Handset", "First Cell", "Last Cell", "IMSI", "Address"]:
            input_with_condition(field)

        st.markdown("### Call Types")
        call_types = [
            "Call-In", "Call-Out", "Roaming Call-In", "Roaming Call-Out",
            "SMS-In", "SMS-Out", "Roaming SMS-In", "Roaming SMS-Out", "Others"
        ]
        cols = st.columns(3)
        for i, call in enumerate(call_types):
            with cols[i % 3]:
                st.checkbox(call)

        st.markdown("### Date & Time")
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.date_input("From Date")
        with c2:
            st.time_input("From Time")
        with c3:
            st.checkbox("Next Day", key="from_next_day")

        c4, c5, c6 = st.columns([2, 2, 1])
        with c4:
            st.date_input("To Date")
        with c5:
            st.time_input("To Time")
        with c6:
            st.checkbox("Not", key="to_not")

        st.markdown("### Duration & Location")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Duration (min)", min_value=0)
        with c2:
            st.number_input("Latitude", format="%.4f")
        with c3:
            st.number_input("Longitude", format="%.4f")

        st.markdown("### Prepaid/Postpaid")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.checkbox("Prepaid")
        with c2:
            st.checkbox("Postpaid")
        with c3:
            st.checkbox("Others")

        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.button("Search")
        with col2:
            st.button("Reset")
        with col3:
            st.button("Save Search")
        with col4:
            st.button("Close")


# ---------- Main Panel ----------
def show_search_panel():
    st.markdown("---")
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14 = st.columns([
        1.1, 1.1, 1.3, 0.7, 1.1, 1.3, 0.7, 1.3, 0.8, 0.5, 0.7, 1.3, 0.8, 0.7
    ])

    with c1:
        st.markdown("**Search Setting**")
        search_mode = st.radio(
            "Mode", ["Advanced", "Combined"], index=0, key="search_mode", label_visibility="collapsed"
        )

    with c2:
        number = st.text_input("Number", label_visibility="collapsed", placeholder="Number", key="number_input")

    with c3:
        imei = st.text_input("IMEI", label_visibility="collapsed", placeholder="IMEI", key="imei_input")

    with c4:
        st.markdown("&nbsp;")
        search_btn = st.button("Search", key="search_btn")

    with c5:
        first_cell = st.text_input("First Cell", label_visibility="collapsed", placeholder="First Cell", key="first_cell_input")

    with c6:
        type_option = st.selectbox(
            "Type", ["Select/Edit Type...", "Incoming", "Outgoing", "SMS", "Data"],
            label_visibility="collapsed", key="type_select"
        )

    with c7:
        st.markdown("&nbsp;")
        reset_btn = st.button("Reset", key="reset_btn")

    with c8:
        from_date = st.date_input("From", value=datetime.now().date() - timedelta(days=1), key="from_date")

    with c9:
        from_time = st.time_input(" ", value=datetime.now().time(), label_visibility="collapsed", key="from_time")

    with c10:
        from_dur = st.number_input(" ", min_value=0, max_value=60, value=0, label_visibility="collapsed", key="from_dur")

    with c11:
        st.markdown("&nbsp;")
        search_time_btn = st.button("Search", key="search_time_btn")

    with c12:
        to_date = st.date_input("To", value=datetime.now().date(), key="to_date")

    with c13:
        to_time = st.time_input(" ", value=datetime.now().time(), label_visibility="collapsed", key="to_time")

    with c14:
        st.markdown("&nbsp;")
        reset_time_btn = st.button("Reset", key="reset_time_btn")

    # Triggered Search Display
    if search_btn or search_time_btn:
        st.markdown("---")
        st.subheader("🔎 Search Triggered")
        st.json({
            "Search Settings": {
                "Mode": search_mode
            },
            "Inputs": {
                "Number": number,
                "IMEI": imei,
                "First Cell": first_cell,
                "Type": type_option,
                "From": f"{from_date} {from_time} (+{from_dur} mins)",
                "To": f"{to_date} {to_time}"
            }
        })

    # Summary Section
    st.markdown("<div style='height: 220px;'></div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    for col, label, columns in zip(
        [col1, col2, col3, col4],
        ["Max Call", "Max Location", "Max Duration", "Max IMEI"],
        [
            ["Total", "Number", "Description"],
            ["Total", "Tower Number", "Tower Address"],
            ["Duration", "Number", "Description"],
            ["Total", "IMEI Number", "Handset Details"]
        ]
    ):
        with col:
            st.markdown(
                f"<div class='summary-box'><div class='summary-header'><h5>{label}</h5><button>📄 Report</button></div>",
                unsafe_allow_html=True
            )
            st.dataframe(pd.DataFrame(columns=columns), use_container_width=True, height=160)
            st.markdown("</div>", unsafe_allow_html=True)
