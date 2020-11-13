#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <>'
__docformat__ = 'restructuredtext en'

import sys, os

from calibre_plugins.comments_cleaner.common_utils import debug_print, debug_text, regex, PYTHON2

regex = regex()


def parseXMLentity(text):
    
    #    " & ' < >
    regx = r'&#x(0022|0026|0027|003C|003E);'
    while regex.search(regx, text):
        m = regex.search(regx, text).group(1)
        text = text.replace('&#x'+m+';', '&#'+str(int(m, base=16))+';')
    
    #    &#38; => &amp
    for c, h, d in entitysHtmlBase() + entitysHtmlQuot() + entitysHtmlApos():
        text = text.replace(d, h)
        #debug_print(h, d, c)
        # &amp; &#38; &
    
    #    &Agrave; &#192; => À
    for c, h, d in entitysHtml2() + entitysHtml3() + entitysHtml4():
        text = text.replace(h, c).replace(d, c)
        #debug_print(h, d, c)
        # &Agrave; &#192; À
    
    
    regx = r'&#(\d+);'
    while regex.search(regx, text):
        m = regex.search(regx, text).group(1)
        
        if PYTHON2:
            text = text.replace('&#'+m+';', unichr(int(m)))
        else:
            text = text.replace('&#'+m+';', chr(int(m)))
        
    
    regx = r'&#x([0-9a-fA-F]+);'
    while regex.search(regx, text):
        m = regex.search(regx, text).group(1)
        
        if PYTHON2:
            text = text.replace('&#x'+m+';', unichr(int(m, base=16)))
        else:
            text = text.replace('&#x'+m+';', chr(int(m, base=16)))
    
    text = regex.loop(r'(>[^<>]*)&quot;([^<>]*<)', r'\1"\2',text)
    text = regex.loop(r'(>[^<>]*)&apos;([^<>]*<)', r"\1'\2",text)
    
    text = regex.loop(r'(<[^<>]*="[^"]*)&apos;([^"]*"[^<>]*>)', r"\1'\2",text)
    
    return text

def XmlHtmlEntity(html, deci):
    
    if PYTHON2:
        cara = unichr(deci)
    else:
        cara = chr(deci)
    
    return (cara, '&'+html+';', '&#'+str(ord(cara))+';')

def entitysHtmlQuot():
        return [
            XmlHtmlEntity('quot', 34),
        ]

def entitysHtmlApos():
        return [
            XmlHtmlEntity('apos', 39),
        ]

def entitysHtmlBase():
        return [
            XmlHtmlEntity('amp', 38),# &
            XmlHtmlEntity('lt', 60), # <
            XmlHtmlEntity('gt', 62), # >
        ]

