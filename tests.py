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
        assert parse(prefix+' title') == '<h{0}>title</h{0}>'.format(count)
        assert parse(prefix+' * title') == '<h{0}>* title</h{0}>'.format(count)
        assert parse(prefix+'name* title') == '<h{0} id="name">title</h{0}>'.format(count)
        assert parse(' * title') == ' * title'

def test_ul():
    assert parse('-li') == '<ul><li>li</li></ul>'
    assert parse('-li\n-li') == '<ul><li>li</li><li>li</li></ul>'
    assert parse('-li\n--li') == '<ul><li>li</li><li>-li</li></ul>'

def test_ol():
    assert parse('+li') == '<ol><li>li</li></ol>'
    assert parse('+li\n+li') == '<ol><li>li</li><li>li</li></ol>'
    assert parse('+li\n++li') == '<ol><li>li</li><li>+li</li></ol>'

def test_dl():
    assert parse(':title:body') == '<dl><dt>title</dt><dd>body</dd></dl>'
    assert parse(':title::body') == '<dl><dt>title</dt><dd>:body</dd></dl>'
    assert parse(':title::body:') == '<dl><dt>title</dt><dd>:body:</dd></dl>'
    assert parse(':title::body:\n:title:body') == '<dl><dt>title</dt><dd>:body:</dd><dt>title</dt><dd>body</dd></dl>'

def test_table():
    assert parse('|aa|bb|cc|') == '<table><tr><td>aa</td><td>bb</td><td>cc</td></tr></table>'
    assert parse('|*aa|bb|*cc|') == '<table><tr><th>aa</th><td>bb</td><th>cc</th></tr></table>'
    assert parse('|aa|bb|cc|\n|dd|ee|ff|') == '<table><tr><td>aa</td><td>bb</td><td>cc</td></tr><tr><td>dd</td><td>ee</td><td>ff</td></tr></table>'

def test_blockquote():
    assert parse('>>aaa<<\n') == '>>aaa<<'
    assert parse('>>\naaa\n<<\n') == '<blockquote>aaa</blockquote>'
    assert parse('>>\naaa\nbbb\n<<\n') == '<blockquote>aaabbb</blockquote>'
    assert parse('>http://example.jp/>\naaa\n<<\n') == '<blockquote cite="http://example.jp/">aaa</blockquote>'

def test_block():
    assert parse('>|aaa|<\n') == '>|aaa|<'
    assert parse('>|\naaa\n|<\n') == '<pre>aaa</pre>'
    assert parse('>|\naaa\nbbb\n|<\n') == '<pre>aaabbb</pre>'
    assert parse('>|a\naaa\nbbb\n|<\n') == '>|aaaabbb|<'
    assert parse('>|a\naaa\nbbb\n|<\n') == '>|aaaabbb|<'
    assert parse('>||\naaa\nbbb\n||<\n') == '<pre>aaabbb</pre>'
    assert parse('>|name|\naaa\nbbb\n||<\n') == '<pre class="prettyprint lang-name">aaabbb</pre>'
    assert parse('>|?|\naaa\nbbb\n||<\n') == '<pre class="prettyprint">aaabbb</pre>'

def test_inline():
    assert parse_inline(r'[http://example.jp/]') == '<a href="http://example.jp/">http://example.jp/</a>'
    assert parse_inline(r'[http://example.jp/:title=titlestr]') == '<a href="http://example.jp/">titlestr</a>'
    assert parse_inline(r'[http://example.jp/:title=titlestr]::[http://example.com/]') == \
           '<a href="http://example.jp/">titlestr</a>::<a href="http://example.com/">http://example.com/</a>'
    assert parse_inline(r'[mailto:a@example.jp]') == '<a href="mailto:a@example.jp">a@example.jp</a>'
    assert parse_inline(r'[mailto:a@example.jp:title=mail]') == '<a href="mailto:a@example.jp">mail</a>'
    assert parse_inline(r'[image:id=333]') == '<img src="/media/entry/333">'
    assert parse_inline(r'[image:url=http://example.jp/333.jpg]') == '<img src="http://example.jp/333.jpg">'

# def test_mix():
#     assert parse('-li\n++li') == '<ul><li>li</li></ul><ol><li>+li</li></ol>'


if __name__ == '__main__':
    pass
