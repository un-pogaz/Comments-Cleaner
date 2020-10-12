#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <>'
__docformat__ = 'restructuredtext en'

import sys, os
from calibre_plugins.comments_cleaner.config import KEY, PREFS
from calibre_plugins.comments_cleaner.common_utils import debug_print, debug_text, RegexSimple, RegexSearch, RegexLoop, CSS_CleanRules


def CleanBasic(text):
	
	text = RegexLoop(r'(&#x202F;|&#8239;)', '\u202F', text);
	text = RegexLoop(r'(&#xA0;|&#160;)', '\u00A0', text);
	
	# line
	text = text.replace('\r\n', '\n').replace('\r', '\n');
	text = RegexLoop(r'( |\t|\n\n)+\n', '\n', text);
	
	text = RegexLoop(r'\s<(p|div|h\d|li|ul|ol|blockquote)', r'<\1', text);
	text = RegexLoop(r'><(p|div|h\d|li|ul|ol|blockquote)', r'>\n<\1', text);
	
	# entity
	text = RegexLoop("&#38;", "&amp;", text);
	text = RegexLoop("&#60;", "&lt;", text);
	text = RegexLoop("&#62;", "&gt;", text);
	
	text = RegexLoop("(&#160;|&nbsp;)", r'\u00A0', text);
	
	text = RegexLoop("(&mdash;|&#8212;)", "—", text);
	text = RegexLoop("(&ndash;|&#8211;)", "–", text);
	text = RegexLoop("(&laquo;|&#171;)", "«", text);
	text = RegexLoop("(&raquo;|&#187;)", "»", text);
	text = RegexLoop("(&hellip;|&#8230;)", "…", text);
	text = RegexLoop("(&rsquo;|&#8217;)", "’", text);
	
	text = RegexLoop(r'<(/?)i\d+([^>]*)>', r'<\1em\2>', text);
	text = RegexLoop(r'<(/?)b\d+([^>]*)>', r'<\1strong\2>', text);
	
	# same inline
	text = RegexLoop(r"<(i|b|em|strong|span)([^>]*)>([^>]*)</\1>\s+<\1\2>", r'<\1\2>\3 ', text);
	text = RegexLoop(r"<(i|b|em|strong|span)([^>]*)>([^>]*)</\1><\1\2>", r'<\1\2>\3', text);
	
	# inline vide
	innerSpace = r"<(i|b|em|strong)[^>]*>\s+</\1>";
	innerEmpty = r"<(i|b|em|strong)[^>]*></\1>";
	outerSpace = r"</(i|b|em|strong)>\s+<\1.*?>";
	outerEmpty = r"</(i|b|em|strong)><\1.*?>";
	
	while (RegexSearch(innerSpace, text) or
		RegexSearch(innerEmpty, text) or
		RegexSearch(outerSpace, text) or
		RegexSearch(outerEmpty, text)):
		
		text = RegexLoop(innerSpace, r' ', text);
		text = RegexLoop(innerEmpty, r'', text);
		
		text = RegexLoop(outerSpace, r' ', text);
		text = RegexLoop(outerEmpty, r'', text);
	
	# double espace et tab dans paragraphe
	text = RegexLoop(r'(<(p|h\d).*?>.*?)(\t| {2,})', r'\1 ', text);
	# tab pour l'indentation
	text = RegexLoop(r'^( *)\t(\s*<)', r'\1  \2', text);
	
	
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
	# style: remove empty
	text = RegexLoop(r' style="\s*"', r'', text);
	
	
	# clean space in attribut
	text = RegexLoop(r' ([^"=<>]+)="\s+([^"]*)"', r' \1="\2"', text);
	text = RegexLoop(r' ([^"=<>]+)="([^"]*)\s+"', r' \1="\2"', text);
	
	#strip span
	text = RegexLoop(r'<span\s*>(.*?)</span>', r'\1', text);
	
	# remplace les triple point invalide
	text = RegexSimple(r'\.\s*\.\s*\.', r'…', text);
	
	# xml format
	text = RegexLoop(r'<([^<>]+)\s{2,}([^<>]+)>', r'<\1 \2>', text);
	text = RegexLoop(r'\s+(|/|\?)\s*>', r'\1>', text);
	text = RegexLoop(r'<\s*(|/|!|\?)\s+', r'<\1', text);
	
	return text;

