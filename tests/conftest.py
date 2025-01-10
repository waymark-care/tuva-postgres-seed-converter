import gzip
import importlib
import os
import sys
from io import BytesIO
from typing import Generator, Any
import boto3
import pytest
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from tuva import TUVA_SEED_FILES_0_8_6, TUVA_SEED_FILES_0_13_0
from typer import Typer
from typer.testing import CliRunner


@pytest.fixture(scope="session")
def app() -> Typer:
    # Update the import path so we can import it
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parentdir)

    main = importlib.import_module("s3-to-s3")
    return main.app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def tuva_s3_bucket() -> str:
    return "tuva-public-resources"


@pytest.fixture
def target_s3_bucket() -> str:
    return "wm-tuva-resources-testing"


@pytest.fixture
def s3(
    tuva_s3_bucket: str, target_s3_bucket: str, request: Any
) -> Generator[S3Client, None, None]:
    version = request.param
    print(f"Using version {version}")

    if version == "0.8.6":
        seed_files = TUVA_SEED_FILES_0_8_6  # pragma: no cover
    elif version == "0.13.0":
        seed_files = TUVA_SEED_FILES_0_13_0  # pragma: no cover
    else:
        raise ValueError(f"Unknown version {version}")  # pragma: no cover

    with mock_aws():
        s3: S3Client = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=tuva_s3_bucket)
        s3.create_bucket(Bucket=target_s3_bucket)

        print(f"Uploading mock seed data for v{version}")
        for s3_key in seed_files:
            contents = BytesIO()
            with gzip.GzipFile(fileobj=contents, mode="w") as f:
                # For now, just put the S3 key as the file contents
                f.write(f"{s3_key}\n".encode("utf-8"))
            contents.seek(0)

            s3.upload_fileobj(contents, tuva_s3_bucket, s3_key)
            print(f"...done uploading mock seed data for v{version} {s3_key}")

        yield s3
