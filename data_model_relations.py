import pandas as pd
from itertools import product

def parse_table_field_relationships(excel_file_path, output_file=None):
    """
    Parse Excel sheet with tablename and fieldname columns to extract databases, tables, and fields.
    
    Parameters:
    excel_file_path (str): Path to the Excel file
    output_file (str, optional): Path to save the result as Excel file
    
    Returns:
    pandas.DataFrame: DataFrame with database, table, and field information
    """
    
    # Read the Excel file
    df = pd.read_excel(excel_file_path)
    
    # Initialize result list
    results = []
    
    # Process each row
    for index, row in df.iterrows():
        tablename_values = str(row['tablename']).split(',')
        fieldname_values = str(row['fieldname']).split(',')
        
        # Parse table information
        tables_info = []
        for table_value in tablename_values:
            table_value = table_value.strip()
            if '.' in table_value:
                db_name, table_name = table_value.split('.', 1)
                tables_info.append({
                    'database': db_name.strip(),
                    'table': table_name.strip()
                })
        
        # Parse field information
        fields_info = []
        for field_value in fieldname_values:
            field_value = field_value.strip()
            if '.' in field_value:
                table_name, field_name = field_value.split('.', 1)
                fields_info.append({
                    'table': table_name.strip(),
                    'field': field_name.strip()
                })
        
        # Create all combinations of tables and fields
        for table_info in tables_info:
            for field_info in fields_info:
                # Only match if table names are the same
                if table_info['table'] == field_info['table']:
                    results.append({
                        'database': table_info['database'],
                        'table': table_info['table'],
                        'field': field_info['field'],
                        'original_row': index + 1  # 1-based indexing for readability
                    })
    
    # Create result DataFrame
    result_df = pd.DataFrame(results)
    
    # Remove duplicates and sort
    result_df = result_df.drop_duplicates().sort_values(['database', 'table', 'field']).reset_index(drop=True)
    
    # Save to Excel if output file is specified
    if output_file:
        result_df.to_excel(output_file, index=False)
        print(f"Results saved to: {output_file}")
    
    return result_df

def alternative_approach(excel_file_path, output_file=None):
    """
    Alternative approach that provides more detailed analysis.
    """
    
    # Read the Excel file
    df = pd.read_excel(excel_file_path)
    
    # Initialize lists for different data
    all_tables = []
    all_fields = []
    
    # Extract all table information
    for index, row in df.iterrows():
        tablename_values = str(row['tablename']).split(',')
        for table_value in tablename_values:
            table_value = table_value.strip()
            if '.' in table_value:
                db_name, table_name = table_value.split('.', 1)
                all_tables.append({
                    'database': db_name.strip(),
                    'table': table_name.strip(),
                    'source_row': index + 1
                })
    
    # Extract all field information
    for index, row in df.iterrows():
        fieldname_values = str(row['fieldname']).split(',')
        for field_value in fieldname_values:
            field_value = field_value.strip()
            if '.' in field_value:
                table_name, field_name = field_value.split('.', 1)
                all_fields.append({
                    'table': table_name.strip(),
                    'field': field_name.strip(),
                    'source_row': index + 1
                })
    
    # Create DataFrames
    tables_df = pd.DataFrame(all_tables).drop_duplicates()
    fields_df = pd.DataFrame(all_fields).drop_duplicates()
    
    # Merge tables and fields based on table name
    merged_df = pd.merge(tables_df, fields_df, on='table', suffixes=('_table', '_field'))
    
    # Select and rename columns
    result_df = merged_df[['database', 'table', 'field']].drop_duplicates().sort_values(['database', 'table', 'field'])
    
    # Save to Excel if output file is specified
    if output_file:
        result_df.to_excel(output_file, index=False)
        print(f"Results saved to: {output_file}")
    
    return result_df

# Example usage
if __name__ == "__main__":
    # Replace with your actual file path
    excel_file_path = "your_file.xlsx"
    
    try:
        # Method 1: Direct parsing with row relationships
        print("Processing Excel file...")
        result1 = parse_table_field_relationships(excel_file_path, "output_method1.xlsx")
        print("Method 1 - Results:")
        print(result1.head(10))
        print(f"\nTotal records found: {len(result1)}")
        
        # Method 2: Alternative approach
        print("\n" + "="*50)
        print("Alternative Approach Results:")
        result2 = alternative_approach(excel_file_path, "output_method2.xlsx")
        print(result2.head(10))
        print(f"Total records found: {len(result2)}")
        
        # Display summary statistics
        print("\n" + "="*50)
        print("SUMMARY STATISTICS:")
        print(f"Unique databases: {result1['database'].nunique()}")
        print(f"Unique tables: {result1['table'].nunique()}")
        print(f"Unique fields: {result1['field'].nunique()}")
        
        # Show database and table breakdown
        db_table_summary = result1.groupby('database')['table'].nunique().reset_index()
        db_table_summary.columns = ['Database', 'Table Count']
        print("\nTables per database:")
        print(db_table_summary)
        
    except FileNotFoundError:
        print(f"Error: File '{excel_file_path}' not found.")
    except KeyError as e:
        print(f"Error: Column {e} not found in the Excel file. Please check your column names.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Additional utility function to create sample data for testing
def create_sample_excel():
    """Create a sample Excel file for testing"""
    sample_data = {
        'tablename': [
            'db1.table1, db1.table2, db2.table3',
            'db1.table1, db3.table4',
            'db2.table3, db3.table4'
        ],
        'fieldname': [
            'table1.field1, table1.field2, table2.field3',
            'table1.field1, table4.field5',
            'table3.field4, table4.field5, table4.field6'
        ]
    }
    
    sample_df = pd.DataFrame(sample_data)
    sample_df.to_excel('sample_data.xlsx', index=False)
    print("Sample Excel file 'sample_data.xlsx' created for testing.")

# Uncomment the line below to create sample data for testing
# create_sample_excel()