from pathlib import Path

import unidecode
import ipyvuetify as v
from ipyvuetify.extra import FileInput 
from sepal_ui import sepalwidgets as sw 
from sepal_ui.scripts import utils as su

from utils import parameter as pm

class DownloadTile(sw.Tile):
    
    SELECT_TYPE = [
                'Shape file (.shp, .shx, .dbf, .prj)',
                'Table file (.csv)'
    ]
    
    # the first 3 one are compulsory
    SHP_SUFFIX = ['.shp', '.dbf', '.shx', '.cpg', '.prj', '.sbn', '.sbx']
    
    def __init__(self):
        
        self.output = sw.Alert().add_msg('import your file')
        
        self.btn = sw.Btn('import', icon = 'mdi-check', class_='mt-4')
        
        self.select_type = v.Select(
            label='Select table type', 
            items= self.SELECT_TYPE,
            v_model = None,
        )
        
        self.input_file = FileInput(
            disabled = True, 
        )
        
        super().__init__(
            'aoi_widget',
            "Import a file",
            btn = self.btn,
            inputs = [self.select_type, self.input_file],
            output = self.output
        )
        
        self.select_type.observe(self.on_type_change, 'v_model')
        self.btn.on_event('click', self.load_file)
        
        
    def on_type_change(self, change):
        
        self.input_file.clear()
        self.input_file.disabled = False
        
        # shape files
        if change['new'] == self.SELECT_TYPE[0]:
            self.input_file.multiple = True
        # table file 
        elif change['new'] == self.SELECT_TYPE[1]:
            self.input_file.multiple = False
        else:
            self.input_file.disabled = True
        
        return
    
    def load_file(self, widget, data, event):
    
        # toggle the btn
        widget.toggle_loading()
    
        self.output.add_msg('start the downlaod')
    
        # load the files
        myfiles = self.input_file.get_files()
    
        # test that the file is not empty 
        if not len(myfiles):
            self.output.add_msg('No file selected', 'error')
            return widget.toggle_loading()
        
        ####################################
        ##      test the file sended      ##
        ####################################
        
        # table type
        if self.select_type.v_model == self.SELECT_TYPE[1]:
            
            if Path(myfiles[0]['name']).suffix != '.csv':
                self.output.add_msg('.csv is the only supported format for tables', 'error')
                return widget.toggle_loading()
            
        # shp type
        if self.select_type.v_model == self.SELECT_TYPE[0]:
            
            
            
            name = set([Path(f['name']).stem for f in myfiles])
            if len(name) > 1:
                self.output.add_msg('the different file of your shapefile should have the same name', 'error')
                return widget.toggle_loading()
            
            suffixes = [Path(f['name']).suffix for f in myfiles]
            if not all(ext in suffixes  for ext in self.SHP_SUFFIX[:3]):
                self.output.add_msg(f'The mimnimum import requires ({", ".join(self.SHP_SUFFIX[:3])})', 'error')
                return widget.toggle_loading()
            
            if not all(ext in self.SHP_SUFFIX  for ext in suffixes):
                self.output.add_msg(f'One of the file does not have an extention included in the ESRI shapefile description ({", ".join(self.SHP_SUFFIX)})', 'error')
                return widget.toggle_loading()
            
        ######################################
        ##      download all the files      ##
        ######################################
        
        for file in myfiles:
        
            # create a path
            path = Path(pm.get_down_dir()).joinpath(unidecode.unidecode(file['name']))
    
            if path.is_file():
                self.output.add_msg(f'File {path} already exists, skipping.', 'warning')
                break
    
            src = file['file_obj'] 
            with path.open('wb') as dst:
                content = bytes(src.read())
                dst.write(content)
            
        
        if self.select_type.v_model == self.SELECT_TYPE[0]:
            path = path.stem + '.shp'
        
        self.output.add_msg(f'Download complete in {path}', 'success')
    
        return widget.toggle_loading()