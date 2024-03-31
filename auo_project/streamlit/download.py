from io import BytesIO
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from sqlalchemy import create_engine

import streamlit as st
from auo_project.core.config import settings
from auo_project.streamlit.decrypt_zip import (
    add_decrypted_files_to_zip,
    create_zip_with_all_raw,
)


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

    st.write("請輸入單人單次網址")
    url = st.text_input("網址", "", disabled=st.session_state.disabled)
    if url == "":
        st.stop()

    choice1 = "解密完整 ZIP"
    choice2 = "解密全部 Channel 全段資料"
    choice3 = "下載原始 ZIP"
    data_type = st.radio(
        "請選擇：",
        [choice1, choice2, choice3],
        disabled=st.session_state.disabled,
    )

    password = st.text_input("密碼", "", disabled=st.session_state.disabled)

    if st.button("確認", disabled=st.session_state.disabled, key="run_button"):
        if password == "":
            st.write("請輸入密碼")
            st.stop()

        elif password == settings.STREAMLIT_PASSWORD and url != "":
            measure_id = url.split("/")[-1]

            engine = create_engine(
                settings.DATABASE_URI,
                connect_args={"connect_timeout": 10},
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=0,
                pool_timeout=10,
            )
            conn = engine.raw_connection()
            print("measure_id", measure_id)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                            select name
                            from app.upload_files as f
                            inner join measure.infos as i on i.file_id = f.id
                            where i.id = %s;
                            """,
                    (measure_id,),
                )
                filename_result = cursor.fetchone()
                print("filename_result", filename_result)
                if filename_result is None:
                    st.write(f"找不到檔案（檢測編號 {measure_id}）")
                    st.stop()
                    # return

            conn.close()
            st.session_state.disabled = True

            filename = filename_result[0]
            if filename is None:
                st.write(f"找不到檔案（檢測編號 {measure_id}）")
                st.stop()

            filep = Path(filename)
            blob_client = blob_service_client.get_blob_client(
                container="raw-backup",
                blob=filename,
            )

            downloader = blob_client.download_blob(max_concurrency=2)
            bytes_file = BytesIO(downloader.readall())
            if data_type == choice1:
                decrpyted_zip = add_decrypted_files_to_zip(bytes_file)
                st.download_button(
                    label="下載解密壓縮檔",
                    data=decrpyted_zip.getvalue(),
                    file_name=f"{filep.stem}_decrpyted{filep.suffix}",
                )
            elif data_type == choice2:
                decrpyted_zip = create_zip_with_all_raw(bytes_file)
                st.download_button(
                    label="下載解密 Channel 全段資料壓縮檔",
                    data=decrpyted_zip.getvalue(),
                    file_name=f"{filep.stem}_all_raw_decrpyted{filep.suffix}",
                )
            elif data_type == choice3:
                st.download_button(
                    label="下載原始壓縮檔",
                    data=bytes_file.getvalue(),
                    file_name=filename,
                )
            else:
                st.write(f"不允許選項: {data_type}")
                st.stop()

            st.session_state.disabled = False

        else:
            st.write("密碼錯誤")
            # st.stop()
            return
