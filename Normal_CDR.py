import streamlit as st
import pandas as pd

def show_normal_cdr():
    # --- Session State Initialization ---
    if "show_call_dropdown" not in st.session_state:
        st.session_state["show_call_dropdown"] = False

    # --- CSS Styling ---
    st.markdown("""
    <style>
        html, body, [data-testid="stApp"] {
            height: 100%;
            margin: 0;
            padding: 0;
        }
        .footer-wrapper {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .footer-spacer {
            flex-grow: 1;
        }
        .section-title {
            text-align: center;
            font-weight: 600;
            margin-bottom: 4px;
            margin-top: 0px;
            font-size: 16px;
        }
        .stButton>button {
            width: 100%;
            height: 42px;
            border-radius: 6px;
            background-color: #f1f3f6;
            color: black;
            border: 1px solid #d3d3d3;
            font-weight: 500;
            font-size: 14px;
        }
        .stButton>button:hover {
            background-color: #e0e0e0;
            color: black;
        }
        .group-box {
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            background-color: #fff;
        }
        .summary-box {
            background-color: #f1f7ff;
            border: 1px solid #cbd6e2;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 0px;
        }
        .summary-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        .summary-header h5 {
            margin: 0;
            font-size: 16px;
            color: #0d1a26;
        }
        .summary-header button {
            font-size: 12px;
            background-color: #e6eefc;
            border: 1px solid #c0c8d3;
            padding: 4px 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        footer {
            visibility: hidden;
            height: 0;
        }
    </style>
    """, unsafe_allow_html=True)


    # --- Top Control Panel ---
    with st.container():
        col1, col2, col3, col4 = st.columns([2.5, 1, 3, 1.5])

        with col1:
            st.markdown("<div class='section-title'>Find Common</div>", unsafe_allow_html=True)
            st.markdown("<div class='group-box'>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.button("A Party")
            with c2:
                st.markdown("""
                <div style='white-space: nowrap;'>
                    <button class='stButton' style="width: 100%; height: 42px; border-radius: 6px; background-color: #f1f3f6; color: black; border: 1px solid #d3d3d3; font-weight: 500; font-size: 14px; cursor: pointer;">Number (A+B)</button>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.button("IMEI")
            with c4:
                st.button("Tower")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='section-title'>CDR</div>", unsafe_allow_html=True)
            st.markdown("<div class='group-box'>", unsafe_allow_html=True)
            st.button("Split")
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("<div class='section-title'>Report</div>", unsafe_allow_html=True)
            st.markdown("<div class='group-box'>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.button("Quick")
            with c2:
                if st.button("Call"):
                    st.session_state["show_call_dropdown"] = not st.session_state["show_call_dropdown"]

                if st.session_state["show_call_dropdown"]:
                    st.selectbox("", options=["SMS-IN", "CALL-OUT"])
            with c3:
                st.button("SMS")
            with c4:
                st.button("Export")
            st.markdown("</div>", unsafe_allow_html=True)

        with col4:
            st.markdown("<div class='section-title'>Other</div>", unsafe_allow_html=True)
            st.markdown("<div class='group-box'>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.button("Conf. - A")
            with c2:
                st.button("Follow Up")
            st.markdown("</div>", unsafe_allow_html=True)
            
    # Add spacing before footer
    st.markdown("<div style='height: 220px;'></div>", unsafe_allow_html=True)

    # ---------------- Footer Tables ----------------
    max_call_df = pd.DataFrame(columns=["Total", "Number", "Description"])
    max_location_df = pd.DataFrame(columns=["Total", "Tower Number", "Tower Address"])
    max_duration_df = pd.DataFrame(columns=["Duration", "Number", "Description"])
    max_imei_df = pd.DataFrame(columns=["Total", "IMEI Number", "Handset Details"])

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
