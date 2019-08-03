import datetime
import requests
import json
import pandas as pd
import os

import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


context_dict = {
    "school.carnegie_basic": {
        -2: 'Not applicable',
        0: '(Not classified)',
        1: 'Associates Colleges: High Transfer-High Traditional',
        2: 'Associates Colleges: High Transfer-Mixed Traditional/Nontraditional',
        3: 'Associates Colleges: High Transfer-High Nontraditional',
        4: 'Associates Colleges: Mixed Transfer/Career & Technical-High Traditional',
        5: ",B7,",
        6: 'Associates Colleges: Mixed Transfer/Career & Technical-High Nontraditional',
        7: 'Associates Colleges: High Career & Technical-High Traditional',
        8: 'Associates Colleges: High Career & Technical-Mixed Traditional/Nontraditional',
        9: 'Associates Colleges: High Career & Technical-High Nontraditional',
        10: 'Special Focus Two-Year: Health Professions',
        11: 'Special Focus Two-Year: Technical Professions',
        12: 'Special Focus Two-Year: Arts & Design',
        13: 'Special Focus Two-Year: Other Fields',
        14: 'Baccalaureate/Associates Colleges: Associates Dominant',
        15: 'Doctoral Universities: Very High Research Activity',
        16: 'Doctoral Universities: High Research Activity',
        17: 'Doctoral/Professional Universities',
        18: 'Masters Colleges & Universities: Larger Programs',
        19: 'Masters Colleges & Universities: Medium Programs',
        20: 'Masters Colleges & Universities: Small Programs',
        21: 'Baccalaureate Colleges: Arts & Sciences Focus',
        22: 'Baccalaureate Colleges: Diverse Fields',
        23: 'Baccalaureate/Associates Colleges: Mixed Baccalaureate/Associates',
        24: 'Special Focus Four-Year: Faith-Related Institutions',
        25: 'Special Focus Four-Year: Medical Schools & Centers',
        26: 'Special Focus Four-Year: Other Health Professions Schools',
        27: 'Special Focus Four-Year: Engineering Schools',
        28: 'Special Focus Four-Year: Other Technology-Related Schools',
        29: 'Special Focus Four-Year: Business & Management Schools',
        30: 'Special Focus Four-Year: Arts, Music & Design Schools',
        31: 'Special Focus Four-Year: Law Schools',
        32: 'Special Focus Four-Year: Other Special Focus Institutions',
        33: 'Tribal Colleges',
    },
    'school.carnegie_undergrad' : {
        -2: 'Not applicable',
        0: 'Not classified (Exclusively Graduate)',
        1: 'Two-year, higher part-time',
        2: 'Two-year, mixed part/full-time',
        3: 'Two-year, medium full-time',
        4: 'Two-year, higher full-time',
        5: 'Four-year, higher part-time',
        6: 'Four-year, medium full-time, inclusive, lower transfer-in',
        7: 'Four-year, medium full-time, inclusive, higher transfer-in',
        8: 'Four-year, medium full-time, selective, lower transfer-in',
        9: 'Four-year, medium full-time , selective, higher transfer-in',
        10: 'Four-year, full-time, inclusive, lower transfer-in',
        11: 'Four-year, full-time, inclusive, higher transfer-in',
        12: 'Four-year, full-time, selective, lower transfer-in',
        13: 'Four-year, full-time, selective, higher transfer-in',
        14: 'Four-year, full-time, more selective, lower transfer-in',
        15: 'Four-year, full-time, more selective, higher transfer-in',  
    },
    "school.region_id": {
        0: 'U.S. Service Schools',
        1: 'New England (CT, ME, MA, NH, RI, VT)',
        2: 'Mid East (DE, DC, MD, NJ, NY, PA)',
        3: 'Great Lakes (IL, IN, MI, OH, WI)',
        4: 'Plains (IA, KS, MN, MO, NE, ND, SD)',
        5: 'Southeast (AL, AR, FL, GA, KY, LA, MS, NC, SC, TN, VA, WV)',
        6: 'Southwest (AZ, NM, OK, TX)',
        7: 'Rocky Mountains (CO, ID, MT, UT, WY)',
        8: 'Far West (AK, CA, HI, NV, OR, WA)',
        9: 'Outlying Areas (AS, FM, GU, MH, MP, PR, PW, VI)',
    },
}


