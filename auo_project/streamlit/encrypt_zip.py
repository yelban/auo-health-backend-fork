from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import streamlit as st
from auo_project.core.config import settings
from auo_project.core.security import encrypt


def page():
    st.subheader("加密壓縮檔")
    st.info(
        """
說明：將壓縮檔中檔名有 _decrypted 的檔案重新加密。
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
                    if "__MACOSX" in file_info.filename:
                        continue
                    checked_file_list.append(file_info)

            decrpyrted_file_list = [
                file_info
                for file_info in checked_file_list
                if "_decrypted" in file_info.filename
            ]
            decrpyrted_file_name_list = [
                file_info.filename for file_info in decrpyrted_file_list
            ]
            print("decrpyted_file_list", decrpyrted_file_list)

            not_decrpyrted_file_list = [
                file_info
                for file_info in checked_file_list
                if "_decrypted" not in file_info.filename
            ]
            for file_info in not_decrpyrted_file_list:
                print("file_info", file_info)
                file_name_p = Path(file_info.filename)
                file_name = file_name_p.name
                # TODO
                # allowed = file_name in allowd_filename_list
                allowed = True
                if allowed:
                    if (
                        file_info.filename.replace(".txt", "_decrypted.txt")
                        in decrpyrted_file_name_list
                    ):
                        print("skip", file_name)
                        continue
                    with measure_zip.open(file_info.filename, mode="r") as f:
                        content = f.read()
                    output_zip_obj.writestr(f"{file_name_p}", content)
            # finally, make decrpyrted files overwrite encrypt files
            for file_info in decrpyrted_file_list:
                print("file_info", file_info)
                file_name_p = Path(file_info.filename)
                file_name = file_name_p.name
                with measure_zip.open(file_info.filename, mode="r") as f:
                    content = f.read()
                encrypted_data = encrypt(
                    settings.TXT_FILE_AES_KEY,
                    settings.TXT_FILE_AES_IV,
                    content,
                )
                output_zip_obj.writestr(
                    f"{file_name_p.parent}/{file_name.replace('_decrypted', '')}",
                    encrypted_data,
                )
                print(
                    "write encrypted:",
                    f"{file_name_p.parent}/{file_name.replace('_decrypted', '')}",
                )

    filep = Path(uploaded_file.name)
    st.download_button(
        label="下載壓縮檔",
        data=output_zip.getvalue(),
        file_name=f"{filep.stem}_encrpyted{filep.suffix}",
    )
