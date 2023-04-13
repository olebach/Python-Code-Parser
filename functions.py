#================================================================
def get_filepaths(directory, file_extention):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    import os
    
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Restrict to partidular file type 
            if '.'+file_extention in filename:
                # Join the two strings in order to form the full filepath.
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.

#================================================================
def read_input(path):
    """
    Open file and read the code into a string
    """
    
    # Read whole file to a string
    text_file = open(path)    
    data = text_file.read()
    text_file.close()
    
    return data

#================================================================
def get_elements(code_strings, file_name, file_path):

    """
    This function searches for text patterns of functions, imports and classes and breaks the code into sections
    """
    
    import re
    
    #--------------------------------------------------------
    # 0 Output list:
    element_list = []
    
    #--------------------------------------------------------
    # 1. Split text by lines:
    code_lines = code_strings.splitlines()
    
    #--------------------------------------------------------
    # 2. Set initial values
    multiline_import = 0
    element_name = ''
    line_num = 1
    line_code = ''
    
    lag_line_type = ''
    lag_line = ''
    lag_element_name = '<INIT>'
    lag_line_num = 1
    
    for line in code_lines:
        
        # ignore comments:
        line_clean = re.sub('#(.*)\n?', '', line) # Comments
        
        #--------------------------------------------------------
        # 3. Encode cases - imports, functions, classes and code:
        # 3.1.a. Import
        if ('import ' in line_clean):
            # Check for multiline import:
            if '(' in line:
                multiline_import = 1    
                # Assign type:
                line_type = 'Import multiline'
            else:
                # Assign type:
                line_type = 'Import'
            # Empty output
            element_name = file_name

        # 3.1.b multiline import case:
        elif multiline_import == 1:
            if ')' in line_clean:
                # reset import
                multiline_import = 0
            # Assign type:
            line_type = 'Import multiline'

        # 3.2 Function
        elif line.startswith('def '):
            # Assign type:
            line_type = 'Function'
            # Fetch function name
            element_name = re.findall('def (.*?)\(', line_clean)[0]
                
        # 3.3 Class
        elif line_clean.startswith('class '):
            # Assign type:
            line_type = 'Class'
            # Fetch class name
            if '(' in line:
                element_name = re.findall('class (.*?)\(', line_clean)[0]
            else:
                element_name = re.findall('class (.*?):', line_clean)[0]   
                
        # 3.4 Code
        elif not ((line_clean.startswith('    ') or line_clean.strip() == '' or line_clean.strip() == '):') and (lag_line_type == 'Function' or lag_line_type == 'Class' or lag_line_type == 'Class')):
            # Assign type:
            line_type = 'Code'            
            # Empty output
            element_name = file_name   
        
        # Correction for inintial values
        if lag_element_name == '<INIT>':
            lag_element_name = element_name
        
        #--------------------------------------------------------
        # 4. Output:
        if ((lag_line_type == line_type) and (lag_element_name == element_name) and (lag_line_type != 'Import')) or lag_line_type =='': 
            
            # Extend lagged values:
            lag_line = lag_line + '\n' + line    
            lag_line_type = line_type
            
        else: 
            
            # Fetch code lines
            if lag_line_num != (line_num-1):
                line_str = 'Lines: '+str(lag_line_num)+'-'+str(line_num-1)
            else:
                line_str = 'Lines: '+str(lag_line_num)
                
            # output everything retained:
            element_list.append(
                {'file_name'     : file_name,
                 'file_location' : file_path,
                 'file_line_number' : line_str,
                 'element_name'  : lag_element_name,
                 'element_type'  : lag_line_type,
                 'element_code'  : lag_line
                }
            )
            
            # Get new lagged values:
            lag_element_name = element_name
            lag_line_type = line_type
            lag_line = line
            lag_line_num = line_num
              
        #--------------------------------------------------------
        # Increase line number:
        line_num +=1
        
    #--------------------------------------------------------
    # Fetch code lines
    if lag_line_num != (line_num-1):
        line_str = 'Lines: '+str(lag_line_num)+'-'+str(line_num-1)
    else:
        line_str = 'Lines: '+str(lag_line_num)
    
    # 5. Output final values:
    element_list.append(
        {'file_name'     : file_name,
         'file_location' : file_path,
         'file_line_number' : line_str,
         'element_name'  : lag_element_name,
         'element_type'  : lag_line_type,
         'element_code'  : lag_line
        }
    )
    
    return element_list

