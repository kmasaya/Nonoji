#!/usr/bin/python3

import re


INLINES = [
    # {
    #     'name': 'tex',
    #     're_str': r'([tex\:(.+?)])',
    # },
    {
        'name': 'mailto',
        're_str': r'(\[mailto\:([^\:]*)(?:\:title=([^\]]+))*\])',
    },
    # {
    #     'name': 'youtube',
    #     're_str': r'([youtube:(.+?)])',
    # },
    # {
    #     'name': 'amazon',
    #     're_str': r'([amazon:(.+?)])',
    # },
    # {
    #     'name': 'twitter',
    #     're_str': r'([twitter:(.+?)])',
    # },
    {
        'name': 'link',
        're_str': r'(\[(http\://[^\:]*)(?:\:title=([^\]]+))*\])',
    },
    {
        'name': 'link',
        're_str': r'(\[(https\://[^\:]*)(?:\:title=([^\]]+))*\])',
    },
    {
        'name': 'link',
        're_str': r'(\[(ftp\://[^\:]*)(?:\:title=([^\]]+))*\])',
    },
    {
        'name': 'image',
        're_str': r'(\[image\:(?:id=([^\]]+))*(?:url=([^\]]+))*\])',
    },
]

def parse_inline(line):
    for inline in INLINES:
        for match in re.finditer(inline['re_str'], line):
            print(match.groups())
            match_string = match.groups()[0]
            if inline['name'] == 'link':
                url = match.groups()[1]
                element = match.groups()[2]
                if element is None:
                    element = url
                tag = '<a href="{1}">{0}</a>'.format(element, url)
            elif inline['name'] == 'mailto':
                mail = match.groups()[1]
                element = match.groups()[2]
                if element is None:
                    element = mail
                tag = '<a href="mailto:{1}">{0}</a>'.format(element, mail)
            elif inline['name'] == 'image':
                image_id = match.groups()[1]
                image_url = match.groups()[2]
                if image_id is None:
                    tag = '<img src="{0}">'.format(image_url)
                else:
                    # XXX 画像をどうとるか
                    tag = '<img src="/media/entry/{0}">'.format(image_id)

            line = line.replace(match_string, tag)

    return line

def parse_h(text, replaces, name, re_str, call):
    for match in re.finditer(re_str, text):
        match_string = match.string
        element = match.groups()[0]
        find_star = element.find('*')
        if find_star >= 1 and element.find(' ', 0, find_star):
            id_attr = element[:find_star]
            element = element[find_star+1:]
            tag = '<{0} id="{1}">{2}</{0}>'.format(name, id_attr, element.strip())
        else:
            tag = '<{0}>{1}</{0}>'.format(name, element.strip())

        replaces.append((match_string, tag))

