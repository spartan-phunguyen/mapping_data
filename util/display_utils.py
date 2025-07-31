"""
Display Utilities Module
Handles all display and formatting functions including:
- Formatting dates and strings
- Displaying summary results
- Showing detailed user information
- Console output formatting
Updated for new flow: traces without images
"""

from datetime import datetime, timezone, timedelta
from config import TABLE_WIDTH, USER_ID_DISPLAY_WIDTH, MAX_DISPLAY_ITEMS
from util.matching_engine import get_matching_statistics

# Target timezone: UTC+07:00 (consistent with matching_engine)
TARGET_TIMEZONE = timezone(timedelta(hours=7))


def truncate_string(text, max_length):
    """
    Truncate string if it's longer than max_length
    
    Args:
        text (str): String to truncate
        max_length (int): Maximum length allowed
        
    Returns:
        str: Truncated string with ellipsis if needed
    """
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text


def format_datetime(dt):
    """
    Format datetime object to readable string in UTC+7 timezone
    Handles various datetime types including Langfuse datetime objects
    
    Args:
        dt: DateTime object (can be Python datetime, Langfuse datetime, or string)
        
    Returns:
        str: Formatted datetime string in UTC+7 timezone or "N/A" if invalid
    """
    if dt is None:
        return "N/A"
    
    try:
        parsed_dt = None
        
        # If it's already a string, try to parse it
        if isinstance(dt, str):
            if 'T' in dt:
                dt_str = dt.replace('Z', '+00:00') if dt.endswith('Z') else dt
                parsed_dt = datetime.fromisoformat(dt_str)
            else:
                return dt[:16] if len(dt) >= 16 else dt
        
        # If it's already a Python datetime
        elif hasattr(dt, 'strftime'):
            parsed_dt = dt
        
        # If it's a Langfuse datetime object, convert to string first
        elif hasattr(dt, 'isoformat'):
            dt_str = dt.isoformat()
            dt_str = dt_str.replace('Z', '+00:00') if dt_str.endswith('Z') else dt_str
            parsed_dt = datetime.fromisoformat(dt_str)
        
        # Try parsing string representation
        else:
            dt_str = str(dt)
            if len(dt_str) >= 16:
                return dt_str[:16].replace('T', ' ')
            return dt_str
        
        # Normalize to UTC+7 timezone and format
        if parsed_dt:
            if parsed_dt.tzinfo is None:
                # If naive datetime, assume UTC
                parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
            # Convert to target timezone and format
            normalized_dt = parsed_dt.astimezone(TARGET_TIMEZONE)
            return normalized_dt.strftime("%Y-%m-%d %H:%M UTC+7")
        
        return "N/A"
        
    except Exception:
        # Fallback: just return string representation
        return str(dt)[:16] if dt else "N/A"


def display_matching_summary(matches, no_counterpart_users, time_filter_days):
    """Display a summary of the enhanced matching results with trace-to-image pairs"""
    print("\n" + "=" * TABLE_WIDTH)
    print("ENHANCED MATCHING RESULTS SUMMARY")
    print("=" * TABLE_WIDTH)

    stats = get_matching_statistics(matches, no_counterpart_users)

    print(f"Time Filter: Past {time_filter_days} day(s)")
    print(f"Total Users: {stats['total_users']}")
    print(f"Users with matches: {stats['users_with_matches']}")
    print(f"Users without counterpart: {stats['users_without_counterpart']}")
    print(f"Total Traces: {stats['total_traces']}")
    print(f"Total Images: {stats['total_images']}")
    print(f"Total Matched Pairs: {stats['total_matched_pairs']}")
    print(f"Match Rate: {stats['match_rate']:.1f}%")
    print(f"Pair Match Efficiency: {stats['pair_match_efficiency']:.1f}%")

    if matches:
        print(f"\nSUCCESSFUL MATCHES ({len(matches)} users):")
        print("-" * TABLE_WIDTH)
        print(f"{'User ID':<40} | {'Pairs':<6} | {'Traces':<7} | {'Images':<7} | {'Efficiency':<10}")
        print("-" * TABLE_WIDTH)

        for match in matches:
            user_id_display = truncate_string(match['user_id'], USER_ID_DISPLAY_WIDTH)
            efficiency = f"{match['match_efficiency']*100:.1f}%"

            print(f"{user_id_display:<40} | {match['matched_pairs_count']:<6} | {match['trace_count']:<7} | {match['image_count']:<7} | {efficiency:<10}")

    if no_counterpart_users:
        print(f"\nUSERS WITHOUT COUNTERPART ({len(no_counterpart_users)} users):")
        print("-" * 70)
        print(f"{'User ID':<40} | {'Missing':<8} | {'Count':<8}")
        print("-" * 70)

        for user_data in no_counterpart_users:
            user_id_display = truncate_string(user_data['user_id'], USER_ID_DISPLAY_WIDTH)
            missing_type = user_data.get('missing_type', 'unknown')
            count = user_data.get('trace_count', user_data.get('image_count', 0))

            print(f"{user_id_display:<40} | {missing_type:<8} | {count:<8}")


