# Python-Code-Parser

The purpose of this repository is to process all codes of the specified format (e.g. .py files) and visualise all dependencies between the scripts. 

For this purpose, there are 2 jupyter files: 
- **Code Parser** - contains a script that generates 3 pickle files:
    - code_dict - a dictionary of lists containing a breakdown of each script into elements - import statements, functions, classes or raw code - as well as information about the file location and lines of the code. i
    - element_profile - a list of dictionaries containing the profile of the element in question - name, type, location, raw code, as well as additional elements - input/output (for function and classes), comments, etc.
    - element_dependencies - a list of dictionaries containing information about the dependencies between two elements, the input parameters as well as the order in which these elements are invoked.
- **Code Visualizer** - this script creates a interactive dashboard containing the visualization of the execution process as well as a lookup table of the code. 