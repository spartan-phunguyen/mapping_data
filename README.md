# Meal Images to Langfuse Traces Mapping

A Python application that matches meal images stored in AWS S3 with Langfuse traces based on user IDs, with configurable time filtering and JSON, DataFrame export capabilities.

## 🔄 **Application Flow (Updated v2.0)**

**New Efficient Flow:**
1. **Start with Langfuse**: Fetch all users who have traces within the specified time range
2. **Match with S3**: For each user with traces, check if they have meal images in S3
3. **1-to-1 Image-Trace Matching**: For each image, find the closest preceding trace (optimized for fewer images than traces)
4. **Generate Results**: Show successful image-trace pairs, unused traces, and unmatched images

This approach is more efficient as it focuses on users who have recent activity in Langfuse and optimizes matching for the typical scenario where images are fewer than traces.

## 🎯 **Enhanced Matching Algorithm**

The application uses a sophisticated timestamp-based matching algorithm:

- **Image-Centric Approach**: Iterates through images (typically fewer) to find matching traces
- **Temporal Logic**: For each image, finds the closest trace where `trace_timestamp < image_timestamp`
- **1-to-1 Matching**: Each image matches with only one trace, ensuring no duplicates
- **Time Difference Tracking**: Records the time gap between trace and subsequent image
- **Comprehensive Results**: Tracks matched pairs, unused traces, and unmatched images

## 📁 Project Structure

The application is organized into multiple modules, each with a clear purpose:

```
├── config.py              # Configuration constants and settings
├── s3_client.py           # S3 operations (fetching images, extracting user IDs)
├── langfuse_client.py     # Langfuse operations (fetching traces, time filtering)
├── matching_engine.py     # Core matching logic between Langfuse and S3
├── display_utils.py       # Display and formatting utilities
├── json_exporter.py       # JSON export functionality
├── main.py               # Main application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🚀 Features

- **Smart Matching**: Start with Langfuse users who have traces, then match with S3 images
- **Time Filtering**: Filter traces by time period (1 day, 7 days, 14 days, 1 month)
- **Detailed Views**: View comprehensive information for specific users
- **JSON Export**: Export results to structured JSON files with metadata
- **Interactive Interface**: User-friendly menu system
- **Batch Mode**: Non-interactive mode for automation
- **Statistics**: Calculate match rates and provide comprehensive analytics
- **Flow Detection**: Automatically detects and handles different data flow types

## 📋 Prerequisites

- Python 3.7+
- AWS credentials configured (for S3 access)
- Langfuse account and API keys
- Required Python packages (see requirements.txt)

## 🔧 Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file with the following variables:
   ```env
   # Langfuse Configuration
   LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
   LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

4. **Expose aws key in command line**
    Sign in aws access portal and then get environment variable, then expose it in command line
    ```
    export AWS_ACCESS_KEY_ID="*****"
    export AWS_SECRET_ACCESS_KEY="*****"
    export AWS_SESSION_TOKEN="*****"
    ```

## 🎯 Usage

### Interactive Mode (Default)

Run the main application:
```bash
python main.py
```

The application will guide you through:
1. Time filter selection (1 day, 7 days, 14 days, 1 month)
2. Langfuse user fetching with real-time progress
3. S3 image matching for each user
4. Results summary with comprehensive statistics
5. Interactive menu for additional operations

### Batch Mode

For automated processing with automatic exports:
```bash
# Basic batch mode (1 day filter)
# Automatically exports JSON and CSV
python main.py --batch

# With custom time filter (7 days)
python main.py --batch 7

# With custom JSON filename (CSV auto-generated)
python main.py --batch 7 my_results.json
```

**Batch Mode Outputs:**
- **JSON**: Complete results in `results/json/`
- **CSV**: Successful pairs DataFrame in `results/csv/` (automatic)

## 📊 Output Examples

### Console Output
```
MEAL IMAGES TO LANGFUSE TRACES MAPPING
============================================================

New Flow (v2.0):
1. Fetches users with traces from Langfuse within time range
2. Matches these users with their S3 meal images
3. Shows users with traces but no images (instead of images without traces)

Starting Langfuse to S3 matching process...
============================================================
Step 1: Fetching Langfuse users with traces for past 1 day(s)...
Fetching all traces from 2025-01-14T10:30:00.000Z to 2025-01-15T10:30:00.000Z
Fetching traces page 1...
Found 8 unique users with traces
Total traces: 25

Step 2: Fetching all S3 meal images...
Fetching S3 objects from bucket: service-dietfit-20250526115059333100000001
Using prefix: meal-images/
Found 15 images for 6 unique users

Step 3: Matching users...
Users with traces: 8
Users with S3 images: 6

MATCHING RESULTS SUMMARY
================================================================================
Time Filter: Past 1 day(s)
Total Users: 8
Users with both images and traces: 5
Users without matches: 3
Total Images: 15
Total Traces: 25
Match Rate: 62.5%

SUCCESSFUL MATCHES (5 users):
--------------------------------------------------------------------------------
User ID                                  | Images   | Traces   | Latest Image
--------------------------------------------------------------------------------
0025fd1f-f5b7-4dcb-8c3e-68f8bd409e46     | 3        | 5        | 2025-01-15 09:30

TRACES WITHOUT IMAGES (3 users):
------------------------------------------------------------
User ID                                  | Traces   | Latest Trace
------------------------------------------------------------
user-abc-123                            | 2        | 2025-01-15 10:15
```

