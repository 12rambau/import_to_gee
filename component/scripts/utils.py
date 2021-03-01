import os

import ee

from component.message import cm

ee.Initialize()

def display_asset(output, asset):
    """remove the manifest from the asset name and display it to the user"""
    
    asset = asset.replace('projects/earthengine-legacy/assets/', '')
    
    output.add_msg(cm.asset_created.format(asset), 'success')
    
    return

def isAsset(asset_descripsion, folder):
    """Check if the asset already exist in the user asset folder
    
    Args: 
        asset_descripsion (str) : the descripsion of the asset
        folder (str): the folder of the glad assets
        
    Returns:
        exist (bool): true if already in folder
    """
    exist = False
    liste = ee.data.listAssets({'parent': folder})['assets']
    for asset in liste:
        if asset['name'] == os.path.join(folder,asset_descripsion):
            exist = True
            break
            
    return exist 