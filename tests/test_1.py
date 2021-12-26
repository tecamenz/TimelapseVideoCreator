import unittest
import os
from glob import glob
from timelapse.processing import get_batch_recursive, get_image, get_image_info, process_Images


class TestGlob(unittest.TestCase):
    def test_flat(self):
        true_res = ['1.jpg', '2.jpg','3.jpg', '4.jpg','5.jpg']
        gen = get_batch_recursive('tests/flat', filetype='jpg')
        for paths in gen:
            res = [os.path.split(x)[-1] for x in paths]
            self.assertEqual(res, true_res)

    def test_deep(self):
            true_res = ['1.jpg', '2.jpg','3.jpg', '4.jpg','5.jpg']
            curr_dir =  os.path.dirname(os.path.realpath(__file__))
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
        ret = get_image_info(params)
        self.assertEqual(ret['datetime'], 1640520023.0)

class TestProcessing(unittest.TestCase):
    def test_processing(self):
        gen = get_batch_recursive('tests/flat', filetype='jpg')
        paths = next(gen)
        process_Images(paths, window=2, step=1, dst='hans', target_height=50, target_width=50)
        

        

if __name__ == '__main__':
    unittest.main()