#================================================================
def extract_import_values(code_str):
    
    """
    Process import code to extract scenarios:
        - from <library> import <function> or from <library> import (<function>,<function>)
        - import <library>.<library>.<function>
        - import <library>
    """
    
    import re
    
    # Clean code string:
    import_element = re.sub('#(.*)\n?', '', code_str) # Comments
    import_element = re.sub(" as (.*)","", import_element) # Aliases
    import_element = re.sub("\n","", import_element)
           

    
    if 'from ' in import_element:
        # fetch library:
        library_name = " ".join(re.findall("from (.*) import", import_element))

        # Fetch imported functions
        functions_all = " ".join(re.findall("import (.*)", import_element, re.DOTALL)) 
        function_list = re.findall("[a-zA-Z_]+", functions_all)
        
        
    # Check for scenario 2
    elif "." in import_element:
        
        # Split string by '.'
        library_functions_str = " ".join(re.findall("import (.*?) ", import_element)).split(".")

        # fetch library:
        library_name = " ".join(library_functions_str[:-1])
        
        # Fetch imported functions
        function_list = library_functions_str[-1:]

    # check for scenario 3
    elif "import " in import_element:

        # remove leading text before import
        all_functions = " ".join(import_element.split('import')[1:]) 

        # Fetch library:
        library_name = " ".join(re.findall("[a-zA-Z_]+", all_functions, re.DOTALL))

        # No imported functions
        function_list = []        

    return library_name, function_list 



def get_imports(code_list, file_name, file_path):
        
    """
    Extract imported libraries and functions
    """
    
    # Output list:    
    values_dict = {}
    
    # Go through all elements:
    for element in code_list:

        # fetch type of structure:
        code_type = element['element_type']   

        # Identify source form which the functions/classes are imported
        if (code_type == 'Import' or code_type == 'Import multiline'):
            
            # fetch code
            code_str = element['element_code']
            
            # extract imports:
            library_name, function_list = extract_import_values(code_str)
            
            # Add or append values to dict
            values_dict[library_name] = values_dict.get(library_name, []) + function_list
            
    #-------------------------------------
    #output dictionary:
    import_dict = {
        'File_name' : file_name,
        'File_location' : file_path,
        'Function_values': values_dict
    }
        
    return import_dict



#================================================================
def profile_elements(code_list):
    
    """
    Code that profiles each element and extracts information.
    """
    
    # Output list of all elements
    element_profile_list = []
    dependency_name_dict = {}
    
    # Go through all elements in a dict:
    for element in code_list:
        
        #-------------------------------------
        # Fetch information:
        code_str = element['element_code']  # code
        element_type = element['element_type'] # element type
        element_name = element['element_name'] # object name
        file_name = element['file_name'] # file name:
            
        if code_str.strip() != '' and code_str.strip() != "\n": # if code not empty

            #-------------------------------------
            # Process functions and classes
            if (element_type == 'Function' or element_type == 'Class'):
                
                #-------------------------------------
                # add values:  
                element['Values'] = extract_element_values(code_str, element_type)
                
                #-------------------------------------
                # output:
                element_profile_list.append(element)   
                
                #-------------------------------------
                # Store values of functions for identyfiying dependencies
                dependency_name_dict[element_name] = dependency_name_dict.get(element_name, []) + [file_name]

            #-------------------------------------
            # Process code
            elif (element_type == 'Code'):
                values_dict = ''

                #-------------------------------------
                # add values:  
                element['Values'] = ''

                #-------------------------------------
                # output:
                element_profile_list.append(element)        
                
                #-------------------------------------
                # Store values of functions for identyfiying dependencies
#                 dependency_name_dict[element_name] = dependency_name_dict.get(element_name, []) + [file_name]

            
    return element_profile_list, dependency_name_dict


