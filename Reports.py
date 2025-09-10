import streamlit as st

def show_reports():
    st.markdown("""
        <style>
            .button-container {
                display: flex;
                justify-content: center;
                margin-top: 30px;
                margin-bottom: 20px;
            }
            .report-button {
                background-color: #a3c648;
                border: none;
                color: white;
                padding: 14px 18px;
                margin: 4px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                border-radius: 6px;
                transition: 0.3s;
            }
            .report-button:hover {
                background-color: #8aaa35;
            }
        </style>

        <div class="button-container">
            <button class="report-button">Export All</button>
            <button class="report-button">Multiple SIM - IMEI</button>
            <button class="report-button">Master ▼</button>
            <button class="report-button">Multiple Numbers</button>
            <button class="report-button">Check A Party</button>
            <button class="report-button">International</button>
            <button class="report-button">Roaming Details</button>
        </div>

        <p style="text-align:center; font-weight:bold; color:#336699;">Reports</p>
    """, unsafe_allow_html=True)
