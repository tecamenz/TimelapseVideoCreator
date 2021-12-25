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

def get_image(path):
    im = Image.open(path).convert('RGB')
    im = np.array(im).astype(np.float32)
    return {'path': path, 'im': im}

def get_date(path, localize='Europe/Zurich'):
    im = Image.open(path)
    date_str = im.getexif()[306]
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
        return {'datetime': 0, 'path': 'ERROR'}
    del im
    return {'datetime': date, 'path': path}

def process_folders(src, dst, window, step, filetype, average):
    
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
        path_dict_list = list(pool.map(get_date, paths))
        click.echo('Sorting files...')
        path_dict_list = sorted(path_dict_list, key = lambda i: i['datetime'])
        image_paths = [x['path'] for x in path_dict_list]
        if average:
            save_paths = process_Images(image_paths=image_paths, window=window, step=step, dst=dest_path)
            processed[dest_path] = save_paths
        else:
            processed[dest_path] = image_paths
    
    return processed
        

def average_Images(batch):
    images = []
    paths = []
    for path in batch['paths']:
        images.append(get_image(path)['im'])
    images = np.array(images)
    new_image_path = batch['new_path']
    try:
        new_image = np.mean(images, axis=0)
        new_image=np.array(np.round(new_image),dtype=np.uint8)
        out = Image.fromarray(new_image, mode="RGB")
        out.save(new_image_path)
        del out
        paths.append(new_image_path)
    except Exception as e:
        logger.error('Failed to average images')
        logger.exception(e)
    finally:
        del images
    
    return paths
    

def process_Images(image_paths, window, step, dst):
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
        batches.append({'paths': tmp, 'new_path': new_path.format(image_idx)})
        image_idx = image_idx + 1
    
    save_paths = list(tqdm(pool.map(average_Images, batches), total=len(batches)))
    return save_paths