def extract_element_values(code_str, element_type):
    """
    Helper function that extracts information about functions/classes.
    """
    
    import re
    
    # Additional values dictionary:
    values_dict = {
        'Input_var' : [],
        'Code_comments' : [],
        'Output_var' : []
    }    
    
    # Get Inputs
    if element_type  == 'Function':
        input_str = ''.join(re.findall('def (.*?):', code_str, re.DOTALL)) # for functions
    elif element_type  == 'Class':
        input_str = ''.join(re.findall('class (.*?):', code_str, re.DOTALL)) # for classes
    
    input_list = re.findall("[a-zA-Z_]+", input_str)
            
    # Get Outputs
    output_str = ''.join(re.findall('return (.*?)', code_str, re.DOTALL))
    output_list = re.findall("[a-zA-Z_]+", output_str)
    
    # Add comment string
    comment_list = re.findall(r'#[^\r\n]*', output_str)    
    
    # Output
    values_dict['Input_var'].extend(input_list)
    values_dict['Code_comments'].extend(comment_list)
    values_dict['Output_var'].extend(output_list)
    
    return values_dict


#================================================================
def get_dependencies(code_list, dependency_name_dict, import_dict):
    
    """
    Function searches for all elements and get their order of invocation and input parameters.
    """
    
    import re
    
    # Output list:
    dependency_list = []
    
    # Go through all elements in dictionary:
    for element in code_list:
            
        # Fetch values:
        code_type = element['element_type'] # type of structure
        if code_type == 'Function' or code_type == 'Class' or code_type == 'Code':
        
            # fetch values
            elem_name = element['element_name'] # element name 
            file_name = element['file_name']    # file name:
            code_str = element['element_code']  # code string
            if code_str.strip() == '': # skip empty strings
                continue    
            
            # Create search pattern:
            search_list_cleaned = [x for x in dependency_name_dict.keys() if x != elem_name]
            search_list_str = '(' + r'\(.*?\))|('.join(search_list_cleaned) + '\(.*?\))' 
            if search_list_cleaned == []: # Skip if list is empty
                continue  
            
            # Find all occurences in code
            found_values = re.findall(search_list_str, code_str, re.DOTALL)
            if found_values == []: # Skip if nothing found
                continue  
            
            # Go through all occurences, identify order of invocation and input parameters
            order_num = 1
            for row in found_values:
                for component in list(row):
                    if component != '':
                        # Reset to avoid cross contamination
                        file_dependent_name = ''
                        
                        # Fetch dependent function name
                        elem_dependent_name = re.findall('(.*?)\(', component, re.DOTALL)[0]

                        # fetch dependent input params
                        input_param = re.findall('\((.*?)\)', component, re.DOTALL)[0].split(',')
                        input_param_clean = [i.replace('\n','').strip() for i in input_param]   # Clean code from newline and empty spaces      

                        # fetch dependent library
                        dependent_library_name = dependency_name_dict[elem_dependent_name]
                        
                        # Check if dependent function is in one library: 
                        if len(dependent_library_name) == 1:
                            file_dependent_name = dependent_library_name[0]
                            
                        # if dependent function has multiple sources:
                        else:
                            
                            # Consult import statements in file:
                            import_value = import_dict[file_name]['Function_values'] # fetch all imported 
                            for key, value in import_value.items():
                                
                                # find match by function name
                                if elem_dependent_name in value:
                                    
                                    # pull library name:
                                    library_name = key.split('.')[-1]+ '.py'
                                    
                                    # Cross reference with sources:
                                    if library_name in dependent_library_name:
                                        file_dependent_name = library_name
                                    
                            # No match - check if func declared in source file
                            if file_dependent_name == '' and file_name in dependent_library_name:
                                 file_dependent_name = file_name
                                    
                            # Otherwise put all sources
                            elif file_dependent_name == '':
                                file_dependent_name = dependent_library_name

                        # output information
                        output_dict = {'function_from': elem_name,
                                       'function_to': elem_dependent_name,
                                       'file_from': file_name,
                                       'file_to': file_dependent_name,
                                       'values' : {'Invocation_order': order_num,
                                                   'Input_parameters': input_param_clean}
                                      }
                        dependency_list.append(output_dict)

                        # increase order
                        order_num += 1

    return dependency_list

