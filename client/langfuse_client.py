"""
Langfuse Client Module
Handles all Langfuse-related operations including:
- Initializing Langfuse client
- Fetching traces for users
- Time range calculations
- Getting all users with traces in time range
"""

import os
from datetime import datetime, timedelta, timezone
from langfuse import get_client
from config import TIME_FILTER_OPTIONS

# Target timezone: UTC+07:00 (consistent with matching_engine)
TARGET_TIMEZONE = timezone(timedelta(hours=7))


def initialize_langfuse_client():
    """Initialize and return Langfuse client"""
    try:
        langfuse_client = get_client()
        return langfuse_client
    except Exception as e:
        print(f"Error initializing Langfuse client: {e}")
        raise


def calculate_time_range(days):
    """
    Calculate start and end timestamps for the given number of days
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        tuple: (from_timestamp, to_timestamp) in ISO format
    """
    end_time = datetime.now(TARGET_TIMEZONE)
    start_time = end_time - timedelta(days=days)
    
    # # Convert to ISO format that Langfuse API expects
    # from_timestamp = start_time.isoformat() + "Z"
    # to_timestamp = end_time.isoformat() + "Z"
    
    return start_time, end_time


def get_all_users_with_traces_in_timerange(langfuse_client, days=1):
    """
    Get all users who have traces within the specified time range
    
    Args:
        langfuse_client: Initialized Langfuse client
        days (int): Number of days to look back
        
    Returns:
        dict: Dictionary with user_id as key and list of traces as value
    """
    from_timestamp, to_timestamp = calculate_time_range(days)
    print(f"Fetching all traces from {from_timestamp} to {to_timestamp}")
    
    users_with_traces = {}
    page = 1
    limit = 50  # Adjust based on your needs
    
    try:
        while True:
            print(f"Fetching traces page {page}...")
            
            # Get traces within time range
            traces_response = langfuse_client.api.trace.list(
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                limit=limit,
                page=page
            )
            
            traces = traces_response.data
            
            if not traces:
                break
            
            # Group traces by user_id
            for trace in traces:
                user_id = trace.user_id
                if user_id:  # Only include traces with user_id
                    if user_id not in users_with_traces:
                        users_with_traces[user_id] = []
                    users_with_traces[user_id].append(trace)
            
            # Check if we got fewer results than the limit (last page)
            if len(traces) < limit:
                break
                
            page += 1
    
    except Exception as e:
        print(f"Error fetching traces: {e}")
        return {}
    
    print(f"Found {len(users_with_traces)} unique users with traces")
    total_traces = sum(len(traces) for traces in users_with_traces.values())
    print(f"Total traces: {total_traces}")
    
    return users_with_traces


def get_langfuse_traces_for_user(langfuse_client, user_id, days=1):
    """
    Get Langfuse traces for a specific user within the specified time range
    
    Args:
        langfuse_client: Initialized Langfuse client
        user_id (str): User ID to fetch traces for
        days (int): Number of days to look back
        
    Returns:
        list: List of trace objects for the user
    """
    from_timestamp, to_timestamp = calculate_time_range(days)
    
    try:
        traces_response = langfuse_client.api.trace.list(
            user_id=user_id,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp
        )
        return traces_response.data
    except Exception as e:
        print(f"Error fetching traces for user {user_id}: {e}")
        return []


def get_time_filter_options():
    """
    Get available time filter options
    
    Returns:
        dict: Dictionary of time filter options
    """
    return TIME_FILTER_OPTIONS


def get_user_time_filter_choice():
    """
    Get user's choice for time filter from interactive input
    
    Returns:
        tuple: (selected_days, selected_name)
    """
    options = get_time_filter_options()
    
    print("\nSelect time filter for Langfuse traces:")
    for key, value in options.items():
        print(f"{key}. {value['name']}")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        if choice in options:
            selected_days = options[choice]["days"]
            selected_name = options[choice]["name"]
            print(f"Selected: {selected_name}")
            return selected_days, selected_name
        else:
            print("Invalid choice. Please select 1-4.")