"""
Main Application Module
Entry point for the Meal Images to Langfuse Traces Mapping application.
Coordinates all other modules and provides the interactive user interface.
Updated for new flow: Start with Langfuse users, then match with S3 images
"""

from client.s3_client import initialize_s3_client
from client.langfuse_client import initialize_langfuse_client, get_user_time_filter_choice
from util.matching_engine import match_images_with_traces
from util.display_utils import (
    display_application_header, display_matching_summary, 
    display_detailed_user_info, display_user_selection_menu,
    display_main_menu
)
from exporter.json_exporter import export_results_to_json
from exporter.dataframe_exporter import create_successful_pairs_dataframe, save_dataframe_to_csv, display_dataframe_summary


def initialize_clients():
    """
    Initialize both S3 and Langfuse clients
    
    Returns:
        tuple: (s3_client, langfuse_client) or (None, None) if failed
    """
    try:
        print("Initializing clients...")
        s3_client = initialize_s3_client()
        langfuse_client = initialize_langfuse_client()
        print("Successfully initialized S3 and Langfuse clients")
        return s3_client, langfuse_client
    except Exception as e:
        print(f"Failed to initialize clients: {e}")
        return None, None


def run_matching_process():
    """
    Run the complete matching process from start to finish
    New flow: Start with Langfuse users who have traces, then match with S3 images
    
    Returns:
        tuple: (matches, users_without_counterpart, time_filter_name) or (None, None, None) if failed
    """
    # Initialize clients
    s3_client, langfuse_client = initialize_clients()
    if not s3_client or not langfuse_client:
        return None, None, None
    
    # Get user's time filter choice
    selected_days, selected_name = get_user_time_filter_choice()
    
    # Perform the matching process (new flow: Langfuse -> S3)
    matches, users_without_counterpart = match_images_with_traces(
        s3_client, langfuse_client, selected_days
    )
    
    # Display results summary
    display_matching_summary(matches, users_without_counterpart, selected_days)
    
    return matches, users_without_counterpart, selected_name


def handle_detailed_view(matches):
    """
    Handle the detailed view option for a specific user
    
    Args:
        matches (list): List of successful matches
    """
    user_index = display_user_selection_menu(matches)
    if user_index is not None:
        display_detailed_user_info(matches[user_index])


def handle_json_export(matches, users_without_counterpart, time_filter_name):
    """
    Handle the JSON export option
    
    Args:
        matches (list): List of successful matches
        users_without_counterpart (list): List of users without matching counterpart  
        time_filter_name (str): Name of the time filter used
    """
    success, filename, error = export_results_to_json(
        matches, users_without_counterpart, time_filter_name
    )
    
    if success:
        print(f"\nJSON export completed successfully!")
        print(f"File saved as: {filename}")
    else:
        print(f"Export failed: {error}")


def handle_dataframe_export(matches):
    """
    Handle DataFrame export option for successful pairs
    
    Args:
        matches: List of successful matches
    """
    print("\nCreating DataFrame for successful pairs...")
    
    # Create DataFrame from successful matches
    df = create_successful_pairs_dataframe(matches)
    
    if df.empty:
        print("No successful pairs found to export.")
        return
    
    # Display summary statistics
    display_dataframe_summary(df)
    
    # Ask user if they want to save to CSV
    save_choice = input("\nSave DataFrame to CSV file? (y/n): ").strip().lower()
    
    if save_choice in ['y', 'yes']:
        try:
            full_path = save_dataframe_to_csv(df)
            print(f"\nDataFrame successfully saved to: {full_path}")
            print(f"Total rows: {len(df)}")
            print(f"Columns: {', '.join(df.columns[:5])}...")  # Show first 5 columns
        except Exception as e:
            print(f"Error saving DataFrame: {e}")
    else:
        print("DataFrame created but not saved.")


def run_interactive_menu(matches, users_without_counterpart, time_filter_name):
    """
    Run the interactive menu for additional options
    
    Args:
        matches (list): List of successful matches
        users_without_counterpart (list): List of users without matching counterpart
        time_filter_name (str): Name of the time filter used
    """
    while True:
        display_main_menu()
        option = input("\nSelect option (1-5): ").strip()
        
        if option == "1":
            handle_detailed_view(matches)
        
        elif option == "2":
            handle_json_export(matches, users_without_counterpart, time_filter_name)
        
        elif option == "3":
            handle_dataframe_export(matches)
        
        elif option == "4":
            print("\nRestarting with new time filter...")
            main()  # Restart the entire process
            break
        
        elif option == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid option. Please select 1-5.")


