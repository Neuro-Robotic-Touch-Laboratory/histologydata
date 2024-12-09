# imports
import os 
import glob
import copy
import json
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib

from lib.UltrasoundPlatform import plot_data_us
from lib.ScannerPlatform  import show_data_scan

import logging

# Set up matplotlib
matplotlib.use('TkAgg')

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(data_path, sample_id, platform_type, verbose):
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    data = load_data(data_path, sample_id, platform_type, verbose)
                
    ## --- Scanner --- ##
    
    if verbose:
        logger.debug('Scanner data contain:')
        
        explore_data(data['ScannerPlatform'])
    
    first_check, second_check, n_scans = validate_scan_data_integrity(data['ScannerPlatform']['top'])
    
    if first_check: 
        logger.info('Scanner available data points : %s', n_scans)
    else: 
        logger.info('Attention! Number of data points do not match')
    
    if second_check: 
        logger.info('All scanner data points and camera poses are valid')
    else: 
        logger.info('Attention! Not all data points corresponds to a camera pose')
    
    show_data_scan(data['ScannerPlatform']['top']['color']['original'], data_path)

    ## --- Ultrasound --- ##
    
    if verbose:
        logger.debug('ultrasound data contain:')
    
        explore_data(data['UltrasoundPlatform'])
    
    first_check, second_check, n_labels = validate_us_data_integrity(data['UltrasoundPlatform'])
          
    if first_check: 
        logger.info('Ultrasound available data points : %s', n_labels)
    else: 
        logger.info('Attention! Number of data points and of labels do not match')
    
    if second_check: 
        logger.info('All ultrasound data points and labels are valid')
    else: 
        logger.info('Attention! Not all data points corresponds')
        
    plot_data_us(data['UltrasoundPlatform'])
    
    logger.debug("Execution completed")


