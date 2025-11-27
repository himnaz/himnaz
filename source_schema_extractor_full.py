import pandas as pd
import math
import os
from pathlib import Path

def write_excel (output_fname,sheet_name,df):
 if os.path.exists(output_fname):
   with pd.ExcelWriter(output_fname, engine='openpyxl', mode='a',if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name=sheet_name, index=False)

 else:
   with pd.ExcelWriter(output_fname, engine='openpyxl', mode='w') as writer:
    df.to_excel(writer, sheet_name=sheet_name, index=False)

def get_primary_keys(pk_list):
    return ','.join(pk_list)

def aws_to_oracle_type_mapper(aws_type):
   if str(aws_type).upper() == 'STRING':
      return 'VARCHAR'
   else :
      return aws_type


def get_coltype(database_name,table_name,field_name,col_type,data_type,transformation):
    temp_data_type=''
    recalculate_type = False
    if (data_type == 'target') & (transformation == 'direct mapping'):
       source_details_df = excel_data_df.loc[(excel_data_df['Target_DatabaseName'] == database_name) & (excel_data_df['Target_Table'] == table_name) & (excel_data_df['Target_FieldName'] == field_name)]
       if len(source_details_df.index) >= 1:
          col_type_df = aws_ddl_df.loc[( aws_ddl_df['Database name'] == str(source_details_df['Source_DatabaseName_AWS'].iloc[0]).strip().lower()) & (aws_ddl_df['Table name'] == str(source_details_df['Source_TableName_AWS'].iloc[0]).strip().lower()) & (aws_ddl_df['Field name'] == str(source_details_df['Source_Variable_AWS'].iloc[0]).strip().lower())]
          if len(col_type_df.index) == 1:
             temp_data_type = col_type_df['type'].iloc[0]
          elif len(col_type_df.index) == 0:
             recalculate_type = True
             target_type_errors.append({ 'source_database_name' : str(source_details_df['Source_DatabaseName_AWS'].iloc[0]).strip().lower() , 'source_table_name' : str(source_details_df['Source_TableName_AWS'].iloc[0]).strip().lower(), 'source_field_name' : str(source_details_df['Source_Variable_AWS'].iloc[0]).strip().lower() ,'target_database_name':database_name,'target_table_name': table_name, 'target_field_name' :field_name, 'target_col_type': col_type, 'data_type': data_type, 'transformation': transformation, 'error': 'AWS Data type record not found and assigning default column type'})
          elif len(col_type_df.index) > 1 :
             target_type_errors.append({'target_database_name':database_name,'target_table_name': table_name, 'target_field_name' :field_name, 'target_col_type': col_type, 'data_type': data_type, 'transformation': transformation, 'error': 'Found multiple AWS columns and assigning the first entry'})
             temp_data_type = col_type_df['type'].iloc[0]
       elif len(source_details_df.index) == 0:
           recalculate_type = True
           target_type_errors.append({'target_database_name':database_name,'target_table_name': table_name, 'target_field_name' :field_name, 'target_col_type': col_type, 'data_type': data_type, 'transformation': transformation, 'error': 'Source entry not found and assigning default column type'})
       elif len(source_details_df.index) > 0:
          target_type_errors.append({'target_database_name':database_name,'target_table_name': table_name, 'target_field_name' :field_name, 'target_col_type': col_type, 'data_type': data_type, 'transformation': transformation, 'error': 'Found multiple source columns entries and assigning the first entry'})
    else:
       recalculate_type = True
       




    if recalculate_type:
       temp_var = str(col_type).strip('[').strip(']').split('(')
       temp_type = temp_var[0].upper()
       temp_suffix = ''
       if len(temp_var)>1 :
           temp_suffix = '(' + temp_var[1]
    
       if temp_type == 'STRING':
             temp_type = 'VARCHAR' 
       elif temp_type == 'INT':
             temp_type = 'INT' 
       elif temp_type == 'NUM':
             temp_type = 'INT' 
       elif temp_type == 'DECIMAL':
             temp_type = 'DECIMAL'
       elif temp_type == 'DATE':
             temp_type = 'DATE'
       else: temp_type = 'VARCHAR' 

       temp_data_type = temp_type+temp_suffix
    else:
       temp_data_type = aws_to_oracle_type_mapper(temp_data_type)
    
    
    type_sets.add(temp_data_type)
    return temp_data_type