def display_detailed_user_info(match_data):
    """Display detailed information for a specific user match with image-to-trace pairs"""
    user_id = match_data['user_id']
    matched_pairs = match_data.get('matched_pairs', [])
    unused_traces = match_data.get('unused_traces', [])
    unmatched_images = match_data.get('unmatched_images', [])

    print(f"\n" + "=" * TABLE_WIDTH)
    print(f"DETAILED VIEW FOR USER: {user_id}")
    print("=" * TABLE_WIDTH)

    # Show matched pairs (image-first approach)
    if matched_pairs:
        print(f"\nMATCHED IMAGE-TRACE PAIRS ({len(matched_pairs)}):")
        print("-" * TABLE_WIDTH)
        for i, pair in enumerate(matched_pairs[:MAX_DISPLAY_ITEMS], 1):
            image_name = pair['image']['key'].split('/')[-1]
            trace_name = pair['trace'].name or "Unnamed"
            time_diff_minutes = pair['time_difference_seconds'] / 60
            
            image_time = format_datetime(pair['image_timestamp'])
            trace_time = format_datetime(pair['trace_timestamp'])
            
            print(f"{i}. IMAGE: {image_name} ({image_time})")
            print(f"   TRACE: {trace_name} ({trace_time})")
            print(f"   TIME DIFF: {time_diff_minutes:.1f} minutes")
            print()

        if len(matched_pairs) > MAX_DISPLAY_ITEMS:
            print(f"... and {len(matched_pairs) - MAX_DISPLAY_ITEMS} more pairs")

    # Show unused traces
    if unused_traces:
        print(f"\nUNUSED TRACES ({len(unused_traces)}):")
        print("-" * 60)
        for i, trace in enumerate(unused_traces[:MAX_DISPLAY_ITEMS], 1):
            trace_name = trace.name or "Unnamed"
            created_at = format_datetime(trace.createdAt)
            print(f"{i}. {trace_name} - {created_at}")

        if len(unused_traces) > MAX_DISPLAY_ITEMS:
            print(f"... and {len(unused_traces) - MAX_DISPLAY_ITEMS} more traces")

    # Show unmatched images
    if unmatched_images:
        print(f"\nUNMATCHED IMAGES ({len(unmatched_images)}):")
        print("-" * 60)
        for i, img in enumerate(unmatched_images[:MAX_DISPLAY_ITEMS], 1):
            filename = img['key'].split('/')[-1]
            size_mb = img['size'] / (1024 * 1024)
            last_modified = format_datetime(img['last_modified'])
            print(f"{i}. {filename} ({size_mb:.2f}MB) - {last_modified}")

        if len(unmatched_images) > MAX_DISPLAY_ITEMS:
            print(f"... and {len(unmatched_images) - MAX_DISPLAY_ITEMS} more images")


def display_detailed_no_match_info(no_match_data):
    """
    Display detailed information for users without matches
    Can handle both images without traces or traces without images
    
    Args:
        no_match_data (dict): User data without matching counterpart
    """
    user_id = no_match_data['user_id']
    images = no_match_data.get('images', [])
    traces = no_match_data.get('traces', [])
    
    print(f"\n" + "=" * TABLE_WIDTH)
    print(f"DETAILED VIEW FOR USER WITHOUT MATCH: {user_id}")
    print("=" * TABLE_WIDTH)
    
    # Display what we have for this user
    if images:
        print(f"\nIMAGES ({len(images)}) - NO MATCHING TRACES:")
        print("-" * 60)
        for i, img in enumerate(images[:MAX_DISPLAY_ITEMS], 1):
            filename = img['key'].split('/')[-1]
            size_mb = img['size'] / (1024 * 1024)
            last_modified = format_datetime(img['last_modified'])
            print(f"{i}. {filename} ({size_mb:.2f}MB) - {last_modified}")
        
        if len(images) > MAX_DISPLAY_ITEMS:
            print(f"... and {len(images) - MAX_DISPLAY_ITEMS} more images")
    
    if traces:
        print(f"\nTRACES ({len(traces)}) - NO MATCHING IMAGES:")
        print("-" * 60)
        for i, trace in enumerate(traces[:MAX_DISPLAY_ITEMS], 1):
            trace_name = trace.name or "Unnamed"
            created_at = format_datetime(trace.createdAt)
            print(f"{i}. {trace_name} - {created_at}")
        
        if len(traces) > MAX_DISPLAY_ITEMS:
            print(f"... and {len(traces) - MAX_DISPLAY_ITEMS} more traces")


def display_user_selection_menu(matches):
    """
    Display menu for user selection from successful matches
    
    Args:
        matches (list): List of successful matches
        
    Returns:
        int or None: Selected user index or None if invalid
    """
    if not matches:
        print("No users with matches available.")
        return None
    
    print(f"\nAvailable users with matches:")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match['user_id']} ({match['image_count']} images, {match['trace_count']} traces)")
    
    try:
        user_choice = int(input("\nSelect user number: ")) - 1
        if 0 <= user_choice < len(matches):
            return user_choice
        else:
            print("Invalid selection")
            return None
    except ValueError:
        print("Please enter a valid number")
        return None


def display_main_menu():
    """Display the main options menu"""
    print(f"\nOPTIONS:")
    print("1. View detailed match for a specific user")
    print("2. Export results to JSON")
    print("3. Export successful pairs to CSV (DataFrame)")
    print("4. Try different time filter")
    print("5. Exit")


def display_application_header():
    """Display the application header"""
    print("MEAL IMAGES TO LANGFUSE TRACES MAPPING")
    print("=" * 60) 