def entitysHtml2():
        return [
            XmlHtmlEntity('Agrave', 192),# À
            XmlHtmlEntity('Aacute', 193),# Á
            XmlHtmlEntity('Acirc', 194), # Â
            XmlHtmlEntity('Atilde', 195),# Ã
            XmlHtmlEntity('Auml', 196),  # Ä
            XmlHtmlEntity('Aring', 197), # Å
            XmlHtmlEntity('AElig', 198), # Æ
            XmlHtmlEntity('Ccedil', 199),# Ç
            XmlHtmlEntity('Egrave', 200),# È
            XmlHtmlEntity('Eacute', 201),# É
            XmlHtmlEntity('Ecirc', 202), # Ê
            XmlHtmlEntity('Euml', 203),  # Ë
            XmlHtmlEntity('Igrave', 204),# Ì
            XmlHtmlEntity('Iacute', 205),# Í
            XmlHtmlEntity('Icirc', 206), # Î
            XmlHtmlEntity('Iuml', 207),  # Ï
            XmlHtmlEntity('ETH', 208),   # Ð
            XmlHtmlEntity('Ntilde', 209),# Ñ
            XmlHtmlEntity('Ograve', 210),# Ò
            XmlHtmlEntity('Oacute', 211),# Ó
            XmlHtmlEntity('Ocirc', 212), # Ô
            XmlHtmlEntity('Otilde', 213),# Õ
            XmlHtmlEntity('Ouml', 214),  # Ö
            XmlHtmlEntity('Oslash', 216),# Ø
            XmlHtmlEntity('Ugrave', 217),# Ù
            XmlHtmlEntity('Uacute', 218),# Ú
            XmlHtmlEntity('Ucirc', 219), # Û
            XmlHtmlEntity('Uuml', 220),  # Ü
            XmlHtmlEntity('Yacute', 221),# Ý
            
            XmlHtmlEntity('THORN', 222), # Þ
            XmlHtmlEntity('szlig', 223), # ß
            
            XmlHtmlEntity('agrave', 224),# à
            XmlHtmlEntity('aacute', 225),# á
            XmlHtmlEntity('acirc', 226), # â
            XmlHtmlEntity('atilde', 227),# ã
            XmlHtmlEntity('auml', 228),  # ä
            XmlHtmlEntity('aring', 229), # å
            XmlHtmlEntity('aelig', 230), # æ
            XmlHtmlEntity('ccedil', 231),# ç
            XmlHtmlEntity('egrave', 232),# è
            XmlHtmlEntity('eacute', 233),# é
            XmlHtmlEntity('ecirc', 234), # ê
            XmlHtmlEntity('euml', 235),  # ë
            XmlHtmlEntity('igrave', 236),# ì
            XmlHtmlEntity('iacute', 237),# í
            XmlHtmlEntity('icirc', 238), # î
            XmlHtmlEntity('iuml', 239),  # ï
            XmlHtmlEntity('eth', 240),   # ð
            XmlHtmlEntity('ntilde', 241),# ñ
            XmlHtmlEntity('ograve', 242),# ò
            XmlHtmlEntity('oacute', 243),# ó
            XmlHtmlEntity('ocirc', 244), # ô
            XmlHtmlEntity('otilde', 245),# õ
            XmlHtmlEntity('ouml', 246),  # ö
            XmlHtmlEntity('oslash', 248),# ø
            XmlHtmlEntity('ugrave', 249),# ù
            XmlHtmlEntity('uacute', 250),# ú
            XmlHtmlEntity('ucirc', 251), # û
            XmlHtmlEntity('uuml', 252),  # ü
            XmlHtmlEntity('yacute', 253),# ý
            
            XmlHtmlEntity('thorn', 254), # þ
            XmlHtmlEntity('yuml', 255),  # ÿ
        ]

def entitysHtml3():
        return [
            XmlHtmlEntity('nbsp', 160),  #  
            XmlHtmlEntity('iexcl', 161), # ¡
            XmlHtmlEntity('cent', 162),  # ¢
            XmlHtmlEntity('pound', 163), # £
            XmlHtmlEntity('curren', 164),# ¤
            XmlHtmlEntity('yen', 165),   # ¥
            XmlHtmlEntity('brvbar', 166),# ¦
            XmlHtmlEntity('sect', 167),  # §
            XmlHtmlEntity('uml', 168),   # ¨
            XmlHtmlEntity('copy', 169),  # ©
            XmlHtmlEntity('ordf', 170),  # ª
            XmlHtmlEntity('laquo', 171), # «
            XmlHtmlEntity('not', 172),   # ¬
            XmlHtmlEntity('shy', 173),   # ­
            XmlHtmlEntity('reg', 174),   # ®
            XmlHtmlEntity('macr', 175),  # ¯
            XmlHtmlEntity('deg', 176),   # °
            XmlHtmlEntity('plusmn', 177),# ±
            XmlHtmlEntity('sup2', 178),  # ²
            XmlHtmlEntity('sup3', 179),  # ³
            XmlHtmlEntity('acute', 180), # ´
            XmlHtmlEntity('micro', 181), # µ
            XmlHtmlEntity('para', 182),  # ¶
            XmlHtmlEntity('middot', 183),# ·
            XmlHtmlEntity('cedil', 184), # ¸
            XmlHtmlEntity('sup1', 185),  # ¹
            XmlHtmlEntity('ordm', 186),  # º
            XmlHtmlEntity('raquo', 187), # »
            XmlHtmlEntity('frac14', 188),# ¼
            XmlHtmlEntity('frac12', 189),# ½
            XmlHtmlEntity('frac34', 190),# ¾
            XmlHtmlEntity('iquest', 191),# ¿
            
            XmlHtmlEntity('times', 215), # ×
            
            XmlHtmlEntity('divide', 247),# ÷
        ]

