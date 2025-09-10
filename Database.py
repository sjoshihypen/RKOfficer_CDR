import streamlit as st
import pandas as pd
import os
import mysql.connector

# --- MySQL Connection Setup ---
def connect_to_mysql():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # <-- change this
            database="CDRINFO"    # <-- change this
        )
        return conn
    except Exception as e:
        st.error(f"MySQL Connection Error: {e}")
        return None

# --- CSV Upload Logic ---
def upload_csv_to_mysql(file_path, table_name, conn):
    try:
        df = pd.read_csv(file_path)
        cursor = conn.cursor()

        # Create table if not exists (basic schema assumption)
        columns = ", ".join([f"`{col}` TEXT" for col in df.columns])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns});")

        # Insert data
        for _, row in df.iterrows():
            values = "', '".join([str(x).replace("'", "''") for x in row])
            cursor.execute(f"INSERT INTO `{table_name}` VALUES ('{values}');")

        conn.commit()
        st.success(f"Uploaded: {file_path}")
    except Exception as e:
        st.error(f"Error uploading {file_path}: {e}")

# --- Recursive Folder Scanner ---
def scan_and_upload_csvs(folder_path, conn):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                full_path = os.path.join(root, file)
                table_name = os.path.splitext(file)[0].replace('-', '_').replace(' ', '_')
                upload_csv_to_mysql(full_path, table_name, conn)

# --- Streamlit UI ---
def main():
    st.markdown(
        """
        <div style="background-color:#e6f2ff;padding:15px;border-radius:10px;">
            <h3 style="color:#003366;">📁 AI-Powered Folder Scanner & CSV Uploader</h3>
        </div>
        """, unsafe_allow_html=True
    )

    folder_path = st.text_input("📂 Enter the Path of Folder:", placeholder="E:/Projects/CSV_Folder")

    if st.button("🔍 Scan & Upload CSVs"):
        if folder_path and os.path.exists(folder_path):
            conn = connect_to_mysql()
            if conn:
                scan_and_upload_csvs(folder_path, conn)
                conn.close()
                st.success("✅ All CSV files scanned and uploaded successfully!")
        else:
            st.warning("❌ Invalid folder path. Please check and try again.")

if __name__ == "__main__":
    main()
