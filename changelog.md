# Changelog - Comments Cleaner

## [1.14.0] - 2024/08/05

### Added
- Possibility of keeping all CSS rules

## [1.13.0] - 2024/02/19

### Added
- Support drag-and-drop books from the library

### Bug fixes
- Fix some untranslated string

## [1.12.2] - 2024/02/10

### Bug fixes
- Fix some wrong bold cleaning

## [1.12.1] - 2024/01/27

### Bug fixes
- Fix wrong text display when customizing keyboard shortcut

## [1.12.0] - 2023/11/17

### Added
- Support for Category Notes
- Option for the images

### Changed
- Drop Python 2 / Calibre 4 compatibility, only Calibre 5 and above

### Bug fixes
- Tags with CAPS name don't propely parsed

## [0.11.1] - 2023/09/31

### Bug fixes
- Don't update the config file when Calibre start

## [1.11.0] - 2023/09/08

### Changed
- Fix double ScrollArea in config dialog

## [1.10.0] - 2023/04/10

### Added
- Support of custom HTML columns

## [1.9.0] - 2022/10/19

### Changed
- Again, big rework of common_utils (use submodule)

## [1.8.0] - 2022/10/11

### Changed
- Big rework of common_utils.py

## [1.7.3] - 2022/09/08

### Bug fixes
- Icon not display when a theme colors is used

## [1.7.2] - 2022/08/17

### Changed
- Small improvement of XMLentity

## [1.7.1] - 2022/07/19

### Changed
- Small improvement of compatibility betwen multiple Calibre version

## [1.7.0] - 2022/07/18

### Changed
- Small technical change for compatibility with Calibre 6

## [1.6.3] - 2022/04/25

### Changed
- Improve a bad parse for raw text comment but containing `<br>` tags

## [1.6.2] - 2022/02/22

### Changed
- Various technical improvement

## [1.6.1] - 2022/01/08

### Bug fixes
- Fix a regression of "del align for list `<li>`"

## [1.6.0] - 2022/01/04

### Changed
- Compatible Calibre6/Qt6

## [1.5.0] - 2021/10/31

### Added
- Improvement of "Single 'Line return'" option: Replace by Space, by new paragraph, no change

## [1.4.1] - 2021/10/03

### Changed
- Clean text full heading

### Bug fixes
- The text of progress dialog is correctly translated, FINALY! \o/

## [1.4.0] - 2021/09/11

### Changed
- Better support of small screens for the config dialog
- Improve `<br>` in `<strong>`/`<em>`
- Improve clean for text fully bold and `<sub>`/`<sup>` paragraphe
- Improved uniformity with the Calibre comment format

## [1.3.4] - 2021/08/30

### Changed
- Clean text fully bold

## [1.3.3] - 2021/08/17

### Changed
- Clean a very rare invalid comment fomat (all in `<sub>`/`<sup>`)

## [1.3.2] - 2021/01/07

### Bug fixes
- Fix convert to list a plain text beginning with a year

## [1.3.1] - 2020/11/26

### Changed
- Reduce the height of the configuration window

## [1.3.0] - 2021/01/07

### Added
- Add new options for the cleaning:
  - Round the Weights value instead of truncated
  - Remove Strikethrough, Underline and Italic
  - Try a conversion from Markdown format (the key word is TRY)
  - Management of empty paragraphs
  - Convert 'Line Return' into paragraph
  - Specific alignment for lists
  - Remove all formatting (NO MERCY!!)

### Changed
- Improvements of mass edit:
  - Add a progres bar window and possibility to cancel the current operation
  - Don't update the unchanged comments in the Database
- and a lot of improvements for the cleaning.

## [1.2.2] - 2020/11/26

### Bug fixes
- Fix rare issue with `LibraryDatabase()`

## [1.2.1] - 2020/11/16

### Bug fixes
- Fix error when loading the Spanish translation 

## [1.2.0] - 2020/10/12

### Added
- Support translation
- Spanish translation by *dunhill*

## [1.1.0] - 2020/10/12

### Added
- Add a option for Multiple Line Return.
- Add a option for the Headings.
- Add a option for the ID and CLASS attributs.

## [1.0.0] - 2020/10/11

### Added/Changed
- Strategy change: All CSS rules are removed. Only a handful basic rules as keep.
  - Add a option to specify additional CSS rules to keep.
  - Saving parameters in a JSON (common to all libraries). ***Your settings will be reset!!***
  - Add an option to remove 'Multiple Line Return' and create a new paragraph instead.

## [0.3.1] - 2020/10/09

### Added
- Transforms non-html (full text) comments to HTML

## [0.3.0] - 2020/10/09

### Added
- Add option for the Weight

## [0.2.1] - 2020/10/08

### Added
- Add "*Delete all align*" in the justification option

## [0.2.0] - 2020/10/08

### First release
