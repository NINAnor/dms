from ..inference import duckdb_inference


def test_duckdb_schema_inference():
    for col in duckdb_inference(
        "https://s3-int-1.nina.no/miljodata-test/ipt/datasets/vanndata_ovrige.parquet"
    ):
        assert col["name"] is not None
        assert col["type"] is not None
        assert col["required"] is not None
