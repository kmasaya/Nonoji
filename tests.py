#!/usr/bin/python3

import main


def parse_inline(parse_str):
    return main.parse_inline(parse_str)

def parse_line(parse_str):
    return main._test_parse(parse_str).replace('\n', '')

def parse_break(parse_str):
    return main._test_break(parse_str).replace('\n', '')


def test_h():
    for count in range(1, 7):
        prefix = '*' * count
        assert parse_line(prefix+'title') == '<h{0}>title</h{0}>'.format(count)
        assert parse_line(prefix+'[http://example.jp/]') == '<h{0}><a href="http://example.jp/">http://example.jp/</a></h{0}>'.format(count)
        assert parse_line(prefix+'[http://example.jp/:title=aaa]') == '<h{0}><a href="http://example.jp/">aaa</a></h{0}>'.format(count)
        assert parse_line(prefix+' title') == '<h{0}>title</h{0}>'.format(count)
        assert parse_line(prefix+' * title') == '<h{0}>* title</h{0}>'.format(count)
        assert parse_line(prefix+'name* title') == '<h{0} id="name">title</h{0}>'.format(count)
        assert parse_line(' * title') == ' * title'

def test_ul():
    assert parse_line('-li') == '<ul><li>li</li></ul>'
    assert parse_line('-li\n-li') == '<ul><li>li</li><li>li</li></ul>'
    assert parse_line('-li\n--li') == '<ul><li>li</li><li>-li</li></ul>'
    assert parse_line('-li\n-li\n-li[http://example.jp/]') == '<ul><li>li</li><li>li</li><li>li<a href="http://example.jp/">http://example.jp/</a></li></ul>'

def test_ol():
    assert parse_line('+li') == '<ol><li>li</li></ol>'
    assert parse_line('+li\n+li') == '<ol><li>li</li><li>li</li></ol>'
    assert parse_line('+li\n++li') == '<ol><li>li</li><li>+li</li></ol>'
    assert parse_line('+li\n+li\n+li[http://example.jp/]') == '<ol><li>li</li><li>li</li><li>li<a href="http://example.jp/">http://example.jp/</a></li></ol>'

def test_dl():
    assert parse_line(':title:body') == '<dl><dt>title</dt><dd>body</dd></dl>'
    assert parse_line(':title::body') == '<dl><dt>title</dt><dd>:body</dd></dl>'
    assert parse_line(':title::body:') == '<dl><dt>title</dt><dd>:body:</dd></dl>'
    assert parse_line(':title::body:\n:title:body') == '<dl><dt>title</dt><dd>:body:</dd><dt>title</dt><dd>body</dd></dl>'
    assert parse_line(':title::body[http://example.jp/]:') == '<dl><dt>title</dt><dd>:body<a href="http://example.jp/">http://example.jp/</a>:</dd></dl>'

def test_table():
    assert parse_line('|aa|bb|cc|') == '<table><tr><td>aa</td><td>bb</td><td>cc</td></tr></table>'
    assert parse_line('|*aa|bb|*cc|') == '<table><tr><th>aa</th><td>bb</td><th>cc</th></tr></table>'
    assert parse_line('|aa|bb|cc|\n|dd|ee|ff|') == '<table><tr><td>aa</td><td>bb</td><td>cc</td></tr><tr><td>dd</td><td>ee</td><td>ff</td></tr></table>'
    assert parse_line('|*aa|[http://example.jp/]|*[http://example.jp/]|') == '<table><tr><th>aa</th><td><a href="http://example.jp/">http://example.jp/</a></td><th><a href="http://example.jp/">http://example.jp/</a></th></tr></table>'

