This module is a 2 step wrapper to upload AOI to Google Earth Engine

## usage 

### Step 1 (optional)

If your file is not yet available in your SEAPL folders, you can upload it using the first menu. 

![import](./doc/img/import.png)

### step 2 

Select a methode to define your AOI between : 

- `draw a shape`: manually draw a shape on the map 
- `Upload file` : Use a shapefile as an asset
- `Use point file` : Use a `.csv` file as an aoi asset. Point file need to have at least 3 columns (id, lattitude and longitude) but you can use any custom names. 

Once you have selected your aoi, click the btn and your AOI will be updated as an asset and available for the others SEPAL modules. 

> the file created in step 1 may not appear in the file selector. refresh the list by opening a folder

If the process is successful, your AOI will be display in green on the map. 

![image](./doc/img/results.png)

