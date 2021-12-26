# TimelapseVideoCreator
Simple command line tool to create timelapse videos from individual images. 

Input images are sorted via EXIF timestamp to ensure correct order. 


## Usage
```cmd
Usage: main.py [OPTIONS] [SRC] [DST]

  Create timelapse from images located in SRC and saves the video to DST

  If SRC contains subfolders, the program recursively scans all subfolders and
  creates a video per subfolder. The folder structure at DSC will be
  preserved, and the output videos are saved in respectively named folders.

  If pre-processing via --average is set to True, the DST will contain
  intermediate (averaged) images along with a output video.

  If --novid is set to True along side with --average, only the intermediate
  (averaged) images are saved. Useful if you like to create the final video in
  a dedicated video editor.

Options:
  --window INTEGER   Defines the number of images to average. Default is 3.
  --step INTEGER     Defines the number of images to step forward. Default is
                     1.
  --filetype TEXT    Defines the image filetype to search for.
  --average          Option to average [window] images into one. Default is
                     False.
  --imscale INTEGER  Defines the width of the output image after averaging.
                     Default is -1 which preserves native resolution.
  --vscale INTEGER   Defines the width of the output video. Default is 1920.
  --novid            If to omit video creation. Only used when --average ==
                     True.
  --localize TEXT    String for timezone conversion.
  --ffmpeg_exe TEXT  Path to ffmpeg.exe.
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
