from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import streamlit as st
from auo_project.core.config import settings
from auo_project.core.security import decrypt


def page():
    st.subheader("解密壓縮檔")
    st.info(
        """
說明：將加密檔案讀入並產出解密檔案，解密檔案檔名以 _decrypted 結尾。
""",
    )

    bytes_data = None
    uploaded_file = st.file_uploader(label="壓縮檔", type=["zip"])
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        bytes_file = BytesIO(bytes_data)

    if not bytes_data:
        return

    checked_file_list = []
    output_zip = BytesIO()

    with ZipFile(bytes_file, mode="r") as measure_zip:
        with ZipFile(output_zip, "a", ZIP_DEFLATED, compresslevel=9) as output_zip_obj:
            infolist = measure_zip.infolist()
            for file_info in infolist:
                if not file_info.is_dir():
                    # TODO
                    # file_info = is_valid_file(file_info)
                    if (
                        "__MACOSX" in file_info.filename
                        or ".DS_Store" in file_info.filename
                    ):
                        continue
                    checked_file_list.append(file_info)

            encrypted_suffixes = ".txt"
            for file_info in checked_file_list:
                print("file_info", file_info)
                file_name_p = Path(file_info.filename)
                file_name = file_name_p.name
                # TODO
                # allowed = file_name in allowd_filename_list
                allowed = True

                if allowed:
                    with measure_zip.open(file_info.filename, mode="r") as f:
                        content = f.read()

                # don't write
                if "_decrypted" in file_name:
                    continue
                elif file_name_p.suffix not in encrypted_suffixes:
                    output_zip_obj.writestr(f"{file_name_p}", content)
                else:
                    output_zip_obj.writestr(f"{file_name_p}", content)
                    decrypted_data = decrypt(
                        settings.TXT_FILE_AES_KEY,
                        settings.TXT_FILE_AES_IV,
                        content,
                    )
                    output_zip_obj.writestr(
                        f"{file_name_p.parent}/{file_name_p.stem}_decrypted{file_name_p.suffix}",
                        decrypted_data,
                    )

    filep = Path(uploaded_file.name)
    st.download_button(
        label="下載壓縮檔",
        data=output_zip.getvalue(),
        file_name=f"{filep.stem}_decrpyted{filep.suffix}",
    )
