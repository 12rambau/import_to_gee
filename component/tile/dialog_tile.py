from sepal_ui import sepalwidgets as sw 
import ipyvuetify as v 

class TileDialog(sw.SepalWidget, v.Dialog):
    
    def __init__(self, tile_tile):
        
        self.tile_tile = tile_tile
        
        self.title = v.CardTitle(children=['Copy this link to you clipboard'])
        self.text = v.CardText(children = ["click on the link then 'ctrl+a' and then 'ctrl+c'"])
        
        self.link = v.TextField(
            class_ = "ma-5",
            v_model = 'je suis un link', 
            outlined = True,
            label = 'link',
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
        
        # self.link.on_event('click', self.select_all) 
        self.tile_tile.btn.observe(self.fire_dialog, 'loading')
    
    # the pyperclip method does not work with SEPAL
    #def select_all(self, widget, data, event):
    #    
    #    # copy the data to clipboard
    #    pyperclip.copy(self.link)
    #    
    #    # select all the link to prevent pyperclip failures
    #    
    #    return
    
    def fire_dialog(self, link):
        
        # the toggle btn has changed let's see if it's for a good reason
        if self.tile_tile.output.type == 'success':
        
            self.value = True
            self.link.v_model = self.tile_tile.assetId.replace('projects/earthengine-legacy/assets/', '')
            
        return