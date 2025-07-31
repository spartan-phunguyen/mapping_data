"""
Matching Engine Module
Handles the core logic for matching S3 meal images with Langfuse traces
Contains the main business logic for the application
New Flow: Start with Langfuse users who have traces, then match with S3 images
Enhanced: 1-to-1 trace-to-image matching based on closest timestamps
"""

from client.s3_client import get_s3_meal_images_by_user
from client.langfuse_client import get_all_users_with_traces_in_timerange
from config import S3_BUCKET_NAME
from datetime import datetime, timezone, timedelta

# Target timezone: UTC+07:00
TARGET_TIMEZONE = timezone(timedelta(hours=7))

def parse_datetime_safe(dt):
    """
    Safely parse various datetime formats to Python datetime object
    
    Args:
        dt: DateTime object (can be Python datetime, Langfuse datetime, string, or None)
        
    Returns:
        datetime: Parsed datetime object or None if parsing fails
    """
    if dt is None:
        return None
    
    try:
        parsed_dt = None
        
        # If it's already a Python datetime
        if isinstance(dt, datetime):
            parsed_dt = dt
            
        # If it's a string, try parsing ISO format
        elif isinstance(dt, str):
            # Remove 'Z' and parse
            dt_str = dt.replace('Z', '+00:00') if dt.endswith('Z') else dt
            parsed_dt = datetime.fromisoformat(dt_str)
        
        # If it has isoformat method (Langfuse datetime)
        elif hasattr(dt, 'isoformat'):
            dt_str = dt.isoformat()
            dt_str = dt_str.replace('Z', '+00:00') if dt_str.endswith('Z') else dt_str
            parsed_dt = datetime.fromisoformat(dt_str)
        
        # Try parsing string representation
        else:
            parsed_dt = datetime.fromisoformat(str(dt))
        
        # Convert to target timezone (UTC+07:00)
        if parsed_dt:
            if parsed_dt.tzinfo is None:
                # If naive datetime, assume UTC
                parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
            # Convert to target timezone
            return parsed_dt.astimezone(TARGET_TIMEZONE)
            
        return None
        
    except Exception:
        return None


def match_traces_to_images_by_timestamp(traces, images):
    """
    Match individual images to individual traces based on closest timestamp
    Rule: Trace timestamp must be < image timestamp, find closest match
    Optimized for fewer images than traces
    
    Args:
        traces (list): List of trace objects
        images (list): List of image data dictionaries
        
    Returns:
        tuple: (matched_pairs, unused_traces, unmatched_images)
    """
    if not traces or not images:
        return [], traces[:], images[:]
    
    # Parse and sort traces by timestamp
    trace_with_time = []
    for trace in traces:
        trace_time = parse_datetime_safe(trace.createdAt)
        if trace_time:
            trace_with_time.append((trace, trace_time))
    
    # Parse and sort images by timestamp
    image_with_time = []
    for image in images:
        image_time = parse_datetime_safe(image['last_modified'])
        if image_time:
            image_with_time.append((image, image_time))
    
    # Sort by timestamp
    trace_with_time.sort(key=lambda x: x[1])
    image_with_time.sort(key=lambda x: x[1], reverse=True)
    
    matched_pairs = []
    used_trace_indices = set()
    unmatched_images = []
    
    # For each image, find the best matching trace (closest preceding trace)
    for image, image_time in image_with_time:
        best_match = None
        best_match_index = None
        latest_trace_time = None
        
        for i, (trace, trace_time) in enumerate(trace_with_time):
            if i in used_trace_indices:
                continue
                
            if trace_time >= image_time and abs((trace_time - image_time).total_seconds()) < 60:
                # Find the trace with the LATEST timestamp that is still before image
                if (latest_trace_time is None) or (trace_time < latest_trace_time):
                    latest_trace_time = trace_time
                    best_match = trace
                    best_match_index = i
        
        # If we found a match
        if best_match is not None:
            time_diff = (image_time - latest_trace_time).total_seconds()
            matched_pairs.append({
                'image': image,
                'trace': best_match,
                'image_timestamp': image_time,
                'trace_timestamp': latest_trace_time,
                'time_difference_seconds': time_diff
            })
            used_trace_indices.add(best_match_index)
        else:
            unmatched_images.append(image)
    
    # Get unused traces
    unused_traces = [trace for i, (trace, _) in enumerate(trace_with_time) 
                    if i not in used_trace_indices]
    
    return matched_pairs, unused_traces, unmatched_images


def get_s3_images_for_user(user_images_dict, user_id):
    """
    Get S3 images for a specific user from the pre-fetched images dictionary
    
    Args:
        user_images_dict (dict): Dictionary of all user images from S3
        user_id (str): User ID to get images for
        
    Returns:
        list: List of image data for the user, empty list if no images found
    """
    return user_images_dict.get(user_id, [])


