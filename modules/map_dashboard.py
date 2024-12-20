import json
from shapely.geometry import MultiPolygon, Polygon
import pandas as pd
import geopandas as gpd
import panel as pn

import matplotlib.pyplot as plt
pn.extension()
import panel as pn
import matplotlib.pyplot as plt


class MapDashboard:
    def __init__(self,geojson, school_data):
        self.geojson = geojson
        self.school_data = school_data
        self.map_gpd = None
        self.merged_df = None
        self.fix_data()

        self.layout0 = ('Introduction',
                            pn.Row(
                                self.tab0_layout(),
                        )
                    )
        
        self.layout1 = ('Average Level 1 Per District, 2018',
                            pn.Row(
                                self.tab1_layout(),
                        )
                    )
        self.layout2 = ('Average Level 1 Per District, 2019',
                            pn.Row(
                                self.tab2_layout(),
                        )
                    )
        self.layout3 = ('Average Level 1 Per District, 2022',
                            pn.Row(
                                self.tab3_layout(),
                        )
                    )
        
        self.layout4 = ('Level 1 Analysis',
                        pn.Row(self.tab4_text(),
                               self.create_level4_map_2922()))

        self.layout = pn.Tabs(self.layout0, self.layout1, self.layout2, self.layout3,self.layout4)



    def introduction_txt(self):
        ''' This function adds introduction text to my dashboard. The beginning page is a map of 
        school districts that may aid in further understanding.'''
        text = """
        To the right is a visualization of the New York City school district map. This map will be helpful in upcoming 
        map analyses and will hopefully aid in understanding the results.
        """
        title = "# Preliminary Information"
        return pn.Column(
            title, pn.layout.Divider(), text,
        )
    
    def make_school_district_jpeg(self):
        ''' Imports jpg image of school districts.
            Returns image in right side of Tab 1.'''
        districts_jpg = pn.pane.JPG('school_district_numbers.jpg')
        return districts_jpg
    
    def tab0_layout(self):
        ''' Layout for all of 'Tab 0'. 
        Takes introduction text and jpg, places them side by side.'''
        introtext = self.introduction_txt()
        districts_image = self.make_school_district_jpeg()
        return pn.Row(introtext,districts_image) 
    


    def fix_data(self):
        ''' Opens NYC school district geojson. Extracts the coordinate info from 'map_df', which includes
        all info about school district numbers and shapes. 'district_coordinates' contains relevant info
        for later. Also creates filtered school data, by finding the mean level percentages for each school
        district per year. Combines them and defines merged data for the class.'''

        with open('school_districts.geojson') as file:
            map_geojson = json.load(file)

        # dealing w map geojson, getting coordinate info
        map_df = pd.json_normalize(map_geojson['features'])
        district_coordinates = map_df[['properties.school_dist', 'geometry.type','geometry.coordinates']]
        district_coordinates.rename(columns ={'properties.school_dist':'school_dist'},inplace = True)
        district_coordinates['school_dist'] = district_coordinates['school_dist'].astype(int)
        

        # dealing w school_data filtering for maps 
        school_avg = self.school_data.groupby(['school_dist','Year'],as_index=False)[['level_1_percentage','level_2_percentage','level_3_percentage','level_4_percentage']].mean().rename(columns={'level_1_percentage':'avgL1','level_2_percentage':'avgL2',
                                                                                     'level_3_percentage':'avgL3','level_4_percentage':'avgL4'})
        school_avg['school_dist'] = school_avg['school_dist'].astype(int)

        self.merged_df = pd.merge(district_coordinates, school_avg, on = 'school_dist')

        # putting flatten and multipolygon inside the data fix 
        def flatten_extend(matrix):
            ''' Geometry coordinates from school_districts.geojson are in a nested list. This creates
        a flat list for shapely transforming and for creation of the geodataframe.'''
            flat_list = []
            for row in matrix:
                flat_list.extend(row)
            return flat_list
        
        # flatten list on merged
        self.merged_df['geometry.coordinates'] = self.merged_df['geometry.coordinates'].apply(flatten_extend)

        def making_multipolygon(coord_list):
            ''' Makes the coordinates into a multipolygon shape. Before this, the coordinates are a list of
        polygons. Need to be made into a Multipolygon for plotting the shape of districts on the map'''
            polygons_list = []
            for coords in coord_list:
                poly = Polygon(coords)
                polygons_list.append(poly)
            return MultiPolygon(polygons_list)
    
        # multipolygon on merged
        self.merged_df['geometry'] = self.merged_df['geometry.coordinates'].apply(making_multipolygon)

        # defining gdf
        self.map_gpd = gpd.GeoDataFrame(self.merged_df, geometry=self.merged_df['geometry'])
        self.map_gpd.set_crs('EPSG:4326')


################################################################################################
           
    def mapping_2018(self):
        '''Creates map for Avg reading level 1 percentage by school dist for 2018. 
    Returns map with legend, colored by district. ''' 
        
        filtered_map_gpd = self.map_gpd[self.map_gpd['Year'] == 2018]

        fig, ax = plt.subplots(figsize=(5,5))
        filtered_map_gpd.plot(column='avgL1', ax=ax, legend=True, cmap = 'PuBu')
        ax.set_title(f'Average Level 1 Percentage for 2018')
        plot = pn.pane.Matplotlib(fig, tight=True)
        return plot

 
    def tab1_text(self):
        ''' This function adds introduction text to my dashboard. The beginning page is a map of 
        school districts that may aid in further understanding.'''
        text1 = """
        This map demonstrates a pre-existing divide in education amongst the boroughs, with increased percentages of
        Level 1 students in certain neighborhoods.  """
        
        title = "# 2018"
        return pn.Column(
            title, pn.layout.Divider(), text1,
        )
    
    def tab1_layout(self):
        ''' Creates layout format for tab 1. Returns 2018 map and text in a row.'''
        plot18 = self.mapping_2018()
        plot18_txt = self.tab1_text()
        return pn.Row(plot18, plot18_txt)