aws_ddl_fname         = 'C:\\app\\aws_ddl\\AWS_Consolidated_Tables List_New&Old_Tagging_20250808_share.xlsx'
primary_keys_fname    = 'C:\\app\\tracker\\tracker_files_out\\combined_table_meta_data.xlsx'
process_fname         = 'C:\\app\\Model\\cc\\Credit Card Detailed Requirements Template - v1.1_updated_final.xlsx'
validation_fname      = 'C:\\app\\model\\cc\\cc_validation.xlsx'
ddl_fname             = 'C:\\app\\Model\\cc\\cc_dm_model.sql'

#excel_data_df = pandas.read_excel('C:\\Users\\c0309205\\Downloads\\mrtp_sources.xlsx', sheet_name='Capital_Sources')
excel_data_df = pd.read_excel(process_fname, sheet_name='Data Modelling ',header=0)
#table_keys =  primary_keys_df.loc[(primary_keys_df['Database'] == df_row['db_name']) & (primary_keys_df['Table_Name'] == df_row['table_name']),['Primary Keys']]
excel_data_df = excel_data_df.loc[(excel_data_df['Modelled'] == 'y') | (excel_data_df['Modelled'] == 'y_extra_variables')].copy()
keys_data_df  = pd.read_excel(process_fname, sheet_name='Primary keys',header=0)

primary_keys_df = pd.read_excel(primary_keys_fname, sheet_name='Sheet1',header=0)
aws_ddl_df = pd.read_excel(aws_ddl_fname, sheet_name='Column Level',header=0)
aws_ddl_df['Database name'] = aws_ddl_df['Database name'].str.lower()
aws_ddl_df['Table name'] = aws_ddl_df['Table name'].str.lower()
aws_ddl_df['Field name'] = aws_ddl_df['Field name'].str.lower()

#print(excel_data_df.columns)
#print(excel_data_df[['DM_Table','DM_ColumnName','DM_ColumnType']])

source_table_list = []
source_table_validation_errors = []
exception_errors = []
target_type_errors = []
tracker_primary_keys = []
type_sets = set()

for index,row in excel_data_df.iterrows():
 try:
    db_list = row['Source_DatabaseName_AWS'].split(',')
    table_list = row['Source_TableName_AWS'].split(',')
    field_list = row['Source_Variable_AWS'].split(',')

    if len(db_list) == 1 and len(table_list) == 1:
        for field_name_lst in field_list:
            fully_qualified_fname = field_name_lst.split('.')
            fully_qualified_tname = table_list[0].split('.')
            #if len(fully_qualified_fname) == 1:
            source_table_list.append({'db_name':str(db_list[0]).lower().strip(), 'table_name':str(fully_qualified_tname[len(fully_qualified_tname) -1]).lower().strip(), 'field_name':str(fully_qualified_fname[len(fully_qualified_tname) -1]).lower().strip(),'field_type':''})

    elif len(db_list) == 1 and len(table_list) > 1:
        for field_name_lst in field_list:
            fully_qualified_fname = field_name_lst.split('.')
            if len(fully_qualified_fname) == 3:
                source_table_list.append({'db_name':str(fully_qualified_fname[0]).lower().strip(), 'table_name':str(fully_qualified_fname[1]).lower().strip(), 'field_name':str(fully_qualified_fname[2]).lower().strip(),'field_type':''})
            elif len(fully_qualified_fname) == 2:
                source_table_list.append({'db_name':str(db_list[0]).lower().strip(), 'table_name':str(fully_qualified_fname[0]).lower().strip(), 'field_name':str(fully_qualified_fname[1]).lower().strip(),'field_type':''})
            else:
                source_table_validation_errors.append(row)
    elif len(db_list) > 1 and len(table_list) > 1:
        for field_name_lst in field_list:
            fully_qualified_fname = field_name_lst.split('.')
            if len(fully_qualified_fname) == 3:
                source_table_list.append({'db_name':str(fully_qualified_fname[0]).lower().strip(), 'table_name':str(fully_qualified_fname[1]).lower().strip(), 'field_name':str(fully_qualified_fname[2]).lower().strip(),'field_type':''})
            else:
                source_table_validation_errors.append(row)

 except:
     exception_errors.append(row)
     

