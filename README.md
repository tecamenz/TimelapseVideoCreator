# TimelapseVideoCreator
<img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/tecamenz/TimelapseVideoCreator/python-app.yml?label=CI">
Simple command line tool to create timelapse videos from individual images. 


## Features:
- Recursive image search in subfolders for batch processing (creates one video per subfolder)
- Input images are sorted via EXIF timestamp to ensure correct ordering regardless of name
- Multithreaded pre-processing pipeline to reduce flicker via rolling average filter
- Using optimized parameters for [ffmpeg](https://ffmpeg.org/) to create good locking videos


## Usage
```text
Usage: main.py [OPTIONS] [SRC] [DST]

  Create timelapse from images located in SRC and saves the video to DST

  If SRC contains subfolders, the program recursively scans all subfolders and
  creates a video per subfolder. The folder structure is replicated at DSC and
  the output videos are saved respectivly.

  If pre-processing via --average is set to True, the DST will contain
  intermediate (averaged) images along with a output video.

  If --novid is set to True along side with --average, only the intermediate
  (averaged) images are saved. Useful if you like to create the final video in
  a dedicated video editor.

Options:
  --window INTEGER   Defines the number of images to average. Default is 3.
  --step INTEGER     Defines the number of images to step forward. Default is
                     1.
  --filetype TEXT    Defines the image filetype to search for. Default is jpg
  --average          Option to average [window] images into one. Default is
                     False.
  --imscale INTEGER  Defines the width of the output image after averaging.
                     Height is calculated to preserve aspect ratio. Default is
                     -1 which preserves native resolution.
  --vscale INTEGER   Defines the width of the output video. Height is
                     calculated to preserve aspect ratio. Default is 1920.
  --novid            If to omit video creation. Only used when --average ==
                     True.
  --localize TEXT    String for timezone conversion.
  --fps INTEGER      Output framerate of the video. Default is 30.
  --bitrate INTEGER  Output bitrate (Mbit/s) of the video. Default is 100.
  --ffmpeg-exe TEXT  Path to ffmpeg.exe. Default is the current directory
  --help             Show this message and exit.

```

### Example

Create a 4k-Video with pre-processing using a window of 4 images and a step size of 2 (2 images overlap). 
```cmd
python main.py \path\to\images out --average True --window 4 --step 2 --vscale 4096 --ffmpeg_exe \ffmpeg-4.4.1-full_build\bin\ffmpeg.exe
```

## Setup Conda Environment
```cmd 
conda create -n timelapse python=3.9
conda activate timelapse
pip install -r requirements.txt
```
