"""
Module that contains the command line app.
"""
import argparse
import os
import traceback
import time
import boto3

from botocore.exceptions import ClientError
from label_studio_sdk import Client

LABEL_STUDIO_URL = os.environ["LABEL_STUDIO_URL"]
S3_BUCKET_NAME = os.environ["AWS_S3_BUCKET_NAME"]
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]


def set_cors_configuration():
    """Set a bucket's CORS policies configuration."""

    print("set_cors_configuration()")
    bucket_name = S3_BUCKET_NAME

    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    cors_configuration = {
        "CORSRules": [
                {
                    "AllowedHeaders": [
                    "*"
                    ],
                    "AllowedMethods": [
                    "GET",
                    "PUT",
                    "POST",
                    "DELETE",
                    "HEAD"
                    ],
                    "AllowedOrigins": [
                    "*"
                    ],
                    "ExposeHeaders": [
                    "x-amz-server-side-encryption",
                    "x-amz-request-id",
                    "x-amz-id-2"
                    ],
                    "MaxAgeSeconds": 3600
                }
            ]   
    }
    
    s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_configuration)
    print(f"Set CORS policies for bucket {bucket_name}")


def view_bucket_metadata():
    """Prints out a bucket's metadata."""

    print("view_bucket_metadata()")
    bucket_name = S3_BUCKET_NAME

    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    try:
        # Get the bucket information (head_bucket gives basic metadata)
        bucket_info = s3.head_bucket(Bucket=bucket_name)
        
        # Get the bucket location
        location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        print(f'Location: {location}')
        # Get the bucket policy (if exists)
        try:
            policy = s3.get_bucket_policy(Bucket=bucket_name)['Policy']
            print(f'Policy: {policy}')
        except ClientError:
            policy = None

        # Get the bucket's CORS configuration
        try:
            cors = s3.get_bucket_cors(Bucket=bucket_name)['CORSRules']
            print(f'Cors: {cors}')
        except ClientError:
            cors = None

        # Get bucket versioning status
        versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        versioning_status = versioning.get('Status', 'Disabled')
        print(f'Versioning Status: {versioning_status}')
        # Print bucket metadata
        print(f"Name: {bucket_name}")
        print(f"Location: {location}")
        print(f"Policy: {policy}")
        print(f"CORS: {cors}")
        print(f"Versioning Status: {versioning_status}")
        print(f"Creation Date: {bucket_info['ResponseMetadata']['HTTPHeaders']['date']}")

    except ClientError as e:
        print(f"Error getting metadata for bucket {bucket_name}: {e}")

def get_projects(api_key):
    print("get_projects")

    # Examples using SDK: https://labelstud.io/sdk/project.html#label_studio_sdk.project.Project
    label_studio_client = Client(url=LABEL_STUDIO_URL, api_key=api_key)
    label_studio_client.check_connection()

    projects = label_studio_client.get_projects()
    print(projects)
    for project in projects:
        print(project.id, project.title, project.description)

    project = label_studio_client.get_project(1)
    print(project)


def get_project_tasks(api_key):
    print("get_project_tasks")

    # Examples using SDK: https://labelstud.io/sdk/project.html#label_studio_sdk.project.Project
    label_studio_client = Client(url=LABEL_STUDIO_URL, api_key=api_key)
    label_studio_client.check_connection()

    projects = label_studio_client.get_projects()
    project_id = projects[0].id
    project = label_studio_client.get_project(project_id)
    print(project)
    # print(project.get_tasks())
    print("Number of tasks:", len(project.tasks))

    labeled_tasks = project.get_labeled_tasks()
    print("Number of labeled tasks:", len(labeled_tasks))
    for labeled_task in labeled_tasks:
        print("Annotations:", labeled_task["annotations"])


def main(args=None):
    if args.cors:
        set_cors_configuration()

    if args.metadata:
        view_bucket_metadata()

    if args.projects or args.tasks:
        if args.key == "":
            parser.error("-k argument i required for API access to LABEL Studio")

    if args.projects:
        get_projects(args.key)

    if args.tasks:
        get_project_tasks(args.key)


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Data Labeling CLI")

    parser.add_argument(
        "-c",
        "--cors",
        action="store_true",
        help="Set the CORS configuration on a GCS bucket",
    )
    parser.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="View the CORS configuration for a bucket",
    )
    parser.add_argument(
        "-p", "--projects", action="store_true", help="List projects in Label studio"
    )
    parser.add_argument(
        "-t", "--tasks", action="store_true", help="View tasks from a project"
    )
    parser.add_argument("-k", "--key", default="", help="Label Studio API Key")

    args = parser.parse_args()

    main(args)
