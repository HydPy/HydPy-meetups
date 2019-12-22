import plotly.offline as pyo
from plotly.graph_objs import *
import plotly.tools as tls
from plotly import tools
import plotly.graph_objs as go
import logging

from sklearn import metrics

'''
Most functions in this class return a plotly "figure" which can be saved/exported by caller - AND optionally plot offline plots to ipython notebook.
'''


def plotDistributions(listOfSeries, title = 'Distribution Summary - ', prefix = '', excludeZeros = True, showPlot = True):
    '''
    Plots distributions of a list of numeric series.... or a list of categorical series
    '''
    isNumeric = all(series.dtype.name == 'int64' or series.dtype.name == 'float64' or series.dtype.name == 'int32'  for series in listOfSeries)
    isCategorical = all(series.dtype.name == 'object' or series.dtype.name == 'bool' or series.dtype.name == 'category'  for series in listOfSeries)

    if not isNumeric and not isCategorical:
        raise ValueError('Inputs seem to contain a mix of numeric and categorical data. Please fix inputs.')

    if isNumeric:
        fig = tools.make_subplots(rows=1, cols=2, subplot_titles=('Boxplot', 'Histogram'), print_grid=False)
        for series in listOfSeries:
            series_box = go.Box(
                y=series,
                name=prefix + ' ' + series.name + '(B)'
            )
            series_hist = go.Histogram(
                x = series[series != 0] if excludeZeros else series,
                name = prefix + ' ' + series.name + '(H)',
                opacity=0.75
            )
            
            fig.append_trace(series_box,1,1)
            fig.append_trace(series_hist,1,2)

        fig['layout'].update(showlegend=True, title=title, barmode='overlay')
    else:
        bar_list = []
        for series in listOfSeries:
            series_bar = go.Bar(
                x = series.groupby(series.values).size().keys(),
                y = series.groupby(series.values).size().values,
                name = title
            )
            bar_list.append(series_bar)
        layout = go.Layout(
            title = title,
            barmode='group'
        )
        fig = go.Figure(data=bar_list, layout=layout)
    
    if showPlot:
        pyo.iplot(fig)

    return fig



def drawPlots(series, title = 'Distribution Summary - ', excludeZeros = True, by = None, showPlot = True):
    '''
    Function to draw basic box-plot and histogram for numerics - 
    and a bar plot for categoricals
    '''
    title = title + series.name;
    if series.dtype.name == 'object' or series.dtype.name == 'bool' or series.dtype.name == 'category':
        # Draw Bar Chart
        if by is None:
            series_bar = go.Bar(
                x = series.groupby(series.values).size().keys(),
                y = series.groupby(series.values).size().values,
                name = title
            )
            fig = [series_bar]
        else:
            bar_list = []

            def processSeries(bySeries, bar_list = bar_list):
                for byValue in bySeries.unique():
                    s = series[bySeries == byValue]
                    s = s.groupby(s.values).size()
                    bar_list.append(go.Bar(
                        x = s.keys(),
                        y = s.values,
                        name = bySeries.name + ' - ' + str(byValue)
                    ))
                return bar_list

            if type(by).__name__ == 'DataFrame':
                for column in by.columns:
                    bar_list = processSeries(by[column], bar_list)
            else:
                bar_list = processSeries(by, bar_list)
            layout = go.Layout(
                title = title,
                barmode='group'
            )
            fig = go.Figure(data=bar_list, layout=layout)

    else:

        if by is not None and len(by.unique()) == len(series):
            # This means the input data is already summarized. A simple bar plot will suffice
            series_bar = go.Bar(
                x = by.tolist(),
                y = series.tolist(),
                name = title
            )
            fig = [series_bar]
        else:
            # Draw Box plot and Histogram
            fig = tools.make_subplots(rows=1, cols=2, subplot_titles=('Boxplot', 'Histogram'), print_grid=False)
            series_box = go.Box(
                y=series,
                name=series.name
            )
            series_hist = go.Histogram(
                x = series[series != 0] if excludeZeros else series,
                name = series.name,
                opacity=0.75
            )
            
            fig.append_trace(series_box,1,1)
            fig.append_trace(series_hist,1,2)
            if by is not None:
                def processSeriesForNumeric(bySeries, fig):
                    series_box = go.Box(
                        y = series,
                        x = bySeries.apply(lambda x: bySeries.name + ' - ' + x),
                        name = series.name + ' - (' +bySeries.name + ')'
                    )
                    fig.append_trace(series_box,1,1)
                    series_box.update(x = bySeries)
                    for byValue in bySeries.unique():
                        s = series[bySeries == byValue]
                        series_hist = go.Histogram(
                            x = s[s != 0] if excludeZeros else s,
                            name = series.name + ' - (' + bySeries.name + '=' + str(byValue) + ')',
                            opacity=0.75
                        )
                        fig.append_trace(series_hist,1,2)
                    return fig

                if type(by).__name__ == 'DataFrame':
                    for column in by.columns:
                        fig = processSeriesForNumeric(by[column], fig)
                else:
                    fig = processSeriesForNumeric(by, fig)

            fig['layout'].update(showlegend=True, title=title, barmode='overlay')

    if showPlot:
        pyo.iplot(fig)
    return fig


