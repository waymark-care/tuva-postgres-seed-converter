from gzip import GzipFile
from io import BytesIO
from pathlib import Path
import pytest
import botocore
from mypy_boto3_s3 import S3Client
from pytest import fail
from typer import Typer
from typer.testing import CliRunner

# this is the current version of tuva that this test will run against
VERSION = "0.13.0"


# pragma: no cover
def assert_does_not_exist(s3: S3Client, bucket: str, key: str) -> None:
    try:
        s3.head_object(Bucket=bucket, Key=key)
        fail(f"Object {key} exists in {bucket}")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            pass
        else:
            raise


# pragma: no cover
def assert_exists(s3: S3Client, bucket: str, key: str, contents: str) -> None:
    bytes = BytesIO()
    s3.download_fileobj(Bucket=bucket, Key=key, Fileobj=bytes)
    bytes.seek(0)
    actual_contents = None
    with GzipFile(fileobj=bytes, mode="r") as f:
        actual_contents = f.read().decode("utf-8").strip()
    assert actual_contents == contents


# pragma: no cover
def assert_headers(s3: S3Client, bucket: str, key: str) -> None:
    head = s3.head_object(Bucket=bucket, Key=key)
    assert head["ContentType"] == "text/csv"
    assert head["ContentEncoding"] == "gzip"


# pragma: no cover
def test_help(app: Typer, runner: CliRunner) -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage: s3-to-s3" in result.stdout


@pytest.mark.parametrize("s3", [VERSION], indirect=True)
def test_sync(
    app: Typer, runner: CliRunner, s3: S3Client, target_s3_bucket: str, tmp_path: Path
) -> None:
    # Make sure a few files we copy over do not exist yet
    assert_does_not_exist(
        s3,
        target_s3_bucket,
        f"versioned_value_sets/{VERSION}/tuva_clinical_concepts.csv_0.csv.gz",
    )
    assert_does_not_exist(
        s3, target_s3_bucket, f"versioned_terminology/{VERSION}/calendar.csv_0.csv.gz"
    )
    assert_does_not_exist(
        s3,
        target_s3_bucket,
        f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_0.csv.gz",
    )

    result = runner.invoke(
        app,
        [target_s3_bucket, f"--tuva-version=v{VERSION}", f"--tmp-dir={str(tmp_path)}"],
    )
    print(result.stdout)
    assert result.exit_code == 0

    assert_exists(
        s3,
        target_s3_bucket,
        f"versioned_value_sets/{VERSION}/tuva_clinical_concepts.csv_0.csv.gz",
        f"versioned_value_sets/{VERSION}/tuva_clinical_concepts.csv_0_0_0.csv.gz",
    )
    assert_headers(
        s3,
        target_s3_bucket,
        f"versioned_value_sets/{VERSION}/tuva_clinical_concepts.csv_0.csv.gz",
    )
    assert_exists(
        s3,
        target_s3_bucket,
        f"versioned_terminology/{VERSION}/calendar.csv_0.csv.gz",
        f"versioned_terminology/{VERSION}/calendar.csv_0_0_0.csv.gz",
    )
    assert_headers(
        s3, target_s3_bucket, f"versioned_terminology/{VERSION}/calendar.csv_0.csv.gz"
    )
    expected = "\n".join(
        [
            f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_0_1_0.csv.gz",
            f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_0_2_0.csv.gz",
            f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_0_3_0.csv.gz",
            f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_1_3_0.csv.gz",
            f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_2_2_0.csv.gz",
            f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_3_1_0.csv.gz",
            f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_3_3_0.csv.gz",
            f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_4_1_0.csv.gz",
        ]
    )
    assert_exists(
        s3,
        target_s3_bucket,
        f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_0.csv.gz",
        expected,
    )
    assert_headers(
        s3,
        target_s3_bucket,
        f"versioned_provider_data/{VERSION}/other_provider_taxonomy.csv_0.csv.gz",
    )
