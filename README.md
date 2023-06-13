# Python-Code-Parser

The purpose of this repository is to process all codes of the specified format (e.g. .py files) and visualise all dependencies between the scripts. 

For this purpose, there are 3 scripts: 
- **Data Structures** - contains a script that generates 5 pickle files:
    - code_list - a list of dictionaries containing a breakdown of each element in the code (functions, classes, import statements or raw code) with information about the file location and its lines in the code.
    - import_dict - a dictionary containing information about all import statements used in the codes.
    - element_profile - a list of dictionaries containing the profile of the element in question - name, type, location, raw code, as well as additional information - input/output components (for functions and classes), comments, etc.
    - element_dependencies - a dictionary containing information about the dependencies between two elements, the input parameters as well as the order in which these elements are invoked.
    - graph - a networkx object containing information about the objects in the project, dependencies between them as well as any other information related to them. Is a combination of the elements described in points 1-4.
- **Plots** - this script creates a interactive dashboard containing the visualization of the execution process as well as a lookup table of the code. 
- **Search** - contains a script that searches for pre-defined patterns:
    - input statements - any elements in the code that require data from the outside, e.g. read_excel, read_pickle, etc.
    - output statements - any elements that store or print data - e.g. loggers, print statements, to_csv, etc.
    - custom statements - any other patterns that the user needs to find in the code. The search pattern can be configured in the settings file. 
    This script returns tables for each group of patterns containing information about the location of the file, lines in which this pattern was found as well as the line itself.