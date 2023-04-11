# Comments Cleaner
[![MobileRead][mobileread-image]][mobileread-url]
[![History][changelog-image]][changelog-url]
[![License][license-image]][license-url]
[![calibre Version][calibre-image]][calibre-url]
[![Status][status-image]][status-image]


*Comments Cleaner* is a small plugin that clean comments from superfluous and unwanted CSS rules (background-color, text color, font-family, among other things), but keeps the basic elements (italic, bold).
The plugin will also try to convert plain-text comments.

The plugin has the following options:

* Keep or remove Hyperlinks
* Weights management
    * Round the value to the hundred (only below Calibre 6)
    * Round to Bold
* Remove Strikethrough, Underline and Italic
* Headings management
    * Converte to a paragraph
    * Converte to a paragraph but keep the bold
* Text alignment
* Automatic justification
    * Force justification
    * Remove alignment
* Specific alignment for lists
* Keep or Delete the ID and CLASS attributs
* Remove all formatting (NO MERCY!!)
* Try a conversion from Mardown format (the key word is TRY)
* Remove Multiple Line Return <br> and create a new paragraph instead
* Convert 'Line Return' into Paragraph or Space
* Management of empty paragraphs
* Ability to specify others CSS rules to keep in addition to the basic CSS rule
* Possibility to apply the cleaning to others custom HTML columns


Basic CSS rules keep by default:
```
text-align
font-weight
font-style
text-decoration
```


**Installation**

Open *Preferences -> Plugins -> Get new plugins* and install the "Comments Cleaner" plugin.
You may also download the attached zip file and install the plugin manually, then restart calibre as described in the [Introduction to plugins thread](https://www.mobileread.com/forums/showthread.php?t=118680")

The plugin works for Calibre 2 and later.<br>
It is therefore compatible for *QtWebKit* (Calibre <4) and *QtWebEngine* (Calibre >=4).

Page: [GitHub](https://github.com/un-pogaz/Comments-Cleaner) | [MobileRead](https://www.mobileread.com/forums/showthread.php?t=333861)

<ins>Note for those who wish to provide a translation:</ins><br>
I am *French*! Although for obvious reasons, the default language of the plugin is English, keep in mind that already a translation.


<br><br>

![configuration panel](https://raw.githubusercontent.com/un-pogaz/Comments-Cleaner/main/static/Comments_Cleaner.png)
![button menu](https://raw.githubusercontent.com/un-pogaz/Comments-Cleaner/main/static/Comments_Cleaner-menu.png)
![example of cleaned comment](https://raw.githubusercontent.com/un-pogaz/Comments-Cleaner/main/static/Comments_Cleaner-exemple.gif)


[mobileread-url]: https://www.mobileread.com/forums/showthread.php?t=333861

[changelog-image]: https://img.shields.io/badge/History-CHANGELOG-blue.svg
[changelog-url]: changelog.md

[license-image]: https://img.shields.io/badge/License-GPL-yellow.svg
[license-url]: LICENSE

[calibre-image]: https://img.shields.io/badge/calibre-2.00.0_and_above-green
[calibre-url]: https://www.calibre-ebook.com/

[status-image]: https://img.shields.io/badge/Status-Stable-green

[mobileread-image]: https://img.shields.io/badge/MobileRead-Plugin%20Thread-blue?logo=data:image/x-icon;base64,AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAns32/zqT5v8SeeD/Enng/xJ54P8SeeD/LYvl/3+78v8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZazv/xJ54P8SeeD/Enng/zqT5v9Jm+n/HoLi/xJ54P8SeeD/OpPm/wAAAAAAAAAAAAAAAAAAAAAAAAAAzub7/xJ54P8SeeD/Enng/4/D9P/p6en/0tLS/8Tc8P8SeeD/Enng/xJ54P+Pw/T/AAAAAAAAAAAAAAAAAAAAAL3e+v8SeeD/Enng/xJ54P+93vr/Wlpa/zc3N/8AAAAAEnng/xJ54P8SeeD/f7vy/wAAAAAAAAAAAAAAAAAAAAAAAAAAHoLi/xJ54P8SeeD/T3+r/yQkJP9+jpz/Zazv/xJ54P8SeeD/Enng/73e+v8AAAAAAAAAAAAAAAAAAAAAz8Kt/66uof+Gj4L/ho+C/5SKb/+Vh2j/ho+C/4aPgv+Gj4L/ho+C/5OVgv+6qYP/yryi/wAAAAAAAAAAp5BW/6eQVv+nkFb/p5BW/6eQVv+nkFb/p5BW/6eQVv+nkFb/p5BW/6eQVv+nkFb/p5BW/6eQVv8AAAAA6ePb46eQVv+nkFb/p5BW/6eQVv+nkFb/xLWY/8/Crf/Pwq3/vq6N/7qogv+6qIL/uqiC/7qogv+nkFb/5uDW/+bg1v+nkFb/p5BW/6eQVv+nkFb/p5BW/+zn4f///////////8zMzP92dnb/VFRU/9nZ2f//////taJ5/8/Crf/m4Nb/p5BW/6eQVv+nkFb/p5BW/6eQVv/m4Nb////////////MzMz/k5OT/8zMzP/z8/P//////8S1mP/EtZj/5uDW/6eQVv+nkFb/p5BW/6eQVv+nkFb/oZ6Z/5OTk//m5ub/////////////////8/Pz/3Z2dv9xcHD/j4h7/9rRwf+nkFb/p5BW/6eQVv+nkFb/VVNP/8zMzP/z8/P/dnZ2/9nZ2f///////////5OTk//z8/P//////3Rxa//Pwq3/p5BW/6eQVv+nkFb/p5BW/2FgYP///////////76+vv/MzMz///////////+ioqL/oqKi/76+vv91b2X/z8Kt/6eQVv+nkFb/p5BW/6eQVv+JfWX/bGtq/4WFhf+FhYX//////////////////////76+vv++vr7/taJ5/8/Crf+nkFb/p5BW/6eQVv+nkFb/p5BW/8m7ov//////+Pb1/+bg1v/g2Mz/z8Kt/8/Crf+6qIL/uqiC/6eQVv/m4Nb/uqmD/7qpg/+nkFb/p5BW/6eQVv+nkFb/rZZh/7qpg/+/r43/z8Kt/8/Crf/m4NYd5uDWVQAAAAAAAAAA8A8AAOAHAADAAwAAwEMAAOADAADAAQAAgAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAA==
