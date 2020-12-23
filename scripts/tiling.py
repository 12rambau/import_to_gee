import json

import numpy as np
import geemap
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from itertools import product
import geopandas as gpd

def set_grid(aoi, grid_size, grid_batch):
    """compute a grid around a given aoi (ee.FeatureCollection)"""
    
    #extract bounds from ee_object 
    ee_bounds = aoi.geometry().bounds().coordinates()
    coords = ee_bounds.get(0).getInfo()
    ll, ur = coords[0], coords[2]

    # Get the bounding box
    min_lon, min_lat, max_lon, max_lat = ll[0], ll[1], ur[0], ur[1]
    
    #get the shape of the aoi 
    aoi_json = geemap.ee_to_geojson(aoi)
    aoi_shp = unary_union([shape(feat['geometry']) for feat in aoi_json['features']])
    
    # we use the equator approximation (.01 deg = 1.11 km)
    # the grid will be latlong squares (not in km)
    buffer_size = grid_size * (.01/1.11)
    
    # compute the longitudes and latitudes top left corner coordinates
    longitudes = np.arange(min_lon, max_lon, buffer_size)
    latitudes = np.arange(min_lat, max_lat, buffer_size)
    
    #create the grid 
    points = []
    batch = []
    for i, coords in enumerate(product(longitudes, latitudes)):
        
        # create grid geometry 
        points.append(Point(coords[0], coords[1]))
        
        # add a batch number 
        batch.append(int(i/grid_batch))
    
    grid = gpd.GeoDataFrame({'batch': batch, 'geometry':points}) \
        .buffer(buffer_size) \
        .envelope \
        .intersection(aoi_shp)
    
    # filter empty geometries
    grid = grid[np.invert(grid.is_empty)]
    
    # convert gdp to GeoJson
    json_df = json.loads(grid.to_json())
    
    return geemap.geojson_to_ee(json_df)
    
    
    
    
    
    