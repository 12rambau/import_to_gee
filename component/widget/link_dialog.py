import ipyvuetify as v 
import pyperclip

from sepal_ui import sepalwidgets as sw

from component.message import cm

class LinkDialog(sw.SepalWidget, v.Dialog):
    
    def __init__(self, tile):
        
        self.tile = tile
        
        self.title = v.CardTitle(children=[cm.dialog.title])
        self.text = v.CardText(children = [cm.dialog.msg])
        
        self.link = v.TextField(
            class_ = "ma-5",
            v_model = 'je suis un link', 
            outlined = True,
            label = cm.dialog.link_lbl,
            readonly = True,
            append_icon = 'mdi-clipboard-outline'
        )     
        
        self.card = v.Card(
            children = [
                self.title,
                self.text,
                self.link,
            ]
        )
        
        super().__init__(
            value = False,
            max_width = '600px',
            children = [self.card]
        )
        
        self.tile.observe(self.fire_dialog, 'updated')
    
    def fire_dialog(self, link):
        
        # the toggle btn has changed let's see if it's for a good reason
        if self.tile.alert.type == 'success':
        
            self.value = True
            self.link.v_model = self.tile.model.asset_name.replace('projects/earthengine-legacy/assets/', '')
            
        return