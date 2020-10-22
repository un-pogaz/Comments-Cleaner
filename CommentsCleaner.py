#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <>'
__docformat__ = 'restructuredtext en'

import sys, os

from calibre_plugins.comments_cleaner.config import KEY, PREFS
from calibre_plugins.comments_cleaner.XMLentity import parseXMLentity
from calibre_plugins.comments_cleaner.common_utils import debug_print, debug_text, RegexSimple, RegexSearch, RegexLoop, CSS_CleanRules, strtobool

nbsp = '\u00A0'

def CleanBasic(text):
	
	text = RegexLoop(r'(&#x202F;|&#8239;)', '\u202F', text);
	text = RegexLoop(r'(&#xA0;|&#160;|&nbsp;)', '\u00A0', text);
	
	text = XMLformat(text);
	
	text = RegexLoop(r'<(/?)i(| [^>]*)>', r'<\1em\2>', text);
	text = RegexLoop(r'<(/?)b(| [^>]*)>', r'<\1strong\2>', text);
	text = RegexLoop(r'<(/?)del(| [^>]*)>', r'<\1s\2>', text);
	text = RegexLoop(r'<(/?)strike(| [^>]*)>', r'<\1s\2>', text);
	
	text = RegexLoop(r'<(/?)dd(| [^>]*)>', r'<\1p\2>', text);
	text = RegexLoop(r'<(/?)dt(| [^>]*)>', r'<\1p\2>', text);
	
	# invalid tag
	text = RegexLoop(r'</?(dl|font|abbr|html|body|img|meta|link|section|form)(| [^>]*)>', r'', text);
	
	text = RegexLoop(r'<script(| [^>]*)>((?!</p>|</div>).)*?</script>', r'', text);
	
	# remove namespaced attribut
	text = RegexLoop(r' [\w\-]+:[\w\-]+="[^"]*"', r'', text);
	
	# clean space in attribut
	text = RegexLoop(r' ([\w\-]+)="\s+([^"]*)"', r' \1="\2"', text);
	text = RegexLoop(r' ([\w\-]+)="([^"]*)\s+"', r' \1="\2"', text);
	
	# management of <br>
	text = RegexLoop(r'<(b|h)r[^>]+>', r'<\1r>', text);
	text = RegexLoop(r'(\s|'+nbsp+r')+<(b|h)r>', r'<\2r>', text);
	text = RegexLoop(r'<(b|h)r>(\s|'+nbsp+r')+', r'<\1r>', text);
	text = RegexLoop(r'<((?:em|strong|sup|sub|u|s|span|a)(?:| [^>]*))><(b|h)r>', r'<\2r><\1>', text);
	text = RegexLoop(r'<(b|h)r></(em|strong|sup|sub|u|s|span|a)>', r'</\2><\1r>', text);
	
	# empty inline
	inlineSpace = r'<(em|strong|sup|sub|u|s|span|a)(| [^>]*)>\s+</\1>';
	inlineEmpty = r'<(em|strong|sup|sub|u|s|span|a)(| [^>]*)></\1>';
	# same inline
	sameSpace = r'<(em|strong|sup|sub|u|s|span|a)(| [^>]*)>([^<]*)</\1>\s+<\1\2>';
	sameEmpty = r'<(em|strong|sup|sub|u|s|span|a)(| [^>]*)>([^<]*)</\1><\1\2>';
	
	while (RegexSearch(inlineSpace, text) or
		RegexSearch(inlineEmpty, text) or
		RegexSearch(sameSpace, text) or
		RegexSearch(sameEmpty, text)):
		
		text = RegexLoop(inlineSpace, r' ', text);
		text = RegexLoop(inlineEmpty, r'', text);
		
		text = RegexLoop(sameSpace, r'<\1\2>\3 ', text);
		text = RegexLoop(sameEmpty, r'<\1\2>\3', text);
	
	
	# space inline
	text = RegexLoop(r'\s+((?:<(em|strong|sup|sub|u|s|span|a)(| [^>]*)>)+)\s+', r' \1', text);
	text = RegexLoop(r'\s+((?:</(em|strong|sup|sub|u|s|span|a)>)+)\s+', r'\1 ', text);
	
	
	#empty block
	text = RegexLoop(r'\s*<(p|div|h\d|li|ol|ul)(| [^>]*)>\s*</\1>', r'', text);
	text = RegexLoop(r'\s*<(p|div|h\d|li|ol|ul)(| [^>]*)/>', r'', text);
	
	
	# double space and tab in <p>
	text = RegexLoop(r'(<(p|h\d)(| [^>]*)>(?:(?!</\2).)*?)(\t|\n| {2,})', r'\1 ', text);
	
	# space and <br> before/after <p>
	rgx = r'((?:</?(?:em|strong|sup|sub|u|s|span|a)(?:| [^>]*)>)*)(</?(?:p|div|h\d|li)(?:| [^>]*)>)((?:</?(?:em|strong|sup|sub|u|s|span|a)(?:| [^>]*)>)*)'
	text = RegexLoop(r'(?:\s|'+nbsp+r'|<br>)*'+rgx+r'(\s|'+nbsp+r'|<br>)+', r'\1\2\3', text);
	text = RegexLoop(r'(?:\s|'+nbsp+r'|<br>)+'+rgx+r'(\s|'+nbsp+r'|<br>)*', r'\1\2\3', text);
	# restore empty <p>
	text = RegexLoop(r'<(p|div|h\d|li)(| [^>]*)>(<(?:em|strong|sup|sub|u|s|span|a)(?:| [^>]*)>)*(?:<br>)*(</(?:em|strong|sup|sub|u|s|span|a)>)*</\1>', r'<\1\2>'+nbsp+r'</\1>', text);
	
	text = RegexLoop(r'><(p|div|h\d|li|ol|ul)', r'>\n<\1', text);
	
	
	# style: del double ;
	text = RegexLoop(r' style="([^"]*);\s+;([^"]*)"', r' style="\1;\2"', text);
	# style: clean space before : ;
	text = RegexLoop(r' style="([^"]*)\s+(;|:)([^"]*)"', r' style="\1\2\3"', text);
	# style: clean space after : ;
	text = RegexLoop(r' style="([^"]*(?:;|:))\s{2,}([^"]*)"', r' style="\1 \2"', text);
	# style: insert space after : ;
	text = RegexLoop(r' style="([^"]*(?:;|:))([^ "])', r' style="\1 \2', text);
	
	# style: remove last ;
	text = RegexLoop(r' style="([^"]*);\s*"', r' style="\1"', text);
	
	
	# remove empty attribut
	text = RegexLoop(r' ([\w\-]+)="\s*"', r'', text);
	
	#strip span
	text = RegexLoop(r'<span\s*>((?:(?!<span).)*?)</span>', r'\1', text);
	
	
	# replaces the invalid triple point
	#text = RegexSimple(r'\.\s*\.\s*\.', r'…', text);
	text = RegexLoop(r'\.\s+\.\s*\.', r'...', text);
	text = RegexLoop(r'\.\s*\.\s+\.', r'...', text);
	
	text = XMLformat(text);
	
	return text;