def display_welcome_message():
    """Display welcome message and application information"""
    display_application_header()
    print("\nThis application matches meal images from S3 with Langfuse traces")
    print("based on user_id and allows filtering by time periods.")
    print("\nNew Flow (v2.0):")
    print("1. Fetches users with traces from Langfuse within time range")
    print("2. Matches these users with their S3 meal images")
    print("3. Shows users with traces but no images (instead of images without traces)")
    print("\nFeatures:")
    print("- Time-based filtering for Langfuse traces")
    print("- Smart user matching by user_id")
    print("- Detailed user information views")
    print("- Comprehensive JSON export with metadata")
    print("- DataFrame export for successful pairs (CSV)")
    print("- Interactive menu system")
    print("- Organized exports: results/json/ and results/csv/")


def main():
    """
    Main application entry point
    Orchestrates the entire application flow
    """
    # Display welcome message
    display_welcome_message()
    
    # Run the matching process
    matches, users_without_counterpart, time_filter_name = run_matching_process()
    
    # Check if matching was successful
    if matches is None:
        print("Application terminated due to initialization errors.")
        return
    
    # If no matches found at all, provide feedback and exit gracefully
    if not matches and not users_without_counterpart:
        print("\nNo data found. Please check your Langfuse configuration and time filter.")
        print("Possible reasons:")
        print("- No traces found in Langfuse for the selected time period")
        print("- No users with traces in the specified time range")
        print("- Langfuse API connectivity issues")
        return
    
    # Run interactive menu for additional operations
    run_interactive_menu(matches, users_without_counterpart, time_filter_name)


def run_batch_mode(time_filter_days=1, export_filename=None):
    """
    Run the application in batch mode (non-interactive)
    Automatically exports both JSON results and CSV DataFrame
    Useful for automated processing or scripting
    
    Args:
        time_filter_days (int): Number of days to look back for traces
        export_filename (str, optional): Custom filename for JSON export
        
    Returns:
        tuple: (success, matches, users_without_counterpart, filename)
    """
    print("Running in batch mode...")
    print(f"Flow: Langfuse users with traces -> S3 image matching")
    
    # Initialize clients
    s3_client, langfuse_client = initialize_clients()
    if not s3_client or not langfuse_client:
        return False, None, None, None
    
    # Perform matching
    matches, users_without_counterpart = match_images_with_traces(
        s3_client, langfuse_client, time_filter_days
    )
    
    # Display summary
    display_matching_summary(matches, users_without_counterpart, time_filter_days)
    
    # Export to JSON
    time_filter_name = f"Past {time_filter_days} day(s)"
    success, filename, error = export_results_to_json(
        matches, users_without_counterpart, time_filter_name, export_filename
    )
    
    # Auto-export DataFrame to CSV in batch mode
    csv_filename = None
    if matches:  # Only create DataFrame if there are successful matches
        try:
            print("Creating and saving DataFrame for successful pairs...")
            df = create_successful_pairs_dataframe(matches)
            if not df.empty:
                csv_filename = save_dataframe_to_csv(df)
                print(f"DataFrame automatically saved to: {csv_filename}")
                print(f"CSV contains {len(df)} successful pairs")
            else:
                print("No successful pairs found - DataFrame not created")
        except Exception as e:
            print(f"Warning: DataFrame export failed: {e}")
    
    if success:
        print(f"Batch processing completed successfully!")
        print(f"JSON exported to: {filename}")
        if csv_filename:
            print(f"CSV exported to: {csv_filename}")
    else:
        print(f"Batch processing failed: {error}")
    
    return success, matches, users_without_counterpart, filename


if __name__ == "__main__":
    # Check if running in batch mode (you can modify this logic as needed)
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        # Example batch mode usage
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        filename = sys.argv[3] if len(sys.argv) > 3 else None
        run_batch_mode(days, filename)
    else:
        # Run in interactive mode
        main() 