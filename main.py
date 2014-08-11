import Image
from os import listdir
from os.path import isdir, join, splitext
import json
import sys
import xml.etree.ElementTree as ET

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

def fuse(data):
  info = {}
  print("Reading station locations")
  xml_root = ET.parse('radar.xml').getroot()
  print(str(xml_root))
  for child in xml_root:
    attrs = child.attrib
    id = attrs['id'][1:]
    info[id] = {
      "lat": attrs['y'],
      "lng": attrs['x'],
      "pn" : attrs['pn']
    }
  print("Find %d locations" % (len(info)))
  print("Find %d ranges" % (len(data)))
  no_loc_count = 0
  update_count = 0
  for id in data:
    if info.has_key(id):
      info[id]['range'] = data[id]
      update_count += 1
    else:
      no_loc_count += 1
      print("Station %s has range but no location" % (id))
  print("Update %d stations" % (update_count))
  to_remove = []
  for id in info:
    if not info[id].has_key('range'):
      print("Station %s has location but no range" % (id))
      to_remove.append(id)
  for id in to_remove:
    del info[id]

  print("Load total %d station inforamtion" % (len(info)))
  return info

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

  content = json.dumps(fuse(results))
  with open(output, 'w+') as f:
    f.write(content)

  print "Output file %s written" % (output)

if __name__ == '__main__':
  data_root = "../data"
  output = "fusion.json"
  if len(sys.argv) != 3:
    print "Usage:"
    print "  main.py data_root output"
    print "Use default args:"
    print "  data_root = ../data"
    print "  output    = fusion.json"
  else:
    data_root = sys.argv[1]
    output = sys.argv[2]
  main(data_root, output)
