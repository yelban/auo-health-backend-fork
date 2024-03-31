from io import BytesIO
from pathlib import Path

from azure.storage.blob import BlobServiceClient

import streamlit as st
from auo_project.core.config import settings


def page():
    if "run_button" in st.session_state and st.session_state.run_button == True:
        st.session_state.disabled = True
    else:
        st.session_state.disabled = False
    blob_service_client = BlobServiceClient(
        account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
        credential={
            "account_name": settings.AZURE_STORAGE_ACCOUNT,
            "account_key": settings.AZURE_STORAGE_KEY,
        },
    )

    filename = st.text_input("請輸入檔案名稱", "", disabled=st.session_state.disabled)
    if filename == "":
        st.stop()

    password = st.text_input("密碼", "", disabled=st.session_state.disabled)

    if st.button("確認", disabled=st.session_state.disabled, key="run_button"):
        if password == "":
            st.write("請輸入密碼")
            st.stop()

        elif password == settings.STREAMLIT_PASSWORD and filename != "":
            filep = Path(filename)
            blob_client = blob_service_client.get_blob_client(
                container="raw-backup",
                blob=filename,
            )

            downloader = blob_client.download_blob(max_concurrency=2)
            bytes_file = BytesIO(downloader.readall())
            st.download_button(
                label="下載原始壓縮檔",
                data=bytes_file.getvalue(),
                file_name=filename,
            )
            st.session_state.disabled = False

        else:
            st.write("密碼錯誤")
            return
