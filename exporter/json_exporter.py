"""
JSON Exporter Module
Handles exporting matching results to JSON files including:
- Formatting data for JSON export
- Converting datetime objects to strings
- Creating structured export files
- Generating timestamped filenames
Updated to handle both old and new flow structures
"""

import json
from datetime import datetime, timezone, timedelta
from util.matching_engine import get_matching_statistics

# Target timezone: UTC+07:00 (same as matching_engine)
TARGET_TIMEZONE = timezone(timedelta(hours=7))


def safe_datetime_to_string(dt):
    """
    Safely convert various datetime types to UTC+7 ISO string format
    
    Args:
        dt: DateTime object (can be Python datetime, Langfuse datetime, string, or None)
        
    Returns:
        str: ISO formatted datetime string in UTC+7 timezone or None
    """
    if dt is None:
        return None
    
    try:
        parsed_dt = None
        
        # If it's already a string, try to parse it first
        if isinstance(dt, str):
            # Skip if it's already an ISO string, but try to normalize timezone
            if dt.endswith('Z'):
                dt = dt.replace('Z', '+00:00')
            try:
                parsed_dt = datetime.fromisoformat(dt)
            except:
                return dt  # Return original string if can't parse
        
        # If it's already a Python datetime
        elif isinstance(dt, datetime):
            parsed_dt = dt
            
        # If it has isoformat method (Langfuse datetime)
        elif hasattr(dt, 'isoformat'):
            dt_str = dt.isoformat()
            dt_str = dt_str.replace('Z', '+00:00') if dt_str.endswith('Z') else dt_str
            parsed_dt = datetime.fromisoformat(dt_str)
        
        # Try parsing string representation
        else:
            parsed_dt = datetime.fromisoformat(str(dt))
        
        # Normalize to UTC+7 timezone and return ISO format
        if parsed_dt:
            if parsed_dt.tzinfo is None:
                # If naive datetime, assume UTC
                parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
            # Convert to target timezone and return ISO format
            normalized_dt = parsed_dt.astimezone(TARGET_TIMEZONE)
            return normalized_dt.isoformat()
        
        return None
        
    except Exception:
        # Fallback: return string representation or None
        return str(dt) if dt else None


def prepare_image_data_for_export(image_data):
    """
    Prepare image data for JSON serialization
    
    Args:
        image_data (dict): Image data dictionary
        
    Returns:
        dict: JSON-serializable image data
    """
    return {
        "key": image_data['key'],
        "size": image_data['size'],
        "last_modified": safe_datetime_to_string(image_data['last_modified']),
        "public_url": image_data['public_url']
    }


def prepare_trace_data_for_export(trace_data):
    """
    Prepare trace data for JSON serialization
    
    Args:
        trace_data: Langfuse trace object
        
    Returns:
        dict: JSON-serializable trace data
    """
    return {
        "id": trace_data.id,
        "name": trace_data.name,
        "created_at": safe_datetime_to_string(trace_data.createdAt),
        "user_id": getattr(trace_data, 'user_id', None)
    }


def prepare_matched_pair_for_export(pair_data):
    """
    Prepare matched image-trace pair for JSON serialization
    
    Args:
        pair_data (dict): Matched pair data
        
    Returns:
        dict: JSON-serializable matched pair data
    """
    return {
        "image": prepare_image_data_for_export(pair_data['image']),
        "trace": prepare_trace_data_for_export(pair_data['trace']),
        "image_timestamp": safe_datetime_to_string(pair_data['image_timestamp']),
        "trace_timestamp": safe_datetime_to_string(pair_data['trace_timestamp']),
        "time_difference_seconds": pair_data['time_difference_seconds'],
        "time_difference_minutes": round(pair_data['time_difference_seconds'] / 60, 2)
    }


def prepare_enhanced_match_data_for_export(match_data):
    """
    Prepare enhanced match data for JSON serialization
    
    Args:
        match_data (dict): Enhanced match data with pairs, unused traces, unmatched images
        
    Returns:
        dict: JSON-serializable enhanced match data
    """
    return {
        "user_id": match_data['user_id'],
        "trace_count": match_data['trace_count'],
        "image_count": match_data['image_count'],
        "matched_pairs_count": match_data['matched_pairs_count'],
        "match_efficiency": round(match_data['match_efficiency'] * 100, 2),  # Convert to percentage
        "matched_pairs": [prepare_matched_pair_for_export(pair) for pair in match_data.get('matched_pairs', [])],
        "unused_traces": [prepare_trace_data_for_export(trace) for trace in match_data.get('unused_traces', [])],
        "unmatched_images": [prepare_image_data_for_export(img) for img in match_data.get('unmatched_images', [])]
    }


def prepare_no_counterpart_data_for_export(no_counterpart_data):
    """
    Prepare no-counterpart user data for JSON serialization
    
    Args:
        no_counterpart_data (dict): User data without counterpart
        
    Returns:
        dict: JSON-serializable no-counterpart data
    """
    base_data = {
        "user_id": no_counterpart_data['user_id'],
        "missing_type": no_counterpart_data.get('missing_type', 'unknown')
    }
    
    # Add traces if present (user has traces but no images)
    if 'traces' in no_counterpart_data:
        base_data.update({
            "trace_count": no_counterpart_data['trace_count'],
            "traces": [prepare_trace_data_for_export(trace) for trace in no_counterpart_data['traces']]
        })
    
    # Add images if present (user has images but no traces) - for backward compatibility
    if 'images' in no_counterpart_data:
        base_data.update({
            "image_count": no_counterpart_data['image_count'],
            "images": [prepare_image_data_for_export(img) for img in no_counterpart_data['images']]
        })
    
    return base_data


