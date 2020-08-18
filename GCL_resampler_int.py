from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProject,QgsRasterLayer
import ast

import processing


class Copernicus(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('raster', 'Input Raster', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Final_resampled', 'Output', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterString('method', 'Resampling method', defaultValue='average', optional=True ))
        self.addParameter(QgsProcessingParameterString('reclassify', 'Reclassify valid data', defaultValue='[-0.08,0.92,1,0.92,255,0]', optional=True ))
        self.addParameter(QgsProcessingParameterString('offset', 'Add offset value', defaultValue= '-0.08', optional=True ))
        self.addParameter(QgsProcessingParameterString('scaling', 'Add scaling value', defaultValue= '250', optional=True))


    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
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
            'TABLE': ast.literal_eval(parameters['reclassify']),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RiclassificaConTabella'] = processing.run('native:reclassifybytable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        print("Checkpoint Charlie: Riclassify done")
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        riclassified= QgsRasterLayer(outputs['RiclassificaConTabella']['OUTPUT'])

        # translate Average
        tra_extra = "-of Gtiff -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 -ot Float32"
        tra_extra += " -projwin " + str(Xmin) + " " + str(Ymax) + " " + str(Xmax) + " " + str(Ymin)
        tra_extra += " -r " + str(parameters['method'])
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
            'INPUT': riclassified,
            'NODATA': None,
            'OPTIONS': '',
            'TARGET_CRS': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TranslateMode'] = processing.run('gdal:translate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        print("Checkpoint Charlie: translate mode done")
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}
        

        average = QgsRasterLayer(outputs['TranslateAverage']['OUTPUT'])
        mode = QgsRasterLayer(outputs['TranslateMode']['OUTPUT'])

        sample_layer = average
        offset = parameters['offset']
        scaling = parameters['scaling']
        print("Checkpoint Charlie: ", offset)

        # raster calculator to add customized offset P*
        alg_params = {
            'LAYERS': [average],
            'FORMULA': '"A@1" + 1 - %s' % offset,
            'SAMPLE': sample_layer,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        print("P* formula: ", alg_params)
        outputs['CopernicusRasterCalculator'] = processing.run('script:copernicusrastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        pvo = QgsRasterLayer(outputs['CopernicusRasterCalculator']['OUTPUT'])
        sample_layer = average

        # raster calculator Mode * PVo
        alg_params = {
            'LAYERS': [pvo, mode],
            'FORMULA': '"A@1" * "B@1"',
            'SAMPLE': sample_layer,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CopernicusRasterCalculatorA'] = processing.run('script:copernicusrastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        reginaPhalange = QgsRasterLayer(outputs['CopernicusRasterCalculatorA']['OUTPUT'])
        print("regina phalange ", reginaPhalange)



        # raster calculator to remove the offset and convert to INT values

        alg_params = {
            'LAYERS': [reginaPhalange],
            'FORMULA': '("A@1" <= 0) * 255 + ("A@1" > 0) * (("A@1"-(1- %s)-%s)*%s)' % (offset, offset, scaling),
            'SAMPLE': sample_layer,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CopernicusRasterCalculatorB'] = processing.run('script:copernicusrastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        #final_res = QgsRasterLayer(outputs['CopernicusRasterCalculatorB']['OUTPUT'])

        print('ci siamo quasi')

        #  # translate compress
        tra_compress = "-of Gtiff -ot UInt32 -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 "
                
        alg_params = {
            'COPY_SUBDATASETS': False,
            'DATA_TYPE': 4,
            'EXTRA': tra_compress,
            'INPUT': outputs['CopernicusRasterCalculatorB']['OUTPUT'],
            'NODATA': None,
            'OPTIONS': '',
            'TARGET_CRS': None,
            'OUTPUT': parameters['Final_resampled']
        }
        
        outputs['TranslateCompress'] = processing.run('gdal:translate', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Final_resampled'] = outputs['TranslateCompress']['OUTPUT']
        
        return results
        
        print("fata anca questa")

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
        return "The CGLS vegetation-related products (i.e. NDVI, LAI, FAPAR…), based on PROBA-V observations, have been distributed at 1km and 333m spatial resolution until June, 2020. However, as of July, 2020, all Near Real Time (NRT) production of the vegetation biophysical variables, based on Sentinel-3 observations, are no longer provided at 1km resolution. Nonetheless, users interested in continuing their 1km time series can use a resample of the new 333m products." \
               "This algorithm allows to resample the 333meters Copernicus Products to 1Km preserving the spatial extension of 1Km time series." \
               "It is possible to choose the resampling method to use. Possible values: nearest, bilinear,cubic,cubicspline,lanczos,average,mode. According to our tests, for NDVI, FAPAR, LAI, RMSE is better to use the Average.  " \


    def createInstance(self):
        return Copernicus()
