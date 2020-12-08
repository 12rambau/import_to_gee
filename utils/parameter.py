import os 

#######################
##      folders      ##
#######################

def create_folder(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    return pathname

def get_down_dir():
    pathname = os.path.expanduser('~/aoi')
    return create_folder(pathname)

