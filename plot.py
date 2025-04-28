import pandas as pd
import plotly.express as px
import argparse
import os

def plot_metrics(input_file):
    """Generate a line plot of pod metrics from a CSV file and save it as an image."""
    # Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

    # Load CSV
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    # Ensure required columns exist
    required_columns = ['timestamp', 'pod_name', 'metric', 'value']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"CSV is missing required columns: {missing_columns}")

    # Convert timestamp to datetime
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    except Exception as e:
        raise ValueError(f"Error converting 'timestamp' to datetime: {e}")

    # Filter by pod_name and metric prefix
    filtered_df = df[
        # df['pod_name'].str.contains('wskowdev-invoker-00', na=False) &
        df['metric'].str.startswith('pod_')
    ]

    # Check if filtered DataFrame is empty
    if filtered_df.empty:
        print("Warning: No data matches the filter criteria (pod_name: 'wskowdev-invoker-00', metric: 'pod_*').")
        return

    # Plot
    fig = px.line(filtered_df, x='timestamp', y='value', color='pod_name',
                  title='Pod Metrics Over Time for stress-ng')

    # Show the plot (optional, can be removed if only saving is needed)
    fig.show()

    # Save the plot as an image
    # try:
    #     fig.write_image(output_image, format='png', width=1200, height=800, scale=2)  # Higher resolution
    #     print(f"Plot saved to {output_image}")
    # except Exception as e:
    #     raise RuntimeError(f"Error saving plot to {output_image}: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Plot pod metrics from a CSV file.")
    parser.add_argument("input_file", help="Path to the input CSV file")
    # parser.add_argument("output_image", help="Path to save the output image (e.g., plot.png)")

    # Parse arguments
    args = parser.parse_args()

    # Generate the plot
    plot_metrics(args.input_file)

if __name__ == "__main__":
    main()