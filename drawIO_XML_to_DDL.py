import xml.etree.ElementTree as ET

def generate_ddl(drawio_file):
    try:
        # Parse the XML file
        tree = ET.parse(drawio_file)
        root = tree.getroot()

        # Namespace handling (DrawIO uses namespaces in newer versions)
        ns = {'mx': 'http://www.w3.org/1999/xhtml'}  # Adjust if needed

        # Dictionary to store tables and their columns
        tables = {}
        relationships = []

        # Find all table elements
        for elem in root.findall('.//mxCell', ns):
            if 'value' not in elem.attrib:
                continue
                
            style = elem.get('style', '')
            value = elem.get('value')
            
            # Identify tables
            if 'shape=table' in style:
                table_name = value
                tables[table_name] = {
                    'columns': [],
                    'pk': [],
                    'fk': [],
                    'id': elem.get('id')
                }
                
            # Identify relationships (edges between tables)
            elif 'entityRelationEdgeStyle' in style:
                relationships.append({
                    'source': elem.get('source'),
                    'target': elem.get('target')
                })

        # Process columns for each table
        for table_name, table_data in tables.items():
            table_id = table_data['id']
            
            # Find all rows in this table
            for row in root.findall(f".//mxCell[@parent='{table_id}']", ns):
                if 'shape=partialRectangle' not in row.get('style', ''):
                    continue
                    
                row_id = row.get('id')
                
                # Find all cells in this row
                left_side_cell = root.findall(f".//mxCell[@parent='{row_id}']", ns)[0]
                if 'value' not in left_side_cell.attrib:
                    p_key = False
                    f_key = False
                elif 'PK' in left_side_cell.get('value').strip():
                    p_key = True
                    f_key = False
                elif 'PK' in left_side_cell.get('value').strip():
                    p_key = False
                    f_key = True
                else:
                    p_key = False
                    f_key = False

                right_side_cell = root.findall(f".//mxCell[@parent='{row_id}']", ns)[1]
                right_cell_value = right_side_cell.get('value').strip()
                right_col_parts = right_cell_value.split()

                col_name = right_col_parts[0]
                col_type = ' '.join(right_col_parts[1:]) if len(right_col_parts) > 1 else 'VARCHAR(255)'
                tables[table_name]['columns'].append({
                        'name': col_name,
                        'type': col_type,
                        'is_pk': p_key,
                        'is_fk': f_key
                    })
                if p_key:
                        tables[table_name]['pk'].append(col_name)
                if f_key:
                        tables[table_name]['fk'].append(col_name)
                continue    

                
                for cell in root.findall(f".//mxCell[@parent='{row_id}']", ns):
                    if 'value' not in cell.attrib:
                        continue
                        
                    cell_value = cell.get('value').strip()
                    cell_style = cell.get('style', '')
                    
                    # Skip empty cells
                    if not cell_value:
                        continue
                        
                    # Determine column properties
                    is_pk = 'PK' in cell_style or 'PK' in cell_value
                    is_fk = 'FK' in cell_style or 'FK' in cell_value
                    
                    # Extract column name and type
                    col_parts = cell_value.split()
                    if len(col_parts) < 1:
                        continue
                        
                    col_name = col_parts[0]
                    col_type = ' '.join(col_parts[1:]) if len(col_parts) > 1 else 'VARCHAR(255)'
                    
                    # Clean up type
                    col_type = col_type.split('NOT NULL')[0].strip()
                    col_type = col_type.rstrip(';,').strip().upper()
                    
                    # Add column to table
                    tables[table_name]['columns'].append({
                        'name': col_name,
                        'type': col_type,
                        'is_pk': is_pk,
                        'is_fk': is_fk
                    })
                    
                    if is_pk:
                        tables[table_name]['pk'] = col_name

        # Generate DDL
        ddl = []
        
        # Create tables
        for table_name, table_data in tables.items():
            create_table = f"CREATE TABLE {table_name} (\n"
            
            for col in table_data['columns']:
                col_def = f"    {col['name']} {col['type']}"
                if col['is_pk']:
                    col_def += " PRIMARY KEY"
                create_table += col_def + ",\n"
            
            create_table = create_table.rstrip(",\n") + "\n);"
            ddl.append(create_table)

        # Add foreign key constraints
        for rel in relationships:
            source_table = find_table_by_id(root, rel['source'], tables, ns)
            target_table = find_table_by_id(root, rel['target'], tables, ns)
            
            if source_table and target_table:
                # Find FK columns in target table that reference source table's PK
                for col in tables[target_table]['columns']:
                    if col['is_fk']:
                        fk_name = col['name']
                        pk_name = tables[source_table]['pk']
                        
                        fk_sql = (f"\nALTER TABLE {target_table}\n"
                                 f"ADD CONSTRAINT fk_{target_table}_{source_table}\n"
                                 f"FOREIGN KEY ({fk_name}) REFERENCES {source_table}({pk_name});")
                        ddl.append(fk_sql)

        return "\n\n".join(ddl)

    except Exception as e:
        return f"Error: {str(e)}"

def find_table_by_id(root, element_id, tables, ns):
    """Find table name by an element ID within the table"""
    elem = root.find(f".//*[@id='{element_id}']", ns)
    if elem is not None:
        parent_id = elem.get('parent')
        if parent_id:
            parent = root.find(f".//*[@id='{parent_id}']", ns)
            if parent is not None and parent.get('value') in tables:
                return parent.get('value')
    return None

# Example usage
drawio_file = "C:\\Metabrowser_output\\test_himaz.xml"  # Replace with your file path
ddl_sql = generate_ddl(drawio_file)
print(ddl_sql)