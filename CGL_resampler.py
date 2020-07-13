from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterFileDestination,QgsProcessingParameterExtent
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsProject,QgsRasterLayer

import processing


class Copernicus(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('raster', 'raster', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Final_resampled', 'final_resampled', createByDefault=True, defaultValue=None))
        #self.addParameter(QgsProcessingParameterExtent('EXTENT', 'EXTENT', defaultValue=None, optional=True))
        #self.addParameter(QgsProcessingParameterRasterLayer('SAMPLE', 'SAMPLE', defaultValue=None, optional=True))
        self.addParameter(QgsProcessingParameterString('method', 'Resampling method', defaultValue='average', optional=True ))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        input_raster = self.parameterAsRasterLayer(parameters, 'raster', context)

        Xmin = -180 + ((1 / 112) / 2)
        Xmax = 180 - ((1 / 112) / 2)
        Ymax = 80 - ((1 / 112) / 2)
        Ymin = -60 + ((1 / 112) / 2)

        pixelX = 1. / 112.
        pixelY = 1. / 112.

        stats = input_raster.dataProvider().bandStatistics(1)

        src_min = stats.minimumValue
        src_max = stats.maximumValue
        dst_min = stats.minimumValue
        dst_max = stats.maximumValue

        print(src_min, src_max, dst_min, dst_max)

        print("Checkpoint Charlie: ", Xmin, Xmax, Ymax, Ymin, pixelX)

        # Riclassifica con tabella
        alg_params = {
            'DATA_TYPE': 5,
            'INPUT_RASTER': parameters['raster'],
            'NODATA_FOR_MISSING': False,
            'NO_DATA': -9999,
            'RANGE_BOUNDARIES': 0,
            'RASTER_BAND': 1,
            'TABLE': [-1,1,1,1,255,0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RiclassificaConTabella'] = processing.run('native:reclassifybytable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        print("Checkpoint Charlie: Riclassify done")
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # translate Average
        tra_extra = "-of Gtiff -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 "
        tra_extra += " -projwin " + str(Xmin) + " " + str(Ymax) + " " + str(Xmax) + " " + str(Ymin)
        tra_extra += " -r " + str(parameters['method'])
        #tra_extra += " -r average"
        tra_extra += " -tr " + str(pixelX) + " " + str(pixelY)
        tra_extra += " -scale " + str(src_min) + " " + str(src_max) + " " + str(dst_min) + " " + str(dst_max)

        alg_params = {
            'COPY_SUBDATASETS': False,
            'DATA_TYPE': 0,
            'EXTRA': tra_extra,
            'INPUT': parameters['raster'],
            'NODATA': None,
            'OPTIONS': '',
            'TARGET_CRS': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TranslateAverage'] = processing.run('gdal:translate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        print("Checkpoint Charlie: translate average done")
        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # translate MODE
        tra_extra_mode = "-of Gtiff -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 "
        tra_extra_mode += " -projwin " + str(Xmin) + " " + str(Ymax) + " " + str(Xmax) + " " + str(Ymin)
        tra_extra_mode += " -r mode -tr " + str(pixelX) + " " + str(pixelY)

        alg_params = {
            'COPY_SUBDATASETS': False,
            'DATA_TYPE': 0,
            'EXTRA': tra_extra_mode,
            'INPUT': outputs['RiclassificaConTabella']['OUTPUT'],
            'NODATA': None,
            'OPTIONS': '',
            'TARGET_CRS': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TranslateMode'] = processing.run('gdal:translate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        print("Checkpoint Charlie: translate mode done")
        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}
        
        print(outputs['TranslateAverage']['OUTPUT'])

        average = QgsRasterLayer(outputs['TranslateAverage']['OUTPUT'])
        mode = QgsRasterLayer(outputs['TranslateMode']['OUTPUT'])

        # if 'SAMPLE' in parameters:
        #     sample_layer = self.parameterAsRasterLayer(parameters,"SAMPLE",context)
        # else:
        #     if 'EXTENT' in parameters:
        #         alg_params = {
        #             'DATA_TYPE': 5,
        #             'INPUT': average,
        #             'NODATA': -9999,
        #             'PROJWIN': parameters['EXTENT'],
        #             'OPTIONS': '',
        #             'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        #         }
        #         output_clip = processing.run('gdal:cliprasterbyextent', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        #         sample_layer = QgsRasterLayer(output_clip['OUTPUT'],'SAMPLE','gdal')
        #     else:
        #         sample_layer = average
                
        sample_layer = average

        print('sample layer', sample_layer)


        # raster calculator
        alg_params = {
            'LAYERS': [average, mode],
            'FORMULA': '"A@1" * "B@1"',
            'SAMPLE': sample_layer,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CopernicusRasterCalculator'] = processing.run('script:copernicusrastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}
        
         # translate compress
        tra_extra_compress = "-of Gtiff -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 "
        tra_extra_compress += " -projwin " + str(Xmin) + " " + str(Ymax) + " " + str(Xmax) + " " + str(Ymin)
        tra_extra_compress += " -tr " + str(pixelX) + " " + str(pixelY)

        alg_params = {
            'COPY_SUBDATASETS': False,
            'DATA_TYPE': 0,
            'EXTRA': tra_extra_compress,
            'INPUT': outputs['CopernicusRasterCalculator']['OUTPUT'],
            'NODATA': None,
            'OPTIONS': '',
            'TARGET_CRS': None,
            'OUTPUT': parameters['Final_resampled']
        }
        outputs['TranslateCompress'] = processing.run('gdal:translate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Final_resampled'] = outputs['TranslateCompress']['OUTPUT']
        return results
      

    def name(self):
        return 'Copernicus'

    def displayName(self):
        return 'Copernicus GL Resampler'

    def group(self):
        return 'Copernicus Global Land Tools'

    def groupId(self):
        return 'Copernicus Global Land Tools'
    
    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return "This algorithm allows to download Copernicus Global Land products and converts the native Netcdf files into geotiff." \
               "Select the product collection to downlad and the day. The algorithm will download the product with the closest date. " \
               "Download directory is the directory in wich the product will be downloaded and converted to geotiff. " \
               "Download file: it is an addionatal parameter, leave empty"

    def createInstance(self):
        return Copernicus()
