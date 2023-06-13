
#===============================================================
# Plotting Graph:

def get_edge_trace(G):
    
    import plotly.graph_objects as go
    
    # Edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(-y0)
        edge_y.append(-y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines') 
    
    return edge_trace


def get_node_trace(G):
    import plotly.graph_objects as go
    
    # Node positions
    list_node_x = []
    list_node_y = []
    
    # File properties
#     list_file_name = []
#     list_file_location = []
#     list_file_lines = []
    
    # Node properties
    list_node_id = []
#     list_node_type = []
#     list_node_code = []
    
    # Node text 
    list_node_text = []
    
    # node shape
    node_shape = []
    
    for node in G.nodes():
        # Node positions
        x, y = G.nodes[node]['pos']
        list_node_x.append(x)
        list_node_y.append(-y)
        
        # File properties
#         file_name = G.nodes[node]['file_name']
        file_location = G.nodes[node]['file_location']
#         file_lines = G.nodes[node]['file_lines']  
        
        # Node properties
        node_name = G.nodes[node]['node_name']
        node_type = G.nodes[node]['node_type']
#         node_code = G.nodes[node]['node_code']

        # Store node_id
        list_node_id.append(node) 
        
        # Get additional attributes and text:
        if node_type == 'Function' or node_type == 'Class': 
            element_input = str(G.nodes[node]['attributes_input']).replace(', ',',<br> ')
            element_comments = G.nodes[node]['attributes_comments']
            element_output = str(G.nodes[node]['attributes_output']).replace(', ',',<br> ')
            
            # Text
            node_text = '<b>Name:</b> {0}<br><b>Type:</b> {1}<br><b>File Location:</b> {2}<br><b>Input:</b> {3}<br><b>Output:</b> {4}'.format(node_name, node_type, file_location, element_input, element_output)
        else:
            # Text
            node_text = '<b>Name:</b> {0}<br><b>Type:</b> {1}<br><b>File Location:</b> {2}'.format(node_name, node_type, file_location)
        list_node_text.append(node_text)
            
        # Assign shapes
        if node_type == 'Function':
            node_shape.append('circle')
        elif node_type == 'Class':
            node_shape.append('star')    
        else:
            node_shape.append('square')    


    # Create text 
    node_trace = go.Scatter(
        # Coordinates
        x=list_node_x, y=list_node_y,
        # Text
        hoverinfo="text",
        text = list_node_text,
        # Meta
        meta = list_node_id,
        # Shapes
        mode='markers',
        marker_symbol=node_shape,        
        marker_line_width=2, marker_size=8,
        marker_line_color="midnightblue", 
        marker_color="lightskyblue"      
        
    )
    
    return node_trace


def plot_graph(edge_trace, node_trace):
    import plotly.graph_objects as go
    
    # plot
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                 showlegend=False,
                 margin=dict(b=20,l=5,r=5,t=40),
                 xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                 yaxis=dict(showgrid=True, gridcolor='silver', griddash = "dot", dtick = 1,  
                            zeroline=False, showticklabels=False)
             )
                   )
    
    
    return fig



#===============================================================
# Creating table:

def get_code_table(G):
    import pandas as pd
    
    # Output dict
    df_dict = {
               'Name' : [],
               'Code' : [],
               'Dependencies' : [],
        'Node ID' : []
              }
    
    for node in G.nodes():        
        df_dict['Node ID'].append(node)

        node_name = 'Name: {0}\nFile location: {1}\nFile Lines: {2}'.format(G.nodes[node]['node_name'], G.nodes[node]['file_location'], G.nodes[node]['file_lines'])

        df_dict['Name'].append(node_name)
        df_dict['Code'].append(G.nodes[node]['node_code'])
        
        dependency_string = get_sucessors(G, node)
        df_dict['Dependencies'].append(dependency_string)
    
    df = pd.DataFrame(df_dict)
    return df

