# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import sys
import urllib
import os
import pandas as pd

def download_extract_data(src_url,file_name, extract_dir):
    '''
    Given a src_url, downloads the archived earthquake data.
    Then, extracts the data into the extract_dir. 
    Will create extract_dir if it doesn't exist.
    '''
    print "Download initialized"
    urllib.urlretrieve(src_url, file_name)
    print "Download complete"

    #create the directory, if it doesn't exist
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    #tar into the target file
    os.system("tar -xvzf %s -C %s" % (file_name, extract_dir))
    print "Extracted data into %s" % extract_dir

    #moving the downloaded file into the extract_dir
    os.system("mv %s %s" % (file_name, extract_dir))


def get_catalog_dict(catalog_dir):
    ''' 
    Given a directory, dict of  *.catalog in the directory.
    Includes RELATIVE location of the file, as well as the name.
    dict <K,V> format of <relative_path_dir+file_name, file_name>
    Will traverse sub-directories.
    example:
    {"temp/SCEC_DC/1999.catalog":"1999.catalog"}
    '''
    catalogs = {}
    for curdir, dirs, files in os.walk(catalog_dir):
        for check_file in files:
            if '.catalog' in check_file: #TODO change to regex to make fancy
                catalogs[os.path.join(curdir,check_file)] = check_file
    print "Grabbed catalog_dict"
    return catalogs

def parse_and_output(catalog_dict, output_dir, format):
    '''
    Outputs the catalogs in catalog_dict into output_dir, in specified format
    Throws @ValueError if format is not supported
    '''
    #create the directory, if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for catalog_path, catalog_name in catalog_dict.items():
        if format == "csv":
            output_csv(catalog_path, catalog_name, output_dir)
        else:
            raise ValueError("Undefined format: '%s'" % format)
    print "Outputted %s items into %s" % (len(catalog_dict), output_dir)

def output_csv(catalog_path, catalog_name, output_dir):
    '''
    Given the path and the name of the catalog,
    Outputs the catalog into output_dir.
    '''
    head_size = 0 
    f = open(catalog_path, 'r')
    #figure out how many lines to skip!
    for line in f:
        if line.startswith("#"):
            head_size += 1
        else:
            break

    skip_length = head_size-1
    head_row_loc = head_size-2

    data_frame = pd.read_csv(catalog_path, header=head_row_loc, skiprows=skip_length, delimiter=r"\s+")
    #data_frame.rename(columns={"#YYY/MD/DD": "YYYY/MD/DD"}, inplace=True)
    data_frame.rename(columns=lambda x: x.replace("#YYY", "YYYY"), inplace=True)
    data_frame.to_csv(os.path.join(output_dir, catalog_name+".csv"), index = False)



if __name__ == "__main__":
    url= 'http://www.data.scec.org/ftp/catalogs/SCEC_DC/SCEDC_catalogs.tar.gz'
    file_name = 'SCED_catalogs.tar.gz'

    #url= 'http://www.data.scec.org/ftp/catalogs/SCSN/SCSN_catalogs.tar.gz'
    #file_name = 'SCSN_catalogs.tar.gz'

    dirty_dir = "dirty_data/"
    clean_dir = "clean_data/"
    download_extract_data(url,file_name, dirty_dir)
    catalog_dict =  get_catalog_dict(dirty_dir)
    parse_and_output(catalog_dict, clean_dir, 'csv')

# <codecell>

#Author: Tristan Tao

from pandas import read_csv
from pandas import concat
import pandas as pd
import re
import os


def grab_data_dict(start_year, end_year, target_dir):
    '''
    Return a dict of catalogs: <relative_path:year>
    The catalogs will fall in the years between start_year and end_year.
    '''

    target_years = range(start_year, end_year+1)
    print "working with the following years %s" % target_years
    catalog_extraction = {}

    for curdir, dirs, files in os.walk(target_dir):
        for check_file in files:
            regex_res = re.findall('\d+', check_file)
            if len(regex_res) == 1: #only one number
                extracted_year = int(regex_res[0])
                if extracted_year in target_years:
                    catalog_extraction[os.path.join(curdir, check_file)] = extracted_year
    return catalog_extraction

def grab_data_frame(catalog_dict):
    '''
    Given a catalog_dict, 
    '''
    data_frame = pd.DataFrame()
    for csv_location, year in catalog_dict.items():
        partial_data = pd.read_csv(csv_location)
        data_frame = concat([data_frame, partial_data])
    return data_frame

# <codecell>

a = grab_data_dict(1998,1999,'clean_data/')

# <codecell>

