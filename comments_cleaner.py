#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <un.pogaz@gmail.com>'
__docformat__ = 'restructuredtext en'

# python3 compatibility
from six.moves import range
from six import text_type as unicode

try:
    from qt.core import QWidget
except ImportError:
    from PyQt5.Qt import QWidget

from calibre.gui2.metadata.basic_widgets import CommentsEdit

from .config import KEY, PREFS, CalibreVersions_Bold, CSS_CleanRules
from .XMLentity import parseXMLentity, Entitys
from .common_utils import debug_print, regex

nbsp = Entitys.nbsp.char

# Qt Supported HTML Subset https://doc.qt.io/qt-5/richtext-html-subset.html
TAGS = [
    'a',
    'address',
    'b',
    'big',
    'blockquote',
    'body',
    'br',
    'center',
    'cite',
    'code',
    'dd',
    'dfn',
    'div',
    'dl',
    'dt',
    'em',
    'font',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'head',
    'hr',
    'html',
    'i',
    'img',
    'kbd',
    'meta',
    'li',
    'nobr',
    'ol',
    'p',
    'pre',
    'qt',
    's',
    'samp',
    'small',
    'span',
    'strong',
    'sub',
    'sup',
    'table',
    'tbody',
    'td',
    'tfoot',
    'th',
    'thead',
    'title',
    'tr',
    'tt',
    'u',
    'ul',
    'var',
]

ATTRIBUTES = [
    'id',
    'class',
    'style',
    'align',
    'href',
]


#fix a imcompatibility betwen multiple Calibre version
if CalibreVersions_Bold:
    font_weight = 'font-weight: 700'
else:
    font_weight = 'font-weight: 600'

def FixWeight(text):
    if CalibreVersions_Bold:
        text = regex.loop(r' style="([^"]*)'+font_weight+r'([^"]*)"', r' style="\1font-weight: bold\2"', text)
    return text