def csv_to_list(filename):
    """
    Converts a csv with one column of all fields into field list. Note that the column must have a row at the beginning and end that can be discarded
    """
    file_in = open(filename, "r")
    lol = []
    for line in file_in:
        line = line[:-1]
        lol.append(line)
    
    return (lol[1:-1]) # removes the wrapers.


def url_end_generator(fields):
    """
    :param fields: a list of strings representing the fields to include when pulling the api
    """
    """
    next few lines create url with correct pagenumbers and fields.
    It also applies various limitations on the data.
    
    Note that ranges are inclusive For example, the range 3..7 matches both 3 and 7, as well as the numbers in between.
    
    school.degrees_awarded.highest=3,4 is a limitation which limits the output to schools whose highest degree awarded 
    is either a bachelors (i.e. Pomona College) or a graduate degree (i.e. Vanderbilt University). Within the API, 
    bachelor's and graduate degrees are represented by 3 and 4, respectively. No degrees granted, certificate degrees, 
    and associate degrees are all excluded and are represented by 0, 1, and 2, respectively 
    """
    limitations = "&school.degrees_awarded.highest=3,4"

    # school.operating=1 is a limitation allowing only schools that are currently operating to be outputed.
    limitations += "&school.operating=1"

    # limitation not allowing schools that have a less than four year completion rate (Not working)
    # limitations += "&latest.completion.completion_rate_less_than_4yr_150nt=None"
    
    url = limitations + "&_fields="
    for field in fields:
        url += field + ","
    url += "&api_key=IGlx37HV88IkLl14qDgb1siyF2bPjrNZ9DXwFZKQ"
    
    return url


def api_to_df(url, object_of_interest):
    """
    Method from https://stackoverflow.com/questions/45787597/parsing-json-data-from-an-api-to-pandas
    :param url: api url
    :param object_of_interest: object that we are interested in. for college data use 'results'
    :return: pandas dataframe for the api
    """
    data = requests.get(url)\
                         .json()[object_of_interest]
    df = pd.DataFrame.from_dict(data)
    return df


def page_flipper(pagenumber, url_start, url_end):
    url = url_start + str(pagenumber) + url_end
    #print(url)
    return url


def multi_api_to_df(pages, object_of_interest, url_start, url_end):
    """
    Method from https://stackoverflow.com/questions/45787597/parsing-json-data-from-an-api-to-pandas
    :param url: api url
    :param object_of_interest: object that we are interested in. for college data use 'results'
    :param url: number of pages in the multipage api
    :return: pandas dataframe for the api
    """
    df = api_to_df(page_flipper(0, url_start, url_end), 'results')
    for i in range(1,pages):
        df = pd.concat([df, api_to_df(page_flipper(i, url_start, url_end), object_of_interest)])
    
    return df


def generate_raw_df(field_list, pgs):
#    field_list = csv_to_list(field_csv)
    url_start = 'https://api.data.gov/ed/collegescorecard/v1/schools.json?_per_page=100&page='
    url_end = url_end_generator(field_list)
    object_of_interest= 'results'
    df = multi_api_to_df(pgs, object_of_interest, url_start, url_end) #there are 27 pages under above limitations
    #df.to_pickle(filename)
    return df


def organize_columns(df, field_list):
    """
    Notice that when df is generated from api, columns are in the wrong order. 
    We restore the original order of the csv file.
    """
    return df[field_list]


def give_context(d, df):
    """
    Now, we fix columns that use numbers to describe text
    """
    dft = df
    for key in d:
        dft = dft.replace({key: d[key]})
        
    return dft
    

def store_df(df, new_filename):
    df.to_pickle(new_filename)


def step_1_main(csv_filename, api_pages, context_dict, plk_filename):
    field_list = csv_to_list("simpleFields2.csv")

    # Generate
    df = generate_raw_df(field_list, api_pages)

    # Clean data
    df = organize_columns(df, field_list)
    df = give_context(context_dict, df) # note that context_dict will prob come in as json and then need to be converted eventually

    # Store Data
    store_df(df, plk_filename)
    

step_1_main("simpleFields2.csv", 27, context_dict, "simple_raw_data.plk" )