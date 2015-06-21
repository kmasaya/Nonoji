#!/usr/bin/python3

import re

IMAGE_LOCAL_URL = '/media/entry/'

AMAZON_ASSOCIATE_TAG = 'w32-22'
AMAZON_TAG = '<iframe src="http://rcm-fe.amazon-adsystem.com/e/cm?lt1=_blank&bc1=000000&IS2=1&bg1=FFFFFF&fc1=000000&lc1=0000FF&t={1}&o=9&p=8&l=as4&m=amazon&f=ifr&ref=ss_til&asins={0}" style="width:120px;height:240px;" scrolling="no" marginwidth="0" marginheight="0" frameborder="0"></iframe>'
YOUTUBE_TAG = '<iframe width="420" height="315" src="https://www.youtube.com/embed/{0}" frameborder="0" allowfullscreen></iframe>'
MORE_TAG = '''
<div class="summary">
%s
</div>
<div class="more">
%s
</div>
'''
# MORE_TAG = '''
# <div class="summary">
# %s
# </div>
# <div class="cm">
# <script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
# <!-- jp.w32 記事中 -->
# <ins class="adsbygoogle"
# style="display:inline-block;width:300px;height:250px"
# data-ad-client="ca-pub-6392284552603348"
# data-ad-slot="6848729146"></ins>
# <script>
# (adsbygoogle = window.adsbygoogle || []).push({});
# </script>
# </div>
# <div class="more">
# %s
# </div>
# '''

