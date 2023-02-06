from subprocess import check_output

import sqlmodel

filepath = sqlmodel.main.__file__
annotation = " # ref: https://github.com/tiangolo/sqlmodel/pull/256"
cmd = f"""sed -i'' -e 's|config = getattr(base, "__config__")|config = getattr(base, "__config__", None){annotation}|' {filepath}"""
print(cmd)
result = check_output(cmd, shell=True)
print("patch sqlmodel finished.")
