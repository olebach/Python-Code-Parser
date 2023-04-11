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
    
    
    
    
def read_input(path):
    """
    Open file and read the code into a string
    """
    
    # Read whole file to a string
    text_file = open(path)    
    data = text_file.read()
    text_file.close()
    
    return data






def process_elements(code_strings, file_name, file_path):

    """
    This function searches for text patterns of functions, imports and classes and breaks the code into sections
    """
    
    import re
    
    #--------------------------------------------------------
    # 0 Output dict:
    element_dict = {
        'file_name'     : [],
        'file_location' : [],
        'element_line_number' : [],
        'element_name'  : [],
        'element_type'  : [],
        'element_code'  : []
    }
    
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
        elif multiline_import == 1 and ')' in line_clean:
            # reset import
            multiline_import = 0

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
        elif not ((line_clean.startswith('    ') or line_clean.strip() == '' or line_clean.strip() == '):') and (lag_line_type == 'Function' or lag_line_type == 'Class')):
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
            # output everything retained:
            element_dict['file_name'].append(file_name)
            element_dict['file_location'].append(file_path) 
            if lag_line_num != (line_num-1):
                element_dict['element_line_number'].append('Lines: '+str(lag_line_num)+'-'+str(line_num-1))
            else:
                element_dict['element_line_number'].append('Lines: '+str(lag_line_num))
            element_dict['element_name'].append(lag_element_name)
            element_dict['element_type'].append(lag_line_type)
            element_dict['element_code'].append(lag_line)   
            
            # Get new lagged values:
            lag_element_name = element_name
            lag_line_type = line_type
            lag_line = line
            lag_line_num = line_num
              
        #--------------------------------------------------------
        # Increase line number:
        line_num +=1
        
    #--------------------------------------------------------
    # 5. Output final values:
    element_dict['file_name'].append(file_name)
    element_dict['file_location'].append(file_path) 
    if lag_line_num != (line_num-1):
        element_dict['element_line_number'].append('Lines: '+str(lag_line_num)+'-'+str(line_num-1))
    else:
        element_dict['element_line_number'].append('Lines: '+str(lag_line_num))
    element_dict['element_name'].append(lag_element_name)
    element_dict['element_type'].append(lag_line_type)
    element_dict['element_code'].append(lag_line)      

    
    return element_dict



def parse_elements(elements_dict):
    
    """
    Code that profiles each element and extracts information.
    """
    
    # Output list of all elements
    element_profile_list = []
    dependency_name_list = []
    values_dict = ''
    
    # Go through all elements in a dict:
    for i in range(len(elements_dict['element_code'])):
        
        #-------------------------------------
        # Fetch information:
        # code info
        code_str = elements_dict['element_code'][i]
                
        # element type
        element_type = elements_dict['element_type'][i]
        
        # Fetch object name:
        element_name = elements_dict['element_name'][i]
                
        if code_str.strip() != '' and code_str.strip() != "\n":

            #-------------------------------------
            # Process functions and classes
            if (element_type == 'Function' or element_type == 'Class'):

                # extract profile:
                values_dict = extract_element_values(code_str, element_type)
                
                # Store values of functions for identyfiying dependencies
                dependency_name_list.append(element_name)
                
            #-------------------------------------  
            # Prosess input structures
            elif (element_type == 'Import' or element_type == 'Import multiline'):
                # extract imports:
                values_dict = extract_import_values(code_str)

            #-------------------------------------
            # Process code
            elif (element_type == 'Code'):
                values_dict = ''

            #-------------------------------------
            #output dictionary:
            element_profile_list.append(
            {
                'File_name' : elements_dict['file_name'][i],
                'File_location' : elements_dict['file_location'][i],
                'File_lines' : elements_dict['element_line_number'][i],
                'Function_name' : element_name,
                'Function_type' : element_type,
                'Function_code' : code_str,      
                'Function_values': values_dict
            }
            )        
            
    return element_profile_list, dependency_name_list





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
    
    
    
def extract_import_values(code_str):
    
    """
    Extract imported libraries and functions
    """
    
    import re
    
    # Clean code string:
    import_element = re.sub('#(.*)\n?', '', code_str) # Comments
    import_element = re.sub(" as (.*)","", import_element) # Aliases
    import_element = re.sub("\n","", import_element)
        
        
    # Identify scenarios:
    #     - from <library> import <function> or from <library> import (<function>,<function>)
    #     - import <library>.<library>.<function>
    #     - import <library>
    
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

    return {library_name: function_list}    





def get_dependencies(element_dict, dependency_name_list):
    
    """
    Function searches for all elements and get their order of invocation and input parameters.
    """
    
    import re
    
    # Output list:
    dependency_list = []
    
    # Go through all elements in dictionary:
    for i in range(len(element_dict['element_code'])):

        # fetch type of structure:
        code_type = element_dict['element_type'][i]  
        
        if code_type == 'Function' or code_type == 'Class' or code_type == 'Code':
            
            # fetch code string
            code_str = element_dict['element_code'][i]
            if code_str.strip() == '':
                continue        
        
            # Fetch element name:
            if code_type == 'Function' or code_type == 'Class':
                elem_name = element_dict['element_name'][i]
            else: 
                elem_name = element_dict['file_name'][i]
                
            # Create search string:
            search_list_cleaned = [x for x in dependency_name_list if x != elem_name] # Create list without current function
            search_list_str = '(' + r'\(.*?\))|('.join(search_list_cleaned) + '\(.*?\))' # Generate search pattern
            
            # Find all occurences in code
            found_values = re.findall(search_list_str, code_str, re.DOTALL)
            if found_values == []:
                continue  
                
            # Go through all occurences, identify order of invocation and input parameters
            order_num = 1
            for row in found_values:
                for element in list(row):
                    if element != '':
                        
                        # Fetch function name
                        func_name = re.findall('(.*?)\(', element, re.DOTALL)[0]
                        
                        # fetch input params
                        input_param = re.findall('\((.*?)\)', element, re.DOTALL)[0].split(',')
                        
                        # Clean code from newline and empty spaces
                        input_param_clean = [i.replace('\n','').strip() for i in input_param]         
                        
                        # output information
                        output_dict = {'function_from': elem_name,
                                       'function_to': func_name,
                                       'values' : {'Invocation_order': order_num,
                                                   'Input_parameters': input_param_clean}
                                      }
                        dependency_list.append(output_dict)
                        
                        # increase order
                        order_num += 1
            
    return dependency_list



