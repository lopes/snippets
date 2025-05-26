#!/usr/bin/env python3

'''
Convert Kindle or O'Reilly annotations to JSON or Markdown format.

Usage:
  moth.py -i <input> -o <output> [-s <source>] [-f <format>]

Example:
  moth.py -i My\\ Clippings.txt -o annotations.json -f json
  moth.py -i My\\ Clippings.txt -o annotations.md
  moth.py -i Annotations.csv -o annotations.json -s oreilly -f json

Kindle:
  Export your Kindle highlights to a file named My Clippings.txt.
  Mount your Kindle as a USB drive and copy the file from the documents folder.

O'Reilly:
  Export your O'Reilly annotations to a file named Annotations.csv.
  In O'Reilly: My O'Reilly > Highlights > Export all highlights

Annotations sorting:
  - Annotations order are based on location (Kindle, most precise) or
    on chapter number (O'Reilly, less precise).
  - As O'Reilly does not provide the  exact location inside the chapter,
    the order might be broken at this level.
  - I try to minimize it by sorting by date but as some annotations
    might have the same date inside the chapter, it loses precision.

Author.: Joe Lopes <lopes.id>
License: MIT
Date...: 2024-07-25
'''

from argparse import ArgumentParser
from re import compile
from json import dumps

parser = ArgumentParser(description='Convert Kindle/O\'Reilly annotations to JSON or Markdown format.')
parser.add_argument('-i', '--input', required=True,
  help='Path to My Clippings.txt or Annotations.csv file.')
parser.add_argument('-o', '--output', required=True,
  help='Path to the output file.')
parser.add_argument('-f', '--format', default='markdown', choices=['markdown','json'],
  help='Output format: json or markdown. Default is markdown.')
parser.add_argument('-s', '--source', default='kindle', choices=['kindle','oreilly'],
  help='Input format: kindle or oreilly. Default is kindle.')
args = parser.parse_args()


def kindle(raw):
  delimiter = '==========\n'
  re_title = compile(r'^(.*?)\(')
  re_author = compile(r'\((.*?)\)')
  re_type = compile(r'Your (Highlight|Note|Bookmark) on page')
  re_page = compile(r'on page (\d+) \|')
  re_location = compile(r'\| Location (\d+(-\d+)?) \|')
  re_date = compile(r'\| Added on (.*)')
  re_index = compile(r'\| Location (\d+)(-\d+)? \|')
  date_format = '%A, %B %d, %Y %I:%M:%S %p'

  annotations = raw.split(delimiter)
  catalog = dict()

  for ann in annotations:
    if ann:
      p = kindle_parser(ann, re_title, re_author, re_type,
          re_page, re_location, re_index, re_date, date_format
        )
      if p['title'] not in catalog:
        catalog[p['title']] = dict()
        catalog[p['title']]['author'] = p['author']
        catalog[p['title']]['highlights'] = list()
      catalog[p['title']]['highlights'].append({
        'type': p['type'],
        'location': p['location'],
        'index': p['index'],
        'date': p['date'],
        'highlight': p['highlight'],
        'note': p['note']
      })
  return catalog

def kindle_parser(ann, retit, reaut, retyp, repag, reloc, reind, redat, datefmt):
  lines = ann.split('\n')
  title = retit.search(lines[0]).group(1)
  author = reaut.search(lines[0]).group(1)
  type = retyp.search(lines[1]).group(1)
  page = repag.search(lines[1]).group(1)
  location = reloc.search(lines[1]).group(1)
  index = int(reind.search(lines[1]).group(1))
  date = datetime.strptime(redat.search(lines[1]).group(1), datefmt).strftime('%Y-%m-%d')

  if type == 'Note':
    highlight = '-'
    note = lines[3]
  else:
    highlight = lines[3]
    note = '-'

  return {
    'title': title,
    'author': author,
    'type': type,
    'index': index,
    'location': f'Page {page} (loc. {location})',
    'date': date,
    'highlight': highlight,
    'note': note
  }

def oreilly(raw):
  re_index = compile(r'^((Chapter )?(?P<index>\d+))')
  re_location = compile(r'^https://.*#(?P<location>[a-zA-Z0-9\-]+)$')
  annotations = csv_reader(str_io(raw), delimiter=',')
  catalog = dict()

  for ann in annotations:
    parsed = oreilly_parser(ann, re_index, re_location)
    if parsed['title'] not in catalog:
      catalog[parsed['title']] = dict()
      catalog[parsed['title']]['author'] = parsed['author']
      catalog[parsed['title']]['highlights'] = list()
    catalog[parsed['title']]['highlights'].append({
      'index': parsed['index'],
      'type': parsed['type'],
      'location': parsed['location'],
      'date': parsed['date'],
      'highlight': parsed['highlight'],
      'note': parsed['note']
    })
  return catalog

def oreilly_parser(ann, reind, reloc):
  if ann['Personal Note']:
    type = 'Note'
    note = ann['Personal Note']
  else:
    type = 'Highlight'
    note = '-'

  try:
    index = int(reind.search(ann['Chapter Title']).group('index'))
  except AttributeError:
    index = 0

  return {
    'title': ann['Book Title'],
    'author': '-',
    'type': type,
    'index': index,
    'location': f'Chapter {index} ({reloc.search(ann["Annotation URL"]).group("location")})',
    'date': ann['Date of Highlight'],
    'highlight': ann['Highlight'],
    'note': note
  }

def to_json(c):
  return dumps(c)

def to_markdown(c):
  md = ''
  for book in c:
    md += f'# {book}\nAuthor: {c[book]["author"]}\n\n' + f'Notes exported by ' + \
      f'[Moth.py](https://gist.github.com/lopes/c42b3e13dfd51771251e7ece86cf7050).\n\n'
    for ann in c[book]['highlights']:
      md += f'\n## {ann["location"]}\n'
      md += f'>{ann["date"]}: Location: {ann["location"]}: *{ann["highlight"]}*\n\n'
      md += f'{ann["note"]}\n'
    md += '---\n\n\n'
  return md


##
# MAIN
#
with open(args.input, 'r') as f:
  raw = f.read()

if args.source == 'kindle':
  from datetime import datetime
  catalog = kindle(raw)
else:
  from csv import DictReader as csv_reader
  from io import StringIO as str_io
  catalog = oreilly(raw)

for book in catalog:
  catalog[book]['highlights'] = sorted(catalog[book]['highlights'], key=lambda x: x['date'])
  catalog[book]['highlights'] = sorted(catalog[book]['highlights'], key=lambda x: x['index'])
  for annotation in catalog[book]['highlights']:
    del annotation['index']

with open(args.output, 'w') as f:
  if args.format == 'markdown':
    f.write(to_markdown(catalog))
  else:
    f.write(to_json(catalog))