write_excel(validation_fname,'source_tables',pd.DataFrame(source_table_list).groupby(['db_name','table_name']).size().reset_index(name = 'count'))
write_excel(validation_fname,'source_fields',pd.DataFrame(source_table_list).groupby(['db_name','table_name','field_name']).size().reset_index(name = 'count'))

#all_table_df = pd.DataFrame(source_table_list).groupby(['db_name','table_name']).size().reset_index(name = 'count')
#print(type(all_table_df))

for index,df_row in pd.DataFrame(source_table_list).groupby(['db_name','table_name']).size().reset_index(name = 'count').iterrows():
   db = df_row['db_name']
   tab = df_row['table_name']
   table_keys = primary_keys_df.loc[(primary_keys_df['Database'] == df_row['db_name']) & (primary_keys_df['Table_Name'] == df_row['table_name']),['Primary Keys']]
   
   if not table_keys.empty:
    table_keys = table_keys['Primary Keys'].iloc[0]
    print(table_keys)
    print(type(table_keys))
    
    for table_key in eval(table_keys):
      print(table_key)
      tracker_primary_keys.append({'Source_DatabaseName_AWS':df_row['db_name'],'Source_TableName_AWS':df_row['table_name'],'Source_Variable_AWS':table_key})
   

write_excel(validation_fname,'tracker_pkey_fields',pd.DataFrame(tracker_primary_keys))



write_excel(validation_fname,'sf_validation_e',pd.DataFrame(source_table_validation_errors))
write_excel(validation_fname,'sf_exceptions_e',pd.DataFrame(exception_errors))
target_df =     excel_data_df[['Target_DatabaseName','Target_Table','Target_FieldName','Target_FieldType','Transformation']].copy()
#print(target_df)
#target_df = target_df.groupby(['Target_DatabaseName','Target_Table','Target_FieldName','Target_FieldType']).size().reset_index(name = 'count')
#print(target_df)
write_excel(validation_fname,'target_fields',target_df.groupby(['Target_DatabaseName','Target_Table','Target_FieldName','Target_FieldType']).size().reset_index(name = 'count'))

#source_df = excel_data_df[['Source_DatabaseName_AWS','Source_TableName_AWS','Source_Variable_AWS','Source_Variable_Type_AWS']].copy()
source_df = pd.DataFrame(source_table_list).groupby(['db_name','table_name','field_name','field_type']).size().reset_index(name = 'count')
source_df.drop(columns=['count'],inplace=True)
source_df.rename(columns={'db_name':'Source_DatabaseName_AWS','table_name':'Source_TableName_AWS','field_name':'Source_Variable_AWS','field_type':'Source_Variable_Type_AWS'}, inplace=True)
source_df['Data_Type'] = 'source'
source_df['Transformation'] = 'source'


keys_df = keys_data_df[['Source_DatabaseName_AWS','Source_TableName_AWS','Source_Variable_AWS','Source_Variable_Type_AWS']].copy()
keys_df['Data_Type'] = 'key'
keys_df['Transformation'] = 'key'
#target_df = excel_data_df[['Target_DatabaseName','Target_Table','Target_FieldName','Target_FieldType']].copy()
target_df.rename(columns={'Target_DatabaseName':'Source_DatabaseName_AWS','Target_Table':'Source_TableName_AWS','Target_FieldName':'Source_Variable_AWS','Target_FieldType':'Source_Variable_Type_AWS'}, inplace=True)
target_df['Data_Type'] = 'target'
#print(target_df)