def CleanHTML(text):
	
	# if no tag = plain text
	if not(RegexSearch(r'<(p|div)[^>]*>', text)):
		text = '<div><p>' + RegexLoop(r'[\r\n]{2,}',r'</p><p>', text) + '</p></div>';
		text = RegexLoop(r'[\r\n]',r'<br>', text)
		text = RegexLoop(r'(_|\*){2}((?:(?!\\\1\1|\1\\\1|<br>).)*?)\1{2}',r'<strong>\2</strong>', text);
		text = RegexLoop(r'(_|\*){1}((?:(?!\\\1\1|\1\\\1|<br>).)*?)\1{1}',r'<em>\2</em>', text);
	
	
	text = CleanBasic(text);
	
	# ID and CLASS attributs
	if PREFS[KEY.ID_CLASS] == 'id_class' or PREFS[KEY.ID_CLASS] == 'id':
		text = RegexLoop(r' id="[^"]*"', r'', text);
	if PREFS[KEY.ID_CLASS] == 'id_class' or PREFS[KEY.ID_CLASS] == 'class':
		text = RegexLoop(r' class="[^"]*"', r'', text);
	
	# Headings
	if PREFS[KEY.HEADINGS] == 'bolder':
		text = RegexLoop(r'<(h\d+)([^>]*) style="((?:(?!font-weight)[^"])*)"([^>]*)>', r'<\1\2 style="\3;font-weight: bold;"\4>', text);
		text = RegexLoop(r'<(h\d+)((?:(?! style=)[^>])*)>', r'<\1\2 style="font-weight: bold;">', text);
	if PREFS[KEY.HEADINGS] == 'conv' or PREFS[KEY.HEADINGS] == 'bolder':
		text = RegexLoop(r'<(/?)h\d+([^>]*)>', r'<\1p\2>', text);
	
	# Hyperlink
	if PREFS[KEY.KEEP_URL] == 'del':
		text = RegexLoop(r'<a.*?>(.*?)</a>', r'\1', text);
	
	text = OrderedAttributs(text);
	
	text = RegexLoop(r'<div([^>]*)>(.*?)<div([^>]*)>(.*?)</div>',r'<div>\2<p\3>\4</p>', text);
	
	# remove namespaced attribut
	text = RegexLoop(r' [^"=<>]+:[^"=<>]+="[^"]*"', r'', text);
	
	# invalid tag
	text = RegexLoop(r'</?(font|html|body|img|meta|link)[^>]*>', r'', text);
	text = RegexLoop(r'<(div|p|li|h1|h2|h3|h4|h5|h6)[^>]*>\s+</(div|p|li|h1|h2|h3|h4|h5|h6)>', r'', text);
	
	# management of <br>
	text = RegexLoop(r'<(b|h)r[^>]+>', r'<\1r>', text);
	text = RegexLoop(r'<(b|h)r>\s+', r'<\1r>', text);
	text = RegexLoop(r'\s+<(b|h)r>', r'<\1r>', text);
	text = RegexLoop(r'<span([^>]*)><(b|h)r>', r'<\2r><span\1>', text);
	text = RegexLoop(r'<(b|h)r></span>', r'</span><\1r>', text);
	
	text = RegexLoop(r'<(div|p|li|h1|h2|h3|h4|h5|h6)([^>]*)>(<br>)+</(div|p|li|h1|h2|h3|h4|h5|h6)>', "<\1\2>\u00A0</\1>", text);
	text = RegexLoop(r'<br></(div|p|li|h1|h2|h3|h4|h5|h6)>', r'</\1>', text);
	text = RegexLoop(r'<(div|p|li|h1|h2|h3|h4|h5|h6)([^>]*)><br>', r'<\1\2>', text);
	
	# Multiple Line Return
	if PREFS[KEY.DOUBLE_BR] == 'new':
		text = RegexLoop(r'<p([^>]*)>((?:(?!</p>).)*?)(<br>){2,}', r'<p\1>\2</p><p\1>', text);
	
	
	# style standardization:  insert ; at the end
	text = RegexLoop(r' style="([^"]*[^";])"', r' style="\1;"', text);
	# style standardization: insert space at the start
	text = text.replace(' style="', ' style=" ');
	
	
	text = CleanAlign(text);
	
	text = CleanStyle(text);
	
	
	# remove empty hyperllink
	text = RegexLoop(r'<a\s*>(.*?)</a>', r'\1', text);
	# remove empty attribut
	text = RegexLoop(r' ([^"=<>]+)="\s*"', r'', text);
	
	text = OrderedAttributs(text);
	
	#
	
	text = CleanBasic(text);
	return text;

# Ordered the attributs
def OrderedAttributs(text):
	attributs = 'align|style|class|id|href'
	for attribut in reversed(sorted(attributs.split('|'))):
		text = RegexLoop(r'<([^\s])([^=>]*=[^>]*)\s+'+attribut+r'="([^"]*)"', r'<\1 '+attribut+r'="\3"\2', text);
	return text;

