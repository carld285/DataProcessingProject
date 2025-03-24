# Data Processor Test Suite

## Overview

This project tests the functionality of a Data Processor module that is part of a larger system. The system collects data via a TCU (Transmission Control Unit) which sends data to a data warehouse. The Data Processor then reads this data and distributes it to multiple modules based on the event type. Our goal is to validate that the Data Processor processes data correctly according to the requirements.

## Requirements

### Input Data
- **CSV Files:**  
  Data for players who played between 1990 and 2000 is provided in CSV format.
- **JSON Files:**  
  Data for players who played from 2000 onward is provided in JSON format.
- All input files are located in the `data/input` directory.

### Processing Logic
- **Event Type Handling:**  
  - If the event type is `ODI`, the data is sent to Customer 2 as `odi_results.csv`.
  - If the event type is `Test`, the data is sent to Customer 1 as `test_results.csv`.
- **Player Type Determination:**  
  A new column called **"Player Type"** is created based on the following criteria:
  - **All-Rounder:** More than 500 runs and 50 or more wickets.
  - **Batsman:** More than 500 runs but fewer than 50 wickets.
  - **Bowler:** Fewer than 500 runs.
- **Data Cleaning:**  
  - Remove any record that lacks runs or wickets data.
  - Remove records for players whose age is less than 15 or greater than 50.
- **Output Integrity:**  
  Ensure that the output contains neither extra nor missing entries.

### Testing Requirements
- **Expected vs. Actual Output:**  
  The test harness reads and processes the input data to create an expected output, then compares it with the Data Processor's actual output.
- **Result Column:**  
  A new column **"Result"** is added to the comparison:
  - **PASS:** When the expected output matches the actual output for a player.
  - **FAIL:** When there is a mismatch.
- The final test results are saved as `test_result.csv` in the `data/temp` directory.

## Folder Structure

A recommended folder structure for the project is as follows:


## Setup and Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/DataProcessingProject.git
   cd DataProcessingProject
python -m venv venv
pip install -r requirements.txt
Running the Test Suite
Prepare the Data:

Place the input data files (CSV and JSON) in the data/input directory.

Place the Data Processor’s output files (e.g., odi_results.csv and test_results.csv) in the data/output directory.

Run the Test Script:

From the project root directory, execute:
python src/test_data_processor.py
The script will:

Read and process the input data to generate the expected output.

Read the actual output files.

Compare the expected and actual outputs.

Save the comparison results as test_result.csv in the data/temp directory.

Contributing
Contributions are welcome! To contribute:

Fork the repository.

Create a new branch for your changes.

Commit your changes with clear messages.

Push your branch and open a pull request.

License
This project is licensed under the MIT License.