def load_data(data_path, sample_id = '',  platform_type = '', verbose =  False):
    """
    Loads data from a specified directory based on the platform types provided. This function 
    supports loading data from ultrasound platforms (CSV data and image files) and scanner platforms 
    (image data of different types such as 'original' and 'segmented').

    Args:
        - data_path (str): The root directory where the platform data is stored.
        - sample_id (str, optional): A specific sample identifier to filter the folders by. Defaults to an empty - string, which means no filtering by sample ID.
        - platform_type (str, optional): A comma-separated list of platform types to load data for. 
                                       Possible values are 'UltrasoundPlatform' and 'ScannerPlatform'. Defaults to an empty string.
        - verbose (bool, optional): If True, enables debug-level logging. If False (default), sets logging to info level.

    Returns:
        - dict: A dictionary containing the loaded data for both Ultrasound and Scanner platforms. 
              - 'UltrasoundPlatform' will contain a 'data' key with a DataFrame of ultrasound signals and an 'images' key with a list of ultrasound images.
              - 'ScannerPlatform' will contain nested dictionaries based on 'top' and 'bottom' scans, with 'color' and 'depth' sides, each containing 'original' and 'segmented' image data.
              
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        
    # String ids of the platforms folders 
    US_ID = 'UltrasoundPlatform'
    SCAN_ID = 'ScannerPlatform'
    
    # Split the provided platform types
    types = platform_type.split(',')
    
    logger.debug('loading %s platforms', len(types))
    
    # List all folders in the given data path
    list_of_folders = [x[0] for x in os.walk(data_path)]
    
    logger.debug('exploring %s folders', len(list_of_folders))
    
    # Initialize dictionaries to hold data
    
    # ultrasound platform dictionary
    us_dict = {'data': pd.DataFrame(), 
               'metadata' : pd.DataFrame(),
                'images': []}
    
    # scanner platform dictionary
    type_dict = {'original': [], 'segmented': []}
    side_dict = {'color': copy.deepcopy(type_dict), 'depth': copy.deepcopy(type_dict), 'poses' : []}
    scan_dict = {'top': copy.deepcopy(side_dict), 'bottom': copy.deepcopy(side_dict)}

        
    data = {US_ID: dict(), 
            SCAN_ID: dict()}
    
    # Iterate through the specified platform types
    for type in types: 
        # logger.debug(type)
        
        # Load data for UltrasoundPlatform
        if type[-3:] in US_ID:
            logger.debug('loading %s platform', type)
            for folder in list_of_folders:
                if US_ID and sample_id in folder: 
                    if 'US_signals' in folder: 
                        logger.debug('loading signals')
                        us_signals = glob.glob(os.path.join(folder,'*.csv'))
                        N_us_signals = len(us_signals)
                        L_us_signals = len(pd.read_csv(us_signals[0]))
                        data_us = pd.DataFrame(index=np.arange(L_us_signals), columns=np.arange(1,N_us_signals+1))
                        col_names = {}
                        for file in us_signals:
                            for us_sig in range(1, N_us_signals + 1):
                                if '_' + str(us_sig) + '_Ascan' in file:
                                    data_us[us_sig] = pd.read_csv(file)
                                    col_names[us_sig] = file.split('_Ascan')[0].split('/')[-1]
                                    logger.debug(data_us[us_sig])
                        data_us.rename(columns=col_names, inplace=True)
                        us_dict['data'] = data_us.T
                    if 'IMG_pictures' in folder: 
                        logger.debug('loading images')
                        images = glob.glob(os.path.join(folder,'*.jpg'))
                        N_images = len(images)
                        imgs = []
                        for img in range(1,N_images+1):
                            for file in images: 
                                if '_'+str(img)+'.jpg' in file:
                                    imgs.append(Image.open(file)) 
                        us_dict['images'] = imgs
                    # if 'IMG' not in folder and 'US' not in folder: 
                    #     logger.debug('getting labels')
                    meta_files = glob.glob(os.path.join(folder,'*.json'))
                    for mf in meta_files:
                        if 'ultrasound' in mf:
                            with open(mf, 'r') as f:
                                meta_us = json.load(f)
                            logger.info(meta_us['Data Labels'])
                            meta_us_df = pd.DataFrame.from_dict(meta_us['Data Labels']).T
                            logger.info(meta_us_df.index)
                            for row in meta_us_df.index: 
                                meta_us_df.loc[row, 'file_id'] = row
                            us_dict['metadata'] = meta_us_df
                            logger.info(meta_us_df)
                    
            
            if len(data_us) > 0:
                logger.debug('ultrasound data loaded')
        
        # Load data for ScannerPlatform
        elif type[-3:] in SCAN_ID:
            logger.debug('loading %s platform', type)
            for folder in list_of_folders:
                if SCAN_ID and sample_id  in folder: 
                    for scan in ['top', 'bottom']:
                        if scan in folder:
                            for side in ['color', 'depth']:
                                if side in folder:
                                    for img_type in ['original', 'segmented']:
                                        if f'IMG_{side}_{img_type}' in folder:
                                            logger.debug('loading images :  %s, %s, %s', scan,side, img_type)
                                            scan_dict[scan][side][img_type] = get_scanner_images(folder)
                            if 'poses' in folder:
                                logger.debug('loading transformation matrices')
                                poses_files = sorted(glob.glob(os.path.join(folder,'*.json'))) 
                                poses_list = []
                                for i in range(1,len(poses_files)+1):
                                    for file in poses_files: 
                                        if f'_{i}.json' in file:
                                            with open(file, 'r') as f:
                                                pose_data = json.load(f)
                                            poses_list.append([np.array(pose) for pose in pose_data])
                                            scan_dict[scan]['poses'] = poses_list
            logger.debug('scanner data loaded')
 
    # Store the loaded ultrasound and scanner data in the final dictionary
    data[US_ID] = us_dict
    data[SCAN_ID] = scan_dict
    
    logger.info('Data loaded')
    
    return data 

def get_scanner_images(folder):
    """
    Retrieves images from a specified folder where each image
    corresponds to a unique index and ends with '_<index>.png'. The function looks for all
    PNG images in the folder and appends those matching the given naming pattern to a list.
    
    Args:
        - folder (str): The path to the folder containing the PNG images. 
    
    Returns:
        - list: A list of PIL Image objects. Each item in the list is an image that matches
              the naming convention from the folder.
              
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    
    # Get all PNG images in the specified folder
    images = glob.glob(os.path.join(folder, '*.png'))
    
    # Get the number of images found
    N_images = len(images)
    
    # List to store the loaded images
    images_list = []
    
    # Iterate over the range of expected image indices (from 1 to N_images)
    for img_idx in range(1, N_images + 1):
        # Iterate over all found images
        for file in images:
            # If the image file matches the expected index pattern
            if f'_{img_idx}.png' in file:
                # Open and append the image to the list
                images_list.append(Image.open(file))

    
    # Return the list of images
    return images_list

