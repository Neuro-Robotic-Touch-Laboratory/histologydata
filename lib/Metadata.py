import os
import json

import logging

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def set_metadata(data_path, sample_id, metadata, verbose = False):
    """
    Function to set the metadata for a sample, organize file paths, and write metadata 
    to appropriate files. This function processes metadata for various parts of the sample 
    data including scanner information, hemisphere data (top/bottom), and type of data (color/depth). 
    
    Args:
        - data_path (str): The root directory path containing the sample data.
        - sample_id (str): The unique identifier of the sample.
        - metadata (dict): A dictionary containing the metadata to be added. It should contain keys like:
        'species', 'gender', 'age', 'material', 'material_add', 'diagn', 'history', 
        'date_scan', 'distance', 'resolution', 'exposure', 'date_us', 'n_points'.
        - verbose (bool, optional): Flag to control logging level (default is False).
    
    Returns:
        - None
        
    Author:
        - Name: Fabrizia Auletta
        - Date: 29/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    path = os.path.join(data_path, sample_id)
    scanner_path = get_child_folders_at_level(path, 1, verbose)[0]
    hemisphere_paths = get_child_folders_at_level(scanner_path, 1, verbose)
    for hemisphere in hemisphere_paths:
        if 'top' in hemisphere:
            top_path = hemisphere
        elif 'bottom' in hemisphere:
            bottom_path = hemisphere
    for type in get_child_folders_at_level(top_path,1, verbose):
        if 'color' in type:
            color_path_t = type
        elif 'depth' in type:
            depth_path_t = type
    for type in get_child_folders_at_level(bottom_path,1, verbose):
        if 'color' in type:
            color_path_b = type
        elif 'depth' in type:
            depth_path_b = type
    ultrasound_path = get_child_folders_at_level(path, 1, verbose)[1]
    
    list_of_paths = [data_path, scanner_path, top_path, color_path_t, depth_path_t, bottom_path, color_path_b, depth_path_b, ultrasound_path]
    
    list_of_filenames = ['sample', 'scanner', 'hemisphere', 'type', 'type','hemisphere', 'type', 'type','ultrasound']
    
    list_of_metadatas = [__metadata_structure_sample__(sample_id, metadata['species'], metadata['gender'], metadata['age'], metadata['material'], metadata['material_add'], metadata['diagn'], metadata['history']), 
                     __metadata_structure_scanner__(metadata['date_scan'], metadata['distance'],metadata['resolution'], metadata['exposure']), 
                     __metadata_structure_hemisphere__('top'), 
                     __metadata_structure_type__('color'),
                     __metadata_structure_type__('depth'),
                     __metadata_structure_hemisphere__('bottom'), 
                     __metadata_structure_type__('color'),
                     __metadata_structure_type__('depth'),
                     __metadata_structure_ultrasound__(metadata['date_us'], metadata['n_points'])
                     ]
    
    write_metadata(list_of_metadatas, list_of_paths, list_of_filenames, verbose)
    
    logger.info('created metadata')
    
def __metadata_structure_sample__(id = '', species= '', gender= '', age = 0, material= '', material_add= '', diagn= '', history= ''):
    struct = {"Tissue ID": id,
        "Species" : species,
        "Gender" : gender, 
        "Age" : age, 
        "Sample material": material, 
        "Sample material additional info" : material_add, 
        "Diagnosis" : diagn,
        "Medical history" : history, 
        "Fixation method" : '',
        "Diagnostic center" : 'University of Camerino',
        "List of scanner_ultrasound pairs " : {"point" : ''},
        "path_level" : 0,
        }
    return struct

def __metadata_structure_scanner__(date= '', distance = 0, resolution = '', exposure = 0):
    struct = {
        "Collector ID" : 'MCM',   
        "Date of acquisition": date,
        "Camera model": 'Intel RealSense D405',
        "Camera serial": 218622277156,
        "Camera distance": distance,
        "Camera resolution" : resolution,
        "Exposure time": exposure,
        "Background": 'white',
        "Illumination" : 'LED',
        "Intrinsic matrix": [
        [
            647.8780517578125,
            0.0,
            639.9894409179688
        ],
        [
            0.0,
            647.115478515625,
            363.3221740722656
        ],
        [
            0.0,
            0.0,
            1.0
        ]
    ],
        "Distortion matrix": [
        -0.0521327443420887,
        0.059997934848070145,
        -1.2732599316223059e-05,
        0.0001820140314521268,
        -0.01927928999066353
    ],
        "path_level": 1,
        }
    return struct

def __metadata_structure_hemisphere__(hemisphere):
    struct = {
        "Tissue hemisphere": hemisphere,
        "path_level": 2,
        }
    return struct

def __metadata_structure_type__(type):
    struct = {
        "Image type": type,
        "Segmentation method": 'remBG u2-general',
        "Number of images": 100,
        "path_level" : 3,
        }
    return struct

def __metadata_usparam__():
    struct = {
        "PulseVoltage" : 40,
        "Pulsewidth" : 14, 
        "PRF[kHz]" : 1,
    }
    return struct

def __data_labels_and_params__():
    struct = {
        "point" : {
        "Label" : '',
        "Height" : 0,
        "Gain" : 0,
        "Filter MHz" : 10,}
    }
    return struct

def __metadata_structure_ultrasound__(date = '', n_points = 0):
    struct = {
        "Collector ID" : 'IB',   
        "Date of acquisition": date,
        "Probe model": 'SPW16',
        "TX/RX device model": 'US-KEY Lecoeur Electronique',
        "TX/RX device params": __metadata_usparam__(),
        "Number of data points": n_points, 
        "Data labels": __data_labels_and_params__(),
        "path_level": 1,
        }
    return struct

def get_child_folders_at_level(path, target_level, verbose = False):
    """
    Retrieves a list of child folders at a specific depth level from the root directory.

    Args:
        - path : str
            The root directory from which to start the search.
        - target_level : int
            The depth level at which child folders should be collected. 
            Level 1 corresponds to folders directly under the root.
        - verbose : bool, optional
            If True, sets the logger to DEBUG level to provide detailed output (default is False).

    Returns:
        - list
            A list of full paths to the child folders found at the specified depth level.

     Author:
        - Name: Fabrizia Auletta
        - Date: 29/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    child_folders = []
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    def traverse_dir(current_path, current_level):
        """
        Recursively traverses directories to locate child folders at the target depth.

        Args:
            - current_path : str
                The directory currently being traversed.
            - current_level : int
                The current depth level relative to the root directory.

        Returns:
            - None
        """
        
        # Stop recursion if the target level is exceeded
        if current_level > target_level:
            return
        
        # If at the target level, collect child folders
        if current_level == target_level:
            try:
                child_folders.extend(
                    os.path.join(current_path, entry)
                    for entry in os.listdir(current_path)
                    if os.path.isdir(os.path.join(current_path, entry))
                )
                
            # Skip folders that cannot be accessed
            except PermissionError:
                pass  
            return
        # Continue traversing deeper levels
        try:
            for entry in os.listdir(current_path):
                entry_path = os.path.join(current_path, entry)
                if os.path.isdir(entry_path):
                    traverse_dir(entry_path, current_level + 1)
                    
        # Skip folders that cannot be accessed
        except PermissionError:
            pass
        
    # Start traversal from the root path
    traverse_dir(path, 1)
    logger.debug(child_folders)
    
    return child_folders