def addToROCPlot(listOfActualsAndProbLists, plotData = [], pos_label = 1):
    '''
    Prepares data for drawing ROC curves. Takes inputs of the form [(label, y_test, y_prob)]
    '''
    for (label, y_test, y_probs) in listOfActualsAndProbLists:
        fpr, tpr, thresholds = metrics.roc_curve(y_test, y_probs, pos_label = pos_label)
        trace1 = go.Scatter(
            x=fpr,
            y=tpr,
            mode='markers',
            marker=dict(size=4,
                        line=dict(width=1)
                       ),
            name=label,
            text=thresholds
                )
        plotData.append(trace1)
    return plotData


def showROCPlot(plotData, name = None, showPlot = True):
    layout = go.Layout(
        title='ROC Curve' + ((' - ' + name) if name is not None else ''),
        showlegend = True,
        hovermode='closest',
        autosize = False,
        width=900,
        height=700,
        xaxis=dict(
            title='False Positive Rate',
            ticklen=5,
            zeroline=False,
            gridwidth=2,
        ),
        yaxis=dict(
            title='True Positive Rate',
            ticklen=5,
            gridwidth=2,
        ),
    )
    fig = go.Figure(data=plotData, layout=layout)

    if showPlot:
        pyo.iplot(fig)
    return fig


def drawBarPlot(df, pivotColumn, barColumns, plotTitle, 
    pivotLabel = None, barLabels = None, summaryTotals = None, percentages = False, 
    showPlot = True, returnTraces = False):
    '''
    Generic function to draw barplots, needs a dataframe with data and the columns to be used for pivot and bars
    '''
    pivotData = df[pivotColumn].tolist()
    if summaryTotals is not None:
        pivotData = zip(pivotData, summaryTotals)
        pivotData = [str(elem[0])+' ('+str(elem[1])+')' for elem in pivotData]
    traces = []
    index = 0
    if type(barColumns) is str:
        barColumns = [barColumns]
    for column in barColumns:
        if df[column].dtype not in (int,float):
            logging.warn('Ignoring column ' + column + ' because it has a non-numeric dtype')
            continue
        trace = go.Bar(
            x=pivotData,
            y=list(df[column]) if not percentages else list(df[column]*100)/sum(df[column]),
            name= ('% - ' if percentages else '') + (column if barLabels is None or len(barLabels) != len(barColumns) else barLabels[index])
        )
        traces = traces + [trace]
        index = index + 1

    if returnTraces:
        return traces

    layout = go.Layout(
        title=plotTitle,
        showlegend = True,
        hovermode='closest',
        autosize = False,
        width=900,
        height=500,
        xaxis=dict(
            title= pivotColumn if pivotLabel is None else pivotLabel,
            ticklen=5,
            zeroline=False,
            gridwidth=2,
        ),
        yaxis=dict(
            title= plotTitle,
            ticklen=5,
            gridwidth=2,
        ),
    )
    fig = go.Figure(data=traces, layout=layout)
    if showPlot:
        pyo.iplot(fig)
    return fig

