# Copernicus Global Land Downloader

A PyQGIS script to download Copernicus Global Land Products and to resample 333m products to 1Km.

The CGLS vegetation-related products (i.e. NDVI, LAI, FAPAR…), based on PROBA-V observations, have been distributed at 1km and 333m spatial resolution until June, 2020. However, as of July, 2020, all Near Real Time (NRT) production of the vegetation biophysical variables, based on Sentinel-3 observations, are no longer provided at 1km resolution. Nonetheless, users interested in continuing their 1km time series can use a resample of the new 333m products. 
This algorithm allows to resample the 333meters Copernicus Products to 1Km preserving the spatial extension of 1Km time series. 

## How to install

A geoprocessing script was implemented for QGIS 3.x.  
The reason behind the choice to develop a new script instead of a QGIS Plugin is that it is known that PyQGIS scripts are the best way to perform tasks within QGIS (Sherman G., 2018). It is possible to use a PyQGIS script in a workflow or in a graphical modeler or to integrate it in a specific plugin. In this case, a geoprocessing tool is more flexible and it can be adapted to each need.  

In order to install these tools, download the repository and open QGIS 3.x.  
Under the Scripts dropdown menu on the top of the Processing toolbox, select **Add script to Toolbox** and then browse to the repository and select the *.py* files.  
Automatically, in the Processing toolbox will be added a new *Scripts* folder with a group of new algorithms named **Copernicus Global Land Tools**.  

![Scripts Toolbox](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/doc/toolbox.JPG?raw=true)

Once installed, will be possible to run each script and will be possible to add these script in a processing chain using the *Graphical Modeler* of QGIS. 


## How to use the Downloader

This tool allows users to connect to the manifest of CGL products and to choose which one the user wants to download. The algorithm downloads the NetCDF file and converts it to Geotiff.  
To use this tool it is necessary to have a valid account to CGL (https://land.copernicus.eu/) website.
- Select the product collection to download and the day. The algorithm will download the product with the closest date.  
- Download directory is the directory in which the product will be downloaded and converted to geotiff.  
- Download file: this is an additional parameter used by the tool, **leave it empty**.

![Downloader](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/doc/downloader.JPG?raw=true)

In order to works this tool requires Pandas library. Usually, this library is installed within QGIS. If your installation doesn't come with Pandas, please install it trough OSGeo4W Installer or via pip. 

## CGL Resampler Tool

First of all, in order to use this tool, is necessary to add in the Processing toolbox both the *raster_calc_copernicus.py* and *CGL_resampler.py* scripts.  
This algorithm allows to resample the 333meters Copernicus Products to 1Km preserving the spatial extension of 1Km time series.  
In order to perform this conversion, the following steps are needed:  
- Reclassify the input raster in 0-1 (where 1 are valid values), 
- Resample the output using mode -so 0 is where at least 5 pixels inside the kernel aren't valid - 
- Multiply these results with the result of 3x3 resampling using average.  
All these steps are needed in order to include the condition that at least 5 out of the 9 pixels have to have valid values (i.e. not NA) to return a valid value for the resampled pixel (333m to 1Km).  

![process](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/process.jpg?raw=true)

The UI of this algorithm is the following:

![resampler_UI](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/doc/resampler.JPG?raw=true)

- Input Raster: the input raster to resample (NetCDF, Geotiff...)
- Resampling method: It is possible to choose the resampling method to use. Possible values: *nearest, bilinear,cubic,cubicspline,lanczos,average,mode* (see GDAL_Translate options). Default value: average.
- Reclassify valid data: this parameter is used to reclassify the input raster to exclude the not valid parameters. Default value: [-1,1,1,1,255,0] . The Default value is set for NDVI products.  [min_valid_value <= max_valid_value --> 1, min_not_valid_data <= max_not_valid_data --> 0]  
- Output: the output file

See the following table to see which method is most suitable for each product:

![resampling methods](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/doc/table.JPG?raw=true)

The original Global Land product files can often contain specific values for invalid pixels (flagged values), which need to be dealt with.  
In the case of the NDVI products, for example, digital values in the netCDF (DN) larger than 250 are flagged and need to be converted to NA (No Data).  
When the netCDF files are read in as a raster object, the digital values are scaled into real NDVI values automatically (-0.08:0.93).  
Therefore, after reading the files, all pixels with NDVI values larger than 0.92 (= 250 x scale + offset; in this case, scale = 0.004 and offset = -0.08) were set to NA.  
In the same way, all the other products’ non-valid values were transformed to NAs according to their valid ranges, which can be seen in nex table.  
In addition, other supporting information of each product can be found both in the netCDF file metadata and in their Product User Manual at https://land.copernicus.eu/global/products/.

See the [Cut-off of valid values for each product/layer](https://github.com/xavi-rp/ResampleTool_notebook/blob/master/Table_cutoff_and_resampleMethod.csv)

### Results of the resampler
The tool has been tested and compared with the results of the [R Notebook](https://github.com/xavi-rp/ResampleTool_notebook)  

| Product | Date | Reclassify table | Resampling method |
|----|----|----|----|
| NDVI |01/05/2019  | [-1,1,1,1,255,0] | Average |
| FAPAR|10/05/2019  | [0,7,1,7,210,0] | Average |
| LAI|10/05/2019  | [-1,1,1,1,255,0] | Average |
| FCOVER |10/05/2019  | [0,1,1,1,250,0] | Average |
| DMP|10/05/2019  | [0,327.67,1,327.67,3267,0] | Average |





[Read more about the Resampling Tool](https://github.com/xavi-rp/ResampleTool_notebook/blob/master/Resample_Report_v2.5.pdf)

### Bibliography

Sherman Gary, 2018. *The PyQGIS Programmer’s Guide*. Locate Press  
QGIS Developers,PyQGIS Developer Cookbook, https://docs.qgis.org/3.10/en/docs/pyqgis_developer_cookbook/index.html  (14/07/2020)


## Acknowledgments & Authors
We thank for the help in developing and testing these tools:  
*Enrico Ferreguti, Xavier Rotllan Puig, Pier Lorenzo Marasco, Martino Boni*  
Author: Federico Gianoli
