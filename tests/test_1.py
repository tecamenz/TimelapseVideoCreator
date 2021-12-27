import unittest
import os
from glob import glob
from timelapse.processing import get_batch_recursive, get_image, get_image_info, process_Images, process_folders
from main import main
import shutil

class TestGlob(unittest.TestCase):
    def test_flat(self):
        true_res = ['1.jpg', '2.jpg','3.jpg', '4.jpg','5.jpg']
        gen = get_batch_recursive('tests/flat', filetype='jpg')
        for paths in gen:
            res = [os.path.split(x)[-1] for x in paths]
            self.assertEqual(res, true_res)

    def test_deep(self):
            true_res = ['1.jpg', '2.jpg','3.jpg', '4.jpg','5.jpg']
            gen = get_batch_recursive('tests/deep', filetype='jpg')
            for paths in gen:
                res = [os.path.split(x)[-1] for x in paths]
                self.assertEqual(res, true_res)

class TestLoader(unittest.TestCase):
    def test_loading(self):
        filepath = 'tests/flat/1.jpg'
        ret = get_image(filepath, 50, 50)
        self.assertEqual(os.path.split(ret['path'])[-1], '1.jpg')
        
    def test_exif(self):
        filepath = 'tests/flat/1.jpg'
        params = {'path': filepath, 'localize': None}
        ret = get_image_info(**params)
        self.assertEqual(ret['datetime'], 1640520023.0)

class TestProcessing(unittest.TestCase):
    def test_process_folders(self):
        expected = {'out\\flat':['tests/flat\\1.jpg', 'tests/flat\\2.jpg', 'tests/flat\\3.jpg', 'tests/flat\\4.jpg', 'tests/flat\\5.jpg']}
        ret = process_folders(src='tests/flat', dst='out', window=2, step=1, filetype='jpg', average=False, imscale=-1, localize=None)
        self.assertEqual(ret, expected)

    def test_process_Images(self):
        gen = get_batch_recursive('tests/flat', filetype='jpg')
        paths = next(gen)
        expected = ['out\\Im_0.JPG', 'out\\Im_1.JPG', 'out\\Im_2.JPG', 'out\\Im_3.JPG', 'out\\Im_4.JPG']
        ret = process_Images(image_paths=paths, window=2, step=1, target_width=50, target_height=50, dst='out')
        self.assertEqual(ret, expected)
        if os.path.exists('out'):
            shutil.rmtree('out')
        else:
            self.assertTrue(False)

    def test_process_Main(self):
        src = 'tests/flat'
        dst = 'out'
        ffmpeg_exe = r'C:\Users\Cami\Documents\Programms\ffmpeg-4.4.1-full_build\bin\ffmpeg.exe'
        main(src=src, dst=dst, window=2, step=1, filetype='jpg', average=True, imscale=-1, vscale=1920, novid=False, localize=None, fps=20, bitrate=10, ffmpeg_exe=ffmpeg_exe)
        if os.path.exists('out'):
            res = glob('out/flat/*.mp4')
            self.assertEqual(len(res), 1)
        else:
            self.assertTrue(False)

    def tearDown(self):
        if os.path.exists('out'):
            shutil.rmtree('out')



       
        

        

if __name__ == '__main__':
    unittest.main()


