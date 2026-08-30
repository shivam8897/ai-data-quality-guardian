import re
import pandas as pd
from sqlalchemy import create_engine
from typing import Dict, Any

from .csv_profiler import profile_dataframe

# Table/column identifiers only — blocks injection via a crafted table_name
_VALID_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def profile_table(connection_string: str, table_name: str, sample_rows: int = None) -> Dict[str, Any]:
    """
    Profile a database table by loading it into a DataFrame and reusing the
    same profiling logic as the CSV profiler.

    connection_string: a SQLAlchemy-compatible URL (e.g. postgresql://user:pass@host/db)
    table_name: the table to profile
    sample_rows: optionally cap the number of rows pulled (useful for large tables)
    """
    if not _VALID_IDENTIFIER.match(table_name):
        raise ValueError(f"Invalid table name: {table_name!r}")

    engine = create_engine(connection_string)
    try:
        query = f'SELECT * FROM "{table_name}"'
        if sample_rows:
            query += f" LIMIT {int(sample_rows)}"

        df = pd.read_sql(query, engine)
    finally:
        engine.dispose()

    result = profile_dataframe(df)
    result["source_table"] = table_name
    return result
