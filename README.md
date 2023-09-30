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
* Removing images
* Ability to specify others CSS rules to keep in addition to the basic CSS rule
* Possibility to apply the cleaning to others custom HTML columns
* Support of Category Notes


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

The plugin works for Calibre 5 and later.

Page: [GitHub](https://github.com/un-pogaz/Comments-Cleaner) | [MobileRead](https://www.mobileread.com/forums/showthread.php?t=333861)

<ins>Note for those who wish to provide a translation:</ins><br>
I am *French*! Although for obvious reasons, the default language of the plugin is English, keep in mind that already a translation.


<br><br>

![configuration panel](https://raw.githubusercontent.com/un-pogaz/Comments-Cleaner/main/static/Comments_Cleaner.png)
![button menu](https://raw.githubusercontent.com/un-pogaz/Comments-Cleaner/main/static/Comments_Cleaner-menu.png)
![example of cleaned comment](https://raw.githubusercontent.com/un-pogaz/Comments-Cleaner/main/static/Comments_Cleaner-exemple.gif)
![selection of notes to clean](https://raw.githubusercontent.com/un-pogaz/Comments-Cleaner/main/static/Comments_Cleaner-notes.png)


[mobileread-url]: https://www.mobileread.com/forums/showthread.php?t=333861

[changelog-image]: https://img.shields.io/badge/History-CHANGELOG-blue.svg
[changelog-url]: changelog.md

[license-image]: https://img.shields.io/badge/License-GPL-yellow.svg
[license-url]: LICENSE

[calibre-image]: https://img.shields.io/badge/calibre-2.00.0_and_above-green?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAllJREFUOMt1kz1MU1EUx3/3fZSP0lJLgVqRNqCDHxApAWcXF9O4oomDcXU06iIuLgxuTi4mrm7GRI2LiYOJ4ldAiBqxqSA2lEc/oNC+d991eI8HRnuGm3tzzv2d/znnXpEb5CHQDoCi8LigruHbrXOTs6Wl6qnkcPTd7SdvTvMfM/I1LgnhHYSgePHm9APheMAbV8e+mZoaR7BCCzMyEehNJXCky0bR2tJcdx7Nc+at0POjiQYokWkJABgcTlGv72AVLXRdQ9d0XKUob4uyF6aGWgE0gO36Jq7dBEBKl6Zt4zgO5bpe8uO6P768HGupACVRrvzHWdwMWbAFwHx96uy9u+UTc68WcmcuTCqljNzMFL80gCNDMfr6O0Eh9gOWq2YZsAFWGyNXYv3h6cLnyph0mllhMBGU8HVxleKKBQIFcKiv1y8HF1gG6NGXqqF2E8cGx3bQYSwA/Mxb1CrbQWYlwDT86iAPMGDMSYDIAcHGagUF4wEgnQ4Tj5t7AFehacLvssgDpPSFMGDH+kKUlssA2aCJ9a0GXV1GADBNA0e6u7g8gC4aaWBxMjc62tbeBpC6/oikBlCtNNmsNQKAbUtPvLf+8DcZJXgfTyYIxyLeCDWyGoAmFNWaDEYgpYNhmP49TwEQ6aT25a85Kx/QHVYkoq6fE1ylgnfhCrkLYDD0YW3/fQFZ7XsVXizAs3ko1Ij0J3pIpw5yOJkk3NHRefJ1egVoABw3nu4Ack8AWWM4yk7wnWHtd2k9Wiytt/kpLGbuuPcnRl27KRsDI/Fj6jxvhcBU8EkoZv8AURDxq1Vav0YAAAAASUVORK5CYII=
[calibre-url]: https://www.calibre-ebook.com/

[status-image]: https://img.shields.io/badge/Status-Stable-green

[mobileread-image]: https://img.shields.io/badge/MobileRead-Plugin%20Thread-blue?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAACJUlEQVQ4EZ3SX0hTYRjH8e+79DQcm5pGba0pQizrJhiMvJDwj3dR2SIoqK68CYouy24sb/TKbsuyC4kwG3gVBpUlqP1hBaUxiMp5aLZyzdn847E6+YQHDkNv+ty88PI8Px6e91XvJ5Nm9MU44t10GjuXplFV5qZIK6SyrARRHdgWAPbvqfT1A6jo8Buz73WcfAf3VnGqMczC4jKJbz9YWDJWzwxiIvkdMf41TQHrKE5P8XxgBP3lI0RraysiFKxAlA4NIRYNz/oBK3qcG7d7EEOrxbFYjFAohOjt7UX4/X5mYk9xlBe7yJf5mZMmcrkcg4ODuN1uLNlslubmZurq6tAcJv+W2DbwjHwNHgNjfo5IJILX68Uioe3t7RjGCq7tAQrYQG19E9UVXoRMMzY2Rk1NDcFgkM7OTq4/GEE42IBrs4adrut0dHSQTCYRiXSWrW4X6oOe0i9Hn/jJU79rpxQgJmcyzBu/sJMnbDtyAAVw/Npdk/9w78IJpVgjHyo385lEIo5Ir3hY/q3wObPYoblR5UEqyko43RhWCpupqwHzz2IO8Uqr5dKdCS6ePUkkME02FsXia+lHq2pQ9iVifHpsNQsOnzlPOBymu+8hpce6FTZLH4exFLBGOUuxM768pauri1QqRaBozpy9dQiLw1mCRWGTud9i2kfVfLvZ5CxmeXoCmc66850bVesGiIVYjzk7ehMjGceucMsO3PuO4mm6orD5CzQt1i+ddfLfAAAAAElFTkSuQmCC
