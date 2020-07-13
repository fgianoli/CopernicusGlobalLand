# Copernicus Global Land Downloader

A PyQGIS script to download Copernicus Global Land Products and to resample 333m products to 1Km.

The CGLS vegetation-related products (i.e. NDVI, LAI, FAPAR…), based on PROBA-V observations, have been distributed at 1km and 333m spatial resolution until June, 2020. However, as of July, 2020, all Near Real Time (NRT) production of the vegetation biophysical variables, based on Sentinel-3 observations, are no longer provided at 1km resolution. Nonetheless, users interested in continuing their 1km time series can use a resample of the new 333m products. 
This algorithm allows to resample the 333meters Copernicus Products to 1Km preserving the spatial extension of 1Km time series. 

## How to install

A geoprocessing script was implemented for QGIS 3.x.  
The reason behind the choice to develop a new script instead of a QGIS Plugin is that it is known that PyQGIS scripts are the best way to perform tasks within QGIS (Sherman G., 2018). It is possible to use a PyQGIS script in a workflow or in a graphical modeler or to integrate it in a specific plugin. In this case, a geoprocessing tool is more flexible and it can be adapted to each need.  

In order to install these tools, download the trpository and open QGIS 3.x.  
Under the Scripts dropdown menu on the top of the Processing toolbox, select **Add script to Toolbox** and then browse to the repository and select the *.py* files.  
Automatically, in the Processing toolbox will be added a new *Scripts* folder with a group of new algorithms named **Copernicus Global Land Tools**.  

![Scripts Toolbox](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/doc/toolbox.JPG?raw=true)

Once installed, will be possible to run each script and will be possible to add these script in a processing chain using the *Graphical Modeler* of QGIS. 


## How to use the Downloader

This tool allows users to connect to the manifest of CGL products and to choose which one the user wants to download. The algorithm downloads the NetCDF file and converts it to Geotiff.  
To use this tool it is necessary to have a valid account to CGL (https://land.copernicus.eu/) website.
- Select the product collection to download and the day. The algorithm will download the product with the closest date.  
- Download directory is the directory in which the product will be downloaded and converted to geotiff.  
- Download file: this is an additional parameter, leave it empty.

![Downloader](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/doc/downloader.JPG?raw=true)

## CGL resampler
first of all....

### Results of the resampler
Lorem ipsum

### Bibliography

Sherman Gary, 2018. *The PyQGIS Programmer’s Guide*. Locate Press  


## Acknowledgments & Authors
We thank for the help in developing and testing these tools:  
*Enrico Ferreguti, Xavier Rotllan Puig, Pier Lorenzo Marasco, Martino Boni*  
Author: Federico Gianoli
