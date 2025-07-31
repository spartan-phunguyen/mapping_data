# Meal Images to Langfuse Traces Mapping

A Python application that matches meal images stored in AWS S3 with Langfuse traces based on user IDs, with configurable time filtering and JSON, DataFrame export capabilities.

## 🔄 **Application Flow**

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

The application is organized into a modular structure with clear separation of concerns:

```
mapping_data/
├── client/                    # External service clients
│   ├── s3_client.py          # AWS S3 operations (images, user extraction)
│   └── langfuse_client.py    # Langfuse operations (traces, time filtering)
├── util/                      # Core utilities and business logic
│   ├── matching_engine.py    # 1-to-1 matching algorithm with timezone normalization
│   └── display_utils.py      # Console display and formatting utilities
├── exporter/                  # Data export modules
│   ├── json_exporter.py      # JSON export with comprehensive metadata
│   └── dataframe_exporter.py # DataFrame/CSV export for successful pairs
├── results/                   # Auto-created export directories
│   ├── json/                 # JSON export files
│   └── csv/                  # DataFrame CSV export files
├── config.py                  # Configuration constants and settings
├── main.py                   # Main application entry point
├── requirements.txt          # Python dependencies (includes pandas)
└── README.md                # Documentation
```

## 🚀 Features

- **Smart Matching**: Start with Langfuse users who have traces, then match with S3 images
- **Advanced 1-to-1 Matching**: Minimal duration algorithm ensuring each image maps to closest preceding trace
- **Timezone Normalization**: All timestamps normalized to UTC+7 for accurate comparisons
- **Time Filtering**: Filter traces by time period (1 day, 7 days, 14 days, 1 month)
- **Dual Export Formats**: 
  - **JSON Export**: Complete results with comprehensive metadata
  - **DataFrame Export**: Successful pairs with trace details (input, prompt, output, cost, model)
- **Organized File Structure**: Auto-creates `results/json/` and `results/csv/` directories
- **Interactive Interface**: User-friendly menu system with detailed statistics
- **Batch Mode**: Non-interactive automation with automatic DataFrame export
- **Rich Analytics**: Match rates, cost analysis, time difference statistics
- **Modular Architecture**: Clean separation of clients, utilities, and exporters

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
Time Filter: Past 1 day(s) (UTC+7 normalized)
Total Users: 8
Users with both images and traces: 5
Users without matches: 3
Total Images: 15
Total Traces: 25
Total Matched Pairs: 12
Match Rate: 62.5%
Pair Match Efficiency: 80.0%

SUCCESSFUL MATCHES (5 users):
--------------------------------------------------------------------------------
User ID                                  | Images   | Traces   | Pairs    | Latest Image UTC+7
--------------------------------------------------------------------------------
0025fd1f-f5b7-4dcb-8c3e-68f8bd409e46     | 3        | 5        | 3        | 2025-01-15 16:30 UTC+7

OPTIONS:
1. View detailed match for a specific user
2. Export results to JSON
3. Export successful pairs to CSV (DataFrame)
4. Try different time filter
5. Exit
```

### Export Outputs

**JSON Export** (`results/json/enhanced_meal_mapping_results_YYYYMMDD_HHMMSS.json`):
```json
{
  "metadata": {
    "export_timestamp": "2025-01-31T17:30:00+07:00",
    "time_filter": "Past 1 day",
    "application_version": "2.0.0",
    "export_type": "enhanced_meal_mapping_results",
    "matching_algorithm": "minimal_duration_1to1"
  },
  "summary": {
    "total_users": 8,
    "users_with_matches": 5,
    "users_without_counterpart": 3,
    "total_images": 15,
    "total_traces": 25,
    "total_matched_pairs": 12,
    "match_rate": 62.5,
    "pair_match_efficiency": 80.0
  },
  "successful_matches": [
    {
      "user_id": "0025fd1f-f5b7-4dcb-8c3e-68f8bd409e46",
      "matched_pairs_count": 3,
      "image_count": 3,
      "trace_count": 5,
      "matched_pairs": [
        {
          "image": {...},
          "trace": {...},
          "trace_timestamp": "2025-01-31T16:25:00+07:00",
          "image_timestamp": "2025-01-31T16:30:00+07:00",
          "time_difference_seconds": 300
        }
      ],
      "unused_traces": [...],
      "unmatched_images": [...]
    }
  ],
  "users_without_counterpart": [
    {
      "user_id": "user-abc-123",
      "trace_count": 2,
      "traces": [...],
      "missing_type": "images"
    }
  ]
}
```

**DataFrame CSV Export** (`results/csv/successful_pairs_dataframe_YYYYMMDD_HHMMSS.csv`):
```csv
user_id,trace_id,trace_name,input,prompt,output,cost,model_name,total_cost,image_name,image_url,trace_timestamp,image_timestamp
0025fd1f-f5b7-4dcb-8c3e-68f8bd409e46,trace-abc-123,meal_analysis,"analyze this meal image","You are a nutrition expert...","This meal contains...","0.0023",gpt-4o-mini,0.0145,meal_001.jpg,https://s3.amazonaws.com/...,2025-01-31T16:25:00+07:00,2025-01-31T16:30:00+07:00
```

The DataFrame export provides:
- **Langfuse Details**: input, prompt, output, cost, model_name for each trace
- **Image Information**: image_name, image_url, image_key
- **Matching Metadata**: timestamps (UTC+7), time differences
- **User Context**: user_id, trace_id, session_id

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
Contains all configuration constants, environment variables, and settings including timezone configuration.

### client/s3_client.py
- Initialize S3 client with AWS credentials
- Fetch meal images from S3 with pagination
- Extract user IDs from S3 object keys
- Generate public URLs for images
- Organize images by user ID

### client/langfuse_client.py
- Initialize Langfuse client with API keys
- Fetch all users with traces in time range (paginated)
- UTC+7 timezone normalization for time calculations
- Handle time filter options and user input

### util/matching_engine.py
- **Advanced 1-to-1 Matching**: Minimal duration algorithm for image-trace pairs
- **Timezone Normalization**: UTC+7 for all timestamp comparisons
- Create enhanced data structures with matched pairs, unused traces, unmatched images
- Calculate comprehensive statistics including pair match efficiency

### util/display_utils.py
- Format console output with UTC+7 timestamps
- Display enhanced summary tables with matching statistics
- Handle user interactions and menu navigation
- Rich formatting for detailed match information

### exporter/json_exporter.py
- Export comprehensive results to JSON format
- UTC+7 timezone normalization for all timestamps
- Enhanced metadata with matching algorithm information
- Auto-saves to `results/json/` directory

### exporter/dataframe_exporter.py
- Extract detailed Langfuse trace information (input, prompt, output, cost, model)
- Create pandas DataFrame for successful image-trace pairs
- Auto-saves to `results/csv/` directory
- Rich analytics: cost analysis, time difference statistics

### main.py
- Application entry point with modular imports
- Interactive mode with 5-option menu including DataFrame export
- **Enhanced Batch Mode**: Automatic JSON + CSV export
- Organized file structure creation

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

**Benefits:**
- More efficient: Only processes users with recent activity
- Better for time-sensitive analysis with timezone normalization
- Comprehensive data export for analysis
- Clean modular codebase for maintainability

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
