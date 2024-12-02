from lib.ImageSegmentation import RemoveBackGround
from lib.PointcloudTransform import Transformation
import os

import logging

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

def main(data_path, sample_id, processing_type = '', verbose = False):
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    AcquisitionFolders = os.path.join(data_path,sample_id)

    types = processing_type.split(',')

    for type in types: 
        
        if 'remove' in type:

            RemoveBackGround(AcquisitionFolders, verbose = verbose)
        
        if 'transform' in type: 
            
            CalibrationFolder = os.path.join(os.path.dirname(AcquisitionFolders),'CalibrationFiles')
            
            Transformation(AcquisitionFolders, CalibrationFolder, verbose = verbose) 

    logger.debug("Execution completed")

if __name__ =='__main__':
    
    # Select the folder containing the data 
    DATA_PATH = './example_data'

    # Select the id of the sample to visualize
    SAMPLE_ID = '290'
    
    main(DATA_PATH, SAMPLE_ID, 'remove, transform', verbose = True)