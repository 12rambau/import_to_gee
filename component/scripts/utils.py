import os

import ee

from component.message import cm

ee.Initialize()


def display_asset(output, asset):
    """remove the manifest from the asset name and display it to the user"""

    asset = asset.replace("projects/earthengine-legacy/assets/", "")

    output.add_msg(cm.asset_created.format(asset), "success")

    return asset