# Cleannig based on Calibre 4 and above (QtWebEngine)
def CleanBasic(text):
    
    text = XMLformat(text)
    
    text = parseXMLentity(text)
    
    
    # convert tag
    text = regex.loop(r'<(/?)(?:i|cite|dfn|var)(| [^>]*)>', r'<\1em\2>', text)
    text = regex.loop(r'<(/?)(?:b)(| [^>]*)>',              r'<\1strong\2>', text)
    text = regex.loop(r'<(/?)(?:del|strike)(| [^>]*)>',     r'<\1s\2>', text)
    
    text = regex.loop(r'<(/?)(?:blockquote|dd|dt|pre)(| [^>]*)>', r'<\1p\2>', text)
    
    # convert tag with content
    text = regex.loop(r'<(center)(| [^>]*)>((?:(?!</p>|</div>).)*?)</\1>', r'<p align="center" \2>\3</p>', text)
    
    # invalid tag with content
    text = regex.loop(r'<(script|style|head|title)(| [^>]*)>((?!</p>|</div>).)*?</\1>', r'', text)
    
    # remove invalid tag
    text = regex.loop(r'</?(?!'+ '|'.join(TAGS) +r')\w+(| [^>]*)>', r'', text)
    
    # remove namespaced attribut
    text = regex.loop(r' [\w\-]+:[\w\-]+="[^"]*"', r'', text)
    
    # remove invalid attribut
    text = regex.loop(r' (?!'+ '|'.join(ATTRIBUTES) +r')[\w\-]+="[^"]*"', r'', text)
    
    # filtre not desired tag
    text = regex.loop(r'</?(font|img|html|body|section|form|dl)(| [^>]*)>', r'', text)
    text = regex.loop(r'</?(address|big|code|kbd|meta|nobr|qt|samp|small|tt)(| [^>]*)>', r'', text)
    
    # invalid attribut tag 
    text = regex.loop(r'<((?!a)\w+)(| [^>]*) href="[^"]*"(| [^>]*)>', r'<\1\2\3>', text)
    text = regex.loop(r'<((?!p|div|h\d|li|ol|ul)\w+)(| [^>]*) align="[^"]*"(| [^>]*)>', r'<\1\2\3>', text)
    
    # clean space in attribut
    text = regex.loop(r' ([\w\-]+)="\s+([^"]*)"', r' \1="\2"', text)
    text = regex.loop(r' ([\w\-]+)="([^"]*)\s+"', r' \1="\2"', text)
    
    # management of <br>
    text = regex.loop(r'<(b|h)r[^>]+>', r'<\1r>', text)
    text = regex.loop(r'(\s|'+nbsp+r')+<(b|h)r>', r'<\2r>', text)
    text = regex.loop(r'<(b|h)r>(\s|'+nbsp+r')+', r'<\1r>', text)
    text = regex.loop(r'<((?:em|strong|sup|sub|u|s|span|a)(?:| [^>]*))><(b|h)r>', r'<\2r><\1>', text)
    text = regex.loop(r'<(b|h)r></(em|strong|sup|sub|u|s|span|a)>', r'</\2><\1r>', text)
    
    # empty inline
    inlineSpace = r'<(em|strong|sup|sub|u|s|span|a)(| [^>]*)>\s+</\1>'
    inlineEmpty = r'<(em|strong|sup|sub|u|s|span|a)(| [^>]*)></\1>'
    # same inline
    sameSpace = r'<(em|strong|sup|sub|u|s|span|a)(| [^>]*)>([^<]*)</\1>\s+<\1\2>'
    sameEmpty = r'<(em|strong|sup|sub|u|s|span|a)(| [^>]*)>([^<]*)</\1><\1\2>'
    
    while (regex.search(inlineSpace, text) or
        regex.search(inlineEmpty, text) or
        regex.search(sameSpace, text) or
        regex.search(sameEmpty, text)):
        
        text = regex.loop(inlineSpace, r' ', text)
        text = regex.loop(inlineEmpty, r'', text)
        
        text = regex.loop(sameSpace, r'<\1\2>\3 ', text)
        text = regex.loop(sameEmpty, r'<\1\2>\3', text)
    
    
    # space inline
    text = regex.loop(r'\s+((?:<(em|strong|sup|sub|u|s|span|a)(| [^>]*)>)+)\s+', r' \1', text)
    text = regex.loop(r'\s+((?:</(em|strong|sup|sub|u|s|span|a)>)+)\s+', r'\1 ', text)
    
    #empty block
    text = regex.loop(r'\s*<(p|div|h\d|li|ol|ul)(| [^>]*)>\s*</\1>', r'', text)
    text = regex.loop(r'\s*<(p|div|h\d|li|ol|ul)(| [^>]*)/>', r'', text)
    
    # double space and tab in <p>
    text = regex.loop(r'(<(p|h\d|li)(| [^>]*)>(?:(?!</\2).)*?)(\t|\n|\s{2,})', r'\1 ', text)
    
    # space and <br> before/after <p>
    rgx = r'((?:</?(?:em|strong|sup|sub|u|s|span|a)(?:| [^>]*)>)*)(</?(?:p|div|h\d|li)(?:| [^>]*)>)((?:</?(?:em|strong|sup|sub|u|s|span|a)(?:| [^>]*)>)*)'
    text = regex.loop(r'(?:\s|'+nbsp+r'|<br>)*'+rgx+r'(?:\s|'+nbsp+r'|<br>)+', r'\1\2\3', text)
    text = regex.loop(r'(?:\s|'+nbsp+r'|<br>)+'+rgx+r'(?:\s|'+nbsp+r'|<br>)*', r'\1\2\3', text)
    # restore empty <p>
    text = regex.loop(r'<(p|div|h\d|li)(| [^>]*)>(<(?:em|strong|sup|sub|u|s|span|a)(?:| [^>]*)>)*(?:<br>)*(</(?:em|strong|sup|sub|u|s|span|a)>)*</\1>', r'<\1\2>'+nbsp+r'</\1>', text)
    
    # space with inline before/after <br>
    rgx = r'((?:</(?:em|strong|sup|sub|u|s|span|a)>)*)(<br>)((?:<(?:em|strong|sup|sub|u|s|span|a)(?:| [^>]*)>)*)'
    text = regex.loop(r'(?:\s|'+nbsp+r')*'+rgx+r'(?:\s|'+nbsp+r')+', r'\1\2\3', text)
    text = regex.loop(r'(?:\s|'+nbsp+r')+'+rgx+r'(?:\s|'+nbsp+r')*', r'\1\2\3', text)
    
    # space line return for lists
    text = regex.loop(r'><(p|div|h\d|li|ol|ul)', r'>\n<\1', text)
    text = regex.loop(r'<(ol|ul)(| [^>]*)>\s+<li', r'<\1\2><li', text)
    text = regex.loop(r'</li>\s+</(ol|ul)>', r'</li></\1>', text)
    
    
    # style: del double 
    text = regex.loop(r' style="([^"]*);\s*;([^"]*)"', r' style="\1;\2"', text)
    # style: clean space before : 
    text = regex.loop(r' style="([^"]*)\s+(;|:)([^"]*)"', r' style="\1\2\3"', text)
    # style: clean space after : 
    text = regex.loop(r' style="([^"]*(?:;|:))\s{2,}([^"]*)"', r' style="\1 \2"', text)
    # style: insert space after : 
    text = regex.loop(r' style="([^"]*(?:;|:))([^ ][^"]*)"', r' style="\1 \2"', text)
    
    # style: remove last 
    text = regex.loop(r' style="([^"]*);\s*"', r' style="\1"', text)
    
    
    # remove empty attribut
    text = regex.loop(r' ([\w\-]+)="\s*"', r'', text)
    
    #strip <span>
    text = regex.loop(r'<span\s*>(((?!<span).)*?)</span>', r'\1', text)
    text = regex.loop(r'<span\s*>(((?!<span).)*?(<span[^>]*>((?!</?span).)*?</span>((?!</?span).)*?)+)</span>', r'\1', text)
    
    # empty hyperlink
    text = regex.loop(r'<a\s*>(.*?)</a>', r'\1', text)
    
    
    ## replaces the invalid triple point
    #text = regex.simple(r'\.\s*\.\s*\.', r'…', text)
    text = regex.loop(r'\.\s+\.\s*\.', r'...', text)
    text = regex.loop(r'\.\s*\.\s+\.', r'...', text)
    
    
    text = XMLformat(text)
    
    text = OrderedAttributs(text)
    
    return text

