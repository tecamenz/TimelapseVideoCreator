import click
from utils import log
from timelapse.processing import process_folders
from timelapse.video import video_from_images, vide_from_paths, create_path_file
import os
from datetime import datetime
import time

log.setup_logging()
logger = log.get_logger(__name__)

def main(src, dst, window, step, filetype, average, imscale, vscale, novid, localize, ffmpeg_exe):
    
    start = time.time()
    click.echo('Start: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    processed = process_folders(src=src, dst=dst, window=window, step=step, filetype=filetype, average=average, imscale=imscale, localize=localize)
    click.echo('Preprocessing done. Creating video...')
    for folder, paths in processed.items():
        if not os.path.exists(folder):
            click.echo('Creating output path: {}'.format(folder))
            os.makedirs(folder)
        
        if (average==True) and (novid==False):
            src_path = os.path.join(folder, 'Im_%d.{}'.format(filetype))
            dest_path = os.path.join(folder, 'timelapse_{}.mp4'.format(datetime.now().strftime('%Y%m%d%H%M%S')))
            video_from_images(src_path=src_path, dest_path=dest_path, vscale=vscale, ffmpeg_exe=ffmpeg_exe)
        elif (average == False):
            src_path = os.path.join(folder, '*.{}'.format(filetype))
            path_file = create_path_file(paths=paths, step=step)
            dest_path = os.path.join(folder, 'timelapse_{}.mp4'.format(datetime.now().strftime('%Y%m%d%H%M%S')))
            vide_from_paths(path_file=path_file, dest_path=dest_path, vscale=vscale, ffmpeg_exe=ffmpeg_exe)

    end = time.time()
    delta = end-start
    click.echo('End: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    click.echo('Processing time: {:.0f}min {:.0f}s'.format(delta//60, delta%60))

@click.command()
@click.argument('src', default='/')
@click.argument('dst', default='/')
@click.option('--window', default=3, help='Defines the number of images to average. Default=3')
@click.option('--step', default=1, help='Defines the number of images to step forward. Default=1')
@click.option('--filetype', default='jpg', help='Defines the image filetype to search for')
@click.option('--average', is_flag=True, default=False, help='Option to average [window] images into one')
@click.option('--imscale', default=-1, help='Defines the width of the output image after averaging. -1 preserves native resolution.')
@click.option('--vscale', default=1920, help='Defines the width of the output video')
@click.option('--novid', is_flag=True, default=False, help='If to omit video creation. Only checkt when --average == True')
@click.option('--localize', default=None, help='String for timezone conversion')
@click.option('--ffmpeg_exe', default='/', help='Path to ffmpeg.exe')
def main_command(src, dst, window, step, filetype, average, imscale, vscale, novid, localize, ffmpeg_exe):
    main(src, dst, window, step, filetype, average, imscale, vscale, novid, localize, ffmpeg_exe)




if __name__ == '__main__':
    main_command()