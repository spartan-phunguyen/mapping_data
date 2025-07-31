import boto3
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

# Create an S3 client
session = boto3.Session()

# session = boto3.Session()
credentials = session.get_credentials()
print("Access Key:", credentials.access_key)
print("Secret Key:", credentials.secret_key)

s3 = session.client(
    's3',
    region_name=os.getenv("AWS_REGION")
)

# ✅ Example: List all buckets
# buckets = s3.list_buckets()
# for b in buckets['Buckets']:
#     print(f"{b['Name']}")

bucket_name = "service-dietfit-20250526115059333100000001"
prefix = "meal-images/"

# Paginated listing to get all objects
paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

print(f"🗂 Listing all objects under: {prefix}\n")
for page in pages:
    print(len(page))
    print(len(page["Contents"]))
    # if "Contents" in page:
    #     for obj in page["Contents"]:
    #         print(obj["Key"])

def get_public_url(bucket: str, region: str, key: str) -> str:
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

print(get_public_url(
    "service-dietfit-20250526115059333100000001",
    "us-west-2",
    "meal-images/0025fd1f-f5b7-4dcb-8c3e-68f8bd409e46/3e6180c7-e96d-492a-9612-19ae34cedd52.jpg"
))