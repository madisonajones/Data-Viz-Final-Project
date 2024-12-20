
# for introduction
import numpy as np
import holoviews as hv
import hvplot.pandas

def plotting_sums(df):
    ''' Preview plot for the introduction. Displays average mean scores per year. Returns a combined line
    and scatter'''
    filtered_df = df[df['Grade'] == 'All Grades']
    filtered_df = filtered_df[filtered_df['Year'].isin([2018,2019,2022])]
    avg_score = filtered_df.groupby('Year')['mean_scale_score'].mean().rename(columns = {'mean_scale_score':{'Mean Scale Score'}})
    avg_score_line = avg_score.hvplot.line(x = 'Year', y = 'mean_scale_score', color = 'teal')
    avg_score_scatter = avg_score.hvplot.scatter(x = 'Year', y = 'Mean Scale Score', color = 'teal')
    avg_score_combined = avg_score_scatter * avg_score_line
    avg_score_combined.opts(title = 'Average Mean Scale Score, per Year')
    return avg_score_combined



    
