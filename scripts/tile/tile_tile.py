import os

import ipyvuetify as v
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import gee
import ee

from scripts.tiling import set_grid
from utils.utils import *

ee.Initialize()

class TileTile(sw.Tile):
    
    def __init__(self, m, aoi_io):
        
        # to store the final asset 
        self.assetId = None 
        
        # the map to display the final tile
        self.m = m
        
        #store the aoi_io 
        self.aoi_io = aoi_io
        
        # inputs 
        self.grid_name = v.TextField(
            label = "Asset name",
            v_model = None
        )
        
        self.size_select = v.Slider(
            label = 'Select the tile size (km)',
            min = 10,
            max = 1000,
            step = 10,
            thumb_label = 'always',
            class_ = 'mt-10',
            v_model = None
        )
        
        self.batch_size = v.Slider(
            label = 'Select number of tiles in a batch',
            min = 1,
            thumb_label = 'always',
            class_ = 'mt-5',
            v_model = None
        )
        
        self.btn = sw.Btn('tile the aoi', icon = 'mdi-check')
        
        self.output = sw.Alert()
        
        super().__init__(
            'tile_widget',
            'Tiling interface',
            btn = self.btn,
            inputs = [self.size_select, self.batch_size, self.grid_name],
            output = self.output
        )
        
        # link the component together 
        self.btn.on_event('click', self.create_grid)
        self.batch_size.observe(self.write_name, 'v_model')
        self.size_select.observe(self.write_name, 'v_model')
        
    def create_grid(self, widget, data, event):
        
        # toggle the btn 
        widget.toggle_loading()
        
        # read the data 
        aoi = self.aoi_io 
        grid_size = self.size_select.v_model
        grid_name = self.grid_name.v_model
        
        #check the vars 
        if not self.output.check_input(aoi.get_aoi_name(), ms.no_aoi): return widget.toggle_loading()
        if not self.output.check_input(grid_size, ms.no_size): return widget.toggle_loading()
        if not self.output.check_input(grid_name, ms.no_name): return widget.toggle_loading()
        
        grid = set_grid(aoi.get_aoi_ee(), grid_size)
        
        # get exportation parameters 
        folder = ee.data.getAssetRoots()[0]['id']
        asset = os.path.join(folder, grid_name)
        
        # export
        if not isAsset(grid_name, folder):
            task_config = {
                'collection': grid, 
                'description':grid_name,
                'assetId': asset
            }
    
            task = ee.batch.Export.table.toAsset(**task_config)
            task.start()
            gee.wait_for_completion(grid_name, self.output)
        
        self.assetId = asset
        
        #display the asset on the map 
        self.m.addLayer(
            ee.FeatureCollection(asset), 
            {'color': v.theme.themes.dark.accent}, 
            'grid'
        )
        
        display_asset(self.output, asset)
        
        # toggle the loading
        widget.toggle_loading()
        
        return
        
    def write_name(self, change):
        
        # read the inputs 
        aoi_name = self.aoi_io.get_aoi_name()
        grid_size = self.size_select.v_model
        grid_batch = self.batch_size.v_model
        
        name = f'{aoi_name}_Grid_{grid_size}x{grid_size}_batch_{grid_batch}' if aoi_name else None
        
        self.grid_name.v_model = name
        
        return