import streamlit as st
st.set_page_config(layout="wide", page_title="CDR Investigation Tool")
import pandas as pd
import os
import io
from streamlit_option_menu import option_menu
from Search import show_search_panel
from Normal_CDR import show_normal_cdr
#from Database import show_run_app
from Reports import show_reports

# ---------------- Session State ----------------
if "show_uploader" not in st.session_state:
    st.session_state["show_uploader"] = False
if "upload_key" not in st.session_state:
    st.session_state["upload_key"] = "new_files"
if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = []

# ---------------- CSS for Summary ----------------
st.markdown("""
<style>
    .summary-box {
        background-color: #f0f7ff;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #90caf9;
        margin-bottom: 10px;
    }
    .summary-header h5 {
        display: inline-block;
        margin-right: 10px;
        color: #0d47a1;
    }
    .summary-header button {
        float: right;
        background-color: #90caf9;
        border: none;
        border-radius: 5px;
        padding: 2px 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Heading ----------------
st.markdown("""
    <h3 style='text-align: center; color: #0d47a1; margin-top: -25px; margin-bottom: 10px;'>
        📁 CDR : Call Data Records 
    </h3>
""", unsafe_allow_html=True)

# ---------------- Top Navigation ----------------
selected_tab = option_menu(
    menu_title=None,
    options=["Home", "Search", "Normal CDR", "Tower CDR", "IPDR", "Groups", "Reports", "Database"],
    icons=["house", "search", "file-earmark", "wifi", "cloud-download", "people", "bar-chart", "database"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#e3efff"},
        "icon": {"color": "#1565c0", "font-size": "18px"},
        "nav-link": {
            "font-size": "15px",
            "text-align": "center",
            "margin": "0 10px",
            "--hover-color": "#d0e3ff",
        },
        "nav-link-selected": {"background-color": "#90caf9"},
    }
)

# ---------------- Column Mapping ----------------
final_columns_map = {
    "Target No": "A Party", "B Party No": "B Party", "Date": "Date", "Time": "Time", "Dur(s)": "Dur(s)",
    "Call Type": "Call Type", "First CGI": "First Cell Id A", "Last CGI": "Last Cell Id A",
    "IMEI": "IMEI A", "IMSI": "IMSI A", "Roam Nw": "Roam Nw", "TOC": "TOC (Connection Type of A)",
    "LRN No": "LRN No", "LRN TSP-LSA": "LRN TSP-LSA", "First CGI Lat/Long": "First CGI Lat/Log",
    "Last CGI Lat/Long": "Last CGI Lat/ Long", "SMSC No": "SMSC No", "Call Fow No": "Call Forward No",
    "Site ID": "Site ID", "Site Name": "Site Name", "Address": "Address",
    "Latitude_Y": "Latitude_Y", "Longitude_X": "Longitude_X"
}

def save_and_prepare_download(df, filename, subfolder=None, as_excel=False):
        base_dir = "D:/CDR Project/Download Summary Report"
        if subfolder:
            target_dir = os.path.join(base_dir, subfolder)
        else:
            target_dir = base_dir
        os.makedirs(target_dir, exist_ok=True)
        filepath = os.path.join(target_dir, filename)

        if as_excel:
            df.to_excel(filepath, index=False)
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False)
            return buffer.getvalue(), filepath
        else:
            df.to_csv(filepath, index=False)
            return df.to_csv(index=False).encode('utf-8'), filepath

# ---------------- Home Tab ----------------
if selected_tab == "Home":
    col_case, _, col_cdr, _, col_opts = st.columns([2.4, 0.1, 1.8, 0.1, 1.5])

    with col_case:
        st.markdown("**📂 Case**")
        row1, row2, row3, row4, row5 = st.columns(5)
        with row1:
            if st.button("🆕 New", use_container_width=True):
                st.session_state["show_uploader"] = True
                st.session_state["upload_key"] = "new_files"
                st.session_state["uploaded_data"] = []
        with row2:
            if st.button("📂 Open", use_container_width=True):
                st.session_state["show_uploader"] = True
                st.session_state["upload_key"] = "open_files"
                st.session_state["uploaded_data"] = []
        with row3:
            if st.button("💾 Save", use_container_width=True):
                if st.session_state["uploaded_data"]:
                    save_dir = "D:/Delhi Police/DataSet"
                    os.makedirs(save_dir, exist_ok=True)
                    for filename, df in st.session_state["uploaded_data"]:
                        filepath = os.path.join(save_dir, f"{filename}_cleaned.csv")
                        df.to_csv(filepath, index=False)
                    st.success(f"Saved to {save_dir}")
        with row4:
            if st.button("📝 Save As", use_container_width=True):
                if st.session_state["uploaded_data"]:
                    for filename, df in st.session_state["uploaded_data"]:
                        buf = io.BytesIO()
                        df.to_csv(buf, index=False)
                        buf.seek(0)
                        st.download_button(
                            label=f"⬇️ Download {filename}",
                            data=buf,
                            file_name=f"{filename}_cleaned.csv",
                            mime="text/csv"
                        )
        with row5:
            if st.button("❌ Close", use_container_width=True):
                st.session_state["show_uploader"] = False
                st.session_state["uploaded_data"] = []

        if st.session_state["show_uploader"]:
            uploaded_files = st.file_uploader(
                "Upload CDR File(s)",
                type=["csv", "xlsx"],
                accept_multiple_files=True,
                key=st.session_state["upload_key"]
            )

            if uploaded_files:
                cleaned_files = []
                for file in uploaded_files:
                    try:
                        file_bytes = file.read()
                        file.seek(0)
                        raw_text = file_bytes.decode(errors='ignore').lower()

                        # Detect and skip unwanted headers
                        if any(keyword in raw_text for keyword in ["bharti airtel limited", "call details", "pan india"]):
                            lines = raw_text.splitlines()
                            skip_rows = 0
                            for i, line in enumerate(lines):
                                if any(k in line for k in ["target no", "a party", "date", "b party"]):
                                    skip_rows = i
                                    break
                            file.seek(0)
                            if file.name.endswith(".csv"):
                                df = pd.read_csv(file, skiprows=skip_rows, on_bad_lines='skip', engine='python')
                            else:
                                df = pd.read_excel(file, skiprows=skip_rows)
                        else:
                            file.seek(0)
                            if file.name.endswith(".csv"):
                                df = pd.read_csv(file, on_bad_lines='skip', engine='python')
                            else:
                                df = pd.read_excel(file)

                        # Remove system-generated footer row if present
                        df = df[~df.astype(str).apply(lambda row: row.str.contains("system generated report", case=False)).any(axis=1)]

                        df.columns = df.columns.str.strip()
                        cleaned_df = pd.DataFrame()
                        for src_col, tgt_col in final_columns_map.items():
                            if src_col in df.columns:
                                cleaned_df[tgt_col] = df[src_col]
                            else:
                                cleaned_df[tgt_col] = "-"

                        cleaned_files.append((file.name, cleaned_df.copy()))
                    except Exception as e:
                        st.error(f"❌ Error loading `{file.name}`: {e}")

                if cleaned_files:
                    st.session_state["uploaded_data"] = cleaned_files
                    st.success(f"✅ {len(cleaned_files)} file(s) uploaded and cleaned successfully.")

    with col_cdr:
        st.markdown("**📶 CDR**")
        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button("➕  New", use_container_width=True):
                st.session_state["show_uploader"] = True
                st.session_state["upload_key"] = "new_files"
                st.session_state["uploaded_data"] = []
        with r2:
            if st.button("➖ Remove", use_container_width=True):
                st.session_state["show_uploader"] = False
                st.session_state["uploaded_data"] = []
        with r3:
            st.button("✏️ Edit", use_container_width=True)

    with col_opts:
        st.markdown("**📊 Columns**")
        c1, c2 = st.columns(2)
        with c1:
            st.button("📊 Hide/Unhide", use_container_width=True)
        with c2:
            st.button("📋 Summary", use_container_width=True)
        st.button("ℹ️ About", use_container_width=True)

    # ---------- Display Each Uploaded File ----------
    if st.session_state["uploaded_data"]:
        st.markdown("### 📂 Cleaned & Imported CDR Data (Multiple Files)")
        tabs = st.tabs([file_name for file_name, _ in st.session_state["uploaded_data"]])
        for (file_name, df), tab in zip(st.session_state["uploaded_data"], tabs):
            with tab:
                st.markdown(f"**📄 File: `{file_name}`**")
                st.dataframe(df, use_container_width=True)

        # --- Selectbox for Summary File ---
        file_names = [file_name for file_name, _ in st.session_state["uploaded_data"]]

        st.markdown(
            "<label style='font-weight:bold; font-size:20px;'>Select File To View Summary:</label>",
            unsafe_allow_html=True
        )
        selected_file_for_summary = st.selectbox(" ", file_names)

        # --- Get dataframe of selected file ---
        selected_df = None
        for fname, df in st.session_state["uploaded_data"]:
            if fname == selected_file_for_summary:
                selected_df = df
                break

        if selected_df is not None:
            # Max Call
            if "A Party" in selected_df.columns and not selected_df["A Party"].isnull().all():
                call_counts = selected_df["A Party"].value_counts().sort_values(ascending=False).head(10)
                df_call = pd.DataFrame({
                    "Number": call_counts.index,
                    "Total Calls": call_counts.values,
                    "Description": ["Frequent calling number"] * len(call_counts)
                })
            else:
                df_call = pd.DataFrame(columns=["Total Calls", "Number", "Description"])

            # Max Location
            if "Site ID" in selected_df.columns and not selected_df["Site ID"].isnull().all():
                location_counts = selected_df["Site ID"].value_counts().sort_values(ascending=False).head(10)
                df_loc = pd.DataFrame({
                    "Tower Number": location_counts.index,
                    "Total Locations": location_counts.values,
                    "Tower Address": ["Frequent Site ID"] * len(location_counts)
                })
            else:
                df_loc = pd.DataFrame(columns=["Total Locations", "Tower Number", "Tower Address"])

            # Max Duration
            if "Dur(s)" in selected_df.columns and not selected_df["Dur(s)"].isnull().all():
                df_dur_sorted = selected_df.sort_values(by="Dur(s)", ascending=False).head(10)
                durations = df_dur_sorted["Dur(s)"].values
                numbers = df_dur_sorted["A Party"].values if "A Party" in selected_df.columns else ["-"] * len(durations)
                df_dur = pd.DataFrame({
                    "Duration": durations,
                    "Number": numbers,
                    "Description": ["Longest call duration"] * len(durations)
                })
            else:
                df_dur = pd.DataFrame(columns=["Duration", "Number", "Description"])

            # Max IMEI
            if "IMEI A" in selected_df.columns and not selected_df["IMEI A"].isnull().all():
                imei_counts = selected_df["IMEI A"].value_counts().sort_values(ascending=False).head(10)
                df_imei = pd.DataFrame({
                    "IMEI Number": imei_counts.index,
                    "Total IMEIs": imei_counts.values,
                    "Handset Details": ["Frequent IMEI"] * len(imei_counts)
                })
            else:
                df_imei = pd.DataFrame(columns=["Total IMEIs", "IMEI Number", "Handset Details"])

            # --- Display summaries with download buttons ---
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                csv_bytes, saved_path = save_and_prepare_download(df_call, f"{selected_file_for_summary}_MaxCall.csv")
                st.markdown(
                    f"<div class='summary-box'><div class='summary-header'><h5>Max Call</h5></div>",
                    unsafe_allow_html=True
                )
                st.dataframe(df_call, use_container_width=True, height=110)
                st.download_button(
                    label="📄 Download & Save Report",
                    data=csv_bytes,
                    file_name=f"{selected_file_for_summary}_MaxCall.csv",
                    mime="text/csv",
                    help=f"Saved to: {saved_path}"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                csv_bytes, saved_path = save_and_prepare_download(df_loc, f"{selected_file_for_summary}_MaxLocation.csv")
                st.markdown(
                    f"<div class='summary-box'><div class='summary-header'><h5>Max Location</h5></div>",
                    unsafe_allow_html=True
                )
                st.dataframe(df_loc, use_container_width=True, height=110)
                st.download_button(
                    label="📄 Download & Save Report",
                    data=csv_bytes,
                    file_name=f"{selected_file_for_summary}_MaxLocation.csv",
                    mime="text/csv",
                    help=f"Saved to: {saved_path}"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with col3:
                csv_bytes, saved_path = save_and_prepare_download(df_dur, f"{selected_file_for_summary}_MaxDuration.csv")
                st.markdown(
                    f"<div class='summary-box'><div class='summary-header'><h5>Max Duration</h5></div>",
                    unsafe_allow_html=True
                )
                st.dataframe(df_dur, use_container_width=True, height=110)
                st.download_button(
                    label="📄 Download & Save Report",
                    data=csv_bytes,
                    file_name=f"{selected_file_for_summary}_MaxDuration.csv",
                    mime="text/csv",
                    help=f"Saved to: {saved_path}"
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with col4:
                csv_bytes, saved_path = save_and_prepare_download(df_imei, f"{selected_file_for_summary}_MaxIMEI.csv")
                st.markdown(
                    f"<div class='summary-box'><div class='summary-header'><h5>Max IMEI</h5></div>",
                    unsafe_allow_html=True
                )
                st.dataframe(df_imei, use_container_width=True, height=110)
                st.download_button(
                    label="📄 Download & Save Report",
                    data=csv_bytes,
                    file_name=f"{selected_file_for_summary}_MaxIMEI.csv",
                    mime="text/csv",
                    help=f"Saved to: {saved_path}"
                )
                st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Other Tabs ----------------
elif selected_tab == "Search":
    show_search_panel()
    st.markdown("<div style='height: 280px;'></div>", unsafe_allow_html=True)

elif selected_tab == "Normal CDR":
    show_normal_cdr()
    st.markdown("<div style='height: 280px;'></div>", unsafe_allow_html=True)

elif selected_tab == "Reports":
    show_reports()
    st.markdown("<div style='height: 280px;'></div>", unsafe_allow_html=True)

#elif selected_tab == "Database":
    #show_run_app()
    #st.markdown("<div style='height: 280px;'></div>", unsafe_allow_html=True)


