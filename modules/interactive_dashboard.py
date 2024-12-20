
import param
import pandas as pd
import panel as pn
import hvplot.pandas
import holoviews as hv
hv.extension('bokeh')
pn.extension()
import json
from shapely.geometry import MultiPolygon, Polygon
import geopandas as gpd


class Dashboard(param.Parameterized):

    def __init__(self, data, **params):
        self.data = data
        

        # year widget
        self.year_widget = pn.widgets.Select(
            name='Year',
            options=list(self.data.Year.unique()))
            #value=list(self.data.Year.unique())[0])
        
        self.reading_level_widget = pn.widgets.MultiSelect(
            name='Reading Level', 
            value = ['Level 1','Level 2','Level 3','Level 4'],
            options = ['Level 1','Level 2','Level 3','Level 4'],
            size=8)
        
        super().__init__(**params)


####################################################################################
# LAYOUT

        
        
        self.layout1 = ('Mean Scale Score',
                        pn.Row(
                            self.tab1_layout
                        )
                    )
        

        # # the differences 
        self.layout2 = ("Mean Score Differences, 2018 - 2022",
                        pn.Row(self.tab2_layout
                        )
                    )

                        
        self.layout3 = ('Grade, Level %, and Year',
                        pn.Row(
                             pn.WidgetBox(self.year_widget,
                                          self.reading_level_widget
                            ),
                            self.tab3_layout,
                        )
                    )
        
        self.layout = pn.Tabs(self.layout1, self.layout2, self.layout3)   
      
####################################################################################
    
# TAB 1

    def interactive_text(self):
        ''' Describes graphs of mean score by grade and level 1 and level 4 trends.'''
        text2 = """
     
    Mean scale score is a great indicator of how well children grades 3 through 8 are performing on state 
     administered tests. Overall, trends seem to indicate both better and worse test scores by grade. Fifth 
     graders, sixth graders, and seventh graders indicated an overwhelming mean score increase from 2019 to 2022.
    While third graders, fourth graders, and eighth graders displayed intense declines from 2019 to 2022. Overall, 
    the average score across all reported grades showed a slight increase from 2019 to 2022, with average scores 
    still being below the average of 2018. 

    Generally, mean ELA scores display decreases between 2018 and 2019, indicating that a decline was already occurring
    before the pandemic. The increase of test scores in 2022 may reveal that post-pandemic recovery policies are 
    becoming effective.  

    ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    Based on on borough, the average mean scale score shows similar trends as grade levels. Wealthier areas with a greater population
    of upper and middle class generally score better on tests overall. However, all boroughs show at least a 1% decreaase from 2018 
    to 2019 in mean test scores. The Bronx' average is noticeably lower than the rest. This could be due to a lack of resources
    and higher rates of poverty in this neighborhood.


        """

        title1 = "# Mean Scale Score Amongst Grades"
        return pn.Column(
            title1, pn.layout.Divider(), text2,
        )
    

    def create_mean_score_line(self):
        ''' Creates mean score line graph by grade. Filters self.data (school_data) to show mean scores
        by year and grade. Returns line graph''' 
        # getting average level % for each year, by grade
        average_scores = self.data.groupby(['Grade','Year'],as_index=False)[['mean_scale_score']].mean()
        average_scores = average_scores[average_scores['Year'].isin([2018,2019,2022])]     
        average_scores['Year'] = pd.Categorical(average_scores['Year'],categories=[2018, 2019, 2022], ordered=True)
        average_scores['Year'] = average_scores['Year'].astype(str)  

        mean_score_line = average_scores.hvplot.line(x = 'Year',y ='mean_scale_score', by = 'Grade')
        mean_score_line.opts(title = "Mean Score by Grade, 2018-2022", xlabel = 'Year', ylabel = 'Average Score', height = 400, width  = 400)
        return mean_score_line


    def create_boroughs_bar(self):
        ''' Creates bar plot for mean scale score of each borough per year. 
        Returns bar plot of all scores for each borough.'''
        boroughs_filter = self.data.groupby(['Year','borough'])[['mean_scale_score']].mean()
        score_bar = boroughs_filter.hvplot.bar(x = "borough", y = 'mean_scale_score', by = 'Year', tools = ['hover'], rot = 90, ylim =(585,605), color=["#f8b195", "#f67280",'#c06c84','#6c5b78','#355c7d'], xlabel = 'Mean Scale Score', ylabel = 'Borough, Year', title = "Mean Scores, per Borough")
        return score_bar



    def tab1_layout(self):
        ''' Layout for tab 2. Combines and puts both graphs in a column for layout. Returns
        side by side text and graphs.'''
        tab1_text = self.interactive_text()
        tab1_graph = self.create_mean_score_line()
        tab1_bar = self.create_boroughs_bar()
        combined_graphs = (tab1_graph+tab1_bar).opts(shared_axes = False).cols(1)
        return pn.Row(tab1_text,combined_graphs)
        