### JSON Export Structure
```json
{
  "metadata": {
    "export_timestamp": "2025-01-15T10:30:00.000Z",
    "time_filter": "Past 1 day",
    "application_version": "1.0.0",
    "export_type": "meal_mapping_results",
    "flow_type": "new_flow"
  },
  "summary": {
    "total_users": 8,
    "users_with_matches": 5,
    "users_without_matches": 3,
    "total_images": 15,
    "total_traces": 25,
    "match_rate_percentage": 62.5,
    "users_with_images_but_no_traces": 0,
    "users_with_traces_but_no_images": 3
  },
  "successful_matches": [
    {
      "user_id": "0025fd1f-f5b7-4dcb-8c3e-68f8bd409e46",
      "image_count": 3,
      "trace_count": 5,
      "images": [...],
      "traces": [...]
    }
  ],
  "users_without_matches": [
    {
      "user_id": "user-abc-123",
      "trace_count": 2,
      "traces": [...],
      "type": "traces_without_images"
    }
  ]
}
```

## 🔧 Configuration

### Main Configuration (config.py)
- **S3_BUCKET_NAME**: Your S3 bucket name
- **S3_PREFIX**: Prefix for meal images (default: "meal-images/")
- **TIME_FILTER_OPTIONS**: Available time filter options
- **Display settings**: Table widths, item limits, etc.

### Customizing Time Filters
Edit `TIME_FILTER_OPTIONS` in `config.py`:
```python
TIME_FILTER_OPTIONS = {
    "1": {"name": "Past 1 day", "days": 1},
    "2": {"name": "Past 7 days", "days": 7},
    "3": {"name": "Past 14 days", "days": 14},
    "4": {"name": "Past 1 month", "days": 30},
    "5": {"name": "Past 3 months", "days": 90}  # Add custom option
}
```

## 📁 Module Details

### config.py
Contains all configuration constants, environment variables, and settings.

### s3_client.py
- Initialize S3 client
- Fetch meal images from S3
- Extract user IDs from S3 object keys
- Generate public URLs

### langfuse_client.py
- Initialize Langfuse client
- **NEW**: Fetch all users with traces in time range (paginated)
- Handle time range calculations
- Manage time filter options

### matching_engine.py
- **NEW**: Core business logic starting with Langfuse users
- Match Langfuse users with S3 images (reversed flow)
- Create standardized data structures
- Calculate matching statistics for both flow types

### display_utils.py
- Format console output for new flow
- **NEW**: Handle both "images without traces" and "traces without images"
- Display summary tables with flow detection
- Handle user interactions

### json_exporter.py
- Export results to JSON format with flow type detection
- **NEW**: Handle both old and new flow data structures
- Validate export data structure
- Generate timestamped filenames with metadata

### main.py
- Application entry point
- Coordinate all modules for new flow
- Handle interactive and batch modes
- **NEW**: Enhanced welcome message explaining flow

## 🔍 Expected Data Structures

### S3 Structure
```
meal-images/
├── {user_id_1}/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── image3.jpg
├── {user_id_2}/
│   ├── image1.jpg
│   └── image2.jpg
└── ...
```

### Langfuse Requirements
- Traces must have `user_id` field populated
- Traces must be within the specified time range
- User IDs should match those used in S3 folder structure

**Benefits of New Flow:**
- More efficient: Only processes users with recent activity
- Better for time-sensitive analysis
- Focuses on active users
- Reduces unnecessary S3 operations

## 🔧 Troubleshooting

### Common Issues

**"No users with traces found in Langfuse"**
- Check time filter settings (try longer periods)
- Verify Langfuse API keys and host URL
- Ensure traces have user_id populated
- Check if traces exist in the specified time range

**"Error fetching traces"**
- Check Langfuse API rate limits
- Verify network connectivity
- Check for datetime formatting issues

**"No meal images found in S3 bucket"**
- Verify S3 bucket name and prefix in config.py
- Check S3 object structure matches expected format
- Verify AWS credentials and permissions

**"Users with traces but no matching images"**
- Check user_id format consistency between Langfuse and S3
- Verify S3 folder structure: `meal-images/{user_id}/`
- Check S3 bucket permissions