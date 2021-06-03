from pathlib import Path

import unidecode
import ipyvuetify as v
from ipyvuetify.extra import FileInput 
from sepal_ui import sepalwidgets as sw 
from sepal_ui.scripts import utils as su

from component import parameter as cp
from component.message import cm

class DownloadTile(sw.Tile):
    
    SELECT_TYPE = [
                'Shape file (.shp, .shx, .dbf, .prj)',
                'Table file (.csv)'
    ]
    
    # the first 3 one are compulsory
    SHP_SUFFIX = ['.shp', '.dbf', '.shx', '.cpg', '.prj', '.sbn', '.sbx']
    
    def __init__(self):
        
        self.select_type = v.Select(
            label= cm.download.select_type, 
            items= self.SELECT_TYPE,
            v_model = None,
        )
        
        self.input_file = FileInput(
            disabled = True, 
        )
        
        super().__init__(
            'aoi_tile',
            cm.download.title,
            inputs = [self.select_type, self.input_file],
            alert = sw.Alert(),
            btn = sw.Btn(cm.download.import_btn, icon = 'mdi-check', class_='mt-4')
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
    
    @su.loading_button(debug=False)
    def load_file(self, widget, data, event):
    
        self.alert.add_msg(cm.download.start)
    
        # load the files
        myfiles = self.input_file.get_files()
    
        # test that the file is not empty 
        if not self.alert.check_input(myfiles, cm.download.no_file): return
        
        ####################################
        ##      test the file sended      ##
        ####################################
        
        # table type
        if self.select_type.v_model == self.SELECT_TYPE[1]:
            
            if Path(myfiles[0]['name']).suffix != '.csv':
                self.alert.add_msg(cm.download.not_csv, 'error')
                return
            
        # shp type
        if self.select_type.v_model == self.SELECT_TYPE[0]:
            
            name = set([Path(f['name']).stem for f in myfiles])
            if len(name) > 1:
                self.alert.add_msg(cm.download.naming_bug, 'error')
                return 
            
            suffixes = [Path(f['name']).suffix for f in myfiles]
            if not all(ext in suffixes  for ext in self.SHP_SUFFIX[:3]):
                self.alert.add_msg(cm.download.missing_files.format(", ".join(self.SHP_SUFFIX[:3])), 'error')
                return 
            
            if not all(ext in self.SHP_SUFFIX  for ext in suffixes):
                self.alert.add_msg(cm.download.unknown_extention.format(", ".join(self.SHP_SUFFIX)), 'error')
                return 
            
        ######################################
        ##      download all the files      ##
        ######################################
        
        for file in myfiles:
        
            # create a path
            path = cp.down_dir.joinpath(unidecode.unidecode(file['name']))
    
            if path.is_file():
                self.alert.add_msg(cm.download.already_exist.format(path), 'warning')
                break
    
            src = file['file_obj'] 
            with path.open('wb') as dst:
                content = bytes(src.read())
                dst.write(content)
            
        
        if self.select_type.v_model == self.SELECT_TYPE[0]:
            path = path.stem + '.shp'
        
        self.alert.add_msg(cm.download.complete.format(path), 'success')
    
        return