################################################################################################
    
    def mapping_2019(self):
        ''' Creates map for Avg reading level 1 percentage by school dist for 2019. Returns
        map with legend, colored by district.'''
        filtered_map_gpd = self.map_gpd[self.map_gpd['Year'] == 2019]

        fig, ax = plt.subplots(figsize=(5,5))
        filtered_map_gpd.plot(column='avgL1', ax=ax, legend=True, cmap = 'PuBu')
        ax.set_title(f'Average Level 1 Percentage for 2019')
        plot = pn.pane.Matplotlib(fig, tight=True)
        return plot
    
    def tab2_text(self):
        ''' This function adds introduction text to my dashboard. The beginning page is a map of 
        school districts that may aid in further understanding.'''
        text1 = """
        
        When comparing 2018 and 2019, take note of the minor increase of Level 1 students, indicating a 
        decline in education before the beginning of the pandemic.

        """
        title = "# 2019"
        return pn.Column(
            title, pn.layout.Divider(), text1,
        )
    
    def tab2_layout(self):
        ''' Creates layout format for tab 2. Returns 2019 map and text in a row.'''
        plot19 = self.mapping_2019()
        plot19_txt = self.tab2_text()
        return pn.Row(plot19, plot19_txt)

################################################################################################
    
    def mapping_2022(self):
        ''' Creates map for Avg reading level 1 percentage by school dist for 2022. Returns
        map with legend, colored by district.'''
        filtered_map_gpd = self.map_gpd[self.map_gpd['Year'] == 2022]

        fig, ax = plt.subplots(figsize=(5,5))
        filtered_map_gpd.plot(column='avgL1', ax=ax, legend=True, cmap = 'PuBu')
        ax.set_title(f'Average Level 1 Percentage for 2022')
        plot = pn.pane.Matplotlib(fig, tight=True)
        return plot
    
    def tab3_text(self):
        ''' This function adds introduction text to my dashboard. The beginning page is a map of 
        school districts that may aid in further understanding.'''
        text1 = """
        
        Note the increased percentages in the Bronx, Brooklyn, and Queens, with the average percentage of Level 1
        students climbing above 30%. Staten Island and Manhattan stay relatively the same, as students in the 
        Level 1 range in these boroughs do not surpass 20%.

        """
        title = "# 2022"
        return pn.Column(
            title, pn.layout.Divider(), text1,
        )
    
    def tab3_layout(self):
        ''' Creates layout format for tab 3. Returns 2022 map and text in a row.'''
        plot2022 = self.mapping_2022()
        plot2022_txt = self.tab3_text()
        return pn.Row(plot2022, plot2022_txt)
   
   ################################################################################################
    def tab4_text(self): 
        ''' Text for map analysis. This function returns analysis text with title'''
        text = """

        The previous maps show the distributions of children who fall under "Level 1" for reading and
        comprehension scores based on state-administered testing. Level 1 is classified as "not meeting 
        learning standards", indicating a child's knowledge is below their grade level.

        As you flip through the maps, you will notice that areas in the Bronx (see purple shaded area in 
        Preliminary Information) have gotten progressively worse, while boroughs, such as Manhattan or 
        Staten Island (see green and blue shaded areas in Preliminary Information) have remained almost 
        the same since pre-pandemic. 
        
        The Bronx has a poverty level of 27.6%, which is significantly higher compared to the national 
        average of 11.1%. The demographic makeup includes an overwhelming majority of Black and Hispanic 
        people, with white, non-Hispanic people taking up only 9% of the population. Alternatively, the borough 
        of Manhattan is a majority white area, with white, non-Hispanics making up 50.7% of the population 
        and a poverty rate of 15.79%. 

        Pew Research Center suggests the idea of the “digital divide”, which describes how majority of Black 
        students and students from low-income households struggle to adapt to online learning due to unreliable 
        Wi-Fi connections and access to computers (Auxier and Anderson, 2020). This caused a pre-existing 
        achievement gap to be widened, leading to the rising percentages of students who fall under the Level 1 range. 

        Systemic racism in the United States is responsible for the overwhelming number of students who are behind 
        in education. Per the map in 2018, it is evident that there is a pre-existing education gap amongst school 
        districts. Lack of funding and district segregation impacted school districts for many years before the COVID-19 
        pandemic. The pandemic caused significant stressors on marginalized communities, such as disproportionate effects 
        on job security, accessible mental and physical health treatments, and food insecurity, leading to additional 
        challenges faced by students and parents (Chen, Byrne, and Vélez, 2022).

        To the right is a map of average Level 3 percentages per district from 2022, for comparison. Level 3 indicates 
        that a student has met learning expectations. The distribution of the averages demonstrates how behind students 
        in these communities are compared to areas with higher amounts of middle and upper class students.


        """
        title = "# Level 1 Maps - Discussion"
        return pn.Column(
            title, pn.layout.Divider(), text)
    
    def create_level4_map_2922(self):
        ''' Map of Level 3 mean percent by school district for 2022. Used to compare Level 1 vs Level 3
        averages, returns map colored by district per legend.'''
        filtered_map_gpd = self.map_gpd[self.map_gpd['Year'] == 2022]

        fig, ax = plt.subplots(figsize=(5,5))
        filtered_map_gpd.plot(column='avgL3', ax=ax, legend=True, cmap = 'PuBu')
        ax.set_title(f'Average Level 3 Percentage for 2022')
        plot = pn.pane.Matplotlib(fig, tight=True)
        return plot
       
   
    
