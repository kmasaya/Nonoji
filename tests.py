#!/usr/bin/python3

import main


def parse_inline(parse_str):
    return main.parse_inline(parse_str)

def parse(parse_str):
    return main.parse(parse_str).replace('\n', '')


def test_h():
    for count in range(1, 7):
        prefix = '*' * count
        assert parse(prefix+'title') == '<h{0}>title</h{0}>'.format(count)
        assert parse(prefix+'[http://example.jp/]') == '<h{0}><a href="http://example.jp/">http://example.jp/</a></h{0}>'.format(count)
        assert parse(prefix+'[http://example.jp/:title=aaa]') == '<h{0}><a href="http://example.jp/">aaa</a></h{0}>'.format(count)
        assert parse(prefix+' title') == '<h{0}>title</h{0}>'.format(count)
        assert parse(prefix+' * title') == '<h{0}>* title</h{0}>'.format(count)
        assert parse(prefix+'name* title') == '<h{0} id="name">title</h{0}>'.format(count)
        assert parse(' * title') == ' * title'

def test_ul():
    assert parse('-li') == '<ul><li>li</li></ul>'
    assert parse('-li\n-li') == '<ul><li>li</li><li>li</li></ul>'
    assert parse('-li\n--li') == '<ul><li>li</li><li>-li</li></ul>'
    assert parse('-li\n-li\n-li[http://example.jp/]') == '<ul><li>li</li><li>li</li><li>li<a href="http://example.jp/">http://example.jp/</a></li></ul>'

def test_ol():
    assert parse('+li') == '<ol><li>li</li></ol>'
    assert parse('+li\n+li') == '<ol><li>li</li><li>li</li></ol>'
    assert parse('+li\n++li') == '<ol><li>li</li><li>+li</li></ol>'
    assert parse('+li\n+li\n+li[http://example.jp/]') == '<ol><li>li</li><li>li</li><li>li<a href="http://example.jp/">http://example.jp/</a></li></ol>'

def test_dl():
    assert parse(':title:body') == '<dl><dt>title</dt><dd>body</dd></dl>'
    assert parse(':title::body') == '<dl><dt>title</dt><dd>:body</dd></dl>'
    assert parse(':title::body:') == '<dl><dt>title</dt><dd>:body:</dd></dl>'
    assert parse(':title::body:\n:title:body') == '<dl><dt>title</dt><dd>:body:</dd><dt>title</dt><dd>body</dd></dl>'
    assert parse(':title::body[http://example.jp/]:') == '<dl><dt>title</dt><dd>:body<a href="http://example.jp/">http://example.jp/</a>:</dd></dl>'

def test_table():
    assert parse('|aa|bb|cc|') == '<table><tr><td>aa</td><td>bb</td><td>cc</td></tr></table>'
    assert parse('|*aa|bb|*cc|') == '<table><tr><th>aa</th><td>bb</td><th>cc</th></tr></table>'
    assert parse('|aa|bb|cc|\n|dd|ee|ff|') == '<table><tr><td>aa</td><td>bb</td><td>cc</td></tr><tr><td>dd</td><td>ee</td><td>ff</td></tr></table>'
    assert parse('|*aa|[http://example.jp/]|*[http://example.jp/]|') == '<table><tr><th>aa</th><td><a href="http://example.jp/">http://example.jp/</a></td><th><a href="http://example.jp/">http://example.jp/</a></th></tr></table>'

def test_blockquote():
    assert parse('>>aaa<<\n') == '>>aaa<<'
    assert parse('>>\naaa\n<<\n') == '<blockquote>aaa</blockquote>'
    assert parse('>>\naaa\nbbb\n<<\n') == '<blockquote>aaabbb</blockquote>'
    assert parse('>http://example.jp/>\n[http://example.jp/]\n<<\n') == '<blockquote cite="http://example.jp/"><a href="http://example.jp/">http://example.jp/</a></blockquote>'

def test_block():
    assert parse('>|aaa|<\n') == '>|aaa|<'
    assert parse('>|\naaa\n|<\n') == '<pre>aaa</pre>'
    assert parse('>|\naaa\nbbb\n|<\n') == '<pre>aaabbb</pre>'
    assert parse('>|a\naaa\nbbb\n|<\n') == '>|aaaabbb|<'
    assert parse('>|a\naaa\nbbb\n|<\n') == '>|aaaabbb|<'
    assert parse('>|\naaa\n[http://example.jp/]\n|<\n') == '<pre>aaa<a href="http://example.jp/">http://example.jp/</a></pre>'
    assert parse('>||\naaa\nbbb\n||<\n') == '<pre>aaabbb</pre>'
    assert parse('>|name|\naaa\nbbb\n||<\n') == '<pre class="prettyprint lang-name">aaabbb</pre>'
    assert parse('>|?|\naaa\nbbb\n||<\n') == '<pre class="prettyprint">aaabbb</pre>'
    assert parse('>|?|\naaa\n[http://example.jp/]\n||<\n') == '<pre class="prettyprint">aaa[http://example.jp/]</pre>'

def test_inline():
    assert parse_inline(r'[http://example.jp/]') == '<a href="http://example.jp/">http://example.jp/</a>'
    assert parse_inline(r'[http://example.jp/:title=titlestr]') == '<a href="http://example.jp/">titlestr</a>'
    assert parse_inline(r'[http://example.jp/:title=titlestr]::[http://example.com/]') == \
           '<a href="http://example.jp/">titlestr</a>::<a href="http://example.com/">http://example.com/</a>'

    assert parse_inline(r'[mailto:a@example.jp]') == '<a href="mailto:a@example.jp">a@example.jp</a>'
    assert parse_inline(r'[mailto:a@example.jp:title=mail]') == '<a href="mailto:a@example.jp">mail</a>'

    assert parse_inline(r'[image:id=333]') == '<img src="/media/entry/333">'
    assert parse_inline(r'[image:url=http://example.jp/333.jpg]') == '<img src="http://example.jp/333.jpg">'

    assert parse_inline(r'[asin:adf93kj]') == main.AMAZON_TAG.format('adf93kj', main.AMAZON_ASSOCIATE_TAG)
    assert parse_inline(r'[youtube:adf93kj]') == main.YOUTUBE_TAG.format('adf93kj')

    assert parse_inline(r'[tex:-3 \times -2 = +6]') == r'<span class="tex">\(-3 \times -2 = +6\)</span>'
    assert parse_inline(r'[tex:-3 \times -2 = +6[\]]') == r'<span class="tex">\(-3 \times -2 = +6[]\)</span>'

def test_more():
    assert parse('aaa\nbbb\n=====\nccc\nddd') == main.MORE_TAG.replace('\n', '') % ('aaabbb', 'cccddd')
    assert parse('aaa\nbbb\n====\nccc\nddd') == 'aaabbb====cccddd'

def test_break():
    assert parse('aaa\n\nbbb') == '<p>aaa</p><p>bbb</p>'
    assert parse('aaa\n\nbbb\n\nccc\n') == '<p>aaa</p><p>bbb</p><p>ccc</p>'
    assert parse('aaa\n\nbbb\n=====\nccc\n') == main.MORE_TAG.replace('\n', '') % ('<p>aaa</p><p>bbb</p>', '<p>ccc</p>')
    assert parse('aaa\n\nbbb\n=====\nccc\n') == main.MORE_TAG.replace('\n', '') % ('<p>aaa</p><p>bbb</p>', '<p>ccc</p>')


# def test_mix():
#     assert parse('-li\n++li') == '<ul><li>li</li></ul><ol><li>+li</li></ol>'


if __name__ == '__main__':
    pass
