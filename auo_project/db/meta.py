from sqlmodel import SQLModel

meta = SQLModel.metadata
# postgresql naming convention
meta.naming_convention = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
