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

### Results of the resampling tool
The tool has been tested and the results have been compared with the Original 1Km series and with the results of the [R Notebook](https://github.com/xavi-rp/ResampleTool_notebook)  

| Product | Date | Reclassify table | Resampling method |
|----|----|----|----|
| NDVI |01/05/2019  | [-1,1,1,1,255,0] | Average |
| FAPAR|10/05/2019  | [0,7,1,7,210,0] | Average |
| LAI|10/05/2019  | [-1,1,1,1,255,0] | Average |
| FCOVER |10/05/2019  | [0,1,1,1,250,0] | Average |
| DMP|10/05/2019  | [0,327.67,1,327.67,3267,0] | Average |





|   | NDVI-Europe                       |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.97951     | 0.05048                | 0.03123             |
| 2 | Original 1Km Product - QGIS Tool  | 0.97532     | 0.05476                | 0.03326             |
| 3 | R Notebook - QGIS Tool            | 0.99999     | 0.00114                | 0.00098             |

![QGIS_Original](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/NDVI_Europe/resample_correlation_QGISAggr.jpg?raw=true=100x100)  ![QGIS_R](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/NDVI_Europe/resample_correlation_R_QGIS_Aggr.jpg?raw=true=100x100) 

|   | LAI-Europe                        |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.9416      | 0.46936                | 0.31021             |
| 2 | Original 1Km Product - QGIS Tool  | 0.94005     | 0.47589                | 0.31375             |
| 3 | R Notebook - QGIS Tool            | 0.99995     | 0.01297                | 0.00737             |

![QGIS_Original](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/LAI_Europe/resample_correlation_QGISAggr.jpg?raw=true=100x100)  ![QGIS_R](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/LAI_Europe/resample_correlation_R_QGIS_Aggr.jpg?raw=true=100x100) 


|   | LAI-Amazonia                      |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.70523     | 0.90322                | 0.65949             |
| 2 | Original 1Km Product - QGIS Tool  | 0.70638     | 0.96189                | 0.68983             |
| 3 | R Notebook - QGIS Tool            | 0.99988     | 0.01338                | 0.00834             |

![QGIS_Original](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/LAI_Amazonia/resample_correlation_QGISAggr.jpg?raw=true=100x100)  ![QGIS_R](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/LAI_Amazonia/resample_correlation_R_QGIS_Aggr.jpg?raw=true=100x100) 


|   | FCOVER-Europe                     |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.97581     | 0.06967                | 0.04841             |
| 2 | Original 1Km Product - QGIS Tool  | 0.97396     | 0.07195                | 0.04931             |
| 3 | R Notebook - QGIS Tool            | 0.99998     | 0.00204                | 0.00095             |

![QGIS_Original](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FCOVER_Europe/resample_correlation_QGISAggr.jpg?raw=true=100x100)  ![QGIS_R](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FCOVER_Europe/resample_correlation_R_QGIS_Aggr.jpg?raw=true=100x100) 


|   | FCOVER-Amazonia                   |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.70206     | 0.11937                | 0.0835              |
| 2 | Original 1Km Product - QGIS Tool  | 0.71047     | 0.12503                | 0.0865              |
| 3 | R Notebook - QGIS Tool            | 0.99988     | 0.00197                | 9e-04               |

![QGIS_Original](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FCOVER_Amazonia/resample_correlation_QGISAggr.jpg?raw=true=100x100)  ![QGIS_R](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FCOVER_Amazonia/resample_correlation_R_QGIS_Aggr.jpg=100x100) 


|   | FAPAR-W Africa                    |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.986       | 0.05055                | 0.02808             |
| 2 | Original 1Km Product - QGIS Tool  | 0.98201     | 0.05913                | 0.03304             |
| 3 | R Notebook - QGIS Tool            | 0.99999     | 0.00101                | 0.00063             |

![QGIS_Original](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FAPAR_WAfrica/resample_correlation_QGISAggr.jpg=100x100)  ![QGIS_R](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FAPAR_WAfrica/resample_correlation_R_QGIS_Aggr.jpg=100x100) 


|   | FAPAR-Europe                      |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.97449     | 0.06302                | 0.04307             |
| 2 | Original 1Km Product - QGIS Tool  | 0.9723      | 0.0655                 | 0.04406             |
| 3 | R Notebook - QGIS Tool            | 0.99998     | 0.0017                 | 0.00096             |

![QGIS_Original](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FAPAR_Europe/resample_correlation_QGISAggr.jpg=100x100)  ![QGIS_R](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FAPAR_Europe/resample_correlation_R_QGIS_Aggr.jpg=100x100) 


|   | FAPAR-Amazonia                    |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.67006     | 0.09832                | 0.0527              |
| 2 | Original 1Km Product - QGIS Tool  | 0.68385     | 0.10462                | 0.0562              |
| 3 | R Notebook - QGIS Tool            | 0.99993     | 0.00111                | 0.00087             |

![QGIS_Original](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FAPAR_Amazonia/resample_correlation_QGISAggr.jpg=100x100)  ![QGIS_R](https://github.com/fgianoli/CopernicusGlobalLand/blob/master/img/scatterplots/FAPAR_Amazonia/resample_correlation_R_QGIS_Aggr.jpg=100x100) 


|   | DMP-W Africa                      |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.98686     | 5.32346                | 2.69047             |
| 2 | Original 1Km Product - QGIS Tool  | 0.98407     | 6.04546                | 3.1398              |
| 3 | R Notebook - QGIS Tool            | 1           | 0.02141                | 0.00264             |

|   | DMP-Europe                        |             |                        |                     |
|---|-----------------------------------|-------------|------------------------|---------------------|
|   |                                   | Pearson's r | Root Mean Square Error | Mean Absolute Error |
| 1 | Original 1Km Product - R Notebook | 0.9763      | 6.14813                | 4.11369             |
| 2 | Original 1Km Product - QGIS Tool  | 0.97586     | 6.19854                | 4.13796             |
| 3 | R Notebook - QGIS Tool            | 0.99999     | 0.0902                 | 0.00527             |





[Read more about the Resampling Tool](https://github.com/xavi-rp/ResampleTool_notebook/blob/master/Resample_Report_v2.5.pdf)

### Bibliography

Sherman Gary, 2018. *The PyQGIS Programmer’s Guide*. Locate Press  
QGIS Developers,PyQGIS Developer Cookbook, https://docs.qgis.org/3.10/en/docs/pyqgis_developer_cookbook/index.html  (14/07/2020)


## Acknowledgments & Authors
We thank for the help in developing and testing these tools:  
*Enrico Ferreguti, Xavier Rotllan Puig, Pier Lorenzo Marasco, Martino Boni*  
Author: Federico Gianoli