def entitysHtml4():
        return [
            XmlHtmlEntity('OElig', 338),   # Œ
            XmlHtmlEntity('oelig', 339),   # œ
            
            XmlHtmlEntity('Scaron', 352),  # Š
            XmlHtmlEntity('scaron', 353),  # š
            
            XmlHtmlEntity('Yuml', 376),    # Ÿ
            
            XmlHtmlEntity('fnof', 402),    # ƒ
            
            XmlHtmlEntity('circ', 710),    # ˆ
            
            XmlHtmlEntity('tilde', 732),   # ˜
            
            XmlHtmlEntity('Alpha', 913 ),  # Α
            XmlHtmlEntity('Beta', 914 ),   # Β
            XmlHtmlEntity('Gamma', 915 ),  # Γ
            XmlHtmlEntity('Delta', 916 ),  # Δ
            XmlHtmlEntity('Epsilon', 917 ),# Ε
            XmlHtmlEntity('Zeta', 918 ),   # Ζ
            XmlHtmlEntity('Eta', 919 ),    # Η
            XmlHtmlEntity('Theta', 920 ),  # Θ
            XmlHtmlEntity('Iota', 921 ),   # Ι
            XmlHtmlEntity('Kappa', 922 ),  # Κ
            XmlHtmlEntity('Lambda', 923 ), # Λ
            XmlHtmlEntity('Mu', 924 ),     # Μ
            XmlHtmlEntity('Nu', 925 ),     # Ν
            XmlHtmlEntity('Xi', 926 ),     # Ξ
            XmlHtmlEntity('Omicron', 927 ),# Ο
            XmlHtmlEntity('Pi', 928 ),     # Π
            XmlHtmlEntity('Rho', 929 ),    # Ρ
            
            XmlHtmlEntity('Sigma', 931 ),  # Σ
            XmlHtmlEntity('Tau', 932 ),    # Τ
            XmlHtmlEntity('Upsilon', 933 ),# Υ
            XmlHtmlEntity('Phi', 934 ),    # Φ
            XmlHtmlEntity('Chi', 935 ),    # Χ
            XmlHtmlEntity('Psi', 936 ),    # Ψ
            XmlHtmlEntity('Omega', 937 ),  # Ω
            XmlHtmlEntity('ohm', 937 ),    # Ω
            
            XmlHtmlEntity('alpha', 945 ),  # α
            XmlHtmlEntity('beta', 946 ),   # β
            XmlHtmlEntity('gamma', 947 ),  # γ
            XmlHtmlEntity('delta', 948 ),  # δ
            XmlHtmlEntity('epsi', 949 ),   # ε
            XmlHtmlEntity('epsilon', 949 ),# ε
            XmlHtmlEntity('zeta', 950 ),   # ζ
            XmlHtmlEntity('eta', 951 ),    # η
            XmlHtmlEntity('theta', 952 ),  # θ
            XmlHtmlEntity('iota', 953 ),   # ι
            XmlHtmlEntity('kappa', 954 ),  # κ
            XmlHtmlEntity('lambda', 955 ), # λ
            XmlHtmlEntity('mu', 956 ),     # μ
            XmlHtmlEntity('nu', 957 ),     # ν
            XmlHtmlEntity('xi', 958 ),     # ξ
            XmlHtmlEntity('omicron', 959 ),# ο
            XmlHtmlEntity('pi', 960 ),     # π
            XmlHtmlEntity('rho', 961 ),    # ρ
            XmlHtmlEntity('sigmav', 962 ), # ς
            XmlHtmlEntity('sigmaf', 962 ), # ς
            XmlHtmlEntity('sigma', 963 ),  # σ
            XmlHtmlEntity('tau', 964 ),    # τ
            XmlHtmlEntity('upsi', 965 ),   # υ
            XmlHtmlEntity('phi', 966 ),    # φ
            XmlHtmlEntity('chi', 967 ),    # χ
            XmlHtmlEntity('psi', 968 ),    # ψ
            XmlHtmlEntity('omega', 969 ),  # ω
            
            XmlHtmlEntity('thetav', 977 ), # ϑ
            XmlHtmlEntity('upsih', 978 ),  # ϒ
            
            XmlHtmlEntity('phiv', 981 ),   # ϕ
            
            XmlHtmlEntity('ensp', 8194),   #  
            XmlHtmlEntity('emsp', 8195),   #  
            
            XmlHtmlEntity('thinsp', 8201), #  
            
            XmlHtmlEntity('zwnj', 8204),   # ‌
            XmlHtmlEntity('zwj', 8205),    # ‍
            XmlHtmlEntity('lrm', 8206),    # ‎
            XmlHtmlEntity('rlm', 8207),    # ‏
            
            XmlHtmlEntity('ndash', 8211),  # –
            XmlHtmlEntity('mdash', 8212),  # —
            
            XmlHtmlEntity('lsquo', 8216),  # ‘
            XmlHtmlEntity('rsquo', 8217),  # ’
            XmlHtmlEntity('rsquor', 8217), # ’
            XmlHtmlEntity('sbquo', 8218),  # ‚
            XmlHtmlEntity('ldquo', 8220),  # “
            XmlHtmlEntity('rdquo', 8221 ), # ”
            XmlHtmlEntity('bdquo', 8222),  # „
            
            XmlHtmlEntity('dagger', 8224), # †
            XmlHtmlEntity('ddagger', 8225),# ‡
            XmlHtmlEntity('bull', 8226),   # •
            
            XmlHtmlEntity('hellip', 8230), # …
            
            XmlHtmlEntity('permil', 8240), # ‰
            
            XmlHtmlEntity('prime', 8242),  # ′
            XmlHtmlEntity('Prime', 8243),  # ″
            
            XmlHtmlEntity('lsaquo', 8249), # ‹
            XmlHtmlEntity('rsaquo', 8250), # ›
            
            XmlHtmlEntity('oline', 8254),  # ‾
            
            XmlHtmlEntity('euro', 8364),   # €
            
            XmlHtmlEntity('image', 8465),  # ℑ
            
            XmlHtmlEntity('weierp', 8472), # ℘
            
            XmlHtmlEntity('real', 8476),   # ℜ
            
            XmlHtmlEntity('trade', 8482),  # ™
            
            XmlHtmlEntity('alefsym', 8501),# ℵ
            
            XmlHtmlEntity('rang', 10217),  # ⟩
            XmlHtmlEntity('loz', 9674),    # ◊
            XmlHtmlEntity('spades', 9824), # ♠
            XmlHtmlEntity('clubs', 9827),  # ♣
            XmlHtmlEntity('hearts', 9829), # ♥
            XmlHtmlEntity('diams', 9830),  # ♦
            XmlHtmlEntity('lang', 10216),  # ⟨
            XmlHtmlEntity('rang', 10217),  # ⟩
        ]


def main():
    print('I reached main when I should not have\n')
    return -1

if __name__ == '__main__':
    sys.exit(main())
