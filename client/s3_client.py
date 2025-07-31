"""
S3 Client Module
Handles all S3-related operations including:
- Initializing S3 client
- Fetching meal images
- Extracting user IDs from S3 keys
- Generating public URLs
"""

import boto3
from collections import defaultdict
from config import S3_BUCKET_NAME, S3_PREFIX, AWS_REGION


def initialize_s3_client():
    """Initialize and return S3 client"""
    try:
        session = boto3.Session()
        s3_client = session.client('s3', region_name=AWS_REGION)
        return s3_client
    except Exception as e:
        print(f"Error initializing S3 client: {e}")
        raise


def extract_user_id_from_s3_key(object_key, prefix=S3_PREFIX):
    """
    Extract user_id from S3 object key
    Expected format: meal-images/{user_id}/{filename}
    
    Args:
        object_key (str): S3 object key
        prefix (str): S3 prefix to remove
        
    Returns:
        str or None: user_id if found, None otherwise
    """
    if not object_key.startswith(prefix):
        return None
    
    # Remove the prefix to get the remaining path
    path_after_prefix = object_key[len(prefix):]
    
    # Split by '/' and get the first part (user_id)
    path_parts = path_after_prefix.split('/')
    if len(path_parts) >= 2:  # Should have user_id/filename.jpg
        return path_parts[0]
    
    return None


def generate_s3_public_url(bucket_name, object_key):
    """
    Generate public URL for S3 object
    
    Args:
        bucket_name (str): S3 bucket name
        object_key (str): S3 object key
        
    Returns:
        str: Public URL for the S3 object
    """
    return f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{object_key}"


def get_s3_meal_images_by_user(s3_client, bucket_name=S3_BUCKET_NAME, prefix=S3_PREFIX):
    """
    Fetch all meal images from S3 and group them by user_id
    
    Args:
        s3_client: Initialized S3 client
        bucket_name (str): S3 bucket name
        prefix (str): S3 prefix to search under
        
    Returns:
        dict: Dictionary with user_id as key and list of image data as value
    """
    print(f"Fetching S3 objects from bucket: {bucket_name}")
    print(f"Using prefix: {prefix}")
    
    # Use paginator to handle large number of objects efficiently
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    user_images = defaultdict(list)
    total_image_count = 0
    
    for page in pages:
        if "Contents" not in page:
            continue
            
        for s3_object in page["Contents"]:
            object_key = s3_object["Key"]
            
            # Skip directory entries
            if object_key.endswith('/'):
                continue
            
            user_id = extract_user_id_from_s3_key(object_key, prefix)
            if user_id:
                image_data = {
                    'key': object_key,
                    'size': s3_object.get('Size', 0),
                    'last_modified': s3_object.get('LastModified'),
                    'public_url': generate_s3_public_url(bucket_name, object_key)
                }
                user_images[user_id].append(image_data)
                total_image_count += 1
    
    print(f"Found {total_image_count} images for {len(user_images)} unique users")
    return user_images 