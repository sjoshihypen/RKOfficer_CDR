import streamlit as st
st.set_page_config(layout="wide", page_title="CDR Investigation Tool")
import pandas as pd
import os
import io
from streamlit_option_menu import option_menu
from streamlit_modal import Modal
from Search import show_search_panel
from Normal_CDR import show_normal_cdr
from Reports import show_reports
import plotly.express as px
import numpy as np

# ---------------- Session State ----------------
if "show_case_uploader" not in st.session_state:
    st.session_state["show_case_uploader"] = False
if "show_cdr_uploader" not in st.session_state:
    st.session_state["show_cdr_uploader"] = False
if "upload_key" not in st.session_state:
    st.session_state["upload_key"] = "None"
if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = []
if "cdr_type" not in st.session_state:
    st.session_state["cdr_type"] = None
if "date_type" not in st.session_state:
    st.session_state["date_type"] = None

# ---------------- Create Modals ----------------
modal = Modal("Select Options", key="select_options", max_width=800)
graph_modal = Modal("Visual Summary", key="graph_modal", max_width=900)

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

# ---------------- Helpers ----------------
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

def safe_to_numeric(series):
    # convert to numeric, coerce errors to NaN
    return pd.to_numeric(series, errors='coerce')

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

# ---------- Utility to render graphs in modal ----------
def render_graphs_in_modal(df, title=None):
    # attempt to sanitize columns
    df = df.copy()
    # Dur(s) numeric
    if "Dur(s)" in df.columns:
        df["Dur(s)"] = safe_to_numeric(df["Dur(s)"])
    # prepare charts
    charts = {}

    # Top callers
    if "A Party" in df.columns and not df["A Party"].isnull().all():
        call_counts = df["A Party"].astype(str).value_counts().head(10)
        df_call = pd.DataFrame({"Number": call_counts.index, "Total Calls": call_counts.values})
        fig_call = px.bar(df_call, x="Number", y="Total Calls", title="Top 10 Callers (A Party)", labels={"Number":"Number","Total Calls":"Calls"})
        charts["Top Callers"] = fig_call
    else:
        charts["Top Callers"] = None

    # Top towers
    if "Site ID" in df.columns and not df["Site ID"].isnull().all():
        location_counts = df["Site ID"].astype(str).value_counts().head(10)
        df_loc = pd.DataFrame({"Site ID": location_counts.index, "Occurrences": location_counts.values})
        fig_loc = px.bar(df_loc, x="Site ID", y="Occurrences", title="Top 10 Site IDs", labels={"Site ID":"Site ID","Occurrences":"Count"})
        charts["Top Towers"] = fig_loc
    else:
        charts["Top Towers"] = None

    # Duration distribution
    if "Dur(s)" in df.columns and df["Dur(s)"].notnull().any():
        durations = df["Dur(s)"].dropna()
        # clip extreme outliers visually for histogram if needed
        q99 = durations.quantile(0.99)
        durations_vis = durations.clip(upper=q99)
        fig_dur = px.histogram(durations_vis, nbins=40, title=f"Call Duration Distribution (clipped at 99th pct: {q99:.1f}s)")
        charts["Duration Distribution"] = fig_dur
    else:
        charts["Duration Distribution"] = None

    # Top IMEI
    if "IMEI A" in df.columns and not df["IMEI A"].isnull().all():
        imei_counts = df["IMEI A"].astype(str).value_counts().head(10)
        df_imei = pd.DataFrame({"IMEI": imei_counts.index, "Count": imei_counts.values})
        fig_imei = px.bar(df_imei, x="IMEI", y="Count", title="Top 10 IMEIs", labels={"IMEI":"IMEI","Count":"Occurrences"})
        charts["Top IMEI"] = fig_imei
    else:
        charts["Top IMEI"] = None

    # Render charts in modal layout
    with graph_modal.container():
        if title:
            st.markdown(f"### 📊 Visual Summary — {title}")
        else:
            st.markdown("### 📊 Visual Summary")
        st.markdown("---")
        # layout: 2x2
        cols = st.columns(2)
        # Top Callers
        if charts["Top Callers"] is not None:
            with cols[0]:
                st.plotly_chart(charts["Top Callers"], use_container_width=True)
        else:
            with cols[0]:
                st.info("No 'A Party' data to render Top Callers chart.")

        # Top Towers
        if charts["Top Towers"] is not None:
            with cols[1]:
                st.plotly_chart(charts["Top Towers"], use_container_width=True)
        else:
            with cols[1]:
                st.info("No 'Site ID' data to render Top Towers chart.")

        # Duration
        cols_bottom = st.columns(2)
        if charts["Duration Distribution"] is not None:
            with cols_bottom[0]:
                st.plotly_chart(charts["Duration Distribution"], use_container_width=True)
        else:
            with cols_bottom[0]:
                st.info("No 'Dur(s)' data to render Duration Distribution chart.")

        # IMEI
        if charts["Top IMEI"] is not None:
            with cols_bottom[1]:
                st.plotly_chart(charts["Top IMEI"], use_container_width=True)
        else:
            with cols_bottom[1]:
                st.info("No 'IMEI A' data to render IMEI chart.")

        st.markdown("---")
        if st.button("Close Visual", key="close_visual_btn"):
            graph_modal.close()

