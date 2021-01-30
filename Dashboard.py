import dash
import numpy as np
import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import json

app = dash.Dash()
x = "G2"
y = "G3"
df =  pd.read_csv("Dataset.csv")
names = df.columns.values
# Turn No's and Yes' to 0's and 1's
orig_df = df.copy(True)
d = {'no':0,'yes':1}
df['activities'] = [d[x[1:-1]] for x in df['activities'].tolist()]
df['paid'] = [d[x[1:-1]] for x in df['paid'].tolist()]
df['internet'] = [d[x[1:-1]] for x in df['internet'].tolist()]

# Create Correlation Matrix
corr_subset = df[['age','studytime','failures','paid','activities','internet','absences','G1','G2','G3']]
names = corr_subset.columns.values
correlation = corr_subset.corr()
corr_color = ['rgb(62, 0, 250)','rgb(185, 132, 251)','rgb(253, 253, 254)','rgb(255, 158, 131)','rgb(255, 40, 0)']
corrFig = px.imshow(correlation,color_continuous_scale=corr_color,zmin = 1,zmax =1,color_continuous_midpoint=0.0)
corrFig.update_layout(title = "10x10 Correlation Matrix")

# Create Parallel Coordinate Display
corrCol = []
cols = []
for col in correlation:
    corrCol.append(sum([abs(x)for x in correlation[col].tolist()]))
    cols.append(col)
corrCol,cols = zip(*sorted(zip(corrCol,cols),reverse=True))
ordered_axes = [cols[0],cols[1]]
remaining = {'G2','G3','G1','studytime','activities','internet','absences','age','failures','paid'} - {cols[0],cols[1]}
while(len(remaining) > 1):
    last = ordered_axes[-1]
    max_rem = 0
    max_name = ""
    for rem in remaining:
        c_val = abs(correlation.loc[last,rem].item())
        if (c_val > max_rem):
            max_rem = c_val
            max_name = rem
    ordered_axes.append(max_name)
    remaining.remove(max_name)
ordered_axes.append(remaining.pop())
pcd_set = df[ordered_axes]
pcdFig = px.parallel_coordinates(pcd_set,dimensions = ordered_axes)