def XMLformat(text):
	# to linux line
	text = text.replace('\r\n', '\n').replace('\r', '\n');
	text = RegexLoop(r'( |\t|\n)+\n', '\n', text);
	
	# XML format
	text = RegexLoop(r'<([^<>]+)(?:\s{2,}|\n|\t)([^<>]+)>', r'<\1 \2>', text);
	text = RegexLoop(r'\s+(|/|\?)\s*>', r'\1>', text);
	text = RegexLoop(r'<\s*(|/|!|\?)\s+', r'<\1', text);
	
	text = RegexLoop(r"='([^']*)'", r'="\1"', text);
	
	return text;


def CleanHTML(text):
	
	# if no tag = plain text
	if not(RegexSearch(r'<(p|div)(| [^>]*)>', text)):
		text = text.replace('\r\n', '\n').replace('\r', '\n');
		text = '<div><p>' + RegexLoop(r'\n{2,}',r'</p><p>', text) + '</p></div>';
		text = RegexLoop(r'\n',r'<br>', text);
		text = RegexLoop(r'(<p>|<br>)\s+', r'\1', text);
		text = RegexLoop(r'\s+(<p>|<br>)', r'\1', text);
		# Markdown
		if PREFS[KEY.MARKDOWN] == 'try':
			text = CleanMarkdown(text);
		
	text = parseXMLentity(text);
	
	# double parse
	# Empirical tests have shown that it was necessary for some very rare and specific cases.
	for p in range(2):
		
		text = CleanBasic(text);
		
		# If <div> is not the racine tag
		if not RegexSearch(r'<div(| [^>]*)>\s*<(p|div|h\d)(| [^>]*)>', text):
			text = '<div>'+text+'</div>';
		
		# Del empty <div>
		text = RegexLoop(r'<div(| [^>]*)>(.*?)<div(| [^>]*)>'+nbsp+r'</div>',r'<div>\2', text);
		
		# Convert <div> after a <div> in <p>
		text = RegexLoop(r'<div(| [^>]*)>(.*?)<div(| [^>]*)>(.*?)</div>',r'<div>\2<p\3>\4</p>', text);
		
		# <p> in <p>
		text = RegexLoop(r'<(p|h\d)(| [^>]*)>\s*<(p|h\d)(| [^>]*)>(.*?)</\3>\s*</\1>',r'<\3\4>\5</\3>', text);
		
		# <p> in <p>
		text = RegexLoop(r'<p(| [^>]*)>((?:(?!</p>).)*?)<p(| [^>]*)>(.*?)</p>\s*</p>',r'<p\1>\2</p><p\3>\4</p>', text);
		
		# Del empty <p> at the start/end
		text = RegexLoop(r'<div(?:| [^>]*)>\s*<(p|h\d)(| [^>]*)>'+nbsp+r'</\1>',r'<div>', text);
		text = RegexLoop(r'<(p|h\d)(| [^>]*)>'+nbsp+r'</\1>\s*</div>',r'</div>', text);
		
		# Multiple Line Return
		if PREFS[KEY.DOUBLE_BR] == 'new':
			text = RegexLoop(r'<p(| [^>]*)>((?:(?!</p>).)*?)(<br>){2,}', r'<p\1>\2</p><p\1>', text);
		elif PREFS[KEY.DOUBLE_BR] == 'empty':
			text = RegexLoop(r'<p(| [^>]*)>((?:(?!</p>).)*?)(<br>){2,}', r'<p\1>\2</p><p\1>'+nbsp+r'</p><p\1>', text);
		
		# Empty paragraph
		if PREFS[KEY.EMPTY_PARA] == 'merge':
			text = RegexLoop(r'(?:<p(| [^>]*)>'+nbsp+r'</p>\s*){2,}', r'<p\1>'+nbsp+r'</p>', text);
		elif PREFS[KEY.EMPTY_PARA] == 'del':
			text = RegexLoop(r'<p(| [^>]*)>'+nbsp+r'</p>', r'', text);
		
		# Markdown
		if PREFS[KEY.MARKDOWN] == 'always':
			text = CleanMarkdown(text);
		
		# Formatting
		if strtobool(PREFS[KEY.FORMATTING]):
			return RemoveFormatting(text);
		
		
		# ID and CLASS attributs
		if PREFS[KEY.ID_CLASS] == 'id_class' or PREFS[KEY.ID_CLASS] == 'id':
			text = RegexLoop(r' id="[^"]*"', r'', text);
		if PREFS[KEY.ID_CLASS] == 'id_class' or PREFS[KEY.ID_CLASS] == 'class':
			text = RegexLoop(r' class="[^"]*"', r'', text);
		
		text = OrderedAttributs(text);
		
		# Headings
		if PREFS[KEY.HEADINGS] == 'bolder':
			text = RegexLoop(r'<(h\d+)([^>]*) style="((?:(?!font-weight)[^"])*)"([^>]*)>', r'<\1\2 style="\3;font-weight: bold;"\4>', text);
			text = RegexLoop(r'<(h\d+)((?:(?! style=)[^>])*)>', r'<\1\2 style="font-weight: bold;">', text);
		if PREFS[KEY.HEADINGS] == 'conv' or PREFS[KEY.HEADINGS] == 'bolder':
			text = RegexLoop(r'<(/?)h\d+(| [^>]*)>', r'<\1p\2>', text);
		
		# Hyperlink
		if PREFS[KEY.KEEP_URL] == 'del':
			text = RegexLoop(r'<a(?:| [^>]*)>(.*?)</a>', r'\1', text);
		
		# remove empty hyperllink
		text = RegexLoop(r'<a\s*>(.*?)</a>', r'\1', text);
		
		
		# style standardization:  insert ; at the end
		text = RegexLoop(r' style="([^"]*[^";])"', r' style="\1;"', text);
		# style standardization: insert space at the start
		text = text.replace(' style="', ' style=" ');
		
		
		text = CleanAlign(text);
		
		text = CleanStyle(text);
		
		
		text = OrderedAttributs(text);
		
		# del attibuts for <div> with <p>
		text = RegexLoop(r'<div[^>]+>\s*<(p|h\d)', r'<div>\n<\1', text);
		
		#
		text = CleanBasic(text);
		
	
	return text;