# Ordered the attributs
def OrderedAttributs(text):
    
    for atr in reversed(sorted(ATTRIBUTES)):
        text = regex.loop(r'<(\w+)\s+([\w\-]+=[^>]*)\s+'+atr+r'="([^"]*)"', r'<\1 '+atr+r'="\3" \2', text)
    
    return text

def XMLformat(text):
    # to linux line
    text = regex.loop(r'(\r\n|\r)', r'\n', text)
    text = regex.loop(r'( |\t|\n)+\n', r'\n', text)
    
    # XML format
    text = regex.loop(r'<([^<>]+)(?:\s{2,}|\n|\t)([^<>]+)>', r'<\1 \2>', text)
    text = regex.loop(r'\s+(|/|\?)\s*>', r'\1>', text)
    text = regex.loop(r'<\s*(|/|!|\?)\s+', r'<\1', text)
    
    text = regex.loop(r"='([^']*)'", r'="\1"', text)
    
    return text

qw = QWidget()
CommentsEditor = CommentsEdit(qw)

# passe the comment in the Calibre comment editor
# fix some last errors, better interpolarity Calibre <> plugin
def CalibreFormat(text):
    
    CommentsEditor.current_val = text
    text = CommentsEditor.current_val
    
    return text


# main function
def CleanComment(text):
    
    # if no tag = plain text
    if not regex.search(r'<(?!br)\w+(| [^>]*)/?>', text): #exclude <br> of the test
        text = regex.loop(r'(\r\n|\r)', r'\n', text)
        text = regex.loop(r'<br(| [^>]*)/?>', r'\n', text)
        text = '<div><p>' + regex.loop(r'\n{2,}', r'</p><p>', text) + '</p></div>'
        text = regex.loop(r'\n', r'<br>', text)
        text = regex.loop(r'(<p>|<br>)\s+', r'\1', text)
        text = regex.loop(r'\s+(<p>|<br>)', r'\1', text)
        # Markdown
        if PREFS[KEY.MARKDOWN] == 'try':
            text = CleanMarkdown(text)
        
    
    # double passe
    # Empirical tests have shown that it was necessary for some very rare and specific cases.
    for passe in range(2):
        
        text = CleanBasic(text)
        
        # If <div> is not the racine tag
        if not regex.search(r'<div(| [^>]*)>\s*<(p|div|h\d)(| [^>]*)>', text):
            text = '<div>'+text+'</div>'
        
        # Del empty <div>
        text = regex.loop(r'<div(| [^>]*)>(.*?)<div(| [^>]*)>'+nbsp+r'</div>', r'<div>\2', text)
        
        # Convert <div> after a <div> in <p>
        text = regex.loop(r'<div(| [^>]*)>(.*?)<div(| [^>]*)>(.*?)</div>', r'<div>\2<p\3>\4</p>', text)
        
        # <p> in \s<p>\s
        text = regex.loop(r'<(p|h\d)(| [^>]*)>\s*<(p|h\d)(| [^>]*)>((?:(?!</(?:p|h\d)>).)*?)</\3>\s*</\1>', r'<\3\4>\5</\3>', text)
        # <p> in ??<p>\s
        text = regex.loop(r'<p(| [^>]*)>((?:(?!</p>).)*?)<p(| [^>]*)>((?:(?!</p>).)*?)</p>\s*</p>', r'<p\1>\2</p><p\3>\4</p>', text)
        # <p> in \s<p>??
        text = regex.loop(r'<p(| [^>]*)>\s*<p(| [^>]*)>((?:(?!</p>).)*?)</p>((?:(?!</p>).)*?)</p>', r'<p\2>\3</p><p\1>\4</p>', text)
        # <p> in ??<p>??
        text = regex.loop(r'<p(| [^>]*)>((?:(?!</p>).)*?)<p(| [^>]*)>((?:(?!</p>).)*?)</p>((?:(?!</p>).)*?)</p>', r'<p\1>\2</p><p\3>\4</p><p\1>\5</p>', text)
        
        # Del empty <p> at the start/end
        text = regex.loop(r'<div(?:| [^>]*)>\s*<(p|h\d)(| [^>]*)>'+nbsp+r'</\1>', r'<div>', text)
        text = regex.loop(r'<(p|h\d)(| [^>]*)>'+nbsp+r'</\1>\s*</div>', r'</div>', text)
        
        # Convert empty <table>to empty <p>
        text = regex.loop(r'<table(| [^>]*)>(?:\s*<tbody>)?\s*(?:<tr(?:| [^>]*)>(?:\s*<td(| [^>]*)>\s*</td>)+\s*</tr>)+(?:\s*</tbody>)?\s*</table>', r'<p\1\2>'+nbsp+r'</p>', text)
        
        # Convert <table> with only 1 row and 1 cell to <p>
        text = regex.loop(r'<table(| [^>]*)>(?:\s*<tbody>)?\s*<tr(?:| [^>]*)>\s*<td(| [^>]*)>(.*?)</td>\s*</tr>(?:\s*</tbody>)?\s*</table>', r'<p\1\2>\3</p>', text)
        
        # Merge duplicate attributs
        text = regex.loop(r' (\w+)="([^"]*)"([^>]*) \1="([^"]*)"', r' \1="\2 \4"\3', text)
        
        # Markdown
        if PREFS[KEY.MARKDOWN] == 'always' and passe == 0:
            text = CleanMarkdown(text)
        
        # Multiple Line Return <br><br>
        if PREFS[KEY.DOUBLE_BR] == 'new':
            text = regex.loop(r'<p(| [^>]*)>((?:(?!</p>).)*?)(<br>){2,}', r'<p\1>\2</p><p\1>', text)
        elif PREFS[KEY.DOUBLE_BR] == 'empty':
            text = regex.loop(r'<p(| [^>]*)>((?:(?!</p>).)*?)(<br>){2,}', r'<p\1>\2</p><p\1>'+nbsp+r'</p><p\1>', text)
        
        # Single Line Return <br>
        if PREFS[KEY.SINGLE_BR] == 'space':
            text = regex.loop(r'<p(| [^>]*)>((?:(?!</p>).)*?)<br>((?:(?!</p>).)*?)</p>', r'<p\1>\2 \3</p>', text)
        elif PREFS[KEY.SINGLE_BR] == 'para':
            text = regex.loop(r'<p(| [^>]*)>((?:(?!</p>).)*?)<br>((?:(?!</p>).)*?)</p>', r'<p\1>\2</p><p\1>\3</p>', text)
            text = regex.loop(r'<p(| [^>]*)></p>', r'<p\1>'+nbsp+r'</p>', text)
        
        # Empty paragraph
        if PREFS[KEY.EMPTY_PARA] == 'merge':
            text = regex.loop(r'(?:<p(| [^>]*)>'+nbsp+r'</p>\s*){2,}', r'<p\1>'+nbsp+r'</p>', text)
        elif PREFS[KEY.EMPTY_PARA] == 'del':
            text = regex.loop(r'<p(| [^>]*)>'+nbsp+r'</p>', r'', text)
        
        
        if PREFS[KEY.DEL_FORMATTING]:
            # Remove Formatting
            text = regex.loop(r'<(/?)(i|b|em|strong|sup|sub|u|s|span|a|ol|ul|hr|dl|code)(|\s[^>]*)>', r'', text)
            text = regex.loop(r'<(/?)(h\d|li|pre|dt|dd)(|\s[^>]*)>', r'<\1p>', text)
            text = regex.loop(r'<p\s[^>]*>', r'<p>', text)
            
        else:
            # ID and CLASS attributs
            if 'id' in PREFS[KEY.ID_CLASS]:
                text = regex.loop(r' id="[^"]*"', r'', text)
            if 'class' in PREFS[KEY.ID_CLASS]:
                text = regex.loop(r' class="[^"]*"', r'', text)
            
            
            # Headings
            if PREFS[KEY.HEADINGS] == 'bolder':
                text = regex.loop(r'<(h\d+)([^>]*) style="((?:(?!font-weight)[^"])*)"([^>]*)>', r'<\1\2 style="\3; font-weight: bold"\4>', text)
                text = regex.loop(r'<(h\d+)((?:(?! style=)[^>])*)>', r'<\1\2 style="font-weight: bold;">', text)
            if PREFS[KEY.HEADINGS] == 'conv' or PREFS[KEY.HEADINGS] == 'bolder':
                text = regex.loop(r'<(/?)h\d+(| [^>]*)>', r'<\1p\2>', text)
            
            # Hyperlink
            if PREFS[KEY.KEEP_URL] == 'del':
                text = regex.loop(r'<a(?:| [^>]*)>(.*?)</a>', r'\1', text)
            
            text = CleanBasic(text)
            # style standardization:  insert ; at the end
            text = regex.loop(r' style="([^"]*[^";])"', r' style="\1;"', text)
            # style standardization: insert space at the start
            text = text.replace(' style="', ' style=" ')
            
            
            text = CleanAlign(text)
            
            text = CleanStyle(text)
            
            
            # Del <sup>/<sub> paragraphe
            text = regex.loop(r'<(p|h\d)(| [^>]*)>\s*<su(p|b)>((?:(?:<br>)|[^<>])*?)</su\3>\s*</\1>', r'<\1\2>\4</\1>', text)
            text = regex.loop(r'<(p|h\d)(| [^>]*)>\s*<su(p|b)>((?:(?:<br>)|[^<>])*?)</su\3>\s*<br>\s*<su(p|b)>((?:(?:<br>)|[^<>])*?)</su\5>\s*</\1>', r'<\1\2>\4<br>\6</\1>', text)
            
            # <br> in same tag
            text = regex.loop(r'<((\w+)(?:| [^>]*))>((?:(?:<br>)|[^<>])*?)</\2><br><\1>', r'<\1>\3<br>', text)
            
            # del attibuts for <div> with <p>
            text = regex.loop(r'<div[^>]+>\s*<(p|h\d)', r'<div>\n<\1', text)
            
            # clean text full heading
            text = regex.loop(r'^\s*<div>\s*<h(\d)(| [^>]*)>((?:(?:<br>)|[^<>])*?)</h\1>\s*</div>\s*$', r'<div><p\2>\3</p></div>', text)
            
            # clean text full bold
            text = regex.loop(r'^\s*<div>\s*<p([^>]*?)font-weight:\s*\d+([^>]*?)>((?:(?:<br>)|[^<>])*?)</p>\s*</div>\s*$', r'<div><p\1\2>\3</p></div>', text)
            
            text = regex.loop(r'^\s*<div>\s*<p([^>]*?)><strong([^>]*?)>((?:(?:<br>)|[^<>])*?)</strong></p>\s*</div>\s*$', r'<div><p\1><span\2>\3</span></p></div>', text)
            text = regex.loop(r'^\s*<div>\s*<p([^>]*?)><strong([^>]*?)>((?:(?:<br>)|[^<>])*?)</strong><br><strong([^>]*?)>((?:(?:<br>)|[^<>])*?)</strong></p>\s*</div>\s*$', r'<div><p\1><span\2>\3</span><br><span\4>\5</span></p></div>', text)
            
            text = regex.loop(r'^\s*<div>\s*<p([^>]*?)><(\w+)([^>]*?)font-weight:\s*\d+([^>]*?)>((?:(?:<br>)|[^<>])*?)</\2></p>\s*</div>\s*$',
                r'<div><p\1><\2\3\4>\5</\2></p></div>', text)
            text = regex.loop(r'^\s*<div>\s*<p([^>]*?)font-weight:\s*\d+([^>]*?)><(\w+)([^>]*?)>((?:(?:<br>)|[^<>])*?)</\3></p>\s*</div>\s*$',
                r'<div><p\1\2><\3\4>\5</\3></p></div>', text)
        
        
        text = CleanBasic(text)
        #
    
    text = FixWeight(text)
    
    text = CalibreFormat(text)
    
    # del align for list <li>
    if PREFS[KEY.LIST_ALIGN] == 'del':
        text = regex.loop(r'<(ol|ul|li)([^>]*) align="[^"]*"', r'<\1\2', text)
    
    return text



