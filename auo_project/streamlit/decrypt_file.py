from pathlib import Path

import streamlit as st
from auo_project.core.config import settings
from auo_project.core.security import decrypt


def page():
    st.subheader("解密單檔")
    st.info(
        """
說明：將加密檔案讀入並產出解密檔案，解密檔案檔名以 _decrypted 結尾。
""",
    )

    bytes_data = None
    uploaded_file = st.file_uploader(label="檔案")

    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()

    if not bytes_data:
        return

    decrypted_data = decrypt(
        settings.TXT_FILE_AES_KEY,
        settings.TXT_FILE_AES_IV,
        bytes_data,
    )
    print("decrypted_data", decrypted_data)
    filep = Path(uploaded_file.name)
    st.download_button(
        label="下載檔案",
        data=decrypted_data,
        file_name=f"{filep.stem}_decrpyted{filep.suffix}",
    )
