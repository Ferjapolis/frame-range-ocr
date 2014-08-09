import Image
from os import listdir
from os.path import isdir, join, splitext
import json
import sys

def scan_rect(image, rect = None):
  p = image.load()
  eigens = []
  current = 0
  x_range = range(image.size[0])
  y_range = range(image.size[1])
  zero = p[image.size[0] - 1, image.size[1] - 1]
  if rect:
    x_range = range(rect['left'], rect['right'])
    y_range = range(rect['top'], rect['bottom'])
  for x in x_range:
    count = 0
    for y in y_range:
      if p[x, y] != zero:
        count += 1
    if count != 0:
      current = current * 10 + count
    # Void
    if current != 0 and count == 0:
      eigens.append(current)
      current = 0
  return eigens

def build_eigen_map():
  sample_image = Image.open('sample.bmp')
  sample_eigens = scan_rect(sample_image)
  eigen_map = {}
  for i in range(10):
    eigen_map[sample_eigens[i]] = i
  return eigen_map

RANGE_RECT = {
  (640, 480): {
    "left": 546,
    "right": 576,
    "top": 82,
    "bottom": 100
  },
  (672, 512): {
    "left": 579,
    "right": 612,
    "top": 82,
    "bottom": 100
  }
}

def recognize(E, path):
  image = Image.open(path)
  rect = RANGE_RECT.get(image.size)
  if not rect:
    print "Unknown image size %s, abort" % (image.size)
    return
  eigens = scan_rect(image, rect)
  number = 0
  for e in eigens:
    number = number * 10 + E[e]
  return number

def main(data_root, output):
  E = build_eigen_map()

  station_count = 0
  frame_count = 0
  fail_count = 0

  station_folders = [f for f in listdir(data_root) if isdir(join(data_root, f))]
  results = {}
  for d in station_folders:
    station_folder = join(data_root, d)
    station_count += 1
    frame_file = None
    for f in listdir(station_folder):
      if f.endswith(".gif") or f.endswith(".GIF"):
        frame_count += 1
        frame_file = join(station_folder, f)
        range = recognize(E, frame_file)
        if not range:
          fail_count += 1
        else:
          results[d] = range
        print "Station %s's range: %d" % (d, range)
        break
    if not frame_file:
      print "No frames found for station %s" % (d)

  print "Found %d frames for %d stations. %d OCR failure." % (frame_count, station_count, fail_count)

  content = json.dumps(results)
  with open(output, 'w+') as f:
    f.write(content)

  print "Output file %s written" % (output)

if __name__ == '__main__':
  data_root = "../data"
  output = "range.json"
  if len(sys.argv) != 3:
    print "Usage:"
    print "  main.py data_root output"
    print "Use default args:"
    print "  data_root = ../data"
    print "  output    = range.json"
  else:
    data_root = sys.argv[1]
    output = sys.argv[2]
  main(data_root, output)