# Ordered the attributs
def OrderedAttributs(text):
	
	attributs = 'align|style|class|id|href';
	
	text = RegexLoop(r' (?!'+attributs+r')[\w\-]+="[^"]*"', r'', text);
	
	for attribut in reversed(sorted(attributs.split('|'))):
		text = RegexLoop(r'<(\w+)\s+([\w\-]+=[^>]*)\s+'+attribut+r'="([^"]*)"', r'<\1 '+attribut+r'="\3" \2', text);
	
	return text;

def CleanAlign(text):
	
	text = OrderedAttributs(text);
	
	# set align
	if PREFS[KEY.FORCE_JUSTIFY] == 'del':
		# del align
		text = RegexLoop(r' align="[^"]*"', r'', text);
		
	else: # empty / all / none
		
		tags = 'p|div|h1|h2|h3|h4|h5|h6';
		
		# insert align left for all
		for tag in tags.split('|'):
			text = text.replace('<'+tag, '<'+tag+' align="left"');
		
		# delete align left if another exist
		text = RegexLoop(r'<('+tags+r') align="left"( align="[^"]*")', r'<\1\2', text);
		
		# swap text-align to align
		text = RegexLoop(r' align="[^"]*"([^>]*) style="([^"]*) text-align:\s*([^;]*)\s*;([^"]*)"', r' align="\3"\1 style="\2\4"', text);
		
		# clean space in attribut
		text = RegexLoop(r' align="\s+([^"]*)"', r' align="\1"', text);
		text = RegexLoop(r' align="([^"]*)\s+"', r' align="\1"', text);
		
		# align valide value
		text = RegexLoop(r' align="(?!left|justify|center|right)[^"]*"', r' align="left"', text);
		
		# set align prefs
		if PREFS[KEY.FORCE_JUSTIFY] == 'empty':
			text = RegexLoop(r' align="left"', r' align="justify"', text);
		elif PREFS[KEY.FORCE_JUSTIFY] == 'all':
			text = RegexLoop(r' align="(left|center|right)"', r' align="justify"', text);
		#else: 'none'
		
	
	# del text-align
	text = RegexLoop(r' style="([^"]*) text-align:\s*([^;]*)\s*;([^"]*)"', r' style="\1\3"', text);
	
	# del align for <li>
	text = RegexLoop(r'<(ol|ul|li) align="[^"]*"', r'<\1', text);
	
	# del justify for <h1>
	text = RegexLoop(r'<(h\d) align="justify"', r'<\1', text);
	
	
	# del text-align left (default value)
	text = RegexLoop(r' align="left"', r'', text);
	
	return text;