def parse_li(text, replaces, name, re_str, re_sub_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        match_string = match.groups()[0]
        tag = ''
        for sub_match in re.finditer(re_sub_str, match_string, re.MULTILINE):
            tag += '<li>{0}</li>'.format(sub_match.groups()[0].strip())
        tag = '<{0}>{1}</{0}>'.format(name, tag)

        replaces.append((match_string, tag))

def parse_dl(text, replaces, name, re_str, re_sub_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        match_string = match.groups()[0]
        print(match_string)

        tag = ''
        for sub_match in re.finditer(re_sub_str, match_string, re.MULTILINE):
            print(sub_match.groups())
            tag += '<dt>{0}</dt><dd>{1}</dd>'.format(sub_match.groups()[0].strip(), sub_match.groups()[1].strip())
        tag = '<{0}>{1}</{0}>'.format(name, tag)

        replaces.append((match_string, tag))

def parse_table(text, replaces, name, re_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        match_string = match.groups()[0]
        # escape block end line
        if match_string.strip() == '|<' or match_string.strip() == '||<':
            continue

        tag = ''
        for line in match_string.split('\n'):
            if line == '':
                continue
            cells = line[1:].split('|')
            if cells[-1] == '':
                del cells[-1]
            line_tag = ''
            for cell in cells:
                if cell.startswith('*'):
                    cell_type = 'th'
                    cell = cell[1:]
                else:
                    cell_type = 'td'
                line_tag += '<{0}>{1}</{0}>'.format(cell_type, cell.strip())
            tag += '<tr>{0}</tr>'.format(line_tag)
        tag = '<{0}>{1}</{0}>'.format(name, tag)

        replaces.append((match_string, tag))

def parse_blockquote(text, replaces, name, re_str, re_sub_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        print(match.groups())
        match_string = match.groups()[0]
        # XXX http記法
        cite = match.groups()[1]

        lines = []
        for i, sub_match in enumerate(re.finditer(re_sub_str, match_string, re.MULTILINE)):
            line = sub_match.groups()[0]
            if i != 0 and line != '<<' and line != '':
                lines.append(line)

        element = '\n'.join(lines)
        if cite != '':
            tag = '<{0} cite="{2}">{1}</{0}>'.format(name, element.strip(), cite)
        else:
            tag = '<{0}>{1}</{0}>'.format(name, element.strip())

        replaces.append((match_string, tag))

def parse_block(text, replaces, name, re_str, re_sub_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        print(match.groups())
        match_string = match.groups()[0]
        block_type = match.groups()[1]

        lines = []
        for i, sub_match in enumerate(re.finditer(re_sub_str, match_string, re.MULTILINE)):
            line = sub_match.groups()[0]
            if i != 0 and line != '|<' and line != '||<' and line != '':
                lines.append(line)

        element = '\n'.join(lines)
        if block_type == '':
            tag = '<{0}>{1}</{0}>'.format(name, element)
        else:
            if block_type == '?':
                tag = '<{0} class="prettyprint">{1}</{0}>'.format(name, element)
            else:
                tag = '<{0} class="prettyprint lang-{2}">{1}</{0}>'.format(name, element, block_type)

        replaces.append((match_string, tag))


LINES = [
    {
        'name': 'h1',
        're_str': r'^\*([^\*].*)$',
        'call': parse_h,
    },
    {
        'name': 'h2',
        're_str': r'^\*\*([^\*].*)$',
        'call': parse_h,
    },
    {
        'name': 'h3',
        're_str': r'^\*\*\*([^\*].*)$',
        'call': parse_h,
    },
    {
        'name': 'h4',
        're_str': r'^\*\*\*\*([^\*].*)$',
        'call': parse_h,
    },
    {
        'name': 'h5',
        're_str': r'^\*\*\*\*\*([^\*].*)$',
        'call': parse_h,
    },
    {
        'name': 'h6',
        're_str': r'^\*\*\*\*\*\*([^\*].*)$',
        'call': parse_h,
    },

    {
        'name': 'ul',
        're_str': r'((?:^\-(.*)$\n)+)',
        're_sub_str': r'^\-(.*)$',
        'call': parse_li,
    },
    {
        'name': 'ol',
        're_str': r'((?:^\+(.*)$\n)+)',
        're_sub_str': r'^\+(.*)$',
        'call': parse_li,
    },

    {
        'name': 'dl',
        're_str': r'((?:^\:([^\:]*):(.+)$\n)+)',
        're_sub_str': r'^\:([^\:]*):(.+)$',
        'call': parse_dl
    },

    {
        'name': 'table',
        're_str': r'((?:^\|.*$\n)+)',
        'call': parse_table
    },

    {
        'name': 'blockquote',
        're_str': r'(^\>(.*)\>$\n(^.*$\n)+?^\<\<$\n)',
        're_sub_str': r'^(.*)$',
        'call': parse_blockquote
    },
    {
        # >| block
        'name': 'pre',
        're_str': r'(^\>\|(.{0})$\n(^.*$\n)+?^\|\<$\n)',
        're_sub_str': r'^(.*)$',
        'call': parse_block
    },
    {
        # >|| block
        'name': 'pre',
        're_str': r'(^\>\|(.*?)\|$\n(^.*$\n)+?^\|\|\<$\n)',
        're_sub_str': r'^(.*)$',
        'call': parse_block
    },

    # ====
    # =====
    # return
    # ><><
]

def parse(text):
    # XXX
    text += '\n'
    replaces = []
    for line in LINES:
        line['call'](text, replaces, **line)

    for replace in replaces:
        text = text.replace(replace[0], replace[1])

    return text
