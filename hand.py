from PIL import Image, ImageFilter, ImageDraw
import skimage
import numpy
import cv2
import sys


__author__ = 'Riley'



def outline(image):
    image = image.copy()
    image = image.convert('RGBA')
    pixels = numpy.array(image)
    print(pixels.shape)
    pixels[:, :] = pixels >> 5 << 5
    for index in numpy.ndindex(pixels.shape[:2]):
        if pixels[index][3] < 100:
            pixels[index] = (255, 255, 255, 255)
    image = Image.fromarray(pixels)
    image = image.filter(ImageFilter.CONTOUR)
    image = image.convert('L')
    pixels = numpy.array(image)
    pixels[pixels < 255] = 0
    image = Image.fromarray(pixels)
    return image


def vectorize(image):
    kernel = numpy.array([1, 1, 1, 1]).reshape((2, 2))
    pixels = numpy.array(image)
    pixels = 255-pixels
    #pixels = cv2.copyMakeBorder(pixels, 50, 50, 50, 50, borderType=cv2.BORDER_CONSTANT, value=0)
    pixels = cv2.dilate(pixels, kernel, iterations=1)
    image = Image.fromarray(pixels)
    _, contours, _ = cv2.findContours(pixels, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_NONE)
    return image, contours


def normalize(num, old_range_,  range_):
    return (num-min(old_range_)) / (max(old_range_)-min(old_range_)) * (max(range_)-min(range_)) + min(range_)


def norm_point(point, old_size, size):
    return [normalize(dim, old_range, range_) for dim, old_range, range_ in zip(point, old_size, size)]



def gcode(contours, image_size, size,  file_name, header, footer):
    with open(file_name[:file_name.rfind('.')] + '.gcode', 'w+') as output:
        preview = Image.new('1', [(max(dim)-min(dim)) * 10 for dim in size[::-1]], color='white')
        draw = ImageDraw.Draw(preview)
        output.write(header)
        for contour in contours[:-1]:
            prev = norm_point(contour[:-1][0][0][::-1], image_size[::-1], size)
            output.write('G91\n')
            output.write('G0 Z6\n')
            output.write('G90\n')
            output.write('G0 X{0:.2f} Y{1:.2f} F1500\n'.format(*prev))
            output.write('G91\n')
            output.write('G0 Z-6\n')
            output.write('G90\n')
            for point in contour[::-1, 0]:
                point = norm_point(point[::-1], image_size[::-1], size)
                output.write('G0 X{0:.2f} Y{1:.2f} F1500\n'.format(*point))
                draw.line([dim * 10 for dim in (
                    norm_point(prev[::-1], size[::-1], [(0, max(dim)-min(dim)) for dim in size[::-1]]) +
                    norm_point(point[::-1], size[::-1], [(0, max(dim)-min(dim)) for dim in size[::-1]])
                )], fill='black', width=2)
                prev = point
        output.write(footer)
        return preview





if __name__== '__main__':

    header = """M73 P0 (enable build progress)
G21 (set units to mm)
G90 (set positioning to absolute)
G54 (Recall offset cooridinate system)
(**** begin homing ****)
G91
G0 Z6
G90
G162 X Y F2500 (home XY axes maximum)
M132 X Y Z A B (Recall stored home offsets for XYZAB axis)
(**** end homing ****)
G1 X112 Y-73 F3300.0 (move to waiting position)
G0 X112 Y-73 (Position Nozzle)
(**** end of start.gcode ****)
G91
G0 Z-7
G90
"""

    footer = """M73 P100 (end  build progress )
G91
G0 Z35
G90
M70 P5 ( We <3 Making Things!)
M72 P1  ( Play Ta-Da song )
    """

    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = 'notes1.fw.png'
    print(normalize(0, (-10, 10), (0, 20)))
    image = Image.open(file_name)
    image = outline(image)
    image.save('outline.png')
    image, contours = vectorize(image)
    image.save('outline2.png')
    print(len(contours))
    image = gcode(contours, [(0, dim) for dim in image.size], ((-70, 130), (-65, 65)), file_name, header, footer)
    image.save('out.png')