def test_blockquote():
    assert parse_line('>>aaa<<\n') == '>>aaa<<'
    assert parse_line('>>\naaa\n<<\n') == '<blockquote>aaa</blockquote>'
    assert parse_line('>>\naaa\nbbb\n<<\n') == '<blockquote>aaabbb</blockquote>'
    assert parse_line('>http://example.jp/>\n[http://example.jp/]\n<<\n') == '<blockquote cite="http://example.jp/"><a href="http://example.jp/">http://example.jp/</a></blockquote>'
    assert parse_break('>>\naaa\nbbb\n\nccc\n<<\n') == '<blockquote>aaabbbccc</blockquote>'

def test_block():
    assert parse_line('>|aaa|<\n') == '>|aaa|<'
    assert parse_line('>|\naaa\n|<\n') == '<pre>aaa</pre>'
    assert parse_line('>|\naaa\nbbb\n|<\n') == '<pre>aaabbb</pre>'
    assert parse_line('>|a\naaa\nbbb\n|<\n') == '>|aaaabbb|<'
    assert parse_line('>|a\naaa\nbbb\n|<\n') == '>|aaaabbb|<'
    assert parse_line('>|\naaa\n[http://example.jp/]\n|<\n') == '<pre>aaa<a href="http://example.jp/">http://example.jp/</a></pre>'
    assert parse_line('>||\naaa\nbbb\n||<\n') == '<pre>aaabbb</pre>'
    assert parse_line('>|name|\naaa\nbbb\n||<\n') == '<pre class="prettyprint lang-name">aaabbb</pre>'
    assert parse_line('>|?|\naaa\nbbb\n||<\n') == '<pre class="prettyprint">aaabbb</pre>'
    assert parse_line('>|?|\naaa\n[http://example.jp/]\n||<\n') == '<pre class="prettyprint">aaa[http://example.jp/]</pre>'

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
    assert parse_break('aaa\nbbb\n=====\nccc\nddd') == main.MORE_TAG.replace('\n', '') % ('<p>aaa<br>bbb</p>', '<p>ccc<br>ddd</p>')
    assert parse_break('aaa\nbbb\n====\nccc\nddd') == '<p>aaa<br>bbb<br>====<br>ccc<br>ddd</p>'

def test_break():
    assert parse_break('aaa\nbbb') == '<p>aaa<br>bbb</p>'
    assert parse_break('aaa\n\nbbb') == '<p>aaa</p><p>bbb</p>'
    assert parse_break('aaa\n\nbbb\n\nccc\n') == '<p>aaa</p><p>bbb</p><p>ccc</p>'
    assert parse_break('aaa\n\nbbb\n=====\nccc\n') == main.MORE_TAG.replace('\n', '') % ('<p>aaa</p><p>bbb</p>', '<p>ccc</p>')
    assert parse_break('aaa\n\nbbb\n\n=====\n\nccc\n') == main.MORE_TAG.replace('\n', '') % ('<p>aaa</p><p>bbb</p>', '<p>ccc</p>')


def test_mix():
    assert parse_line('-li\n++li') == '<ul><li>li</li></ul><ol><li>+li</li></ol>'
    assert parse_line('-li\n*1\naaa\n++li') == '<ul><li>li</li></ul><h1>1</h1>aaa<ol><li>+li</li></ol>'
    assert parse_break('-li\n*1\naaa\n++li') == '<ul><li>li</li></ul><h1>1</h1><p>aaa</p><ol><li>+li</li></ol>'
    assert parse_break('-li\n*1\n<span>aaa</span>\n++li') == '<ul><li>li</li></ul><h1>1</h1><span>aaa</span><ol><li>+li</li></ol>'
    assert parse_break('-li\n*1\n <span>aaa</span>\n++li') == '<ul><li>li</li></ul><h1>1</h1><p><span>aaa</span></p><ol><li>+li</li></ol>'
    assert parse_break('-li\n*1\n <span>aaa</span>\n=====\n++li') == main.MORE_TAG.replace('\n', '') % ('<ul><li>li</li></ul><h1>1</h1><p><span>aaa</span></p>','<ol><li>+li</li></ol>')


if __name__ == '__main__':
    pass
