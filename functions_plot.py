def get_coordinates(G, source_node):

    import pandas as pd
    
    # Output source node:
    node_order_dict = {source_node : '1'}

    # Get subsequent nodes
    node_order_dict = traverse_node(G, source_node, node_order_dict)

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
        y_coord = len(row["order"])

        # get y coordinate
        if lag_y_coord >= y_coord:
            x_coord += 1

        # Output
        pos[node] = (x_coord, y_coord)

        lag_y_coord = y_coord

    return pos




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





def get_code_table(G):
    import pandas as pd
    
    # Output dict
    df_dict = {'file_name' : [],
               'file_desc' : [],
               'element_code' : []
              }
    
    for node in G.nodes():        
        df_dict['file_name'].append(node)
        df_dict['file_desc'].append(G.nodes[node]['file_location'] + '\n' + G.nodes[node]['file_lines'])
        df_dict['element_code'].append(G.nodes[node]['element_code'])
    
    df = pd.DataFrame(df_dict)
    return df


def draw_table(df):
    
    from dash import dash_table
    
    table = dash_table.DataTable(id='table',
                                 columns=[{'name': i, 'id': i} for i in df.columns], 
                                 data=df.to_dict('records'),
                                 # Filtering
                                 filter_action='native',
                                 filter_query='',
                                 # Styles
                                 style_header={'fontWeight': 'bold',
                                               'backgroundColor': 'rgb(48, 84, 150)',
                                               'color': 'white'},
                                 style_filter={'backgroundColor': 'rgb(142, 169, 219)',
                                               'color': 'white'},
                                 style_cell={'backgroundColor': 'rgb(217, 225, 242)',
                                             'textAlign': 'left',
                                             'vertical-align' : 'top',
                                             'color': 'black',
                                             'white-space': 'pre'},
                                 # Column size
                                 style_cell_conditional=[{'if': {'column_id': 'file_name'}, 'width': '5%'},
                                                         {'if': {'column_id': 'file_desc'}, 'width': '10%'},
                                                         {'if': {'column_id': 'element_code'}, 'width': '85%'}],
                                 # Table size
                                 fixed_rows={'headers': True},
                                 style_table={'overflowY': 'scroll', 
                                              'border': 'thin lightgrey solid',
                                              'width': '100vw', 
                                              'height': '50vh'}
                                )      
    return table



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
    
     # Nodes
    list_node_x = []
    list_node_y = []
    list_node_text = []
    node_text = []
    node_shape = []
    #node_color = []
    node_name = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        list_node_x.append(x)
        list_node_y.append(-y)
        
        # Get main attributes:
        node_file = G.nodes[node]['file_name']
        node_location = G.nodes[node]['file_location']
        node_type = G.nodes[node]['element_type']
        node_code = G.nodes[node]['element_code']
    
        # Get additional attributes:
        if node_type == 'Function' or node_type == 'Class': 
            element_input = G.nodes[node]['element_input']
            element_comments = G.nodes[node]['element_comments']
            element_output = G.nodes[node]['element_output']
            # Text
            node_text = '<i>Name: {0}<br>File Location: {1}<br>Input: {2}<br>Output: {3}'.format(node, node_location, element_input, element_output)
        else:
            # Text
            node_text = '<i>Name: {0}<br>File Location: {1}'.format(node, node_location)
   
        node_name.append(node)
        list_node_text.append(node_text)
            
        # Assign shapes
        if node_type == 'Function':
            node_shape.append('circle')
        elif node_type == 'Class':
            node_shape.append('star')    
        else:
            node_shape.append('square')    
        # Assign color
        #node_color = G.nodes[node]['output_fields']
        

    # Create text 
    node_trace = go.Scatter(
        x=list_node_x, y=list_node_y,
        mode='markers',
        text = list_node_text,
        marker_symbol=node_shape,
        
        marker_line_width=2, marker_size=8,
        marker_line_color="midnightblue", 
        marker_color="lightskyblue",
        
        # Meta
        meta = node_name
    )
    
    return node_trace


def plot_graph(edge_trace, node_trace):
    import plotly.graph_objects as go
    
    # plot
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
#                  width= 1500,
#                  height= 1000,
                 showlegend=False,
                 margin=dict(b=20,l=5,r=5,t=40),
                 xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                 yaxis=dict(showgrid=True, gridcolor='silver', griddash = "dot", dtick = 1,  
                            zeroline=False, showticklabels=False)
             )
                   )
    
#     fig.update_layout(xaxis_range=[-5,100])
#     fig.update_layout(yaxis_range=[18,0])
    
    return fig



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
            query = query + '{file_name} = ' + str(filter_value) + ' or '
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
    step_list = list(dff['file_name'])
    
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


#======================================================================
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