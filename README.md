# Radar Frame Range OCR Tool

Radar frames have different ranges and there are no official data for that.

A very simple OCR algorithm is implemented in this tool.
It will pick one frame in each station folder and recognize the range, then store the results in a JSON file.

Dependencies:

* PIL

Usage:

> main.py [data_root] [output]

Example:

```shell
$ main.py ../data range.json
```

`../data` folder should contain a clone of [catx-weather/data](https://github.com/catx-weather/data) repository.
