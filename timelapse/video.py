import ffmpeg
from glob import glob

def create_path_file(paths, step=1):
    path_file = 'path_file.txt'
    paths = paths[0::step]
    with open(path_file, 'w') as f:
        for path in paths:
            path = path.replace('\\', '/')
            f.write('file ' + path + '\n')
    return path_file

def video_from_images(src_path, dest_path, vscale, ffmpeg_exe):
    input_args = {
    "f": "image2",
    "r": "30"
    }

    output_args = {
    # "vf": "scale=2160:-1,hflip,vflip",
    "vf": "scale={}:-1".format(vscale),
    "c:v": "h264_nvenc",
    "rc:v": "vbr",
    "cq:v": "1",
    "b:v": "20M",
    "maxrate:v": "100M",
    "profile:v": "high",
    "pix_fmt": "yuv420p",
    # "framerate": "30"
    }


    (
    ffmpeg
    .input(src_path, **input_args)
    # .filter('deflicker', mode='pm', size=10)
    .output(dest_path, **output_args)
    .run(cmd=ffmpeg_exe)
    )

def video_from_paths(path_file, dest_path, vscale, ffmpeg_exe):
    input_args = {
    "safe": "0",
    "f": 'concat',
    "r": "30"
    }
    
    output_args = {
    # "vf": "scale=2160:-1,hflip,vflip",
    "vf": "scale={}:-1".format(vscale),
    "c:v": "h264_nvenc",
    "rc:v": "vbr",
    "cq:v": "1",
    "b:v": "20M",
    "maxrate:v": "100M",
    "profile:v": "high",
    "pix_fmt": "yuv420p",
    # "framerate": "30"
    }

    (
    ffmpeg
    .input(path_file, **input_args)
    .output(dest_path, **output_args)
    .run(cmd=ffmpeg_exe)
    )