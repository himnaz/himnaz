import pandas as pd

def process_file_to_excel(input_file_path, output_excel_path):
    """
    Reads a file 5 rows at a time, creates dictionaries for each row,
    collects them in a list, and exports to an Excel file.
    
    Args:
        input_file_path (str): Path to the input file
        output_excel_path (str): Path for the output Excel file
    """
    # List to hold all dictionaries
    data_list = []
    
    # Open the input file
    with open(input_file_path, 'r') as file:
        while True:
            # Read 5 lines at a time
            lines = [file.readline().strip() for _ in range(5)]
            
            # If all lines are empty, we've reached end of file
            if not any(lines):
                break
                
            # Create 5 dictionary variables (row1 to row5)
            row_dicts = []
            for i, line in enumerate(lines, 1):
                if line:  # Only process non-empty lines
                    # Create a dictionary for this row
                    # Assuming each line contains key-value pairs separated by commas
                    # Adjust this parsing based on your actual file format
                    row_data = {}
                    pairs = line.split(',')  # Change delimiter if needed
                    for pair in pairs:
                        if ':' in pair:
                            key, value = pair.split(':', 1)
                            row_data[key.strip()] = value.strip()
                        else:
                            row_data[f'Column{i}'] = pair.strip()
                    
                    # Add dictionary to our temporary list
                    row_dicts.append(row_data)
            
            # Add the 5 dictionaries to our main list
            data_list.extend(row_dicts)
    
    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data_list)
    
    # Write the DataFrame to an Excel file
    df.to_excel(output_excel_path, index=False)
    print(f"Excel file created successfully at: {output_excel_path}")

# Example usage
if __name__ == "__main__":
    input_file = "input.txt"  # Change to your input file path
    output_file = "output.xlsx"  # Change to your desired output path
    
    process_file_to_excel(input_file, output_file)