# ---------------- Home Tab ----------------
if selected_tab == "Home":
    col_case, _, col_cdr, _, col_opts = st.columns([2.4, 0.1, 1.8, 0.1, 1.5])

    # ---- Case Section ----
    with col_case:
        st.markdown("**📂 Case**")
        row1, row2, row3, row4, row5 = st.columns(5)

        with row1:
            if st.button("🆕 New", use_container_width=True, key="btn_new"):
                modal.open()

        # ---------------- MODAL CONTENT ----------------
        if modal.is_open():
            with modal.container():
                st.markdown(
                    "<h3 style='text-align:center; color:#2E86C1;'>📌 Select CDR and Date Options</h3>",
                    unsafe_allow_html=True
                )

                # ---- CDR TYPE ----
                st.markdown(
                    """
                    <div style="border:2px solid #2E86C1; border-radius:10px; padding:15px; margin-bottom:15px; background-color:#F8F9F9;">
                        <h4 style='color:#117A65;'>📡 CDR Type</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                cdr_type = st.radio(
                    "",
                    ["Normal", "Normal GPRS/IDPR", "Tower", "Tower GPRS/IPDR",
                     "IMEI", "IPDR", "ILD", "DSL", "Landline", "M2M"],
                    horizontal=True
                )

                # ---- DATE TYPE ----
                st.markdown(
                    """
                    <div style="border:2px solid #D35400; border-radius:10px; padding:15px; margin-top:10px; background-color:#FEF9E7;">
                        <h4 style='color:#B03A2E;'>📅 Date Type</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                date_type = st.radio(
                    "",
                    ["Auto Select", "DD/MM/YYYY", "MM/DD/YYYY", "YYYY/MM/DD", "YYYY/DD/MM"],
                    horizontal=True
                )

                # ---- CENTERED BUTTONS ----
                col_a, col_b, col_c, col_d, col_e = st.columns([2, 1, 1, 1, 2])
                with col_b:
                    if st.button("✅ Ok", key="modal_ok"):
                        st.session_state["cdr_type"] = cdr_type
                        st.session_state["date_type"] = date_type
                        st.session_state["show_case_uploader"] = True
                        st.session_state["show_cdr_uploader"] = False
                        st.session_state["upload_key"] = "new_files"
                        st.session_state["uploaded_data"] = []
                        st.success(f"Selected: {cdr_type} | {date_type}")
                        modal.close()
                with col_c:
                    if st.button("❌ Cancel", key="modal_cancel"):
                        modal.close()

        with row2:
            if st.button("📂 Open", use_container_width=True, key="btn_open"):
                st.session_state["show_case_uploader"] = True
                st.session_state["upload_key"] = "open_files"
            # do not clear uploaded_data on open, user may want to append

        with row3:
            if st.button("💾 Save", use_container_width=True, key="btn_save"):
                if st.session_state["uploaded_data"]:
                    save_dir = "D:/Delhi Police/DataSet"
                    os.makedirs(save_dir, exist_ok=True)
                    errors = []
                    for filename, df in st.session_state["uploaded_data"]:
                        try:
                            filepath = os.path.join(save_dir, f"{filename}_cleaned.csv")
                            df.to_csv(filepath, index=False)
                        except Exception as e:
                            errors.append((filename, str(e)))
                    if errors:
                        st.error(f"Some files failed to save: {errors}")
                    else:
                        st.success(f"Saved {len(st.session_state['uploaded_data'])} files to {save_dir}")

        with row4:
            if st.button("📝 Save As", use_container_width=True, key="btn_saveas"):
                if st.session_state["uploaded_data"]:
                    for filename, df in st.session_state["uploaded_data"]:
                        buf = io.BytesIO()
                        df.to_csv(buf, index=False)
                        buf.seek(0)
                        st.download_button(
                            label=f"⬇️ Download {filename}",
                            data=buf,
                            file_name=f"{filename}_cleaned.csv",
                            mime="text/csv",
                            key=f"download_{filename}"
                        )
                else:
                    st.warning("No uploaded files available for download.")

        with row5:
            if st.button("❌ Close", use_container_width=True, key="btn_close"):
                st.session_state["show_case_uploader"] = False
                st.session_state["uploaded_data"] = []

        if st.session_state["show_case_uploader"]:
            uploaded_files = st.file_uploader(
                "Upload Case File(s)",
                type=["csv", "xlsx"],
                accept_multiple_files=True,
                key=st.session_state["upload_key"] + "_case"
            )

            if uploaded_files:
                cleaned_files = []
                existing_files = {fname for fname, _ in st.session_state["uploaded_data"]}
                for file in uploaded_files:
                    if file.name in existing_files:
                        continue  # ✅ Skip duplicate files
                    try:
                        file_bytes = file.read()
                        file.seek(0)
                        raw_text = file_bytes.decode(errors='ignore').lower()

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

                        df = df[~df.astype(str).apply(lambda row: row.str.contains("system generated report", case=False)).any(axis=1)]
                        df.columns = df.columns.str.strip()

                        cleaned_df = pd.DataFrame()
                        for src_col, tgt_col in final_columns_map.items():
                            cleaned_df[tgt_col] = df[src_col] if src_col in df.columns else "-"

                        cleaned_files.append((file.name, cleaned_df.copy()))
                    except Exception as e:
                        st.error(f"❌ Error loading `{file.name}`: {e}")

                if cleaned_files:
                    st.session_state["uploaded_data"].extend(cleaned_files)
                    st.success(f"✅ {len(cleaned_files)} new file(s) added. Total files: {len(st.session_state['uploaded_data'])}")

    # ---- CDR Section ----
    with col_cdr:
        st.markdown("**📶 CDR**")
        r1, r2, r3 = st.columns(3)
        with r1:
            if st.button("➕  Add", use_container_width=True, key="cdr_new"):
             st.session_state["show_cdr_uploader"] = True   # ✅ open only CDR uploader
             st.session_state["show_case_uploader"] = False # ✅ close case uploader
             st.session_state["upload_key"] = "new_files"


        with r2:
            if st.button("➖ Remove", use_container_width=True, key="cdr_remove"):
                if st.session_state["uploaded_data"]:
                    file_names = [fname for fname, _ in st.session_state["uploaded_data"]]
                    file_to_remove = st.selectbox("Select file to remove:", file_names, key="remove_select")
                    if st.button("🗑️ Confirm Remove", key="confirm_remove"):
                        st.session_state["uploaded_data"] = [
                            (fname, df) for fname, df in st.session_state["uploaded_data"]
                            if fname != file_to_remove
                        ]
                        st.success(f"✅ Removed {file_to_remove}")

        with r3:
            if st.button("✏️ Edit", use_container_width=True, key="cdr_edit"):
                st.info("Edit action: implement your edit functionality here.")

        if st.session_state["show_cdr_uploader"]:
            uploaded_files = st.file_uploader(
                "Upload CDR File(s)",
                type=["csv", "xlsx"],
                accept_multiple_files=True,
                key=st.session_state["upload_key"] + "_cdr"
            )

            if uploaded_files:
                cleaned_files = []
                existing_files = {fname for fname, _ in st.session_state["uploaded_data"]}
                for file in uploaded_files:
                    if file.name in existing_files:
                        continue  # ✅ Skip duplicate files
                    try:
                        file_bytes = file.read()
                        file.seek(0)
                        raw_text = file_bytes.decode(errors='ignore').lower()

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

                        df = df[~df.astype(str).apply(lambda row: row.str.contains("system generated report", case=False)).any(axis=1)]
                        df.columns = df.columns.str.strip()

                        cleaned_df = pd.DataFrame()
                        for src_col, tgt_col in final_columns_map.items():
                            cleaned_df[tgt_col] = df[src_col] if src_col in df.columns else "-"

                        cleaned_files.append((file.name, cleaned_df.copy()))
                    except Exception as e:
                        st.error(f"❌ Error loading `{file.name}`: {e}")

                if cleaned_files:
                    st.session_state["uploaded_data"].extend(cleaned_files)
                    st.success(f"✅ {len(cleaned_files)} new file(s) added. Total files: {len(st.session_state['uploaded_data'])}")

    # ---- Columns Section ----
    with col_opts:
        st.markdown("**📊 Columns**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📊 Hide/Unhide", use_container_width=True, key="col_toggle"):
                # on click, open the graph modal
                if not st.session_state["uploaded_data"]:
                    st.warning("No files uploaded. Please upload at least one CDR file to visualize.")
                else:
                    # prepare for graph modal:
                    graph_modal.open()

        with c2:
            if st.button("📋 Summary", use_container_width=True, key="col_summary"):
                st.info("Summary action - the summary panel below will update automatically.")
        if st.button("ℹ️ About", key="about_btn"):
            st.info("CDR Investigation Tool — updated uploader & save/import flow.")

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

# When graph modal is open, allow user to select file to visualize
if graph_modal.is_open():
    with graph_modal.container():
        st.markdown("<h3 style='text-align:center;'>📊 Visualize CDR Data</h3>", unsafe_allow_html=True)

        # File selection
        file_names = [fname for fname, _ in st.session_state["uploaded_data"]]
        selected_for_graph = st.selectbox("Select file:", file_names, key="select_graph_file")

        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])

        with col2:
            if st.button("✅ Ok", key="ok_graph_modal"):
                st.session_state["show_graphs"] = True
                st.session_state["graph_file"] = selected_for_graph

            if st.button("❌ Cancel", key="cancel_graph_modal"):
                st.session_state["show_graphs"] = False
                graph_modal.close()

        # Render graphs if flag is set
        if st.session_state.get("show_graphs", False):
            df_to_plot = None
            for fname, df in st.session_state["uploaded_data"]:
                if fname == st.session_state["graph_file"]:
                    df_to_plot = df
                    break

            if df_to_plot is not None:
                render_graphs_in_modal(df_to_plot, title=st.session_state["graph_file"])
            else:
                st.error("❌ Selected file not found.")


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