INLINES = [
    {
        'name': 'tex',
        're_str': r'(\[tex\:(.+?[^\\])\])',
    },
    {
        'name': 'mailto',
        're_str': r'(\[mailto\:([^\:]*)(?:\:title=([^\]]+))*\])',
    },
    {
        'name': 'youtube',
        're_str': r'(\[youtube\:(.+?)\])',
    },
    {
        'name': 'asin',
        're_str': r'(\[asin\:(.+?)\])',
    },
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
                    tag = '<img src="{0}{1}">'.format(IMAGE_LOCAL_URL, image_id)
            elif inline['name'] == 'asin':
                asin_id = match.groups()[1]
                tag = AMAZON_TAG.format(asin_id, AMAZON_ASSOCIATE_TAG)
            elif inline['name'] == 'youtube':
                youtube_id = match.groups()[1]
                tag = YOUTUBE_TAG.format(youtube_id)
            elif inline['name'] == 'tex':
                tex = match.groups()[1]
                tag = r'<span class="tex">\({0}\)</span>'.format(tex).replace(r'\]', ']')

            line = line.replace(match_string, tag)
    return line

def parse_h(text, replaces, name, re_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        match_string = match.groups()[0]
        element = match.groups()[1]
        find_star = element.find('*')
        if find_star >= 1 and element.find(' ', 0, find_star):
            id_attr = element[:find_star]
            element = element[find_star+1:]
            element = parse_inline(element)
            tag = '<{0} id="{1}">{2}</{0}>'.format(name, id_attr, element.strip())
        else:
            element = parse_inline(element)
            tag = '<{0}>{1}</{0}>'.format(name, element.strip())

        replaces.append((match_string, tag))

def parse_li(text, replaces, name, re_str, re_sub_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        match_string = match.groups()[0]
        tag = ''
        for sub_match in re.finditer(re_sub_str, match_string, re.MULTILINE):
            element = sub_match.groups()[0]
            element = parse_inline(element)
            tag += '<li>{0}</li>\n'.format(element.strip())
        tag = '<{0}>\n{1}</{0}>\n\n'.format(name, tag)

        replaces.append((match_string, tag))

def parse_dl(text, replaces, name, re_str, re_sub_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        match_string = match.groups()[0]
        tag = ''
        for sub_match in re.finditer(re_sub_str, match_string, re.MULTILINE):
            dt_element = sub_match.groups()[0].strip()
            dt_element = parse_inline(dt_element)
            dd_element = sub_match.groups()[1].strip()
            dd_element = parse_inline(dd_element)
            tag += '<dt>{0}</dt><dd>{1}</dd>\n'.format(dt_element, dd_element)
        tag = '<{0}>\n{1}</{0}>\n\n'.format(name, tag)

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
                cell = parse_inline(cell.strip())
                line_tag += '<{0}>{1}</{0}>\n'.format(cell_type, cell)
            tag += '<tr>\n{0}</tr>\n'.format(line_tag)
        tag = '<{0}>\n{1}</{0}>\n\n'.format(name, tag)

        replaces.append((match_string, tag))

def parse_blockquote(text, replaces, name, re_str, re_sub_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        match_string = match.groups()[0]
        cite = match.groups()[1]

        lines = []
        for i, sub_match in enumerate(re.finditer(re_sub_str, match_string, re.MULTILINE)):
            line = sub_match.groups()[0]
            if i != 0 and line != '<<':
                lines.append(line)

        element = '\n'.join(lines)
        element = parse_inline(element.strip())
        if cite != '':
            tag = '<{0} cite="{2}">\n{1}\n</{0}>\n\n'.format(name, element, cite)
        else:
            tag = '<{0}>\n{1}\n</{0}>\n\n'.format(name, element)

        replaces.append((match_string, tag))

def parse_block(text, replaces, name, re_str, re_sub_str, call):
    for match in re.finditer(re_str, text, re.MULTILINE):
        match_string = match.groups()[0]
        if len(match.groups()) > 1:
            block_type = match.groups()[1]
        else:
            block_type = None

        lines = []
        for i, sub_match in enumerate(re.finditer(re_sub_str, match_string, re.MULTILINE)):
            line = sub_match.groups()[0]
            if i != 0 and line != '|<' and line != '||<':
                lines.append(line)

        element = '\n'.join(lines)

        if block_type is None:
            element = parse_inline(element)
            tag = '><\n<{0}>\n{1}</{0}>\n><\n\n'.format(name, element)
        else:
            element = element.replace('<', '&lt;').replace('>', '&gt;')
            if block_type == '':
                tag = '><\n<{0}>\n{1}</{0}>\n><\n\n'.format(name, element)
            elif block_type == '?':
                tag = '><\n<{0} class="prettyprint">\n{1}</{0}>\n><\n\n'.format(name, element)
            else:
                tag = '><\n<{0} class="prettyprint lang-{2}">\n{1}</{0}>\n><\n\n'.format(name, element, block_type)

        replaces.append((match_string, tag))

def parse_more(text, name, re_str, call):
    if re.search(re_str, text, re.MULTILINE) is not None:
        summary, more = re.split(re_str, text, 1, re.MULTILINE)
        return MORE_TAG % (summary, more)
    else:
        return text


LINES = [
    {
        'name': 'h1',
        're_str': r'^(\*([^\*].*)$)',
        'call': parse_h,
    },
    {
        'name': 'h2',
        're_str': r'^(\*\*([^\*].*)$)',
        'call': parse_h,
    },
    {
        'name': 'h3',
        're_str': r'^(\*\*\*([^\*].*)$)',
        'call': parse_h,
    },
    {
        'name': 'h4',
        're_str': r'^(\*\*\*\*([^\*].*)$)',
        'call': parse_h,
    },
    {
        'name': 'h5',
        're_str': r'^(\*\*\*\*\*([^\*].*)$)',
        'call': parse_h,
    },
    {
        'name': 'h6',
        're_str': r'^(\*\*\*\*\*\*([^\*].*)$)',
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
        're_str': r'(^\>\|$\n(?:^.*$\n)+?^\|\<$\n)',
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
]

MORES = [
    {
        'name': 'more',
        're_str': r'^=====$\n',
        'call': parse_more
    }
]

def parse_break(text, name, re_str, call):
    replaces = []
    through_replaces = []
    for match in re.finditer(BREAK_THROUGH[0]['re_str'], text, re.MULTILINE):
        match_string = match.groups()[0]
        escape_string = match_string.replace('\n', '')
        through_replaces.append((match_string, escape_string))
        text = text.replace(match_string, '<'+escape_string, 1)

    for match in re.finditer(re_str, text, re.MULTILINE):
        match_string = match.groups()[0]
        element = match.groups()[0].strip()
        element = '<br>\n'.join([parse_inline(line) for line in element.split('\n')])
        tag = '<p>{0}</p>\n\n'.format(element)

        replaces.append((match_string, tag))

    for replace in replaces:
        text = text.replace(replace[0], replace[1], 1)

    for through_replace in through_replaces:
        text = text.replace('<'+through_replace[1], through_replace[0])

    return re.sub(r'^\>\<$\n', '', text, 0, re.MULTILINE)


BREAK_THROUGH = [
    {
        'name': 'break_throught',
        're_str': r'(^\>\<$\n(?:^.*$\n)+^\>\<$\n)',
    }
]

BREAKS = [
    {
        'name': 'break',
        're_str': r'((?:^(?!$\n)(?!=====$\n)[^<].*$\n)+)',
        'call': parse_break
    }
]


def _test_parse(text):
    text = '{0}\n\n'.format(text)
    replaces = []
    for line in LINES:
        line['call'](text, replaces, **line)
    for replace in replaces:
        text = text.replace(replace[0], replace[1]+'\n', 1)

    return text

def _test_break(text):
    text = _test_parse(text)

    for break_point in BREAKS:
        text = break_point['call'](text, **break_point)

    for more in MORES:
        text = more['call'](text, **more)

    return text

def parse(text):
    # XXX
    text = '{0}\n\n'.format(text.replace('\r\n', '\n').replace('\r', '\n'))
    replaces = []
    for line in LINES:
        line['call'](text, replaces, **line)

    for replace in replaces:
        text = text.replace(replace[0], replace[1], 1)

    for break_point in BREAKS:
        text = break_point['call'](text, **break_point)

    for more in MORES:
        text = more['call'](text, **more)

    return text
