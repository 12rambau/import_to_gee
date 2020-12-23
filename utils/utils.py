from utils import message as ms

def display_asset(output, asset):
    """remove the manifest from the asset name and display it to the user"""
    
    asset = asset.replace('projects/earthengine-legacy/assets/', '')
    
    output.add_msg(ms.asset_created.format(asset), 'success')
    
    return