# Create Scatter
scatter =  px.scatter(df,x=x,y=y,title="The Effect of " + x + " on " + y,color_discrete_sequence=[px.colors.sequential.Blugrn[4]])
scatter.update_layout(dragmode='select',xaxis_showgrid=False, yaxis_showgrid=False)
scatter.update_xaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
scatter.update_yaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
scatter.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
def barUpdate(value):
    global orig_df
    valCol = orig_df[value].tolist()
    valMap = {}
    for val in valCol:
        if val in valMap:
            valMap[val]+=1
        else:
            valMap[val] = 1
    x_val = [i for i in valMap.keys()]
    y_val = [valMap[i] for i in x_val]
    data = {value: x_val, 'Number of '+value:y_val}
    fig = px.bar(pd.DataFrame(data),x=value,y='Number of '+value,title="Histogram of "+value,color_discrete_sequence=[px.colors.sequential.Blugrn[4]])
    fig.update_layout(dragmode='select',xaxis_showgrid=False, yaxis_showgrid=False)
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    return fig
#Create bar
bar1 = barUpdate(x)
bar2 = barUpdate(y)
defaults = {'scatter': go.Figure(scatter),'bar1': go.Figure(bar1),'bar2': go.Figure(bar2),'PCD': go.Figure(pcdFig)}
@app.callback(
    Output('Scatter', 'figure'),
    Output('Bar1', 'figure'),
    Output('Bar2', 'figure'),
    Output('PCD', 'figure'),
    Input('CorrMat', 'clickData'),
    Input('Scatter', 'selectedData'),
    Input('Stories','value'), prevent_initial_call=True
)
def setScatter(click,selection,stories):
    global pcd_set,orderd_axes,pcdFig,scatter,x,y,bar1,bar2,orig_df
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id']
    if trigger == 'CorrMat.clickData':
        x = click['points'][0]['x'] if click != None else x
        y = click['points'][0]['y'] if click != None else y
        bar1 = barUpdate(x)
        bar2 = barUpdate(y)
        if x != None:
            scatter =  px.scatter(orig_df,x=x,y=y,title="The Effect of " + x + " on " + y)
            scatter.update_traces(selectedpoints=None, mode='markers', marker={ 'color': "red"}, unselected={'marker': {'color':px.colors.sequential.Blugrn[4]}})
            scatter.update_layout(dragmode='select',xaxis_showgrid=False, yaxis_showgrid=False)
            scatter.update_xaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
            scatter.update_yaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
            scatter.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
        return scatter,bar1,bar2,defaults['PCD']
    elif trigger == 'Scatter.selectedData':
        selectedpoints = df.index
        if selection != None:
            selectedpoints = np.intersect1d(selectedpoints,[p['pointNumber'] for p in selection['points']])
            if len(selectedpoints) > 0:
                newFig = px.parallel_coordinates(pcd_set.iloc[selectedpoints],dimensions = ordered_axes,color_continuous_scale=[px.colors.sequential.Blugrn[4]])
                scatter = px.scatter(orig_df,x=x,y=y,title="The Effect of " + x + " on " + y,color_discrete_sequence=[px.colors.sequential.Blugrn[4]])
                scatter.update_traces(selectedpoints=selectedpoints, mode='markers', marker={ 'color': "red"}, unselected={'marker': {'color':px.colors.sequential.Blugrn[4]}})
                scatter.update_layout(dragmode='select',xaxis_showgrid=False, yaxis_showgrid=False)
                scatter.update_xaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
                scatter.update_yaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
                scatter.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
                return scatter,bar1,bar2,newFig
            else:
                return scatter,bar1,bar2,pcdFig
        else: 
            return scatter,bar1,bar2,pcdFig
    else:
        if stories == None:
            return defaults['scatter'],defaults['bar1'],defaults['bar2'],defaults['PCD']
        else:
            if stories == 1:
                x = "G1"
                y = "G3"
                selectedpts = [8,15,31,47,51,56,57,59,60,65,69,87,101,104,109,113,115,116,135, 151, 181, 183, 185, 196, 238, 240, 243, 250, 265, 266, 267, 276, 296, 300, 303, 306,312, 314, 316, 327, 332, 335, 336, 337, 338,343, 344, 348, 349, 356, 359, 365, 374, 378,381, 386, 387, 396, 400, 416, 427, 448, 450, 499, 509, 510, 525, 549, 594, 595, 596, 606,615, 617, 618, 620, 623, 630, 634, 636, 645]
            else:
                x = "studytime"
                y = "failures"
                selectedpts = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 128, 129, 130, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 164, 165, 166, 167, 168, 171, 172, 174, 176, 177, 178, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 280, 281, 282, 283, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 408, 409, 410, 411, 412, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 479, 480, 481, 482, 483, 484, 485, 486, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 544, 545, 546, 547, 548, 549, 550, 551, 553, 554, 555, 556, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 570, 573, 574, 575, 576, 577, 578, 579, 580, 582, 583, 584, 585, 586, 587, 588, 589, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648]
            newFig = px.parallel_coordinates(pcd_set.iloc[selectedpts],dimensions = ordered_axes,color_continuous_scale=[px.colors.sequential.Blugrn[4]])
            scatter = px.scatter(orig_df,x=x,y=y,title="The Effect of " + x + " on " + y,color_discrete_sequence=[px.colors.sequential.Blugrn[4]])
            scatter.update_traces(selectedpoints=selectedpts, mode='markers', marker={ 'color': "red"}, unselected={'marker': {'color':px.colors.sequential.Blugrn[4]}})
            scatter.update_layout(dragmode='select',xaxis_showgrid=False, yaxis_showgrid=False)
            scatter.update_xaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
            scatter.update_yaxes(showline=True, linewidth=2, linecolor='black',zeroline=False)
            scatter.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'})
            bar1 = barUpdate(x)
            bar2 = barUpdate(y)
            return scatter,bar1,bar2,newFig
@app.callback(
    Output('Stories', 'value'),
    Input('CorrMat', 'clickData'),
    Input('Scatter', 'selectedData'),prevent_initial_call=True
)
def updateDropdown(click,selection):
    return None
app.layout = html.Div(children=[
    html.Div(children = [
        html.Div(children = [html.H1('Student Grade Dataset')]),
        html.Div(children = [dcc.Dropdown(id="Stories",options=[{'label':"Story 1", 'value':1},{'label':'Story 2', 'value':2}])],style={'width':'30%'})
        
    ],style={'width':'99.5%','display': 'flex','justify-content':'space-between','align-items':'baseline'}),
    html.Div(children = [
        dcc.Graph(id='CorrMat',figure = corrFig)
    ],style={'height':'40%','width':'33%','display': 'inline-block'}),
    html.Div(children = [
        dcc.Graph(id='Bar1',figure = bar1)
    ],style={'height':'40%','width':'33%','display': 'inline-block'}),
    html.Div(children = [
        dcc.Graph(id='Bar2',figure = bar2)
    ],style={'height':'40%','width':'33%','display': 'inline-block'}),
    html.Div(children = [
        dcc.Graph(id='Scatter',figure = scatter)
    ],style={'height':'40%','width':'100%','display': 'inline-block'}),
    html.Div(children = [
        dcc.Graph(id='PCD',figure = pcdFig)
    ],style={'width':'100%','display': 'inline-block'})
    
])
app.run_server(debug=True)