def match_images_with_traces(s3_client, langfuse_client, time_filter_days, bucket_name=S3_BUCKET_NAME):
    """
    Main function to match S3 meal images with Langfuse traces by user_id
    Enhanced with 1-to-1 trace-to-image matching based on timestamps
    
    Args:
        s3_client: Initialized S3 client
        langfuse_client: Initialized Langfuse client  
        time_filter_days (int): Number of days to filter traces
        bucket_name (str): S3 bucket name
        
    Returns:
        tuple: (successful_matches, users_without_counterpart)
    """
    print("Starting Langfuse to S3 matching process...")
    print("=" * 60)
    
    # Step 1: Get all users with traces in time range
    print(f"Fetching users with traces from past {time_filter_days} day(s)...")
    users_with_traces = get_all_users_with_traces_in_timerange(langfuse_client, time_filter_days)
    
    if not users_with_traces:
        print("No users with traces found in the specified time range")
        return [], []
    
    print(f"Found {len(users_with_traces)} users with traces")
    
    # Step 2: Get all S3 images (we'll filter by user later)
    print("Fetching S3 meal images...")
    user_images_dict = get_s3_meal_images_by_user(s3_client, bucket_name)
    
    successful_matches = []
    users_without_counterpart = []
    
    # Step 3: For each user with traces, try to match with their S3 images
    for user_id, user_traces in users_with_traces.items():
        print(f"\nProcessing user: {user_id}")
        print(f"Found {len(user_traces)} traces (timezone normalized to UTC+07:00)")
        
        # Get S3 images for this user
        user_images = get_s3_images_for_user(user_images_dict, user_id)
        
        if user_images:
            print(f"Found {len(user_images)} images")
            
            # Perform sophisticated 1-to-1 matching
            matched_pairs, unused_traces, unmatched_images = match_traces_to_images_by_timestamp(
                user_traces, user_images
            )
            
            print(f"Matched {len(matched_pairs)} image-trace pairs")
            if unused_traces:
                print(f"{len(unused_traces)} traces not matched to images")
            if unmatched_images:
                print(f"{len(unmatched_images)} images without matching traces")
            
            # Create enhanced match data
            match_data = create_enhanced_match_data(
                user_id, user_traces, user_images, matched_pairs, 
                unused_traces, unmatched_images
            )
            successful_matches.append(match_data)
        else:
            print("No images found")
            no_counterpart_data = create_no_counterpart_data(user_id, user_traces, 'images')
            users_without_counterpart.append(no_counterpart_data)
    
    return successful_matches, users_without_counterpart


def create_enhanced_match_data(user_id, traces, images, matched_pairs, unused_traces, unmatched_images):
    """Create enhanced match data structure with detailed image-to-trace matching"""
    return {
        'user_id': user_id,
        'traces': traces,
        'images': images,
        'matched_pairs': matched_pairs,
        'unused_traces': unused_traces,
        'unmatched_images': unmatched_images,
        'trace_count': len(traces),
        'image_count': len(images),
        'matched_pairs_count': len(matched_pairs),
        'match_efficiency': len(matched_pairs) / max(len(traces), len(images)) if traces and images else 0
    }


def create_no_counterpart_data(user_id, data_list, missing_type):
    """Create a standardized no-counterpart data structure"""
    if missing_type == 'images':
        return {
            'user_id': user_id,
            'traces': data_list,
            'trace_count': len(data_list),
            'missing_type': missing_type
        }
    else:  # missing traces
        return {
            'user_id': user_id,
            'images': data_list,
            'image_count': len(data_list),
            'missing_type': missing_type
        }


def get_matching_statistics(successful_matches, users_without_counterpart):
    """Calculate statistics from matching results"""
    total_users = len(successful_matches) + len(users_without_counterpart)
    total_traces = sum(match['trace_count'] for match in successful_matches)
    total_traces += sum(user.get('trace_count', 0) for user in users_without_counterpart)
    total_images = sum(match['image_count'] for match in successful_matches)
    total_images += sum(user.get('image_count', 0) for user in users_without_counterpart)
    total_matched_pairs = sum(match['matched_pairs_count'] for match in successful_matches)

    return {
        'total_users': total_users,
        'users_with_matches': len(successful_matches),
        'users_without_counterpart': len(users_without_counterpart),
        'total_traces': total_traces,
        'total_images': total_images,
        'total_matched_pairs': total_matched_pairs,
        'match_rate': len(successful_matches) / total_users * 100 if total_users > 0 else 0,
        'pair_match_efficiency': total_matched_pairs / max(total_traces, total_images) * 100 if total_traces and total_images else 0
    } 