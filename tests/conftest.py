import gzip
import importlib
import os
import sys
from io import BytesIO
from typing import Generator

import boto3
import pytest
from moto import mock_aws
from mypy_boto3_s3 import S3Client
from tuva import TUVA_SEED_FILES_0_8_6
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
def s3(tuva_s3_bucket: str, target_s3_bucket: str) -> Generator[S3Client, None, None]:
    with mock_aws():
        s3: S3Client = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=tuva_s3_bucket)
        s3.create_bucket(Bucket=target_s3_bucket)

        print("Uploading mock seed data for v0.8.6")
        for s3_key in TUVA_SEED_FILES_0_8_6:
            contents = BytesIO()
            with gzip.GzipFile(fileobj=contents, mode="w") as f:
                # For now, just put the S3 key as the file contents
                f.write(f"{s3_key}\n".encode("utf-8"))
            contents.seek(0)

            s3.upload_fileobj(contents, tuva_s3_bucket, s3_key)
        print("...done uploading mock seed data for v0.8.6")

        yield s3
