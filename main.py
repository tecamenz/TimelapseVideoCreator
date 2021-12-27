import click
from utils import log
from timelapse.processing import process_folders
from timelapse.video import video_from_images, video_from_paths, create_path_file
import os
from datetime import datetime
import time

log.setup_logging()
logger = log.get_logger(__name__)

def main(src, dst, window, step, filetype, average, imscale, vscale, novid, localize, fps, bitrate, ffmpeg_exe):
    
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
            video_from_images(src_path=src_path, dest_path=dest_path, vscale=vscale, fps=fps, bitrate=bitrate, ffmpeg_exe=ffmpeg_exe)
        elif (average == False):
            src_path = os.path.join(folder, '*.{}'.format(filetype))
            path_file = create_path_file(paths=paths, step=step)
            dest_path = os.path.join(folder, 'timelapse_{}.mp4'.format(datetime.now().strftime('%Y%m%d%H%M%S')))
            video_from_paths(path_file=path_file, dest_path=dest_path, vscale=vscale, fps=fps, bitrate=bitrate, ffmpeg_exe=ffmpeg_exe)
            try:
                os.remove(path=path_file)
            except Exception as e:
                logger.error("Can't remove path_file")
                logger.exception(e)

    end = time.time()
    delta = end-start
    click.echo('End: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    click.echo('Processing time: {:.0f}min {:.0f}s'.format(delta//60, delta%60))

@click.command()
@click.argument('src', default='/')
@click.argument('dst', default='out')
@click.option('--window', default=3, help='Defines the number of images to average. Default is 3.')
@click.option('--step', default=1, help='Defines the number of images to step forward. Default is 1.')
@click.option('--filetype', default='jpg', help='Defines the image filetype to search for. Default is jpg')
@click.option('--average', is_flag=True, default=False, help='Option to average [window] images into one. Default is False.')
@click.option('--imscale', default=-1, help='Defines the width of the output image after averaging. Height is calculated to preserve aspect ratio. Default is -1 which preserves native resolution.')
@click.option('--vscale', default=1920, help='Defines the width of the output video. Height is calculated to preserve aspect ratio. Default is 1920.')
@click.option('--novid', is_flag=True, default=False, help='If to omit video creation. Only used when --average == True.')
@click.option('--localize', default=None, help='String for timezone conversion.')
@click.option('--fps', default=30, help='Output framerate of the video. Default is 30.')
@click.option('--bitrate', default=100, help='Output bitrate (Mbit/s) of the video. Default is 100.')
@click.option('--ffmpeg-exe', default='/ffmpeg.exe', help='Path to ffmpeg.exe. Default is the current directory')
def main_command(src, dst, window, step, filetype, average, imscale, vscale, novid, localize, fps, bitrate, ffmpeg_exe):
    """Create timelapse from images located in SRC and saves the video to DST

    If SRC contains subfolders, the program recursively scans all subfolders and creates a video per subfolder. The folder structure is replicated at DSC and the output videos are saved respectivly. 
    
    If pre-processing via --average is set to True, the DST will contain intermediate (averaged) images along with a output video.
    
    If --novid is set to True along side with --average, only the intermediate (averaged) images are saved. Useful if you like to create the final video in a dedicated video editor.
    """
    main(src, dst, window, step, filetype, average, imscale, vscale, novid, localize, fps, bitrate, ffmpeg_exe)




if __name__ == '__main__':
    main_command()