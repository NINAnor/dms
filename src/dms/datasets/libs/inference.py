import duckdb


def to_tabular_resource(column):
    match column["column_type"]:
        case "VARCHAR":
            col_type = "string"
        case "DOUBLE":
            col_type = "double"
        case "BIGINT":
            col_type = "integer"
        case _:
            col_type = "string"

    return {
        "name": column["column_name"],
        "type": col_type,
        "required": column["null"] == "FALSE",
        "default": column["default"],
    }


def duckdb_inference(path: str):
    conn = duckdb.connect()
    conn.sql("set memory_limit = '250MB'")
    table = conn.sql(f"describe from '{path}'").to_arrow_table()
    return list(map(to_tabular_resource, table.to_pylist()))
