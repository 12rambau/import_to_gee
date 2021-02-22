import json

import numpy as np
import geemap
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from itertools import product
import geopandas as gpd

def set_grid(aoi, grid_size, grid_batch, output):
    """compute a grid around a given aoi (ee.FeatureCollection)"""
    
    # get the shape of the aoi in mercator proj 
    aoi_json = geemap.ee_to_geojson(aoi)
    aoi_shp = unary_union([shape(feat['geometry']) for feat in aoi_json['features']])
    aoi_gdf = gpd.GeoDataFrame({'geometry': [aoi_shp]}, crs="EPSG:4326").to_crs('EPSG:3857')
    
    output.add_live_msg('Digest the selected AOI')
    
    # extract the aoi shape in mercator projection 
    aoi_shp_proj = aoi_gdf['geometry'][0]
    
    # extract bounds from gdf 
    min_lon, min_lat, max_lon, max_lat = aoi_gdf.total_bounds

    # mercator is in metter so we change unit
    buffer_size = grid_size * 1000
    
    # compute the longitudes and latitudes top left corner coordinates
    longitudes = np.arange(min_lon, max_lon, buffer_size)
    latitudes = np.arange(min_lat, max_lat, buffer_size)
    
    output.add_live_msg('Building the grid')
    
    #create the grid 
    points = []
    batch = []
    for i, coords in enumerate(product(longitudes, latitudes)):
        
        # create grid geometry 
        points.append(Point(coords[0], coords[1]))
        
        # add a batch number 
        batch.append(int(i/grid_batch))
    
    # create a buffer grid in lat-long
    grid = gpd.GeoDataFrame({'batch': batch, 'geometry':points}, crs='EPSG:3857') \
        .buffer(buffer_size) \
        .envelope \
        .intersection(aoi_shp_proj) \
        .to_crs('EPSG:4326')
    
    # filter empty geometries
    grid = grid[np.invert(grid.is_empty)]
    
    # convert gdp to GeoJson
    json_df = json.loads(grid.to_json())
    
    output.add_live_msg('Grid build completed', 'success')
    
    return geemap.geojson_to_ee(json_df)

def preview_square(geometry, grid_size):
    
    # get the center of the aoi
    center = geometry.centroid().getInfo()['coordinates']
    
    # create the square 
    square = gpd.GeoDataFrame({'geometry': [Point(center[0], center[1])]}, crs='EPSG:4326') \
        .to_crs('EPSG:3857') \
        .buffer(grid_size*1000) \
        .envelope \
        .to_crs('EPSG:4326')
    
    # convert gpd to GeoJson
    json_df = json.loads(square.to_json())
    
    return geemap.geojson_to_ee(json_df)
    
    
    
    
    
    