def CleanAlign(text):
    
    text = OrderedAttributs(text)
    
    # set align
    if PREFS[KEY.FORCE_JUSTIFY] == 'del':
        # del align
        text = regex.loop(r' align="[^"]*"', r'', text)
        
    else: # empty / all / none
        
        # insert align left for all
        text = regex.simple(r'<(p|div|li|h1|h2|h3|h4|h5|h6)', r'<\1 align="left"', text)
        
        # delete align left if another exist
        text = regex.loop(r'<(p|div|li|h1|h2|h3|h4|h5|h6) align="left"( align="[^"]*")', r'<\1\2', text)
        
        # swap text-align to align
        text = regex.loop(r' align="[^"]*"([^>]*) style="([^"]*) text-align:\s*([^;]*)\s*;([^"]*)"', r' align="\3"\1 style="\2\4"', text)
        
        # clean space in attribut
        text = regex.loop(r' align="\s+([^"]*)"', r' align="\1"', text)
        text = regex.loop(r' align="([^"]*)\s+"', r' align="\1"', text)
        
        # align valide value
        text = regex.loop(r' align="justify-all"', r' align="justify"', text)
        text = regex.loop(r' align="(?!left|justify|center|right)[^"]*"', r' align="left"', text)
        
        # apply cascading heritage for list
        text = regex.loop(r'<(ol|ul) align="left"', r'<\1', text)
        text = regex.loop(r'<(ol|ul) align="([^"]*)"([^>]*)>((?:(?!</\1>).)*)<li align="left"', r'<\1 align="\2"\3>\4<li align="\2"', text)
        text = regex.loop(r'<(ol|ul) align="([^"]*)"', r'<\1', text)
        
        # set align prefs
        if PREFS[KEY.FORCE_JUSTIFY] == 'empty':
            text = regex.loop(r' align="left"', r' align="justify"', text)
        elif PREFS[KEY.FORCE_JUSTIFY] == 'all':
            text = regex.loop(r' align="(left|center|right)"', r' align="justify"', text)
        #else: 'none'
        
    
    # del text-align
    text = regex.loop(r' style="([^"]*) text-align:([^;]*);([^"]*)"', r' style="\1\3"', text)
    
    # del justify for <h1>
    text = regex.loop(r'<(h\d) align="justify"', r'<\1', text)
    
    
    # del text-align left (default value)
    text = regex.loop(r' align="left"', r'', text)
    
    return text


