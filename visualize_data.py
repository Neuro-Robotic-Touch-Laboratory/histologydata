from load_dataframe_demo import load_data
import lib.ScannerPlatform as scanP
import lib.UltrasoundPlatform as usP

import logging

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main(data_path, sample_id, platform_type, verbose):
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    data = load_data(data_path, sample_id, platform_type, verbose)
     
    
    for type in platform_type.split(','): 
        
        if 'scanner' in type: 
            
    ## --- Scanner --- ##

            scanP.plot_data_scan_aggregated(data['ScannerPlatform']['top'])

            scanP.plot_data_scan_aggregated(data['ScannerPlatform']['bottom'])

    ## --- Ultrasound --- ##
    
        if 'ultrasound' in type: 
    
            usP.plot_data_us_oneSignal(data['UltrasoundPlatform'])
            
            usP.plot_data_us_aggregated(data['UltrasoundPlatform'])
            
            usP.plot_data_us_aggregated(data['UltrasoundPlatform'], datatype='hf_norm')
            
    logger.debug("Execution completed")
    
if __name__ == '__main__':
    
    # Select the folder containing the data 
    DATA_PATH = './histologydata/example_data'

    # Select the id of the sample to visualize
    SAMPLE_ID = '290'
    
    main(DATA_PATH, SAMPLE_ID, 'ultrasound, scanner', verbose=True)