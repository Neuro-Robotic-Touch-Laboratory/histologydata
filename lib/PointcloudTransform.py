import os
import json
import shutil
import numpy as np
import re
import open3d as o3d
import copy

import logging

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def Transformation(AcquisitionFolders,CalibrationFolder,LoadingCalibrationFiles=True,transformPointclouds=True,transformToOriginalPointcloudOrientation=False, verbose = False):
    """
    Perform calibration and transformation of point clouds in the specified acquisition folders.

    This function handles the following tasks:
    1. Load calibration files from a specified folder and copy them to acquisition subfolders if conditions are met.
    2. Transform point clouds using corresponding transformation matrices if available.
    3. Optionally revert the transformation to the original orientation.

    Args:
        - AcquisitionFolders (str): Path to the main folder containing point cloud acquisition data.
        - CalibrationFolder (str): Path to the folder containing calibration data and transformation matrices.
        - LoadingCalibrationFiles (bool, optional): If True, loads and copies calibration files to relevant subfolders. Defaults to True.
        - transformPointclouds (bool, optional): If True, applies transformations to point clouds based on calibration files. Defaults to True.
        - transformToOriginalPointcloudOrientation (bool, optional): If True, reverses the transformation matrices to restore point clouds to their original orientation. Defaults to False. 
        - verbose (bool, optional): If True, enables debug-level logging for detailed output. Defaults to False.

    Returns:
        - None

    Notes:
        - The function assumes that point cloud files have the `.ply` extension and calibration files are in JSON format.
        - Calibration files are expected to follow a specific structure, including `Camera distance` and `Number of images` fields.
        - ArUco based transformation matrices are applied on the acquired raw pointclouds. For new photogrammetry-based alignment methods, transform back the pointclouds to the original state by using the inverse of the transformation matrces.
        
    Author:
        - Name: Marton C. Mezei
        - Date: 21/11/2024
        - Contact: martoncsaba.mezei@santannapisa.it

    """

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


    if LoadingCalibrationFiles==True:
        
        for item in os.listdir(AcquisitionFolders):
            old_path = os.path.join(AcquisitionFolders, item)
            #If the config json file is already created we can load the transformation matrices
            if os.path.isdir(os.path.join(AcquisitionFolders, item)) and CalibrationFolder not in item:
                if os.path.exists(os.path.join(old_path, "CAMERA_config.json")):
                    with open(os.path.join(old_path, "CAMERA_config.json"), 'r') as f:
                        #Load camera configuration file
                        cameraConfiguration = json.load(f)
                        #If the configuration file is correctly populated with the camera distance and we used 100 images during the acquisitions
                        if cameraConfiguration['Camera distance']!='?' and cameraConfiguration['Number of images']==100: 
                            #We collect the cameraposes corresponding to the used camera distance
                            nameOfCurrentCalibration='CAMERA_poses_{}mm_100'.format(int(cameraConfiguration['Camera distance']))
    
                            folderOfCurrentCalibration=os.path.join(CalibrationFolder,nameOfCurrentCalibration)
                            if os.path.exists(os.path.join(old_path,'CAMERA_poses')):
                                #Copying all the transformation matrices
                                files = os.listdir(folderOfCurrentCalibration)
                                for filename in os.listdir(folderOfCurrentCalibration):
                                    full_file_name = os.path.join(folderOfCurrentCalibration, filename)
                                    if os.path.isfile(full_file_name):
                                        shutil.copy(full_file_name, os.path.join(old_path,'CAMERA_poses')) 

        logger.info('Calibration files loaded')

    if transformPointclouds==True:
        for dirpath, foldernames, filenames in os.walk(AcquisitionFolders, topdown=False):
            
            for pointcloud in filenames:
                old_path = os.path.join(dirpath, pointcloud)
                
                if '.ply' in pointcloud:
                    ID=int(re.findall('\d+', str(pointcloud))[0])
        
                    for dirpathcamposes, foldernamescamposes, cameraposes in os.walk(dirpath.replace('PointClouds','CAMERA_poses'), topdown=False):
                        
                        for camerapose in cameraposes:
                            cameraposeNumber=int(re.findall('\d+', str(camerapose))[0])
                            
                            if 'Transformation_matrix' in camerapose and cameraposeNumber==ID:
                                logger.debug(camerapose)
                                logger.debug(pointcloud)
                                
                                transformationMatrix=np.zeros((4,4))
                                
                                #Reading the transformation matrix
                                with open(os.path.join(dirpathcamposes, camerapose), 'r') as f:

                                    pose_data = json.load(f)

                                    pose = [np.array(pose) for pose in pose_data]

                                    logger.debug(len(pose_data))
                                    
                                    for pose in pose_data:
                                        logger.debug(len(pose))

                                    for i in range(len(pose_data)):
                                        for j in range(len(pose_data[i])):
                                            transformationMatrix[i,j] = pose_data[i][j]
                                    
                                    logger.debug(transformationMatrix)

                                    originalPC = o3d.io.read_point_cloud(os.path.join(dirpath, pointcloud))
                                    
                                    if transformToOriginalPointcloudOrientation==True:
                                        transformationMatrix=np.linalg.inv(transformationMatrix)
                                        
                                    
                                    transformedPC = copy.deepcopy(originalPC).transform(transformationMatrix)
                                    o3d.io.write_point_cloud(os.path.join(dirpath, pointcloud),transformedPC)         
                                    
                                    logger.debug('Creating the pointcloud with the transformed coordinate system for fileID %s', ID)     
                                    
    
                                                               