####################################################################################
# TAB 2 DIFFERENCES

    def plotting_differences(self):
        ''' Plots differences in mean scale score by year and grade. Creates two new filtered dataframes
        from school data for 2018 and 2022. Subtracts difference (2022-2018). Returns bar chart of 
        difference per grade.'''
        grade_year_filter = self.data.groupby(['Grade','Year'],as_index=False)[['mean_scale_score']].mean().rename(columns = {'Grade':'grade','Year':'year','mean_scale_score':'mean'})


        filtered_df_2018 = grade_year_filter[grade_year_filter['year'] == 2018]
        filtered_df_2018.drop('year', axis=1, inplace=True)
        filtered_df_2018 = filtered_df_2018.rename(columns={"mean": "mean_2018"})

        filtered_df_2022 = grade_year_filter[grade_year_filter['year'] == 2022]
        filtered_df_2022.drop('year', axis=1, inplace=True)
        filtered_df_2022 = filtered_df_2022.rename(columns={"mean": "mean_2022"})


        years_combined = pd.merge(filtered_df_2018,filtered_df_2022, on = 'grade')

        years_combined['difference'] = years_combined['mean_2022'] - years_combined['mean_2018']

        mean_differences_bar = years_combined.hvplot.bar(x = "grade",y = 'difference', color=["#f67280"]).opts(title = "Difference in Mean Scale Score Between 2018 and 2022", xlabel = "Grade", ylabel = "Mean Scale Score Difference (2022 - 2018)")

        return mean_differences_bar
    
    def create_tab2_txt(self):
        ''' Creates analysis for tab 2. Returns title and text in column.'''
        text = '''

    This graph shows the difference in mean scale score from 2018 to 2022 for each grade level. Younger children
    seem to be the primary victims of the pandemic. Fourth graders are the most impacted, with the mean test score 
    has dropped by approximately five points. Third graders are the second group that is most impacted by the pandemic,
    with average test scores dropping almost two points. Overall, the average test score across all grades has 
    dropped, with a difference in half of a point, suggesting slight educational loss for all students. 

''' 
        title1 = "# Mean Score Differences"
        
        return pn.Column(
            title1, pn.layout.Divider(), text,
        )

    def tab2_layout(self):
        ''' Layout for tab 2 with the differences plot and text.
          Returns plot and text in a column.'''
        differences_plot = self.plotting_differences()
        tab2_txt = self.create_tab2_txt()
        return pn.Column(differences_plot, tab2_txt)
    
    ####################################################################################

    # TAB 3 USER INTERACTIVE

    @param.depends(
        "year_widget.value",
        "reading_level_widget.value"
    )

    def create_tab3_widgets(self):
        ''' Interactive plot that allows user to select one Year and multiple reading levels to display a bar
        graph. Returns interactive bar graph by grade, level, and year.'''
        school_avg = self.data.groupby(['Grade','Year'],as_index=False)[['level_1_percentage','level_2_percentage','level_3_percentage','level_4_percentage']].mean().rename(columns={'level_1_percentage':'Level 1','level_2_percentage':'Level 2',
                                                                                     'level_3_percentage':'Level 3','level_4_percentage':'Level 4'})
       
        data = school_avg.loc[(school_avg.Year.isin([self.year_widget.value]))]

      
        if self.reading_level_widget.value:
            level_values = self.reading_level_widget.value
            data = data[['Year','Grade'] + level_values]


        return data.hvplot.bar(x = 'Grade', y = level_values, stacked = False, color=["#f8b195", "#f67280",'#c06c84','#6c5b78'], rot = 90, xlabel = "Grade, Reading Level", ylabel = '%', title = "Percentage of Students for Each Level, by Grade and Year")


    def create_tab3_text(self):
        ''' Creates explanation text for Tab 3. Returns text in a column with title.'''
        text2 = '''
      
    Younger grades seem to be the ones struggling the most in a post-pandemic education system. Both third and 
    fourth graders had intense spikes in Level 1 readers compared to the 2019 percentage level. The percentage 
    of Level 1 readers increased for third and fourth graders by two and eight percentage points, respectively. 
    This demonstrates the learning loss for younger students due to the disruption of their kindergarten and first 
    grade learning. According to the New York Times, academically challenged students have been an ongoing struggle 
    post-pandemic. The youngest learners during the pandemic lack basic knowledge to help them succeed in school, 
    such as writing, the alphabet, and behavioral management (Mervosh & Miller). The alternative is prevalent in 
    higher grades, seventh and eighth, who have excelled in performance post pandemic with percentage increases of 
    over 1% for Level 3 readers and an 8% increase for seventh grade Level 4 readers.

    An important thing to note is the decline in education from 2018 to 2019, which demonstrates at least 1% increase 
    in Level 1 readers grades four, five, six, and seven over  the course of a year. This suggests an education system 
    that was already failing, heightened by classroom disruption. 
        '''

        title1 = "# Discussion"
        return pn.Column(
            title1, pn.layout.Divider(), text2,
        )
    
    def tab3_layout(self):
        ''' Layout for tab 3. Returns interactive plot and widgets in a row, with text below in line
        with the plot in a column.'''
        tab5_widgets_graph = self.create_tab3_widgets
        tab5_widgets_text = self.create_tab3_text
        return pn.Column(tab5_widgets_graph,tab5_widgets_text)