def CleanStyle(text):
	
	text = OrderedAttributs(text);
	
	text = RegexLoop(r' x-style="[^"]*"', r'', text);
	text = text.replace(' style="',' x-style="" style=" ');
	
	rule_all = 'text-align font-weight font-style text-decoration';
	rule_tbl = CSS_CleanRules(rule_all +' '+ PREFS[KEY.CSS_KEEP]).split(' ');
	
	for rule in rule_tbl:
		text = RegexLoop(r' x-style="([^"]*)" style="([^"]*) '+rule+r':\s*([^;]*)\s*;([^"]*)"', r' x-style="\1 '+rule+r': \3;" style="\2 \4"', text);
	
	text = RegexLoop(r' x-style="([^"]*)" style="[^"]*"', r' style="\1"', text);
	text = RegexLoop(r' x-style="[^"]*"', r'', text);
	
	
	# font-weight
	text = RegexLoop(r' style="([^"]*) font-weight:\s*(normal|lighter|inherit|initial|unset)\s*;([^"]*)"', r' style="\1\3"', text);
	text = RegexLoop(r' style="([^"]*) font-weight:\s*(bold|bolder)\s*;([^"]*)"', r' style="\1font-weight: 600\3"', text);
	text = RegexLoop(r' style="([^"]*) font-weight:\s*(\d){4,}(?:\.\d+)?\s*;([^"]*)"', r' style="\1font-weight: 900;\3"', text);
	text = RegexLoop(r' style="([^"]*) font-weight:\s*(\d){1,2}(?:\.\d+)?\s*;([^"]*)"', r' style="\1font-weight: 100;\3"', text);
	
	if PREFS[KEY.FONT_WEIGHT] == 'bold':
		text = RegexLoop(r' style="([^"]*) font-weight:\s*[5-9]\d\d(?:\.\d+)?\s*;([^"]*)"', r' style="\1 font-weight: xxx;\2"', text);
		text = RegexLoop(r' style="([^"]*) font-weight:\s*xxx\s*;([^"]*)"', r' style="\1 font-weight: 600;\2"', text);
		text = RegexLoop(r' style="([^"]*) font-weight:\s*[1-4]\d\d(?:\.\d+)?\s*;([^"]*)"', r' style="\1\2"', text);
	elif PREFS[KEY.FONT_WEIGHT] == 'trunc':
		text = RegexLoop(r' style="([^"]*) font-weight:\s*(?P<name>\d)\d\d(?:\.\d+)?\s*;([^"]*)"', r' style="\1 font-weight: \g<name>xx;\3"', text);
		text = RegexLoop(r' style="([^"]*) font-weight:\s*(?P<name>\d)xx\s*;([^"]*)"', r' style="\1 font-weight: \g<name>00;\3"', text);
	elif PREFS[KEY.FONT_WEIGHT] == 'del':
		text = RegexLoop(r'<(/?)strong(| [^>]*)>', r'<\1span\2>', text);
		text = RegexLoop(r' style="([^"]*) font-weight:\s*[^;]*\s*;([^"]*)"', r' style="\1\2"', text);
	
	# font-style
	text = RegexLoop(r' style="([^"]*) font-style:\s*(normal|inherit|initial|unset)\s*;([^"]*)"', r' style="\1\3"', text);
	if strtobool(PREFS[KEY.DEL_ITALIC]):
		text = RegexLoop(r'<(/?)em(| [^>]*)>', r'<\1span\2>', text);
		text = RegexLoop(r' style="([^"]*) font-style:\s*[^;]*\s*;([^"]*)"', r' style="\1\2"', text);
	else:
		text = RegexLoop(r' style="([^"]*) font-style:\s*(oblique(?:\s+\d+deg)?)\s*;([^"]*)"', r' style="\1 font-style: italic;\3"', text);
	
	
	# text-decoration
	text = RegexLoop(r' style="([^"]* text-decoration:\s*[^;]*)(?:none|blink|overline|inherit|initial|unset)([^;]*\s*;[^"]*)"', r' style="\1\2"', text);
	
	if strtobool(PREFS[KEY.DEL_UNDER]):
		text = RegexLoop(r'<(/?)u(| [^>]*)>', r'<\1span\2>', text);
		text = RegexLoop(r' style="([^"]* text-decoration:\s*[^;]*)underline([^;]*\s*;[^"]*)"', r' style="\1\2"', text);
	if strtobool(PREFS[KEY.DEL_STRIKE]):
		text = RegexLoop(r'<(/?)s(| [^>]*)>', r'<\1span\2>', text);
		text = RegexLoop(r' style="([^"]* text-decoration:\s*[^;]*)line-through([^;]*\s*;[^"]*)"', r' style="\1\2"', text);
	
	text = RegexLoop(r'<(p|h\d)(| [^>]*)( style="[^"]* text-decoration:\s*[^;]*)underline([^;]*\s*;[^"]*"[^>]*)>(.*?)</\1>',    r'<\1\2\3\4><u>\5</u></\1>', text);
	text = RegexLoop(r'<(p|h\d)(| [^>]*)( style="[^"]* text-decoration:\s*[^;]*)line-through([^;]*\s*;[^"]*"[^>]*)>(.*?)</\1>', r'<\1\2\3\4><s>\5</s></\1>', text);
	
	text = RegexLoop(r' style="([^"]*) text-decoration:\s*;([^"]*)"', r' style="\1\2"', text);
	
	#
	
	return text;


