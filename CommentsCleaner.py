#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)


__copyright__ = '2020, un_pogaz <>'
__docformat__ = 'restructuredtext en'

import sys, os
import calibre_plugins.comments_cleaner.config as cfg
from calibre_plugins.comments_cleaner.common_utils import debug_print, RegexSimple, RegexSearch, RegexLoop



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
	
	
	# attribut style
	text = RegexLoop(r'style="([^"]*);\s+;([^"]*)"', r'style="\1;\2"', text);
	text = RegexLoop(r'style="([^"]*)(;|:)\s{2,}([^"]*)"', r'style="\1\2 \3"', text);
	text = RegexLoop(r'style="([^"]*)\s+(;|:)([^"]*)"', r'style="\1\2\3"', text);
	
	text = RegexLoop(r'style="([^"]*);\s*"', r'style="\1"', text);
	text = RegexLoop(r'style="\s*"', r'', text);
	
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
	text = CleanBasic(text);
	
	if cfg.prefs[cfg.KEY_KEEP_URL] == 'none':
		text = RegexLoop(r'<a.*?>(.*?)</a>', r'\1', text);
	
	if not(RegexSearch(r'<(p|div)[^>]*>', text)):
		text = '<div><p>' + RegexLoop(r'[\r\n]+',r'</p><p>', text) + '</p></div>'
	
	# uniformise les attribut style
	text = RegexLoop(r'style="([^"]*[^";])"', r'style="\1;"', text);
	
	text = RegexLoop(r'(<font[^>]*>|</font>|<html[^>]*>|</html>|<body[^>]*>|</body>)', r'', text);
	text = RegexLoop(r'<(img|meta|link)[^>]*>', r'', text);
	
	text = RegexLoop(r'(id|class)=".*?"', r'', text);
	text = RegexLoop(r'<(div|p|li|h1|h2|h3|h4|h5|h6)[^>]*>\s+</(div|p|li|h1|h2|h3|h4|h5|h6)>', r'', text);
	text = RegexLoop(r'<(b|h)r[^>]+>', r'<\1r>', text);
	text = RegexLoop(r'<(b|h)r>\s+', r'<\1r>', text);
	text = RegexLoop(r'\s+<(b|h)r>', r'<\1r>', text);
	
	text = RegexLoop(r'<(div|p|li|h1|h2|h3|h4|h5|h6)([^>]*)><br></(div|p|li|h1|h2|h3|h4|h5|h6)>', "<\1\2>\u00A0</\1>", text);
	text = RegexLoop(r'<br></(div|p|li|h1|h2|h3|h4|h5|h6)>', r'</\1>', text);
	text = RegexLoop(r'<(div|p|li|h1|h2|h3|h4|h5|h6)([^>]*)><br>', r'<\1\2>', text);
	
	text = RegexLoop(r'<p([^>]*)>([^>]*)<br><br>', r'<p\1>\2</p><p\1>', text);
	
	atr_tbl = [
		r'(background-color)',
		r'(color)',
		r'(text-indent|letter-spacing|white-space|word-spacing|word-wrap|overflow)',
		r'(margin|padding|border|box-sizing|outline|orphans|widows|float|display|visibility|text-rendering)',
		r'(page-break|clear|cursor|text-autospace|transition|tab-stops|zoom)',
		r'(background|opacity|text-shadow|list-style-position)',
		r'(position|top|bottom|left|right)',
		r'(max-|z-|)(width|height|index)',
		r'-{0,2}((?:mso-|moz-|webkit-|qt-)[^:]+)',
		r'(font-family|font-variant|font-stretch|font-size|line-height)'
	];
	
	for atr in atr_tbl:
		text = RegexLoop(r'style="([^"]*)'+ atr +'\s*:[^;]*;([^"]*)"', r'style="\1\3"', text);
	
	# font-weight
	text = RegexLoop(r'style="([^"]*)font-weight\s*:\s*(normal|inherit|initial)\s*;([^"]*)"', r'style="\1\3"', text);
	text = RegexLoop(r'style="([^"]*)font-weight\s*:\s*(bold)\s*;([^"]*)"', r'style="\1font-weight: 600\3"', text);
	text = RegexLoop(r'style="([^"]*)font-weight\s*:\s*(\d){4,}(?:\.\d+)?\s*;([^"]*)"', r'style="\1font-weight: 900;\3"', text);
	text = RegexLoop(r'style="([^"]*)font-weight\s*:\s*(\d){1,2}(?:\.\d+)?\s*;([^"]*)"', r'style="\1font-weight: 100;\3"', text);
	
	if cfg.prefs[cfg.KEY_FONT_WEIGHT] == 'none':
		n=None;
	elif cfg.prefs[cfg.KEY_FONT_WEIGHT] == 'bold':
		text = RegexLoop(r'style="([^"]*)font-weight\s*:\s*[5-9]\d\d(?:\.\d+)?\s*;([^"]*)"', r'style="\1 font-weight: xxx;\2"', text);
		text = RegexLoop(r'style="([^"]*)font-weight\s*:\s*xxx\s*;([^"]*)"', r'style="\1 font-weight: 600;\2"', text);
		text = RegexLoop(r'style="([^"]*)font-weight\s*:\s*[1-4]\d\d(?:\.\d+)?\s*;([^"]*)"', r'style="\1\2"', text);
	else: #trunc
		text = RegexLoop(r'style="([^"]*)font-weight\s*:\s*(?P<name>\d)\d\d(?:\.\d+)?\s*;([^"]*)"', r'style="\1 font-weight: \g<name>xx;\3"', text);
		text = RegexLoop(r'style="([^"]*)font-weight\s*:\s*(?P<name>\d)xx\s*;([^"]*)"', r'style="\1 font-weight: \g<name>00;\3"', text);
	
	# font-style
	text = RegexLoop(r'style="([^"]*)font-style\s*:\s*(normal|inherit|initial)\s*;([^"]*)"', r'style="\1\3"', text);
	text = RegexLoop(r'style="([^"]*)font-style\s*:\s*(oblique(?:\s+\d+deg))\s*;([^"]*)"', r'style="\1font-style: italic;\3"', text);
	
	
	# align
	text = RegexLoop(r'<(p|div)([^=]*=[^>]*)\s*align="([^"]*)"', r'<\1 align="\3"\2', text);
	
	# align / empty|all
	if ((cfg.prefs[cfg.KEY_FORCE_JUSTIFY] == 'empty') or (cfg.prefs[cfg.KEY_FORCE_JUSTIFY] == 'all')):
		# align for all
		text = text.replace('<p', '<p align="justify"').replace('<div', '<div align="justify"');
		text = RegexLoop(r'<(p|div)\s*align="justify"([^>]*align="[^"]*")', r'<\1\2', text);
		text = RegexLoop(r'<div\s*align="[^"]*"\s*>\s*<p', r'<div>\n<p', text);
		
		# align only
		text = RegexLoop(r'align="\s*(?!justify|center|right)[^"]*"', r'align="justify"', text);
		
		# align center or right
		if (cfg.prefs[cfg.KEY_FORCE_JUSTIFY] == 'empty'):
			text = RegexLoop(r'align="[^"]*"([^>]*)style="([^"]*)text-align\s*:\s*(center|right)\s*;([^"]*)"', r'align="\3"\1style="\2\4"', text);
		if (cfg.prefs[cfg.KEY_FORCE_JUSTIFY] == 'all'):
			text = RegexLoop(r'align="(left|center|right)"', r'align="justify"', text);
	
	# align / none
	if ((cfg.prefs[cfg.KEY_FORCE_JUSTIFY] == 'none')):
		# align left
		text = text.replace('<p', '<p align="left"').replace('<div', '<div align="left"');
		text = RegexLoop(r'<(p|div)\s*align="left"([^>]*align="[^"]*")', r'<\1\2', text);
		
		# align center or right or justify
		text = RegexLoop(r'align="[^"]*"([^>]*)style="([^"]*)text-align\s*:\s*(center|right|justify)\s*;([^"]*)"', r'align="\3"\1style="\2\4"', text);
	
	# align / delete
	if ((cfg.prefs[cfg.KEY_FORCE_JUSTIFY] == 'del')):
		text = RegexLoop(r'align="[^"]*"', r'', text);
	
	
	# del text-align
	text = RegexLoop(r'style="([^"]*)text-align\s*:\s*([^;]*)\s*;([^"]*)"', r'style="\1\3"', text);
	# del align for <li>
	text = RegexLoop(r'<(ol|ul|li)([^>]*)align="[^"]*"', r'<\1\2', text);
	
	text = RegexLoop(r'align="left"', r'', text);
	text = RegexLoop(r'<div\s*align="[^"]*"\s*>\s*<p', r'<div>\n<p', text);
	# clean
	
	text = RegexLoop(r'<a\s*>(.*?)</a>', r'\1', text);
	text = RegexLoop(r'style="\s+([^"]*)"', r'style="\1"', text);
	text = RegexLoop(r'style="([^"]*)\s+"', r'style="\1"', text);
	
	#
	
	text = CleanBasic(text)
	return text;


def main():
	print("I reached main when I should not have\n");
	return -1;

if __name__ == "__main__":
	sys.exit(main())