b = grab_data_frame(a)
teststr = str(b["YYYY/MM/DD"][0])
c = re.split("\\s+", teststr)[1]
re.split("/", c)[0]

# <codecell>

b = grab_data_frame(a)
teststr = b["YYYY/MM/DD"].apply(str)

# <codecell>

test = b[0:10]
b[0:10]

# <codecell>

b = grab_data_frame(a)[1:2]
teststr = b["YYYY/MM/DD"]
c = re.split("\\s+", str(teststr))[1]
d = re.split("/", c)[0]
d

# <codecell>

def get_year(entry):
    a = str(entry["YYYY/MM/DD"])
    b = re.split("\\s+", a)[1]
    return int(re.split("/", b)[0])

# <codecell>

def get_plot_res(years):
    data_dict = grab_data_dict(years[0],years[1],'clean_data/')
    quakes = grab_data_frame(data_dict)

    max_lat = quakes['LAT'].max()
    min_lat = quakes['LAT'].min()
    max_lon = quakes['LON'].max()
    min_lon = quakes['LON'].min()
    dimensions = ((max_lat-min_lat), (max_lon-min_lon))

    threshold = [1,10,100,1000,10000]
    res = ['f','h','i','l','c']
    area = dimensions[0]*dimensions[1]

    for i in range(5):
        if area <= threshold[i]:
            res = res[i]
            break
        if i == 5:
            res = res[5]
            
    return res

# <codecell>

def get_colormap(years):
    num_years = years[1]-years[0]
    year_color = np.arange(0, num_years + 1).astype(float)/(num_years + 1)
    
    colormap = [0]*(num_years+1)
    for i in range(0, num_years + 1):
        colormap[i] = pylab.cm.Reds(year_color[i])
    
    return colormap

# <codecell>

colors = get_colormap((1998,2000))
colors

# <codecell>

def get_quakes_subset(years, quantity):
    
    quakes = grab_data_frame(grab_data_dict(years[0],years[0],'clean_data/'))[0:quantity]
    
    for year in range(years[0] + 1, years[1] + 1): 
        data_dict = grab_data_dict(year,year,'clean_data/')
        df = grab_data_frame(data_dict)[0:quantity]
        quakes = pd.DataFrame.append(quakes, df)
        
    return quakes

# <codecell>

from mpl_toolkits.basemap import Basemap

def plot_quakes(years, figsize, quantity):
    
    res = get_plot_res(years)
    
    colors = get_colormap(years)
    
    quakes = get_quakes_subset(years, quantity)
    
    lat_0 = quakes['LAT'].mean()
    lon_0 = quakes['LON'].mean()
    fig = matplotlib.pyplot.figure(figsize=(9,9))
    m = Basemap(resolution = res, projection='nsper',
                area_thresh = 1000., satellite_height = 200000,
                lat_0 = lat_0, lon_0 = lon_0)
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    m.fillcontinents(color = 'green', lake_color = 'aqua')
    m.drawmapboundary(fill_color = 'blue')
    x, y = m(quakes.LON, quakes.LAT)
    
    for i in range(0, len(x) - 1):
        color = colors[get_year(quakes[i:i+1])-years[0]]
        m.plot(x[i:i+1], y[i:i+1], color = color, 
               marker = 'o', markersize = (pi*(quakes.MAG[i:i+1]).apply(float)**2), 
               alpha = 0.5)

# <codecell>

plot_quakes((1998,2013),(15,15),10)

# <codecell>

from mpl_toolkits.basemap import Basemap

def plot_quakes_points(years, figsize, quantity):
    
    res = get_plot_res(years)
    
    colors = get_colormap(years)
    
    quakes = get_quakes_subset(years, quantity)
    
    lat_0 = quakes['LAT'].mean()
    lon_0 = quakes['LON'].mean()
    fig = matplotlib.pyplot.figure(figsize=(9,9))
    m = Basemap(resolution = res, projection='nsper',
                area_thresh = 1000., satellite_height = 200000,
                lat_0 = lat_0, lon_0 = lon_0)
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    m.fillcontinents(color = 'green', lake_color = 'aqua')
    m.drawmapboundary(fill_color = 'blue')
    x, y = m(quakes.LON, quakes.LAT)
    
    for i in range(0, len(x) - 1):
        color = colors[get_year(quakes[i:i+1])-years[0]]
        m.plot(x[i:i+1], y[i:i+1], color = color, 
               marker = 'o', markersize = 2*pi, 
               alpha = 0.5)

# <codecell>

plot_quakes_points((1998,2013),(15,15),10)