def write_metadata(metadatas: list, paths: list, filenames : list, verbose = False):
    
    """
    Writes metadata dictionaries to JSON files in specified paths with specified filenames.

    Args:
        - metadatas : list
            A list of metadata dictionaries, where each dictionary contains the metadata for a specific item.
        - paths : list
            A list of directory paths where the JSON files should be saved.
        - filenames : list
            A list of filenames (without extensions) to be used for the JSON files.
        - verbose : bool, optional
            If True, sets the logger to DEBUG level to provide detailed output (default is False).

    Returns:
        - bool
            Returns True after successfully writing all metadata files.

    Author:
        - Name: Fabrizia Auletta
        - Date: 29/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """

    
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    # Iterate through the provided metadata, paths, and filenames 
    for d, p, f in zip(metadatas, paths, filenames):
        logger.debug(os.path.join(p,f+'_metadata.json'))
        logger.debug(d.keys())
        
        # Write the metadata dictionary to a JSON file
        with open(os.path.join(p,f+'_metadata.json'),'w') as file:
            json.dump(d,file)
    return True

if __name__ == '__main__':
    
    # Select the folder containing the data 
    DATA_PATH = './histologydata/example_data'
     
    # Select the id of the sample to visualize
    SAMPLE_ID = '290'
    
    METADATA = {
    "species" : 'dog',
    "gender" : 'male',
    "age" : 12,
    "material" : '',
    "material_add" : '',
    "diagn" : '',
    "history" : '',
    "date_scan" : '20241003',
    "distance" : 90,
    "resolution" : '1280x720',
    "exposure" : 7000,
    "date_us" : '20240528',
    "n_points" : 11,
}
    
    set_metadata(DATA_PATH, SAMPLE_ID, METADATA, verbose=True)
    