def get_sucessors(G, node):
    import networkx as nx
    
    # fetch sucessors:
    successors_list = list(G.successors(node))
    invocation_properties = {} 
    
    # extract information about sucesssor invocation
    for sucessor in successors_list:
        invocation = G.edges()[node, sucessor]['invocation']
        function_to_name = G.edges()[node, sucessor]['edge_to']
        function_to_location = G.edges()[node, sucessor]['file_to']
        
        for element in invocation:
            input_param = str(element['Input_parameters']).replace(', ', ',\n ')
            invocation_properties[element['Invocation_order']] = 'Order: ' + str(element['Invocation_order']) + ',\nName: ' + function_to_name + ',\nFile location: ' + function_to_location + ',\nParameters: ' + input_param + '\n'
    
    # Reorder based on invocation and prepare description:
    
    output_str = ''
    for k, v in invocation_properties.items(): 
        output_str = output_str + v +'\n'
    
    return output_str



def draw_table(df):
    
    from dash import dash_table
    
    table = dash_table.DataTable(id='table',
                                 columns=[{'name': i, 'id': i} for i in df.columns], 
                                 data=df.to_dict('records'),
                                 # Filtering
                                 filter_action='native',
                                 filter_query='',
                                 
#                                  hidden_columns=['Node ID'],
                                 
                                 # Styles
                                 style_header={'fontWeight': 'bold',
                                               'backgroundColor': 'rgb(48, 84, 150)',
                                               'color': 'white'},
                                 style_filter={'backgroundColor': 'rgb(142, 169, 219)',
                                               'color': 'white'},
                                 style_cell={'backgroundColor': 'rgb(217, 225, 242)',
                                             'textAlign': 'left',
                                             'vertical-align' : 'top',
                                             'color': 'black'
                                            },
                                 # Column size
                                 style_cell_conditional=[{'if': {'column_id': 'Node ID'}, 
                                                          'max-width': '0vh'},
                                                         {'if': {'column_id': 'Name'}, 
                                                          'Width': '10vh',
                                                          'overflow-wrap': 'anywhere',
                                                          'whiteSpace':'pre-wrap', 
                                                          'height':'auto'},
                                                         {'if': {'column_id': 'Code'}, 
                                                          'Width': '70vh',
                                                          'white-space': 'pre-wrap'},
                                                         {'if': {'column_id': 'Dependencies'}, 
                                                          'Width': '20vh',
                                                          'overflow-wrap': 'anywhere',
                                                          'whiteSpace':'pre-wrap', 
                                                          'height':'auto'}],
                                 # Table size
                                 fixed_rows={'headers': True},
                                 style_table={'overflowY': 'scroll', 
                                              'border': 'thin lightgrey solid',
                                              'width': '100vw', 
                                              'height': '50vh'}
                                )      
    return table

#===============================================================
# Adding interactions:

#  Scatter -> Table interaction
def update_query(selectedData):    
    
    # Get list of selected Step IDs
    x_values = []
    for elements in selectedData['points']:
        if 'meta' in elements:
            if elements['meta'] not in x_values:
                x_values.append( elements['meta'] )  
             
    # Generate filter query
    query =''
    if len(x_values) != 0:
        # 2.1 Formulate query
        for filter_value in x_values:
            query = query + '{Node ID} = ' + str(filter_value) + ' or '
        # 2.2. Remove last or
        query = ' '.join(query.split(' ')[:-2])
    
    return query


# Table -> Scatter interaction
def update_scatter(filter_query, fig_net, df):
 
    import copy
    
    # 1. Make copy of df and figure
    dff = copy.copy(df) 
    fig_copy = copy.copy(fig_net) 

    # 2. Fetch step ids based on filter query
    filtering_expressions = filter_query.split(' && ')
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]   
        elif operator == 'datestartswith':
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]
    step_list = list(dff['Node ID'])
    
    # 3. Select figure traces that are in the filtered data
    selected_points = []
    fig_data = fig_copy['data'] # fetch data from figure
    
    # fetch meta list:
    meta_list = list(fig_data[1]['meta'])
    #loop through all elements in list
    for i in range(len(meta_list)):
        if meta_list[i] in step_list:
            selected_points.append(i)   
    
    # 4. Update figure
    fig_copy.update_traces(selectedpoints = selected_points)

    return fig_copy

# Filter query syntax split
def split_filter_part(filter_part):
    # Operator dict
    operators = [['ge ', '>='],
                 ['le ', '<='],
                 ['lt ', '<'],
                 ['gt ', '>'],
                 ['ne ', '!='],
                 ['eq ', '='],
                 ['contains '],
                 ['datestartswith ']]
        
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                return name, operator_type[0].strip(), value

    return [None] * 3