def CleanAlign(text):
	
	text = OrderedAttributs(text);
	
	# set align
	if ((PREFS[KEY.FORCE_JUSTIFY] == 'del')):
		# del align
		text = RegexLoop(r' align="[^"]*"', r'', text);
		
	else: # empty / all / none
		
		tags = 'p|div|h1|h2|h3|h4|h5|h6';
		
		# insert align left for all
		for tag in tags.split('|'):
			text = text.replace('<'+tag, '<'+tag+' align="left"');
		
		# insert align left for all
		text = RegexLoop(r'<('+tags+') align="left"( align="[^"]*")', r'<\1\2', text);
		
		# swap text-align to align
		text = RegexLoop(r' align="[^"]*"([^>]*)style="([^"]*) text-align:\s*([^;]*)\s*;([^"]*)"', r' align="\3"\1style="\2\4"', text);
		
		# clean space in attribut
		text = RegexLoop(r' align="\s+([^"]*)"', r' align="\1"', text);
		text = RegexLoop(r' align="([^"]*)\s+"', r' align="\1"', text);
		
		# align valide value
		text = RegexLoop(r' align="(?!left|justify|center|right)[^"]*"', r' align="left"', text);
		
		# set align prefs
		if (PREFS[KEY.FORCE_JUSTIFY] == 'empty'):
			text = RegexLoop(r' align="left"', r' align="justify"', text);
		elif (PREFS[KEY.FORCE_JUSTIFY] == 'all'):
			text = RegexLoop(r' align="(left|center|right)"', r' align="justify"', text);
		#else: 'none'
		
	
	# del text-align
	text = RegexLoop(r' style="([^"]*) text-align\s*:\s*([^;]*)\s*;([^"]*)"', r' style="\1\3"', text);
	
	# del align left (default value)
	text = RegexLoop(r' align="left"', r'', text);
	
	# del attibut for <div> with <p>
	text = RegexLoop(r'<div align="[^"]*"[^>]>\s*<p', r'<div>\n<p', text);
	
	# del align for <li>
	text = RegexLoop(r'<(ol|ul|li) align="[^"]*"', r'<\1', text);
	
	# del justify for <h1>
	text = RegexLoop(r'<(h1|h2|h3|h4|h5|h6) align="justify"', r'<\1', text);
	
	text = RegexLoop(r' align="left"', r'', text);
	text = RegexLoop(r'<div align="[^"]*"\s*>\s*<p', r'<div>\n<p', text);
	
	return text;


def CleanStyle(text):
	
	text = text.replace(' style="',' x-style="" style=" ');
	
	rule_all = 'text-align font-weight font-style text-decoration text-decoration-line';
	rule_tbl = CSS_CleanRules(rule_all +' '+ PREFS[KEY.CSS_KEEP]).split(' ');
	
	for rule in rule_tbl:
		text = RegexLoop(r' x-style="([^"]*)" style="([^"]*) '+rule+r':\s*([^;]*)\s*;([^"]*)"', r' x-style="\1 '+rule+r': \3;" style="\2 \4"', text);
	
	text = RegexLoop(r' x-style="([^"]*)" style="[^"]*"', r' style="\1"', text);
	
	# font-weight
	text = RegexLoop(r' style="([^"]*) font-weight:\s*(normal|inherit|initial)\s*;([^"]*)"', r' style="\1\3"', text);
	text = RegexLoop(r' style="([^"]*) font-weight:\s*(bold)\s*;([^"]*)"', r' style="\1font-weight: 600\3"', text);
	text = RegexLoop(r' style="([^"]*) font-weight:\s*(\d){4,}(?:\.\d+)?\s*;([^"]*)"', r' style="\1font-weight: 900;\3"', text);
	text = RegexLoop(r' style="([^"]*) font-weight:\s*(\d){1,2}(?:\.\d+)?\s*;([^"]*)"', r' style="\1font-weight: 100;\3"', text);
	
	if PREFS[KEY.FONT_WEIGHT] == 'bold':
		text = RegexLoop(r' style="([^"]*) font-weight:\s*[5-9]\d\d(?:\.\d+)?\s*;([^"]*)"', r' style="\1 font-weight: xxx;\2"', text);
		text = RegexLoop(r' style="([^"]*) font-weight:\s*xxx\s*;([^"]*)"', r' style="\1 font-weight: 600;\2"', text);
		text = RegexLoop(r' style="([^"]*) font-weight:\s*[1-4]\d\d(?:\.\d+)?\s*;([^"]*)"', r' style="\1\2"', text);
	elif PREFS[KEY.FONT_WEIGHT] == 'trunc':
		text = RegexLoop(r' style="([^"]*) font-weight:\s*(?P<name>\d)\d\d(?:\.\d+)?\s*;([^"]*)"', r' style="\1 font-weight: \g<name>xx;\3"', text);
		text = RegexLoop(r' style="([^"]*) font-weight:\s*(?P<name>\d)xx\s*;([^"]*)"', r' style="\1 font-weight: \g<name>00;\3"', text);
	#else: 'none'
	
	# font-style
	text = RegexLoop(r' style="([^"]*) font-style:\s*(normal|inherit|initial)\s*;([^"]*)"', r' style="\1\3"', text);
	text = RegexLoop(r' style="([^"]*) font-style:\s*(oblique(?:\s+\d+deg))\s*;([^"]*)"', r' style="\1 font-style: italic;\3"', text);
	
	return text;

def main():
	print("I reached main when I should not have\n");
	return -1;

if __name__ == "__main__":
	sys.exit(main())
