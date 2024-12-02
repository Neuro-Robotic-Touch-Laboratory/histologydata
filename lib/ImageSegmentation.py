import os
from rembg import remove, new_session
import cv2
import numpy as np
import re

import logging

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#Using the rembg AI tool to remove the background of the images
def RemoveBackGround(AcquisitionFolders, erodeSize=10, FGThreshold=230, BGThreshold=40, SegmentationModel='u2net', backgroundColor = np.array([255, 255, 255]), verbose = False):
    """
    Removes the background of images in a given folder using the rembg AI tool and applies segmentation 
    to both color and corresponding depth images. The segmented images are automatically saved in a new folder identified by the paramenter 's'

    Args:
        - AcquisitionFolders (str): The path to the root folder containing subfolders with image datasets.
        - erodeSize (int, optional): The size of erosion for the alpha matting operation. Default is 10.
        - FGThreshold (int, optional): Foreground threshold for alpha matting. Default is 230.
        - BGThreshold (int, optional): Background threshold for alpha matting. Default is 40.
        - SegmentationModel (str, optional): The name of the segmentation model to use (e.g., 'u2net'). Default is 'u2net': the segmentation model proposed by remBG https://github.com/danielgatis/rembg
        - backgroundColor (np.array, optional): RGB values for the background color to use in the segmented images. 
                                              Default is white ([255, 255, 255]).

    Returns:
        - None: Outputs are saved directly to files in the relevant directories.

    Author:
        - Name: Marton C. Mezei
        - Date: 21/11/2024
        - Contact: martoncsaba.mezei@santannapisa.it
    """

    s = 'segmented'

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.info('Started background segmentation')

    logger.debug(AcquisitionFolders)

    for directorypath, namesOfFolders, nameOfFiles in os.walk(AcquisitionFolders):
        for acquisitionFolder in namesOfFolders:
            if '_bottom' in acquisitionFolder or '_top' in acquisitionFolder:
                pathOfDataset = os.path.join(directorypath, acquisitionFolder)
                pathOfImages=os.path.join(pathOfDataset, "IMG_color/IMG_color_original")
                
                logger.debug(pathOfImages)

                if os.path.exists(pathOfImages):
                    for dirpath, foldernames, filenames in os.walk(pathOfImages):

                        for image in filenames[:2]:
                            logger.debug(image)

                            if '.png' in image and 'IMG_color_original' in image:

                                logger.debug('Processing %s', image)
 
                                input_path = os.path.join(pathOfImages,image)
                                output_path = input_path.replace('original',s)

                                t = output_path.split(s)[0] + s

                                if not os.path.exists(t):
                                    os.makedirs(t)
                                    logger.debug('Created folder '+ t)

                                #Choosing the segmentation model, "isnet-general" can also be used succesfully
                                model_name = SegmentationModel
                                session = new_session(model_name)
                                #Finding the image ID number in the string corresponding to the name of the png image. [0] -> means that we expect to only find 1 number
                                imageID=int(re.findall('\d+', str(image))[0])
                                with open(input_path, 'rb') as i:
                                    with open(output_path, 'wb') as o:

                                        logger.debug('Removing background in color image..')

                                        input = i.read()

                                        output = remove(input, alpha_matting=True, alpha_matting_foreground_threshold=FGThreshold,alpha_matting_background_threshold=BGThreshold, alpha_matting_erode_size=erodeSize, session=session, post_process_mask=True)#, bgcolor=[255,255,255,255]
                                        #Saving segmented image to the output_path
                                        o.write(output)
                                        #Reading the segmented image which currently has an alpha channel and no background color
                                        segmentedImage=cv2.imread(output_path,flags=cv2.IMREAD_UNCHANGED)

                                        logger.debug(segmentedImage.shape)

                                        #Get alpha channel to mask depth images
                                        alphaMask=segmentedImage[:,:,3]
                                        #Background color of segmented color image
                                        bg = backgroundColor
                                        alpha = (segmentedImage[:, :, 3] / 255).reshape(segmentedImage.shape[:2] + (1,))
                                        image = ((bg * (1 - alpha)) + (segmentedImage[:, :, :3] * alpha)).astype(np.uint8)
                                        #Saving color image with white background 
                                        cv2.imwrite(output_path,image)

                                        #Getting the corresponding depth image
                                        pathOfDepth=os.path.join(pathOfDataset,'IMG_depth/IMG_depth_original')
                                        pathOfDepth_output = os.path.join(pathOfDataset,'IMG_depth/IMG_depth_'+s)

                                        if not os.path.exists(pathOfDepth_output):
                                            os.makedirs(pathOfDepth_output)
                                            logger.debug('Created folder '+ t)

                                        if os.path.exists(pathOfDepth):
                                            logger.debug('Removing background depth image..')
                                            for dirpathdepth, foldernamesdepth, filenamesdepth in os.walk(pathOfDepth):
                                                for depthimage in filenamesdepth:
                                                    depthImageID=int(re.findall('\d+', str(depthimage))[0])
                                                    
                                                    if '.png' in depthimage and 'IMG_depth_original' in depthimage and depthImageID==imageID:
                                                        logger.debug('Processing %s' , depthimage)
                                                        
                                                        rawDepthImage=cv2.imread(os.path.join(pathOfDepth,depthimage),flags=cv2.IMREAD_UNCHANGED)
                                                        
                                                        alphaMask = (2*(alphaMask.astype(np.float32))-255.0).clip(0,255).astype(np.uint8)

                                                        if alphaMask.shape != rawDepthImage.shape[:2]:
                                                            alphaMask = cv2.resize(alphaMask, (rawDepthImage.shape[1], rawDepthImage.shape[0]))
                               
                                                        result_image = cv2.bitwise_and(rawDepthImage, rawDepthImage, mask=alphaMask)
                                                        
                                                        #Save the segmented depth images
                                                        cv2.imwrite(os.path.join(pathOfDepth_output, depthimage.replace('original',s)), result_image)

                                                               