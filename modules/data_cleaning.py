import pandas as pd 

# #combining school_data_chunk1.csv and school_data_chunk2.csv
def combine_data(df1,df2):
    ''' Data is too large to be directly put into GitHub, so it was split externally into
     two pieces. This merges the data. Returns one dataset '''
    school_data_combined = pd.concat([df1, df2], ignore_index=True)
    return school_data_combined

def cleaning_data(df):
    ''' This function cleans the data, drops NAs, filters by years I want to use, changes column names,
    Returns cleaned dataset.'''
    clean_df = df.dropna(axis ='rows')
    clean_df = clean_df[clean_df['Year'].isin([2018,2019,2022])]
    clean_df = clean_df.rename({'DBN': 'dbn',
                                'School Name': 'school_name',
                                'Number Tested': "number_tested",
                                'Mean Scale Score':"mean_scale_score",
                                '# Level 1': "level_1_count", 
                                '% Level 1': "level_1_percentage",
                                '# Level 2':'level_2_count',
                                '% Level 2': 'level_2_percentage',
                                '# Level 3':"level_3_count",
                                '% Level 3': 'level_3_percentage',
                                '# Level 4':'level_4_count',
                                '% Level 4': 'level_4_percentage',
                                '# Level 3+4': "level_3_4_count",
                                '% Level 3+4': 'level_3_4_percentage'},axis = 'columns')
    return clean_df




def create_borough_column(district):
    ''' Splitting data into boroughs by school district. Returns a column for school district
    corresponding with five boroughs.'''
    if district in ['01','02','03','04','05','06']:
        return 'Manhattan'
    if district in ['07','08','09','10','11','12']:
        return "Bronx"
    if district in ['14','15','16','17','18','19','20','21','22','32']:
        return "Brooklyn"
    if district in ['24','25','26','27','28','29','30']:
        return "Queens"
    if district == '31':
        return "Staten Island"