def CleanStyle(text):
    
    text = OrderedAttributs(text)
    
    text = regex.loop(r' x-style="[^"]*"', r'', text)
    text = text.replace(' style="', ' x-style="" style=" ')
    
    rule_all = 'text-align font-weight font-style text-decoration'
    rule_tbl = CSS_CleanRules(rule_all +' '+ PREFS[KEY.CSS_KEEP]).split(' ')
    
    for rule in rule_tbl:
        text = regex.loop(r' x-style="([^"]*)" style="([^"]*) '+rule+r':\s*([^;]*?)\s*;([^"]*)"', r' x-style="\1 '+rule+r': \3;" style="\2 \4"', text)
    
    text = regex.loop(r' x-style="([^"]*)" style="[^"]*"', r' style="\1"', text)
    text = regex.loop(r' x-style="[^"]*"', r'', text)
    
    
    # font-weight
    text = regex.loop(r' style="([^"]*) font-weight: (?!bold|bolder|\d+)[^;]*;([^"]*)"', r' style="\1\2"', text)
    text = regex.loop(r' style="([^"]*) font-weight: (bold|bolder);([^"]*)"', r' style="\1 '+font_weight+r';\3"', text)
    text = regex.loop(r' style="([^"]*) font-weight: (\d{4,})(?:\.\d+)?;([^"]*)"', r' style="\1 font-weight: 900;\3"', text)
    text = regex.loop(r' style="([^"]*) font-weight: (\d{1,2})(?:\.\d+)?;([^"]*)"', r' style="\1 font-weight: 100;\3"', text)
    text = regex.simple(r' style="([^"]*) font-weight: (\d{3})(?:\.\d+)?;([^"]*)"', r' style="\1 font-weight: \2;\3"', text)
    
    if PREFS[KEY.FONT_WEIGHT] == 'trunc' or PREFS[KEY.FONT_WEIGHT] == 'bold':
        
        text = regex.loop(r' style="([^"]*) font-weight: (?P<name>\d\d)0;([^"]*)"', r' style="\1 font-weight: \g<name>1;\3"', text)
        regx = r' style="([^"]*) font-weight: (?P<name>\d\d[1-9]);([^"]*)"'
        while regex.search(regx, text):
            
            m = regex.search(regx, text)
            d = m.group('name')
            rpl = regex.loop(regx, r' style="\1 font-weight: '+str(int(round(int(d),-2)))+r';\3"', m.group(0))
            text = text.replace(m.group(0), rpl)
    
    if PREFS[KEY.FONT_WEIGHT] == 'bold':
        text = regex.loop(r' style="([^"]*) font-weight: [5-9]\d\d;([^"]*)"', r' style="\1 font-weight: xxx;\2"', text)
        text = regex.loop(r' style="([^"]*) font-weight: xxx;([^"]*)"', r' style="\1 '+font_weight+r';\2"', text)
        text = regex.loop(r' style="([^"]*) font-weight: [1-4]\d\d;([^"]*)"', r' style="\1\2"', text)
        
    elif PREFS[KEY.FONT_WEIGHT] == 'del':
        text = regex.loop(r'<(/?)strong(| [^>]*)>', r'<\1span\2>', text)
        text = regex.loop(r' style="([^"]*) font-weight:[^;]*;([^"]*)"', r' style="\1\2"', text)
    
    
    # font-style
    text = regex.loop(r' style="([^"]*) font-style: (?!oblique|italic)[^;]*;([^"]*)"', r' style="\1\2"', text)
    if PREFS[KEY.DEL_ITALIC]:
        text = regex.loop(r'<(/?)em(| [^>]*)>', r'<\1span\2>', text)
        text = regex.loop(r' style="([^"]*) font-style:[^;]*;([^"]*)"', r' style="\1\2"', text)
    else:
        text = regex.loop(r' style="([^"]*) font-style: (oblique(?:\s+\d+deg)?);([^"]*)"', r' style="\1 font-style: italic;\3"', text)
    
    
    # text-decoration
    text = regex.loop(r' style="([^"]* text-decoration:[^;]*) (?:none|blink|overline|inherit|initial|unset)([^;]*;[^"]*)"', r' style="\1\2"', text)
    
    if PREFS[KEY.DEL_UNDER]:
        text = regex.loop(r'<(/?)u(| [^>]*)>', r'<\1span\2>', text)
        text = regex.loop(r' style="([^"]* text-decoration:[^;]*) underline([^;]*;[^"]*)"', r' style="\1\2"', text)
    if PREFS[KEY.DEL_STRIKE]:
        text = regex.loop(r'<(/?)s(| [^>]*)>', r'<\1span\2>', text)
        text = regex.loop(r' style="([^"]* text-decoration:[^;]*) line-through([^;]*;[^"]*)"', r' style="\1\2"', text)
    
    text = regex.loop(r'<(p|h\d)(| [^>]*)( style="[^"]* text-decoration:[^;]*) underline([^;]*;[^"]*"[^>]*)>(.*?)</\1>',    r'<\1\2\3\4><u>\5</u></\1>', text)
    text = regex.loop(r'<(p|h\d)(| [^>]*)( style="[^"]* text-decoration:[^;]*) line-through([^;]*;[^"]*"[^>]*)>(.*?)</\1>', r'<\1\2\3\4><s>\5</s></\1>', text)
    
    text = regex.loop(r' style="([^"]*) text-decoration:\s*;([^"]*)"', r' style="\1\2"', text)
    
    
    ######
    return text


