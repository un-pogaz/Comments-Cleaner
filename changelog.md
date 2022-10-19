### version 1.9.0
[internal] again, big rework of common_utils (use submodule)

### version 1.8.0
[internal] big rework of common_utils.py

### version 1.7.3
[fix] icon not display when a theme colors is used

### version 1.7.2
[internal] Small improvement of XMLentity

### version 1.7.1
Small improvement of compatibility betwen multiple Calibre version

### version 1.7.0
Small technical change due compatibility with Calibre 6

### version 1.6.3
Improve a bad parse for raw text comment but containing \<br\> tags

### version 1.6.2
Various technical improvement

### version 1.6.1
fix a regression of "del align for list \<li\>"

### version 1.6.0
Compatible Calibre6/Qt6

### version 1.5.0
Improvement of "Single 'Line return'" option: Replace by Space, by new paragraph, no change

### version 1.4.1
Clean text full heading<br>
[Fix] The text of progress dialog is correctly translated, FINALY! \o/

### version 1.4.0
Better support of small screens for the config dialog<br>
Improve \<br\> in \<strong\>/<em\><br>
Improve clean for text fully bold and \<sup\>/\<sub\> paragraphe<br>
Improved uniformity with the Calibre comment format

### version 1.3.4
Clean text fully bold

### version 1.3.3
Clean a very rare invalid comment fomat (all in \<sub\>/\<sup\>)

### version 1.3.2
[Fix] convert to list a plain text beginning with a year

### version 1.3.1
Reduce the height of the configuration window

### version 1.3
Improvements of mass edit:
- Add a progres bar window and possibility to cancel the current operation
- *(internal)* Don't update the unchanged comments in the Database

Add new options for the cleaning:
- Round the Weights value instead of truncated
- Remove Strikethrough, Underline and Italic
- Try a conversion from Markdown format (the key word is TRY)
- Management of empty paragraphs
- Convert 'Line Return' into paragraph
- Specific alignment for lists
- Remove all formatting (NO MERCY!!)

and a lot of improvements for the cleaning. *(internal, too many)*

### version 1.2.2
[Fix] rare issue with *LibraryDatabase()*

### version 1.2.1
[Fix] error when loading the Spanish translation 

### version 1.2.0
Support translation
Spanish translation by *dunhill*

### version 1.1.0
- Add a option for Multiple Line Return.
- Add a option for the Headings.
- Add a option for the ID and CLASS attributs.

### version 1.0.0
Strategy change: All CSS rules are removed. Only a handful basic rules as keep.
- Add a option to specify additional CSS rules to keep.
- Saving parameters in a JSON (common to all libraries). ***Your settings will be reset!!***
- Add an option to remove 'Multiple Line Return' and create a new paragraph instead.

### version 0.3.1
[Fix] Transforms non-html (full text) comments to HTML

### version 0.3
Add option for the Weight

### version 0.2.1
Add "*Delete all align*" in the justification option

### version 0.2
First release