all_col_df = pd.concat([source_df,keys_df,target_df]) 

#print(all_col_df)

#table_list = all_col_df['Source_TableName_AWS'].copy().dropna().unique()
db_table_df = all_col_df[['Source_DatabaseName_AWS','Source_TableName_AWS']].copy()
db_table_df = db_table_df.groupby(['Source_DatabaseName_AWS','Source_TableName_AWS']).size().reset_index(name = 'count')
#print(db_table_df)
ddl_list = []
#for table_name in table_list:
for index,db_table_row in db_table_df.iterrows():
    table_name = db_table_row['Source_TableName_AWS']
    database_name = db_table_row['Source_DatabaseName_AWS']
    table_ddl_str = "CREATE TABLE " + '"'+ table_name + '"' + " (\n"

    first_col_ind = True
    #column_df = all_col_df[all_col_df['Source_TableName_AWS'] == table_name]
    #column_df = column_df.drop_duplicates()
    column_df = all_col_df.loc[(all_col_df['Source_TableName_AWS'] == table_name) & (all_col_df['Source_DatabaseName_AWS'] == database_name),['Source_Variable_AWS','Source_Variable_Type_AWS','Data_Type','Transformation']].copy()
    column_df['Source_Variable_AWS'] = column_df['Source_Variable_AWS'].str.lower()
    #column_df['Source_Variable_Type_AWS'] = column_df.apply(lambda row: get_coltype(row['Source_Variable_Type_AWS']),axis=1)
    column_df['Source_Variable_Type_AWS'] = column_df['Source_Variable_Type_AWS'].str.lower()
    column_df = column_df.groupby(['Source_Variable_AWS','Source_Variable_Type_AWS','Data_Type','Transformation']).size().reset_index(name = 'count')

    #print(column_df)
    for index,column_name in column_df.iterrows():
        if first_col_ind:
           table_ddl_str = table_ddl_str + str(column_name['Source_Variable_AWS']).lower().strip() + ' ' + get_coltype(database_name,table_name,str(column_name['Source_Variable_AWS']).lower().strip(),column_name['Source_Variable_Type_AWS'],column_name['Data_Type'],str(column_name['Transformation']).lower().strip())
           first_col_ind = False
        else:
            table_ddl_str = table_ddl_str + ',\n'
            table_ddl_str = table_ddl_str + str(column_name['Source_Variable_AWS']).lower().strip() + ' ' + get_coltype(database_name,table_name,str(column_name['Source_Variable_AWS']).lower().strip(),column_name['Source_Variable_Type_AWS'],column_name['Data_Type'],str(column_name['Transformation']).lower().strip())
    #table_columns = all_data.loc[(all_data['enriched_table_name']== table['Table_Name']) & (all_data['source_sheet'] == table['Tab Name'])]
    pk_df = keys_data_df[(keys_data_df['Source_TableName_AWS'] == table_name) & (keys_data_df['DM_PKey'] == 'pk')]
    if pk_df.empty:        
      table_ddl_str = table_ddl_str + '\n'
    else:
        table_ddl_str = table_ddl_str + ',\n'
        table_ddl_str = table_ddl_str + 'PRIMARY KEY (' + get_primary_keys(pk_df['Source_Variable_AWS'].to_list()) + ')\n'

    table_ddl_str = table_ddl_str + ');\n'
    table_ddl_str = table_ddl_str + '\n' 
    ddl_list.append(table_ddl_str)
#print(ddl_list)
write_excel(validation_fname,'type_errors',pd.DataFrame(target_type_errors))
write_excel(validation_fname,'aws_type_sets',pd.DataFrame(type_sets))

with open(ddl_fname, 'w') as fp:
    for table_ddl in ddl_list:
        fp.write("%s\n" % table_ddl)
