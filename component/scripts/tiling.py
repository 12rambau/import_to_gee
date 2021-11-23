import json
from itertools import product

import numpy as np
import decimal as d

import geemap
from shapely import geometry as sg
from shapely.ops import unary_union
import geopandas as gpd
from pyproj import CRS, Transformer
from pathlib import Path

from component.message import cm
from component import parameter as cp

d.getcontext().prec = 15

def set_grid(aoi, grid_batch, grid_name, output):
    """compute a grid around a given aoi (ee.FeatureCollection) that fits the Planet Lab requirements"""
    
    # get the shape of the aoi in EPSG:4326 proj 
    aoi_gdf = aoi.to_crs('EPSG:3857')
    
    output.add_live_msg(cm.digest_aoi)
    
    # retreive the bounding box
    aoi_bb = sg.box(*aoi_gdf.total_bounds)
    aoi_bb.bounds
    
    # compute the longitude and latitude in the apropriate CRS
    crs_4326 = CRS.from_epsg(4326)
    crs_3857 = CRS.from_epsg(3857)
    crs_min_x, crs_min_y, crs_max_x, crs_max_y = crs_3857.area_of_use.bounds

    proj = Transformer.from_crs(4326, 3857, always_xy=True)
    bl = proj.transform(crs_min_x, crs_min_y)
    tr = proj.transform(crs_max_x, crs_max_y)

    # the planet grid is constructing a 2048x2048 grid of SQUARES. 
    # The latitude extends is bigger (20048966.10m VS 20026376.39) so to ensure the "squariness"
    # Planet lab have based the numerotation and extends of it square grid on the longitude only. 
    # the extreme -90 and +90 band it thus exlucded but there are no forest there so we don't care
    longitudes = np.linspace(bl[0], tr[0], 2048+1)

    # the planet grid size cut the world in 248 squares vertically and horizontally
    box_size = (tr[0]-bl[0])/2048

    
    # filter with the geometry bounds
    min_lon, min_lat, max_lon, max_lat = aoi_gdf.total_bounds

    # filter lon and lat 
    lon_filter = longitudes[(longitudes > (min_lon - box_size)) & (longitudes < max_lon + box_size)]
    lat_filter = longitudes[(longitudes > (min_lat - box_size)) & (longitudes < max_lat + box_size)]

    # get the index offset 
    x_offset = np.nonzero(longitudes == lon_filter[0])[0][0]
    y_offset = np.nonzero(longitudes == lat_filter[0])[0][0]
    
    output.add_live_msg(cm.build_grid)
    
    # count the number of batch cell in width 
    batch_width = (len(lat_filter)-1) // grid_batch
    # create the grid
    batch, x, y, names, squares = [], [], [], [], []
    for ix, iy in product(range(len(lon_filter)-1), range(len(lat_filter)-1)):
        
        # fill the grid values
        batch_id = (ix // grid_batch) * (batch_width + 1) + (iy // grid_batch)
        batch.append(batch_id)   
        x.append(ix + x_offset)
        y.append(iy + y_offset)
        names.append(f'L15-{x[-1]:4d}E-{y[-1]:4d}N.tif')
        squares.append(sg.box(lon_filter[ix], lat_filter[iy], lon_filter[ix+1], lat_filter[iy+1]))
        
    # create a buffer grid in lat-long
    grid = gpd.GeoDataFrame({'batch': batch, 'x':x, 'y':y, 'names':names, 'geometry':squares}, crs='EPSG:3857')

    # cut the grid to the aoi extends 
    mask = grid.intersects(aoi_gdf.dissolve()['geometry'][0])
    grid = grid.loc[mask]
    
    # project back to 4326
    grid = grid.to_crs('EPSG:4326')
    
    # export the grid as a json file 
    path = cp.down_dir.joinpath(f'{grid_name}.geojson')
    grid.to_file(path, driver='GeoJSON')
    
    output.add_live_msg(cm.grid_complete, 'success')
    
    return geemap.geojson_to_ee(grid.__geo_interface__)

def preview_square(geometry, grid_size):
    
    # get the center of the aoi
    center = geometry.centroid().getInfo()['coordinates']
    
    # create the square 
    square = gpd.GeoDataFrame({'geometry': [Point(center[0], center[1])]}, crs='EPSG:4326') \
        .to_crs('EPSG:3857') \
        .buffer(grid_size*1000) \
        .envelope \
        .to_crs('EPSG:4326')
    
    return geemap.geojson_to_ee(square.__geo_interface__)
    
    
    
    
    
    