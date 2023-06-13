#======================================================================
# libraries
import pickle                                             # Loading data
import networkx as nx                                     # Graph
import dash                                               # Plots
from dash import Dash, dcc, html, Input, Output
from functions.plot_functions import *                              # Invocation functions

#======================================================================
# load Element profiles
with open('output/5.graph.pkl', 'rb') as f: 
    G = pickle.load(f) 

#======================================================================    
# Create traces   
# network trace
edge_trace = get_edge_trace(G)
node_trace = get_node_trace(G)
fig_net = plot_graph(edge_trace, node_trace)
# Table trace
df = get_code_table(G)
fig_table  = draw_table(df)    
    
#======================================================================    
# Dash object

# Server start
app = Dash()

# Dash plot
app.layout = html.Div(children = [
                       # Reset button
                          html.Button('Reset Graphs', 
                                      id='reset_button', 
                                      n_clicks=0,
                                      style={'height': '3vh'}), 
                       # Plot
                          dcc.Graph(id='network', 
                                 figure=fig_net,
                                 style={'width': '100vw',
                                       'height': '43vh'}),
                       
                       # Table
                          fig_table                     
                      ])                   
    
# Callbacks
@app.callback([Output('reset_button','n_clicks'), Output('table', 'filter_query'), Output('network', 'selectedData'), Output('network', 'figure')],
              [Input('reset_button','n_clicks'), Input('table', 'filter_query'), Input('network', 'selectedData')])
def update_figures(n_clicks, filter_query, selectedData):
    
    # 1. If reset is clicked - restart table and scatter
    if n_clicks is not None and n_clicks > 0:  
        return 0, '', None, fig_net  
    
    # 2. If filter is applied to Network -> update Table
    elif selectedData is not None:
        selected_query = update_query(selectedData)
        if filter_query != '':            
            full_query = '(' + filter_query + ') and (' + selected_query + ')' # Data selected based on query and scatter
            return dash.no_update, full_query, dash.no_update, dash.no_update
        else:
            return dash.no_update, selected_query, None, dash.no_update
        
    # 3. If filter is applied to Table - update Network
    elif filter_query is not None and filter_query != '': 
        fig_updated = update_scatter(filter_query, fig_net, df)
        return dash.no_update, dash.no_update,  None, fig_updated
    
    # 4. If filter query is reset - update Network
    elif filter_query == '' and selectedData is None:
        return dash.no_update, dash.no_update,  None, fig_net        
    
    # 5. No change
    else:
        raise dash.exceptions.PreventUpdate

app.run_server(debug=False)    