def validate_us_data_integrity(data):
    """
    Validates the integrity of the ultrasound platform data by checking:
    1. If the number of data points (signals), metadata, and images match.
    2. If the unique `file_id` values in the metadata match the corresponding data points and image files.

    Args:
        - data (dict): 
            A dictionary containing keys:
            - 'UltrasoundPlatform':
            - 'data': A DataFrame where each row represents signal data (indexed by `file_id`).
            - 'metadata': A DataFrame with metadata, including `file_id` and labels.
            - 'images': A list of image objects, each having a filename property that should match `file_id`.

    Returns:
        - first_check (bool): True if the number of data points (signals), metadata, and images match.
        - second_check (bool): True if the file_id values in metadata match the corresponding data and image files.
        - n_labels (int): The number of unique `file_id` values in the metadata (if the first check is True).

    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    
    # Check if the number of data points (signals), metadata, and images are the same
    if (len(data['data']) == len(data['metadata']) == len(data['images'])):
        first_check = True
        n_labels = len(data['metadata']['file_id'].unique())
    else:
        first_check = False
        n_labels = 0  # No valid labels if the first check fails

    # Second check: If file_id values in metadata match data and image filenames
    if first_check:
        if (data['metadata']['file_id'].unique() == data['data'].index.values).all():
            checklist = []
            for el, file_id in zip(data['images'], data['metadata']['file_id']):
                checklist.append(file_id in el.filename)
            second_check = sum(checklist) == n_labels
        else:
            second_check = False
    else:
        second_check = False

    return first_check, second_check, n_labels

def validate_scan_data_integrity(data):
    """
    Validates the integrity of scan data by checking for consistency in the lengths of key data components.

    Args:
        data (dict): A dictionary containing scan data with the following structure:
            {
                "color": {
                    "original": list_of_original_color_scans,
                    "segmented": list_of_segmented_color_scans
                },
                "depth": {
                    "original": list_of_original_depth_scans,
                    "segmented": list_of_segmented_depth_scans
                },
                "poses": list_of_poses
            }

    Returns:
        - first_check (bool): True if the lengths of all color and depth datasets match; otherwise False.
        - second_check (bool): True if the length of the 'original' color scans matches the number of poses; otherwise False.
        - n_scans (int): Number of valid scans if the first check passes; otherwise 0.
        
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    # Check if the lengths of all color and depth lists are equal
    if (len(data['color']['segmented']) == 
        len(data['color']['original']) == 
        len(data['depth']['segmented']) == 
        len(data['depth']['original'])):
        first_check = True  # All lists have matching lengths
        n_scans = len(data['color']['original'])  # Number of scans based on matching data lengths
    else:
        first_check = False  # Lengths are inconsistent
        n_scans = 0  # Set to 0 since the data is invalid

    # Second check: validate against the number of poses
    if first_check:
        if len(data['color']['original']) == len(data['poses']):
            second_check = True  # Matching number of scans and poses
        else:
            second_check = False  # Mismatch between scans and poses
    else:
        second_check = False  # Skip this check if the first check fails

    # Return the results of the checks and the number of valid scans
    return first_check, second_check, n_scans


def explore_data(d):
    """
    Recursively explores and prints the structure of a nested dictionary.

    Args:
        - d (dict): The dictionary to explore. It can have nested dictionaries as values.

    Returns:
        - None: The function prints the structure to the console and does not return any value.

    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    for el1 in d:
        print(el1)  # Print the top-level key
        if isinstance(d[el1], dict):  # Check if the value is a dictionary
            for el2 in d[el1]:
                print('>', el2)  # Print the second-level key, indented
                if isinstance(d[el1][el2], dict):  # Check if the value is a dictionary
                    for el3 in d[el1][el2]:
                        print('>>', el3)  # Print the third-level key, further indented


if __name__ == '__main__':
    
    # Select the folder containing the data 
    DATA_PATH = './histologydata/example_data'
     
    # Select the id of the sample to visualize
    SAMPLE_ID = '290'
    
    main(DATA_PATH, SAMPLE_ID, 'ultrasound,scanner', verbose=False)
    