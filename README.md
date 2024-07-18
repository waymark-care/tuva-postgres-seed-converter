# Tuva Health Seed Data Converter for Postgres

This script will create a postgres-friendly format of the Tuva Health seed data, copying it from the source bucket into a bucket of your choosing. This can be used in conjunction with the custom postgres implementation of the [load_seed](https://github.com/tuva-health/tuva/blob/main/macros/load_seed.sql) macro in the tuva project to load data into a postgres database.

To start with run `python s3-to-s3.py --help` to see the available options.

Here's a quickstart command that will download the v0.10.0 Tuva Health seed data to a local directory and load it into a bucket named "my-company-tuva-data"

    python s3-to-s3.py my-company-tuva-data --tmp-dir ./tuva-seed-data-v0.10.0/ --tuva-version v0.10.0


> **NOTE**: you can pass any valid git tag/branch/sha for the version in case you need to test this against a non-released version of the `dbt_project.yml` file.

## Setup

This project uses [direnv](https://direnv.net/), [pyenv](https://github.com/pyenv/pyenv), and [poetry](https://python-poetry.org/). The first two are optional, but poetry is not and is used to setup your python virtual environment as well as installing dependencies. All commands in this readme assume you're using a ~3.12 version of python and have activated your virtual env. The following commands should do it:

    poetry install
    poetry shell

From there, you can run some of the commands (particularly around formatting, linting, etc) using [poe the poet](https://poethepoet.natn.io/index.html) commands. You can run all of the "ci" checks via

    poe ci

## AWS Setup and Next Steps (dbt + tuva)

In order to use this script, you'll need an AWS S3 bucket setup where you can write data to as well as have your local environment setup so boto3 can authenticate and write to that S3 bucket. Refer to the AWS and boto3 documentation for more details here.

Once the script has loaded the data into S3, you'll need to setup access to the S3 Bucket from dbt. This is done via the `aws_s3` RDS postgres extension. You'll also need to setup authentication to the S3 bucket. The easiest way to do this is to create an IAM Role and attach it to your RDS instance/cluster, but you can also create an Access Key/Secret Key pair. Here's some links that may be helpful:

* [AWS Docs on IAM and RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAM.html)
* [aws_s3 postgres extension docs](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_PostgreSQL.S3Import.html)

## Changes to the seed data

Curious about what changes were made to the seed data? Here's an outline:

* Consolidate all multi-part seed data files into a single file with an `_0` suffix to work around `aws_s3` not supporting wildcards.
* Remove the quotes around null markers (`"\N"` ➡️ `\N`) to deal with a Postgres limitation on custom null markers and quotes.
* Add `Content-Type` and `Content-Encoding` headers to the S3 objects because `aws_s3` relies on this to know to decompress the csv before processing.
