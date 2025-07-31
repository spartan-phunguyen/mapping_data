"""
DataFrame Exporter Module
Handles exporting successful matching pairs to pandas DataFrame including:
- Langfuse trace details (input, output, cost, model name)
- S3 image information (image name, URL)
- Matching metadata (timestamps, time difference)
"""

import pandas as pd
from datetime import datetime
import os


def extract_langfuse_trace_details(trace):
    """
    Extract detailed information from a Langfuse trace object
    
    Args:
        trace: Langfuse trace object
        
    Returns:
        dict: Dictionary with trace details
    """
    try:
        # Basic trace information
        trace_details = {
            'trace_id': getattr(trace, 'id', None),
            'trace_name': getattr(trace, 'name', None),
            'user_id': getattr(trace, 'userId', None),
            'created_at': getattr(trace, 'createdAt', None),
            'input': None,
            'output': None,
            'total_cost': getattr(trace, 'calculatedTotalCost', 0),
            'trace_tags': getattr(trace, 'tags', []),
            'trace_metadata': getattr(trace, 'metadata', {})
        }
        
        # Extract input/output from trace
        if hasattr(trace, 'input'):
            trace_details['input'] = str(trace.input) if trace.input else None
            
        if hasattr(trace, 'output'):
            trace_details['output'] = str(trace.output) if trace.output else None
        
        # Try to extract from observations/generations if available
        if hasattr(trace, 'observations') and trace.observations:
            for obs in trace.observations:
                # Look for generation observations
                if hasattr(obs, 'type') and obs.type == 'GENERATION':
                    if hasattr(obs, 'input') and obs.input and not trace_details['input']:
                        trace_details['input'] = str(obs.input)
                    if hasattr(obs, 'output') and obs.output and not trace_details['output']:
                        trace_details['output'] = str(obs.output)
        
        return trace_details
        
    except Exception as e:
        print(f"Error extracting trace details: {e}")
        return {
            'trace_id': getattr(trace, 'id', None),
            'trace_name': getattr(trace, 'name', None),
            'user_id': getattr(trace, 'userId', None),
            'created_at': getattr(trace, 'createdAt', None),
            'input': None,
            'output': None,
            'total_cost': 0,
            'trace_tags': [],
            'trace_metadata': {}
        }


def extract_image_details(image_data):
    """
    Extract detailed information from S3 image data
    
    Args:
        image_data: Dictionary containing S3 image information
        
    Returns:
        dict: Dictionary with image details
    """
    try:
        # Extract image name from S3 key
        s3_key = image_data.get('key', '')
        image_name = os.path.basename(s3_key) if s3_key else 'unknown'
        
        return {
            'image_name': image_name,
            'image_key': s3_key,
            'image_url': image_data.get('public_url', ''),
            'image_size': image_data.get('size', 0),
            'last_modified': image_data.get('last_modified', None),
            'content_type': image_data.get('content_type', 'image/jpeg')
        }
        
    except Exception as e:
        print(f"Error extracting image details: {e}")
        return {
            'image_name': 'error',
            'image_key': '',
            'image_url': '',
            'image_size': 0,
            'last_modified': None,
            'content_type': 'unknown'
        }


def create_successful_pairs_dataframe(successful_matches):
    """
    Create a pandas DataFrame from successful matching pairs
    
    Args:
        successful_matches: List of successful match data from matching engine
        
    Returns:
        pd.DataFrame: DataFrame with detailed pair information
    """
    rows = []
    
    for match_data in successful_matches:
        user_id = match_data['user_id']
        matched_pairs = match_data.get('matched_pairs', [])
        
        for pair in matched_pairs:
            # Extract trace details
            trace = pair['trace']
            trace_details = extract_langfuse_trace_details(trace)
            
            # Extract image details
            image = pair['image']
            image_details = extract_image_details(image)
            
            # Create combined row
            row = {
                # User information
                'user_id': user_id,
                
                # Langfuse trace information
                'trace_id': trace_details['trace_id'],
                'trace_name': trace_details['trace_name'],
                'input': trace_details['input'],
                'output': trace_details['output'],
                'total_cost': trace_details['total_cost'],
                'trace_tags': str(trace_details['trace_tags']),
                'trace_metadata': str(trace_details['trace_metadata']),
                
                # Image information
                'image_name': image_details['image_name'],
                'image_key': image_details['image_key'],
                'image_url': image_details['image_url'],
                'image_size': image_details['image_size'],
                'content_type': image_details['content_type'],
                
                # Matching information
                'trace_timestamp': pair['trace_timestamp'],
                'image_timestamp': pair['image_timestamp']
            }
            
            rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    return df


def save_dataframe_to_csv(df, filename=None):
    """
    Save DataFrame to CSV file in results/csv/ directory
    
    Args:
        df: pandas DataFrame
        filename: Optional filename, if None, generates timestamped filename
        
    Returns:
        str: Full path of saved file
    """
    # Create results/csv directory if it doesn't exist
    csv_dir = os.path.join("results", "csv")
    os.makedirs(csv_dir, exist_ok=True)
    
    if filename is None:
        from datetime import timezone, timedelta
        TARGET_TIMEZONE = timezone(timedelta(hours=7))
        timestamp = datetime.now(TARGET_TIMEZONE).strftime("%Y%m%d_%H%M%S")
        filename = f"successful_pairs_dataframe_{timestamp}.csv"
    
    # Full path to save file
    full_path = os.path.join(csv_dir, filename)
    df.to_csv(full_path, index=False)
    return full_path


def display_dataframe_summary(df):
    """
    Display summary statistics of the DataFrame
    
    Args:
        df: pandas DataFrame
    """
    if df.empty:
        print("No successful pairs found to display")
        return
    
    print("\n" + "=" * 60)
    print("SUCCESSFUL PAIRS DATAFRAME SUMMARY")
    print("=" * 60)
    
    print(f"Total successful pairs: {len(df)}")
    print(f"Unique users: {df['user_id'].nunique()}")
    print(f"Unique traces: {df['trace_id'].nunique()}")
    print(f"Unique images: {df['image_name'].nunique()}")
    
    print("\nDataFrame columns:")
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        print(f"  {col}: {non_null_count}/{len(df)} non-null values") 