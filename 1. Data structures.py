#================================================================
# libraries
from functions.processing_functions import *                                     # All functions for processsing
import os                                                              # Reading file locations
import pickle                                                          # Outputting data

from functions.graph_functions import *                                          # Graph objects

# Variables
from settings import rootdir, file_extention

#================================================================
# Generate data structures

# 0. Output 
output_code_list = []
output_import_dict = {}
output_element_profile_list = []
output_dependency_dict = {}
output_import_list = []

# 1. Create list of all subdirectories + file names
full_file_paths = get_filepaths(rootdir, file_extention)

# 2. loop through all files
for folder_directory in full_file_paths:

    # 3. Read file into string
    code_strings = read_input(folder_directory)

    # 4. Fetch file name and location:
    file_path = folder_directory.replace(rootdir, '')
    file_name = os.path.split(folder_directory)[-1]

    # 5. Segment code into elements
    code_list = get_elements(code_strings, file_name, file_path)

    # 6. Create information about imports used in each file:
    import_dict = get_imports(code_list, file_name, file_path)

    # 7. Process elements and create a profile for them:
    element_profile_list, dependency_name_dict = profile_elements(code_list)

    # 8. Output information
    output_code_list.extend(code_list) # codes
    output_import_dict[file_name] = import_dict # imports
    output_element_profile_list.extend(element_profile_list) # Functions
    
    for key, value in dependency_name_dict.items():
        output_dependency_dict[key] = output_dependency_dict.get(key, []) + [value[0]] # Dependencies
        
# 9. Get dependencies between elements
dependency_list = get_dependencies(output_code_list, output_dependency_dict, output_import_dict)

# 10. Create graph
G = create_graph(output_element_profile_list, dependency_list, output_import_dict, rootdir, file_extention)


#================================================================
# Store results

# Codes
with open('output/1.code.pkl', 'wb') as f: 
    pickle.dump(output_code_list, f) 
    
# Imports
with open('output/2.import.pkl', 'wb') as f: 
    pickle.dump(output_import_dict, f) 
    
# Element profiles
with open('output/3.element.pkl', 'wb') as f: 
    pickle.dump(output_element_profile_list, f) 
    
# Element dependencies
with open('output/4.dependencies.pkl', 'wb') as f: 
    pickle.dump(dependency_list, f)   
    
# Graph structure
with open('output/5.graph.pkl', 'wb') as f: 
    pickle.dump(G, f) 