#!/usr/bin/python

import re

Notations = [
    {
        'pattern': r'^\*([^\*].*)$',
        'replace': r'<h1>\1</h1>',
        'flag': re.MULTILINE,
        'option': 'line',
    },
    {
        'pattern': r'^\*\*([^\*].*)$',
        'replace': r'<h2>\1</h2>',
        'flag': re.MULTILINE,
        'option': 'line',
    },
    {
        'pattern': r'^\*\*\*([^\*].*)$',
        'replace': r'<h3>\1</h3>',
        'flag': re.MULTILINE,
        'option': 'line',
    },
    {
        'pattern': r'^\*\*\*\*([^\*].*)$',
        'replace': r'<h4>\1</h4>',
        'flag': re.MULTILINE,
        'option': 'line',
    },
    {
        'pattern': r'^\*\*\*\*\*([^\*].*)$',
        'replace': r'<h5>\1</h5>',
        'flag': re.MULTILINE,
        'option': 'line',
    },
    {
        'pattern': r'^\*\*\*\*\*\*([^\*].*)$',
        'replace': r'<h6>\1</h6>',
        'flag': re.MULTILINE,
        'option': 'line',
    },

    {
        'pattern': r'((?:^\-(.*)$\n)+)',
        'sub_pattern': r'^\-(.*)$',
        'replace': '<ul>\n\\1</ul>\n',
        'sub_replace': r'<li>\1</li>',
        'flag': re.MULTILINE,
        'option': 'nest',

    },
    {
        'pattern': r'((?:^\+(.*)$\n)+)',
        'sub_pattern': r'^\+(.*)$',
        'replace': '<ol>\n\\1</ol>\n',
        'sub_replace': r'<li>\1</li>',
        'flag': re.MULTILINE,
        'option': 'nest',

    },

    {
        'pattern': r'((?:^\:([^\:]*):(.+)$\n)+)',
        'sub_pattern': r'^\:([^\:]*):(.+)$',
        'replace': '<dl>\n\\1</dl>\n',
        'sub_replace': r'<dt>\1</dt><dd>\2</dd>',
        'flag': re.MULTILINE,
        'option': 'nest',

    },

    {
        'pattern': r'((?:^\|.*$\n)+)',
        'split': '|',
        'replace': '<table>\n\\1</table>\n',
        'sub_replace': '<tr>\n\\1</tr>\n',
        'sub_sub_replace': r'<td>\1</td>\n',
        'flag': re.MULTILINE,
        'option': 'table',

    },

    # ('^\>\>^\<\<', '', ''),
    # ('^\>\|.*\|\<', '', ''),
    # ('^\>\|.*\|^\|\|\<', '', ''),
    # ('\(\(.*\)\)', '', ''),
    # ('^====', '', ''),go
    # ('^=====', '', ''),
    # ('\r\r', '', ''),
    # ('^><', '', ''),
    # ('[tex:]', '', ''),
    # ('[uke:]', '', ''),
]


def parse(text):
    text += '\n'
    replaces = []
    for notation in Notations:
        if notation['option'] is 'line':
            replaces.append((notation['pattern'], notation['replace'], notation['flag']))
        elif notation['option'] == 'nest':
            regexp = re.compile(notation['pattern'], notation['flag'])
            match_all = regexp.findall(text)
            for match in match_all:
                sub_regexp = re.compile(notation['sub_pattern'], notation['flag'])
                subs = re.sub(sub_regexp, notation['sub_replace'], match[0])
                replaces.append((re.escape(match[0]), notation['replace'].replace(r'\1', subs), notation['flag']))
        elif notation['option'] == 'table':
            regexp = re.compile(notation['pattern'], notation['flag'])
            match_all = regexp.findall(text)
            for match in match_all:
                lines = match.split('\n')
                cell_lines = []
                for line in lines:
                    cells = line.split('|')
                    while cells.count('') > 0:
                        cells.remove('')
                    if len(cells) > 0:
                        cell_lines.append(cells)
                rows = []
                for cell_line in cell_lines:
                    row = []
                    for cell in cell_line:
                        row.append(notation['sub_sub_replace'].replace(r'\1', cell))
                    rows.append(notation['sub_replace'].replace(r'\1', ''.join(row)))
                replaces.append((re.escape(match), notation['replace'].replace(r'\1', ''.join(rows)), notation['flag']))

    for replace in replaces:
        text = re.sub(re.compile(replace[0], replace[2]), replace[1], text)

    return text
