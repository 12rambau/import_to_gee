import ipyvuetify as v
from traitlets import Int
from sepal_ui import aoi
from sepal_ui import mapping as sm

from component.message import cm


class ExportTile(aoi.AoiTile):
    """adapt the AoiTile object for this specifi usage"""

    ready = Int(0).tag(sync=True)

    def __init__(self, **kwargs):
        """add a download behaviour for admin areas"""

        # set the accepted methods
        kwargs["methods"] = ["ADMIN2", "DRAW", "SHAPE", "POINTS"]

        # call the constructor
        super().__init__(**kwargs)

        # set the title
        self.set_title(cm.to_gee.title)

        # add js behaviour
        self.view.observe(self.export_data, "updated")

    def export_data(self, *args):
        """trigger the exportation to Earth Engine"""

        if self.view.model.method == "ADMIN2":

            self.view.model.export_to_asset()

        # update the message
        self.view.alert.add_msg(cm.to_gee.success, "success")

        self.ready += 1

        return
