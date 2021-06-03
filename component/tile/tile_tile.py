import os
from types import SimpleNamespace

import ipyvuetify as v
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import gee
from sepal_ui.scripts import utils as su
from sepal_ui import color
import ee
from traitlets import Int

from component import scripts as cs
from component.message import cm

ee.Initialize()

class TileTile(sw.Tile):
    
    updated = Int(0).tag(sync=True)
    
    def __init__(self, m, aoi_model):
        
        # to store the final asset 
        self.assetId = None 
        
        # the map to display the final tile
        self.m = m
        
        #store the aoi_model 
        self.aoi_model = aoi_model
        
        # inputs 
        self.grid_name = v.TextField(
            label = cm.tile.asset_lbl,
            v_model = None
        )
        
        self.batch_size = sw.NumberField(
            label = cm.tile.nb_batch_lbl,
            v_model=1,
            max_=100,
            type = 'number'
        )
        
        # the aoi default btn is not set to btn anymore (to avoid conflict with the standard btn)
        # to mimic its behaviour in the dialog interface we wire 2 attribute btn and aoi_btn to the same Btn object
        self.model = SimpleNamespace(asset_name=None)
        
        super().__init__(
            'tile_widget',
            cm.tile.title,
            inputs = [self.batch_size, self.grid_name],
            alert = sw.Alert(),
            btn = sw.Btn(cm.tile.btn, icon = 'mdi-check')
        )
        
        # link the component together 
        self.btn.on_event('click', self.create_grid)
        self.batch_size.observe(self.write_name, 'v_model')
        
    @su.loading_button(debug=False)
    def create_grid(self, widget, data, event):
        
        # read the data 
        aoi = self.aoi_model 
        grid_name = self.grid_name.v_model
        grid_batch = int(self.batch_size.v_model)
        
        #check the vars 
        if not self.alert.check_input(aoi.name, cm.no_aoi): return 
        if not self.alert.check_input(grid_batch, cm.no_size): return 
        if not self.alert.check_input(grid_name, cm.no_name): return
        
        grid = cs.set_grid(aoi.gdf, grid_batch, grid_name, self.alert)
            
        # get exportation parameters 
        folder = ee.data.getAssetRoots()[0]['id']
        asset = os.path.join(folder, grid_name)
        
        # export
        if not gee.is_asset(grid_name, folder):
            
            task_config = {
                'collection': grid, 
                'description':grid_name,
                'assetId': asset
            }
    
            task = ee.batch.Export.table.toAsset(**task_config)
            task.start()
            gee.wait_for_completion(grid_name, self.alert)
        
        self.assetId = asset
            
        # remove the preview square from the map
        for layer in self.m.layers:
            if layer.name == 'preview square size':
                self.m.remove_layer(layer)
        
        # display the asset on the map 
        self.m.addLayer(
            ee.FeatureCollection(asset), 
            {'color': color.accent}, 
            cm.tile.grid_layer
        )
        
        self.model.asset_name = cs.display_asset(self.alert, asset)
        
        self.updated += 1
        
        return
        
    def write_name(self, change):
        
        # read the inputs 
        aoi_name = self.aoi_model.name
        grid_batch = int(self.batch_size.v_model) if self.batch_size.v_model else 0
        
        name = f'{aoi_name}_Grid_{grid_batch}' if aoi_name else None
        
        self.grid_name.v_model = name
        
        return