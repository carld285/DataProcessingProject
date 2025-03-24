import os
import pandas as pd
import numpy as np

# Define the base project path and data directories
base_path = r'C:\Users\carld\Documents\DataProcessingProject'
input_folder = os.path.join(base_path, 'data', 'input')
output_folder = os.path.join(base_path, 'data', 'output')
temp_folder = os.path.join(base_path, 'data', 'temp')

# Ensure that the temp folder exists
os.makedirs(temp_folder, exist_ok=True)


###############################
# Functions for Input Handling
###############################

def read_input_files(folder):
    """
    Read all CSV and JSON files from the provided folder and merge them into a single DataFrame.
    This function attempts to detect delimiters for CSV files.
    """
    csv_files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    json_files = [f for f in os.listdir(folder) if f.endswith('.json')]

    df_list = []

    # Read CSV files with delimiter detection
    for file in csv_files:
        file_path = os.path.join(folder, file)
        try:
            with open(file_path, 'r') as f:
                first_line = f.readline()
            if ';' in first_line and ',' not in first_line:
                df = pd.read_csv(file_path, delimiter=';')
            else:
                df = pd.read_csv(file_path)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading CSV file {file_path}: {e}")

    # Read JSON files
    for file in json_files:
        file_path = os.path.join(folder, file)
        try:
            df = pd.read_json(file_path)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading JSON file {file_path}: {e}")

    if df_list:
        return pd.concat(df_list, ignore_index=True)
    else:
        return pd.DataFrame()


def process_data(df):
    """
    Process the input DataFrame to generate the expected output.
    This includes:
      - Dropping rows with missing 'runs' or 'wickets'.
      - Removing players with age outside 15-50.
      - Creating a 'Player Type' column based on performance criteria.
    Expected columns: 'player_name', 'runs', 'wickets', 'age', 'event_type'
    """
    # Drop rows missing runs or wickets
    df = df.dropna(subset=['runs', 'wickets'])

    # Filter out players with age > 50 or age < 15
    df = df[(df['age'] <= 50) & (df['age'] >= 15)]

    # Create the 'Player Type' column:
    # All-Rounder: runs > 500 and wickets >= 50
    # Batsman: runs > 500 and wickets < 50
    # Bowler: runs < 500
    conditions = [
        (df['runs'] > 500) & (df['wickets'] >= 50),
        (df['runs'] > 500) & (df['wickets'] < 50),
        (df['runs'] < 500)
    ]
    choices = ['All-Rounder', 'Batsman', 'Bowler']
    df['Player Type'] = np.select(conditions, choices, default='Unknown')

    return df


###############################
# Functions for Output Handling
###############################

def read_output_file(file_path):
    """
    Read a CSV output file with proper delimiter detection and rename columns if necessary.
    """
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline()
        if ';' in first_line and ',' not in first_line:
            df = pd.read_csv(file_path, delimiter=';')
        else:
            df = pd.read_csv(file_path)

        # Rename columns if needed:
        rename_map = {}
        if 'eventType' in df.columns:
            rename_map['eventType'] = 'event_type'
        if 'playerName' in df.columns:
            rename_map['playerName'] = 'player_name'
        if 'playerType' in df.columns:
            rename_map['playerType'] = 'Player Type'
        if rename_map:
            df = df.rename(columns=rename_map)

        return df
    except Exception as e:
        print(f"Error reading output file {file_path}: {e}")
        return None


###############################
# Comparison Function
###############################

def compare_results(expected_df, actual_df):
    """
    Compare the expected DataFrame with the actual DataFrame.
    For each record (matched by 'player_name'), compare key columns and mark the record as PASS if all match; otherwise, FAIL.
    Returns a merged DataFrame with a 'Result' column.
    """
    # Check if 'player_name' is in both DataFrames
    if 'player_name' not in expected_df.columns or 'player_name' not in actual_df.columns:
        print("Error: 'player_name' column must be present in both DataFrames.")
        return None

    # Define columns to compare
    compare_cols = ['runs', 'wickets', 'age', 'event_type', 'Player Type']

    # Merge on 'player_name' with suffixes for expected and actual values
    merged_df = expected_df.merge(actual_df, on='player_name', suffixes=('_expected', '_actual'), how='outer')

    # Function to compare each row
    def record_result(row):
        for col in compare_cols:
            expected_val = row.get(f"{col}_expected")
            actual_val = row.get(f"{col}_actual")
            # Consider NaNs as equal
            if pd.isna(expected_val) and pd.isna(actual_val):
                continue
            if expected_val != actual_val:
                return 'FAIL'
        return 'PASS'

    merged_df['Result'] = merged_df.apply(record_result, axis=1)
    return merged_df


###############################
# Main Execution
###############################

if __name__ == '__main__':
    # Step 1: Read and process input data to generate the expected DataFrame
    input_df = read_input_files(input_folder)
    if input_df.empty:
        print("No input data found in:", input_folder)
        expected_df = pd.DataFrame()  # or handle error appropriately
    else:
        expected_df = process_data(input_df)
        print("Processed expected data:")
        print(expected_df.head())

    # Step 2: Read the output files using the output file reader
    output_files = {
        'test': os.path.join(output_folder, 'test.csv'),
        'odi': os.path.join(output_folder, 'odi.csv')
    }

    actual_dfs = []
    for key, file_path in output_files.items():
        if os.path.exists(file_path):
            df_out = read_output_file(file_path)
            if df_out is not None:
                actual_dfs.append(df_out)
                print(f"Loaded {file_path}")
        else:
            print(f"{file_path} not found.")

    if not actual_dfs:
        print("No output files found in the output folder:", output_folder)
    else:
        actual_df = pd.concat(actual_dfs, ignore_index=True)
        print("Columns in actual_df after reading output files:", actual_df.columns.tolist())
        print(actual_df.head())

        # Step 3: Compare the expected data with the actual output data
        final_df = compare_results(expected_df, actual_df)
        if final_df is not None:
            # Step 4: Save the final comparison result to test_result.csv in the temp folder
            final_result_path = os.path.join(temp_folder, 'test_result.csv')
            final_df.to_csv(final_result_path, index=False)
            print(f"Test results stored in: {final_result_path}")
            print("Sample of final comparison result:")
            print(final_df.head())
        else:
            print("Comparison failed; final_df is None.")
