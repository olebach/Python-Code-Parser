def create_graph(output_element_profile_list, dependency_list, output_import_dict, rootdir, file_extention):
    
    import networkx as nx                                      # Graph
    
    #-----------------------------
    # Create empty graph
    G = nx.DiGraph()

    #-----------------------------
    # Add nodes
    for node in output_element_profile_list:

        # Fetch node properties:
        file_name  = node['file_name']
        file_location = node['file_location']
        file_lines = node['file_line_number']
        node_name = node['element_name'].lower()
        node_type = node['element_type']
        node_code = node['element_code']
        node_attributes = node['Values'] 
        node_id = file_name + '|' + node_name

        # check if node already exists:
        if G.has_node(node_id):
            # fetch code element
            node_code_prev = G.nodes[node_id]['node_code']
            # Extend code element
            G.nodes[node_id]['node_code'] = node_code_prev + '\n' + node_code

        # otherwise create node:
        else:

            # Get optional attributes:
            if node_type == 'Code':
                element_input = ''
                element_comments = ''
                element_output = ''
            elif node_type == 'Function' or node_type == 'Class':    
                element_input = node_attributes['Input_var']
                element_comments = node_attributes['Code_comments']
                element_output = node_attributes['Output_var']

            # output results
            G.add_node(node_id,
                       # Attributes
                       file_name = file_name,
                       file_location = file_location,
                       file_lines = file_lines,
                       node_name = node_name,
                       node_type = node_type,
                       node_code = node_code,
                       attributes_input = element_input,
                       attributes_comments = element_comments,
                       attributes_output = element_output
                      )      

    #-----------------------------
    # Add edges to graph
    for edges in dependency_list:

        # Fetch
        edge_from = edges['function_from'].lower()
        edge_to = edges['function_to'].lower()
        file_from = edges['file_from']
        file_to = edges['file_to']
        edge_from_id = file_from + '|' + edge_from
        edge_to_id = file_to + '|' + edge_to   


        # check if edge already exists
        if G.has_edge(edge_from_id, edge_to_id):
            # Fetch attributes
            attribute = G[edge_from_id][edge_to_id]["invocation"]
            # Extend values
            attribute.append(edges['values']) 
            # Modify edge
            G[edge_from_id][edge_to_id]["invocation"] = attribute

        else:
            # Create edge
            G.add_edge(edge_from_id, edge_to_id, 
                       # Attributes
                       invocation = [edges['values']],
                       edge_from = edge_from,
                       edge_to = edge_to,
                       file_from = file_from,
                       file_to = file_to
                      )

    # Add import information
    G = add_imports(G,
                    import_dict = output_import_dict,
                    rootdir = rootdir,
                    file_extention = file_extention)


    # Add positions to the graph
    pos = get_coordinates(G)
    nx.set_node_attributes(G, pos, 'pos')     
    
    return G


#===============================================================
# Plotting coordinates:
def get_coordinates(G):

    import pandas as pd
    
    # Output
    
    node_order_dict = {}
    order = 1
    
    
    # Determine all source nodes in order of importnce:
    source_list = source_node_order(G)  
    
    # Traverse through all source nodes and fetch depth nodes in 
    for source_node in source_list:
        # Output source node:
        node_order_dict[source_node] = str(order)

        # Get subsequent nodes
        node_order_dict = traverse_node(G, source_node, node_order_dict)        

        # increase order num
        order += 1
        
        
    # sort elements in order
    df = pd.DataFrame.from_dict(node_order_dict.items()).rename(columns={0: "Node", 1: "order"}).sort_values("order")

    # Start coord
    lag_y_coord = 0
    x_coord = 0

    # Output dict
    pos = {}

    for index, row in df.iterrows():
        # get node name
        node = row["Node"]

        # get x coordinate
        y_coord = len(row["order"].split("."))

        # get y coordinate
        if lag_y_coord >= y_coord:
            x_coord += 1

        # Output
        pos[node] = (x_coord, y_coord)

        lag_y_coord = y_coord

    return pos


def source_node_order(G):
    
    import networkx as nx
    
    # output 
    node_len_dict = {}
    
    #fetch all source nodes:
    source_nodes = sorted([node for node in G.nodes() if G.in_degree(node) == 0])
    
    for source in source_nodes:
        # determine size of traversal path
        node_len_dict[source] = len(nx.dfs_tree(G, source))
        
    # reorder list based on length of elements
    return [k for k, v in sorted(node_len_dict.items(), key=lambda item: item[1], reverse=True)]


def traverse_node(G, source_node, node_order_dict):
    # Fetch all neighbours for node
    node_neighbours = list(G.neighbors(source_node))
    
    if node_neighbours == []:
        return node_order_dict
    
    # Output string
    neighbour_list = []
     
    for node in node_neighbours:
        # Check if node in dict
        if node in list(node_order_dict.keys()):
            continue
        
        # Identify node order
        node_order = G[source_node][node]["invocation"][0]['Invocation_order']
        
        # Inherit previous node number
        prev_number = node_order_dict[source_node]
        
        #Store value:
        node_order_dict[node] = '{}.{}'.format(prev_number, node_order)
        
        # Repeat story for this node:
        node_order_dict = traverse_node(G, node, node_order_dict)
        
    return node_order_dict


#================================================================
# Getting import information
def add_imports(G, import_dict, rootdir, file_extention):
    
    """
    Cross references the import statements with the code in each node
    """
    
    # Invocation functions
    from functions.processing_functions import get_filepaths
    
    # Get list of custom functions
    full_file_paths = get_filepaths(rootdir, file_extention) # list of all subdirectories + file names
    path_list = [folder_directory.replace(rootdir+'\\', '').replace('.py', '').replace('\\', '.') for folder_directory in full_file_paths]

    
    for nodes in G.nodes():
        # fetch function name
#         node_name = G.nodes()[nodes]['node_name']
        file_name = G.nodes()[nodes]['file_name'] # settings.py
        node_code = G.nodes()[nodes]['node_code']
#         file_location = G.nodes()[nodes]['file_location']

        # fetch library names
        library_dict = import_dict[file_name]['Function_values']

        # fetch aliases
        alias_dict = import_dict[file_name]['library_aliases']
    
    
        # Fetch all libraries found in file
        found_libraries = []
        for key, value in library_dict.items():
            if not value:
                # determine what to search:
                if key in alias_dict.keys():
                    # Check for alias
                    search_value = alias_dict[key][0]
                else:
                    # Check for library
                    search_value = key 

                # Find and output
                if search_value in node_code:
                    found_libraries.append(key)

            else:
                # Check for functions
                for v in value:
                    search_value = v  # determine what to search
                    if search_value in node_code: 
                        found_libraries.append(key)

        # remove duplicates
        found_libraries = list(dict.fromkeys(found_libraries))
        
        # Compile the lists
        python_libraries = [library for library in found_libraries if library not in path_list]
        custom_libraries = [library for library in found_libraries if library in path_list]
    
        # output results
        G.nodes()[nodes]['python_libraries'] = python_libraries
        G.nodes()[nodes]['custom_libraries'] = custom_libraries
        
    return G


