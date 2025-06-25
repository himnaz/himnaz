import pandas as pd
import os
from pathlib import Path

def concatenate_excel_files_with_validation(input_folder, output_file):
    """
    Concatenates all sheets (except first two) from all Excel files in a folder into one DataFrame,
    with column name validation.
    
    Args:
        input_folder (str): Path to folder containing Excel files
        output_file (str): Path for output Excel file
    """
    all_data = pd.DataFrame()
    reference_columns = None
    error_log = []
    
    # Get all Excel files in the input folder
    excel_files = [f for f in os.listdir(input_folder) if f.endswith(('.xlsx', '.xls'))]
    
    if not excel_files:
        print("No Excel files found in the specified folder.")
        return
    
    for file in excel_files:
        file_path = os.path.join(input_folder, file)
        print(f"\nProcessing file: {file}")
        
        try:
            # Get all sheet names in the Excel file
            xl = pd.ExcelFile(file_path)
            sheet_names = xl.sheet_names
            
            # Skip first two sheets (Version Control and Table Summary)
            sheets_to_process = sheet_names[2:] if len(sheet_names) > 2 else []
            
            if not sheets_to_process:
                print(f"  No additional sheets found in {file}")
                continue
                
            for sheet in sheets_to_process:
                print(f"  Processing sheet: {sheet}")
                try:
                    # Read the sheet, using row 1 as header (0-based index)
                    df = pd.read_excel(file_path, sheet_name=sheet, header=1)
                    
                    # Skip empty sheets
                    if df.empty:
                        print(f"    Sheet {sheet} is empty - skipping")
                        continue
                        
                    # Standardize column names (strip whitespace, make lowercase, etc.)
                    df.columns = df.columns.str.strip().str.lower()
                    
                    # Check if this is the first valid sheet we're processing
                    if reference_columns is None:
                        reference_columns = set(df.columns)
                        print(f"    Setting reference columns: {reference_columns}")
                    
                    # Validate column names
                    current_columns = set(df.columns)
                    if current_columns != reference_columns:
                        error_msg = f"Column mismatch in {file} - {sheet}. Expected: {reference_columns}, Found: {current_columns}"
                        error_log.append(error_msg)
                        print(f"    ERROR: {error_msg}")
                        continue
                    
                    # Add origin file and sheet name as columns
                    df['source_file'] = file
                    df['source_sheet'] = sheet
                    
                    # Concatenate with main DataFrame
                    all_data = pd.concat([all_data, df], ignore_index=True)
                    print(f"    Successfully added {len(df)} rows")
                    
                except Exception as e:
                    error_msg = f"Error processing {file} - {sheet}: {str(e)}"
                    error_log.append(error_msg)
                    print(f"    ERROR: {error_msg}")
                    
        except Exception as e:
            error_msg = f"Error opening file {file}: {str(e)}"
            error_log.append(error_msg)
            print(f"  ERROR: {error_msg}")
    
    # Write the output if we have valid data
    if not all_data.empty:
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the combined data
        all_data.to_excel(output_file, index=False)
        print(f"\nSuccess! Combined data saved to {output_file}")
        print(f"Total rows: {len(all_data)}")
        
        # Write error log if there were any errors
        if error_log:
            error_log_file = output_path.with_name(f"{output_path.stem}_errors.txt")
            with open(error_log_file, 'w') as f:
                f.write("\n".join(error_log))
            print(f"Error log saved to {error_log_file}")
    else:
        print("\nNo valid data was combined. Output file not created.")
        
    return all_data, error_log

# Example usage
if __name__ == "__main__":
    input_folder = "path/to/your/excel/files"  # Change this to your folder path
    output_file = "path/to/output/combined_data.xlsx"  # Change this to your desired output path
    
    concatenate_excel_files_with_validation(input_folder, output_file)
