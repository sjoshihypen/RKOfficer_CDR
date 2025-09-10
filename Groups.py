# import streamlit as st
# from datetime import datetime, timedelta

# st.set_page_config(page_title="Advance Search UI", layout="wide")

# def show_groups():
#     st.title("🔍 Advance Search")

#     # --------- Helper Function for Columns with Condition + Not Checkbox ---------
#     def condition_row(label):
#         c1, c2, c3, c4 = st.columns([1.5, 2, 1, 1])
#         with c1: st.text_input(label, key=label)
#         with c2: st.selectbox("Condition", ["Contains", "Equals", "Starts With", "Ends With"], key=f"{label}_cond", label_visibility="collapsed")
#         with c3: st.checkbox("Not", key=f"{label}_not")
#         st.markdown("")

#     # --------- Row 1: Number + From File + Party Type ---------
#         col1, col2, col3, col4 = st.columns([3, 1, 3, 3])
#         with col1: st.text_input("Number", key="number")
#         with col2: st.button("From File", key="number_file")
#         with col3: st.selectbox("Circle", ["", "North", "East", "West", "South"], key="circle")
#         with col4:
#          st.markdown("**Party Type**")
#          st.radio(" ", ["A Party", "B Party", "Both"], horizontal=True, key="party_type", label_visibility="collapsed")

#     # --------- Row 2: IMEI + From File ---------
#         col5, col6 = st.columns([3, 1])
#         with col5: st.text_input("IMEI", key="imei")
#         with col6: st.button("From File", key="imei_file")

#     # --------- Fields with Condition ---------
#         condition_row("Handset")
#         condition_row("First Cell")
#         condition_row("Last Cell")
#         condition_row("IMSI")
#         condition_row("Address")

#     # --------- Date, Time, Duration, Lat/Long ---------
#         st.markdown("---")
#         c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.5, 1.5, 1, 1, 1.5, 1.5, 1.5, 1.5])

#         with c1: from_date = st.date_input("From Date", value=datetime.now().date() - timedelta(days=1))
#         with c2: from_time = st.time_input("From Time", value=datetime.now().time())
#         with c3: st.checkbox("Next Day", key="next_day")
#         with c4: from_dur = st.number_input("Duration", min_value=0, value=0)

#         with c5: to_date = st.date_input("To Date", value=datetime.now().date())
#         with c6: to_time = st.time_input("To Time", value=datetime.now().time())
#         with c7: to_dur = st.number_input("To Duration", min_value=0, value=0)
#         with c8:
#             st.text_input("Latitude", value="0.0000", key="lat")
#             st.text_input("Longitude", value="0.0000", key="lon")

#         # --------- Call Types ---------
#         st.markdown("---")
#         col_ct, col_pp = st.columns([4, 2])
#         with col_ct:
#             st.markdown("**Call Types**")
#             st.columns(4)
#         ct1, ct2 = st.columns(2)
#         with ct1:
#          st.checkbox("Call-In")
#          st.checkbox("Call-Out")
#          st.checkbox("Roaming Call-In")
#          st.checkbox("Roaming Call-Out")
#         with ct2:
#          st.checkbox("SMS-In")
#          st.checkbox("SMS-Out")
#          st.checkbox("Roaming SMS-In")
#          st.checkbox("Roaming SMS-Out")
#          st.checkbox("Others")

# # --------- Prepaid/Postpaid ---------
#         with col_pp:
#          st.markdown("**Prepaid / Postpaid**")
#          st.checkbox("Prepaid")
#          st.checkbox("Postpaid")
#          st.checkbox("Others")

# # --------- Footer Buttons ---------
#     st.markdown("---")
#     cb1, cb2, cb3, cb4, cb5 = st.columns([1, 1, 2, 2, 1])
#     with cb1: st.button("Search")
#     with cb2: st.button("Reset")
#     with cb3: st.button("Save Search")
#     with cb4: st.button("Load Search")
#     with cb5: st.button("Close")