# Try to convert Markdown to HTML
def CleanMarkdown(text): # key word: TRY!
    # image
    text = regex.loop(r'!\[((?:(?!<br>|</p>).)*?)\]\(((?:(?!<br>|</p>).)*?)\)', r'<img alt"\1" src="\2">', text)
    # hyperlink
    text = regex.loop( r'\[((?:(?!<br>|</p>).)*?)\]\(((?:(?!<br>|</p>).)*?)\)', r'<a href="\2">\1</a>', text)
    
    # heading 1, 2
    for h, n in [('=', '1'),('-', '2')]:
        text = regex.loop(r'(<br>|</p><p>)(.*?)(<br>|</p><p>)'+h+r'{2,}(<br>|</p><p>)', r'</p><h'+n+r'>\2</h'+n+r'><p>', text)
        text = regex.loop(r'(<br>|</p><p>)(.*?)(<br>|</p><p>)'+h+r'{2,}(</p>)'        , r'</p><h'+n+r'>\2</h'+n+r'>'   , text)
        text = regex.loop(         r'(<p>)(.*?)(<br>|</p><p>)'+h+r'{2,}(<br>|</p><p>)',     r'<h'+n+r'>\2</h'+n+r'><p>', text)
        text = regex.loop(         r'(<p>)(.*?)(<br>|</p><p>)'+h+r'{2,}(</p>)'        ,     r'<h'+n+r'>\2</h'+n+r'>'   , text)
    
    # heading
    for h in range(1, 6):
        h = str(h)
        text = regex.loop(r'(<br>|</p><p>)#{'+h+r'}\s+(.*?)(<br>|</p><p>)', r'</p><h'+h+r'>\2</h'+h+r'><p>', text)
        text = regex.loop(r'(<br>|</p><p>)#{'+h+r'}\s+(.*?)(</p>)'        , r'</p><h'+h+r'>\2</h'+h+r'>'   , text)
        text = regex.loop(         r'(<p>)#{'+h+r'}\s+(.*?)(<br>|</p><p>)',     r'<h'+h+r'>\2</h'+h+r'><p>', text)
        text = regex.loop(         r'(<p>)#{'+h+r'}\s+(.*?)(</p>)'        ,     r'<h'+h+r'>\2</h'+h+r'>',    text)
    
    
    # u liste
    text = regex.loop(r'(<br>|</p><p>)(?:\*|-)\s+((?:(?!<br>|</p>|</li>).)*?)(<br>|</p><p>)', r'</p><ul><li>\2</li></ul><p>', text)
    text = regex.loop(r'(<br>|</p><p>)(?:\*|-)\s+((?:(?!<br>|</p>|</li>).)*?)(</p>)'        , r'</p><ul><li>\2</li></ul>'   , text)
    text = regex.loop(         r'(<p>)(?:\*|-)\s+((?:(?!<br>|</p>|</li>).)*?)(<br>|</p><p>)'    , r'<ul><li>\2</li></ul><p>', text)
    text = regex.loop(         r'(<p>)(?:\*|-)\s+((?:(?!<br>|</p>|</li>).)*?)(</p>)'            , r'<ul><li>\2</li></ul>'   , text)
    text = regex.loop(r'</li></ul><ul><li>', r'</li><li>', text)
    
    # o liste
    text = regex.loop(r'(<br>|</p><p>)\d{1,2}(?:\)|\.)\s+((?:(?!<br>|</p>|</li>).)*?)(<br>|</p><p>)', r'</p><ol><li>\2</li></ol><p>', text)
    text = regex.loop(r'(<br>|</p><p>)\d{1,2}(?:\)|\.)\s+((?:(?!<br>|</p>|</li>).)*?)(</p>)'        , r'</p><ol><li>\2</li></ol>'   , text)
    text = regex.loop(         r'(<p>)\d{1,2}(?:\)|\.)\s+((?:(?!<br>|</p>|</li>).)*?)(<br>|</p><p>)',     r'<ol><li>\2</li></ol><p>', text)
    text = regex.loop(         r'(<p>)\d{1,2}(?:\)|\.)\s+((?:(?!<br>|</p>|</li>).)*?)(</p>)'        ,     r'<ol><li>\2</li></ol>'   , text)
    text = regex.loop(r'</li></ol><ol><li>', r'</li><li>', text)
    
    # <hr>
    text = regex.loop(r'(<br>|</p><p>)(?:-|\*|_){3,}(<br>|</p><p>)', r'</p><hr><p>', text)
    text = regex.loop(r'(<br>|</p><p>)(?:-|\*|_){3,}(</p>)'        , r'</p><hr>'   , text)
    text = regex.loop(         r'(<p>)(?:-|\*|_){3,}(<br>|</p><p>)', r'<hr><p>'    , text)
    
    # bold
    text = regex.loop(r'([^\\])((?:_|\*){2})((?:(?!<br>|</p>).)*?[^\\])\2', r'\1<strong>\3</strong>', text)
    # italic
    text = regex.loop(r'([^\\])((?:_|\*){1})((?:(?!<br>|</p>).)*?[^\\])\2', r'\1<em>\3</em>', text)
    
    #
    text = regex.loop(r'\\(_|\*)', r'\1', text)
    
    return text


def main():
    print("I reached main when I should not have\n")
    return -1

if __name__ == "__main__":
    sys.exit(main())