def create_export_data_structure(matches, no_counterpart_users, time_filter_name):
    """Create the complete enhanced data structure for JSON export"""
    stats = get_matching_statistics(matches, no_counterpart_users)

    export_data = {
        "metadata": {
            "export_timestamp": datetime.now(TARGET_TIMEZONE).isoformat(),
            "time_filter": time_filter_name,
            "application_version": "2.0.0",  # Updated version for enhanced matching
            "export_type": "enhanced_meal_mapping_results",
            "matching_algorithm": "1-to-1 trace-to-image timestamp matching"
        },
        "summary": {
            "total_users": stats['total_users'],
            "users_with_matches": stats['users_with_matches'],
            "users_without_counterpart": stats['users_without_counterpart'],
            "total_traces": stats['total_traces'],
            "total_images": stats['total_images'],
            "total_matched_pairs": stats['total_matched_pairs'],
            "match_rate_percentage": round(stats['match_rate'], 2),
            "pair_match_efficiency_percentage": round(stats['pair_match_efficiency'], 2)
        },
        "enhanced_matches": [prepare_enhanced_match_data_for_export(match) for match in matches],
        "users_without_counterpart": [prepare_no_counterpart_data_for_export(user_data) for user_data in no_counterpart_users]
    }

    return export_data


def generate_export_filename():
    """Generate a timestamped filename for export in results/json/ directory"""
    import os
    
    # Create results/json directory if it doesn't exist
    json_dir = os.path.join("results", "json")
    os.makedirs(json_dir, exist_ok=True)
    
    timestamp = datetime.now(TARGET_TIMEZONE).strftime("%Y%m%d_%H%M%S")
    filename = f"enhanced_meal_mapping_results_{timestamp}.json"
    return os.path.join(json_dir, filename)


def export_results_to_json(matches, no_counterpart_users, time_filter_name, filename=None):
    """
    Export matching results to a JSON file
    
    Args:
        matches (list): List of successful matches
        no_counterpart_users (list): List of users without matching counterpart
        time_filter_name (str): Name of the time filter used
        filename (str, optional): Custom filename. If None, generates timestamped filename
        
    Returns:
        tuple: (success_bool, filename, error_message)
    """
    try:
        # Generate filename if not provided
        if filename is None:
            filename = generate_export_filename()
        else:
            # Ensure custom filename is saved in results/json directory
            import os
            json_dir = os.path.join("results", "json")
            os.makedirs(json_dir, exist_ok=True)
            if not filename.startswith(json_dir):
                filename = os.path.join(json_dir, os.path.basename(filename))
        
        # Create the export data structure
        export_data = create_export_data_structure(matches, no_counterpart_users, time_filter_name)
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Results exported to: {filename}")
        print(f"Export contains:")
        print(f"  - {len(matches)} users with matches")
        print(f"  - {len(no_counterpart_users)} users without counterpart")
        print(f"  - Total of {export_data['summary']['total_images']} images")
        print(f"  - Total of {export_data['summary']['total_traces']} traces")
        print(f"  - Total of {export_data['summary']['total_matched_pairs']} matched pairs")

        return True, filename, None

    except Exception as e:
        error_message = f"Error exporting to JSON: {e}"
        print(error_message)
        return False, filename, error_message


def load_results_from_json(filename):
    """
    Load previously exported results from JSON file
    
    Args:
        filename (str): JSON file to load
        
    Returns:
        tuple: (success, data, error_message)
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Successfully loaded results from: {filename}")
        
        # Display loaded data summary
        if 'summary' in data:
            summary = data['summary']
            print(f"Loaded data contains:")
            print(f"  - {summary.get('users_with_matches', 0)} users with matches")
            print(f"  - {summary.get('users_without_matches', 0)} users without matches")
            print(f"  - {summary.get('total_images', 0)} total images")
            print(f"  - {summary.get('total_traces', 0)} total traces")
            
            if 'metadata' in data and 'flow_type' in data['metadata']:
                print(f"  - Flow type: {data['metadata']['flow_type']}")
        
        return True, data, None
        
    except FileNotFoundError:
        error_message = f"File not found: {filename}"
        print(error_message)
        return False, None, error_message
        
    except json.JSONDecodeError as e:
        error_message = f"Invalid JSON format: {e}"
        print(error_message)
        return False, None, error_message
        
    except Exception as e:
        error_message = f"Error loading JSON file: {e}"
        print(error_message)
        return False, None, error_message


def validate_export_data(data):
    """
    Validate the structure of export data
    
    Args:
        data (dict): Export data to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_keys = ['metadata', 'summary', 'successful_matches', 'users_without_matches']
    
    for key in required_keys:
        if key not in data:
            return False, f"Missing required key: {key}"
    
    if not isinstance(data['successful_matches'], list):
        return False, "successful_matches must be a list"
    
    if not isinstance(data['users_without_matches'], list):
        return False, "users_without_matches must be a list"
    
    return True, None 