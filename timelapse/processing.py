from glob import glob
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time
import os
from PIL import Image
import numpy as np
from datetime import datetime
import pytz
from utils import log
import click
import numpy as np

logger = log.get_logger(__name__)

def get_batch_recursive(src, filetype):
    tmp = sorted(glob(src + '/*'))
    if len(tmp) > 0:
        # check for subfolder
        if os.path.isdir(tmp[0]):
            # assume we only have subfolders
            for subdir in tmp:
                gen = get_batch_recursive(subdir, filetype=filetype)
                for paths in gen:
                    yield paths
        elif tmp[0].split('.')[-1] == filetype:
            yield tmp

def get_image(path, target_width, target_heigth):
    im = Image.open(path).convert('RGB')
    width, height = im.size
    if (width == target_width) and (height == target_heigth):
        im = np.array(im).astype(np.float32)
    else:
        logger.info('Resizing {}'. format(path))
        im = im.resize((target_width, target_heigth), Image.LANCZOS)
        im = np.array(im).astype(np.float32)
    return {'path': path, 'im': im}

def get_image_info(params):
    """Get information such as creation date and size from the images

    Args:
        params (dict): Key "path" provides path to image
                       Key "localize" provides string of timezone convertsion
        localize (str, optional): Identifier for the timezone. Defaults to 'Europe/Zurich'.

    Returns:
        [type]: [description]
    """    
    path = params['path']
    localize = params['localize']
    im = Image.open(path)
    date_str = im.getexif()[306]
    width, height = im.size
    im.close()
    try:
        date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        logger.error('Could not parse datestring')
        logger.exception(e)
    
    if localize is not None:
        try:
            local = pytz.timezone(localize)
            local_dt = local.localize(date_obj, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            date = utc_dt.timestamp()
        except Exception as e:
            logger.error('Could not localize datetime object')
            logger.exception(e)
    else:
        try:
            date = date_obj.timestamp()
        except Exception as e:
            logger.error('Could not convert tu POSIX timestamp')
            logger.exception(e)

    if date is None:
        return {'datetime': 0, 'width': width, 'height':height, 'path': 'ERROR'}
    del im
    return {'datetime': date, 'width': width, 'height':height, 'path': path}

def process_folders(src, dst, window, step, filetype, average, imscale, localize):
    """Processing the source path (src) to find and sort images. Additional pre-processing is applied via simple sliding window approach. 


    Args:
        src (str): Path to the source location where the images or subfolders are located
        dst (str): Path to the destination folder, where the final video and optional the processed images are stored
        window (int): Number of images to average. The new image will be the mean of consecutive images and saved in the destination folder
        step (int): Number of images to step forwared each time. This is used regardless of the average flag.
        filetype (str): Defines the filetype to search for
        average (bool): Flat indicating if to apply pre-processing to the images
        imscale (int): Defines the width of the output image after averaging. -1 preserves native resolution.
        localize (str): Defines string for timezone conversion 

    Returns:
        list: List containing a dictionary for each folder where the key is the respective folder path and values are the paths to the images
    """
    
    pool = ThreadPoolExecutor(max_workers=100)
    folders = get_batch_recursive(src=src, filetype=filetype) # iterator yielding image paths per day-folder
    processed = {}
    click.echo("")
    click.echo('Searching subfolders...')
    for paths in folders:
        foldername = os.path.dirname(paths[0])
        foldername = os.path.basename(foldername)
        click.echo('Processing subfolder "{}" ({} images)'.format(foldername, len(paths)))
        dest_path = os.path.join(dst, foldername)
        params = [{'path': path, 'localize': localize} for path in paths]
        image_info = list(pool.map(get_image_info, params))
        click.echo('Checking size')
        # calculate the median of width / height to get the most common values
        width = np.median([x['width'] for x in image_info])
        height = np.median([x['height'] for x in image_info])
        # if caling was provided, calculate new target size 
        if imscale > 0:
            target_width = imscale
            scaling = target_width/float(width)
            target_height = int(height * scaling)
        else:
            target_width = int(width)
            target_height = int(height)
            

        click.echo('Sorting files...')
        image_info = sorted(image_info, key = lambda i: i['datetime'])
        image_paths = [x['path'] for x in image_info]
        if average:
            save_paths = process_Images(image_paths=image_paths, window=window, step=step, target_width=target_width, target_height=target_height, dst=dest_path)
            processed[dest_path] = save_paths
        else:
            processed[dest_path] = image_paths
    
    return processed
        

def average_Images(batch):
    """Function to load and average images 

    Args:
        batch (dict): Key "paths" provides a set of image paths to average. 
                      Key "new_path" provides the location the resulting image is saved
                      Key "target_width" Defines the width of the output image after averaging.
                      Key "target_height" Defines the height of the output image after averaging.

    Returns:
        str: Paths where images successfully were saved
    """    
    paths = batch['paths']
    new_path = batch['new_path']
    target_width = batch['target_width']
    target_height = batch['target_height']

    images = []
    processed_path = None
    for path in paths:
        images.append(get_image(path, target_width, target_height)['im'])
    images = np.array(images)
    new_image_path = new_path
    try:
        new_image = np.mean(images, axis=0)
        new_image=np.array(np.round(new_image),dtype=np.uint8)
        out = Image.fromarray(new_image, mode="RGB")
        out.save(new_image_path)
        del out
        processed_path = new_image_path
    except Exception as e:
        logger.error('Failed to average images {} {}'.format(new_image_path, batch['paths']))
        logger.exception(e)
    finally:
        del images
    
    return processed_path
    

def process_Images(image_paths, window, step, target_width, target_height, dst):
    """Function to execute the averaging process via a pool of threads

    Args:
        image_paths (list): Paths to the images
        window (int): Number of images to average. The new image will be the mean of consecutive images and saved in the destination folder
        step (int): Number of images to step forwared each time. This is used regardless of the average flag.
        target_width (int): Defines the width of the output image after averaging.
        target_height (int): Defines the height of the output image after averaging.
        dst (str): Path to the destination folder, where the final video and optional the processed images are stored

    Returns:
        [type]: [description]
    """    
    junksize = int(100/window)
    pool = ThreadPoolExecutor(max_workers=junksize)

    if dst is None:
        dst = '.tmp_img/'
    
    if not os.path.exists(dst):
        click.echo('Creating output path: {}'.format(dst))
        os.makedirs(dst)

    click.echo('Generating average of {} images with step size {} (overlap={})'.format(window, step, window-step))
    image_idx = 0
    tmp = image_paths[0]

    new_filename = 'Im_{}.JPG'
    new_path = os.path.join(dst, new_filename)

    # prepare for processing
    batches = []
    for i in range(0, len(image_paths), step):
        tmp = image_paths[i: i+window]
        batches.append({'paths': tmp, 'new_path': new_path.format(image_idx), 'target_width': target_width, 'target_height': target_height})
        image_idx = image_idx + 1
    
    save_paths = list(tqdm(pool.map(average_Images, batches), total=len(batches)))
    return save_paths