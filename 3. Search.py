# File path
from settings import rootdir, file_extention, custom_search_patterns, input_search_patterns, output_search_patterns
# All functions for processsing
from functions.processing_functions import get_filepaths, read_input, identify_pattern_lines, get_elements, add_element_to_statements
# Reading file locations
import os
# output file
import pandas as pd



# 0. Output
output_df = pd.DataFrame()
input_df = pd.DataFrame() 
if custom_search_patterns:
    custom_df = pd.DataFrame() 

# 1. Create list of all subdirectories + file names
full_file_paths = get_filepaths(rootdir, file_extention)

# 2. loop through all files
for folder_directory in full_file_paths:

    # 3. Read file into string
    code_strings = read_input(folder_directory)

    # 4. Fetch file name and location:
    file_path = folder_directory.replace(rootdir, '')
    file_name = os.path.split(folder_directory)[-1]

    # 5a. Get all input statements
    input_dict = identify_pattern_lines(code_strings=code_strings, 
                                             search_patterns = input_search_patterns,
                                             file_name=file_name, 
                                             file_path=file_path)

    # 5b. Get all output statements
    output_dict = identify_pattern_lines(code_strings=code_strings, 
                                              search_patterns = output_search_patterns,
                                              file_name=file_name,
                                              file_path=file_path)
    
    # 5c. Custom search:
    if custom_search_patterns:
        custom_dict = identify_pattern_lines(code_strings=code_strings, 
                                                  search_patterns = custom_search_patterns,
                                                  file_name=file_name,
                                                  file_path=file_path)        

    # 6. Get functions and their lines.
    code_list = get_elements(code_strings, file_name, file_path)

    # 7. Add function name
    input_dict_full = add_element_to_statements(found_dict=input_dict, code_list = code_list)
    output_dict_full = add_element_to_statements(found_dict=output_dict, code_list = code_list)
    if custom_search_patterns:
        custom_dict_full = add_element_to_statements(found_dict=custom_dict, code_list = code_list)

    # 8. Convert to df
    temp_input_df = pd.DataFrame(input_dict_full)
    temp_output_df = pd.DataFrame(output_dict_full)
    if custom_search_patterns:
        temp_custom_df = pd.DataFrame(custom_dict_full)

    # Output
    input_df = pd.concat([input_df, temp_input_df]) 
    output_df = pd.concat([output_df, temp_output_df])
    if custom_search_patterns:
        custom_df = pd.concat([custom_df, temp_custom_df])
    
    
# Store results
input_df.to_csv('output/input_df.csv', index=False)
output_df.to_csv('output/output_df.csv', index=False)
if custom_search_patterns:
    custom_df.to_csv('output/custom_df.csv', index=False)