# Try to convert Markdown to HTML
def CleanMarkdown(text): # key word: TRY!
	# image
	text = RegexLoop(r'!\[((?:(?!<br>|</p>).)*?)\]\(((?:(?!<br>|</p>).)*?)\)',r'<img alt"\1" src="\2">', text);
	# hyperlink
	text = RegexLoop( r'\[((?:(?!<br>|</p>).)*?)\]\(((?:(?!<br>|</p>).)*?)\)',r'<a href="\2">\1</a>', text);
	
	# heading 1 & 2
	for h, n in [('=', '1'),('-', '2')]:
		text = RegexLoop(r'(<br>|</p><p>)(.*?)(<br>|</p><p>)'+h+r'{2,}(<br>|</p><p>)', r'</p><h'+n+r'>\2</h'+n+r'><p>', text);
		text = RegexLoop(r'(<br>|</p><p>)(.*?)(<br>|</p><p>)'+h+r'{2,}(</p>)'        , r'</p><h'+n+r'>\2</h'+n+r'>'   , text);
		text = RegexLoop(         r'(<p>)(.*?)(<br>|</p><p>)'+h+r'{2,}(<br>|</p><p>)',     r'<h'+n+r'>\2</h'+n+r'><p>', text);
		text = RegexLoop(         r'(<p>)(.*?)(<br>|</p><p>)'+h+r'{2,}(</p>)'        ,     r'<h'+n+r'>\2</h'+n+r'>'   , text);
	
	# heading
	for h in range(1, 6):
		h = str(h);
		text = RegexLoop(r'(<br>|</p><p>)#{'+h+r'}\s*(.*?)(<br>|</p><p>)', r'</p><h'+h+r'>\2</h'+h+r'><p>', text);
		text = RegexLoop(r'(<br>|</p><p>)#{'+h+r'}\s*(.*?)(</p>)'        , r'</p><h'+h+r'>\2</h'+h+r'>'   , text);
		text = RegexLoop(         r'(<p>)#{'+h+r'}\s*(.*?)(<br>|</p><p>)',     r'<h'+h+r'>\2</h'+h+r'><p>', text);
		text = RegexLoop(         r'(<p>)#{'+h+r'}\s*(.*?)(</p>)'        ,     r'<h'+h+r'>\2</h'+h+r'>',    text);
	
	
	# u liste
	text = RegexLoop(r'(<br>|</p><p>)(?:\*|-)\s+(.*?)(<br>|</p><p>)', r'</p><ul><li>\2</li></ul><p>', text);
	text = RegexLoop(r'(<br>|</p><p>)(?:\*|-)\s+(.*?)(</p>)'        , r'</p><ul><li>\2</li></ul>'   , text);
	text = RegexLoop(         r'(<p>)(?:\*|-)\s+(.*?)(<br>|</p><p>)'    , r'<ul><li>\2</li></ul><p>', text);
	text = RegexLoop(         r'(<p>)(?:\*|-)\s+(.*?)(</p>)'            , r'<ul><li>\2</li></ul>'   , text);
	text = RegexLoop(r'</li></ul><ul><li>', r'</li><li>', text);
	
	# o liste
	text = RegexLoop(r'(<br>|</p><p>)\d+(?:\)|\.)\s+(.*?)(<br>|</p><p>)', r'</p><ol><li>\2</li></ol><p>', text);
	text = RegexLoop(r'(<br>|</p><p>)\d+(?:\)|\.)\s+(.*?)(</p>)'        , r'</p><ol><li>\2</li></ol>'   , text);
	text = RegexLoop(         r'(<p>)\d+(?:\)|\.)\s+(.*?)(<br>|</p><p>)',     r'<ol><li>\2</li></ol><p>', text);
	text = RegexLoop(         r'(<p>)\d+(?:\)|\.)\s+(.*?)(</p>)'        ,     r'<ol><li>\2</li></ol>'   , text);
	text = RegexLoop(r'</li></ol><ol><li>', r'</li><li>', text);
	
	# <hr>
	text = RegexLoop(r'(<br>|</p><p>)(?:-|\*){2,}(<br>|</p><p>)', r'</p><hr><p>', text);
	text = RegexLoop(r'(<br>|</p><p>)(?:-|\*){2,}(</p>)'        , r'</p><hr>'   , text);
	text = RegexLoop(         r'(<p>)(?:-|\*){2,}(<br>|</p><p>)', r'<hr><p>'    , text);
	
	# bold
	text = RegexLoop(r'([^\\])((?:_|\*){2})((?:(?!<br>|</p>).)*?[^\\])\2',r'\1<strong>\3</strong>', text);
	# italic
	text = RegexLoop(r'([^\\])((?:_|\*){1})((?:(?!<br>|</p>).)*?[^\\])\2',r'\1<em>\3</em>', text);
	
	#
	text = RegexLoop(r'\\(_|\*)',r'\1', text);
	
	return text;


def RemoveFormatting(text):
	
	text = RegexLoop(r'</?(i|b|em|strong|sup|sub|u|s|span|a|ol|ul|hr|dl|code)(|\s[^>]*)>', r'', text);
	
	text = RegexLoop(r'<(/?)(h\d|li|pre|dt|dd)(|\s[^>]*)>', r'<\1p>', text);
	
	text = RegexLoop(r'<p\s[^>]*>', r'<p>', text);
	
	return CleanBasic(text);


def main():
	print("I reached main when I should not have\n");
	return -1;

if __name__ == "__main__":
	sys.exit(main())
