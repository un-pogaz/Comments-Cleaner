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
from polyglot.builtins import iteritems, itervalues

try:
    load_translations()
except NameError:
    pass # load_translations() added in calibre 1.9

from collections import defaultdict, OrderedDict
from functools import partial

try:
    from qt.core import (
        Qt, QCheckBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
        QLineEdit, QPushButton, QScrollArea,
        QVBoxLayout, QWidget,
    )
except ImportError:
    from PyQt5.Qt import (
        Qt, QCheckBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
        QLineEdit, QPushButton, QScrollArea,
        QVBoxLayout, QWidget,
    )

from .common_utils import debug_print, get_icon, GUI, PREFS_json, regex, calibre_version
from .common_utils.dialogs import KeyboardConfigDialogButton
from .common_utils.widgets import ImageTitleLayout, KeyValueComboBox, SelectNotesWidget, SelectFieldValuesWidget


PLUGIN_ICON = 'images/plugin.png'
NOTES_ICON = 'images/notes.png'

class KEY:
    KEEP_URL = 'KeepUrl'
    HEADINGS = 'Headings'
    FONT_WEIGHT = 'FontWeight'
    DEL_ITALIC = 'RemoveItalic'
    DEL_UNDER = 'RemoveUnderline'
    DEL_STRIKE = 'RemoveStrikethrough'
    FORCE_JUSTIFY = 'ForceJustify'
    LIST_ALIGN = 'ListAlign'
    ID_CLASS = 'ID_Class'
    CSS_KEEP = 'CSStoKeep'
    
    DEL_FORMATTING = 'RemoveFormatting'
    
    MARKDOWN = 'Markdown'
    DOUBLE_BR = 'DoubleBR'
    SINGLE_BR = 'SingleBR'
    EMPTY_PARA = 'EmptyParagraph'
    IMG_TAG = 'ImgTag'
    
    CUSTOM_COLUMN = 'CustomColumn'
    
    NOTES_SETTINGS = 'NotesSettings'

KEEP_URL = OrderedDict([
                    ('keep', _('Keep URL')),
                    ('del', _('Delete URL'))])

HEADINGS = OrderedDict([
                        ('conv', _('Converte to a paragraph')),
                        ('bolder', _('Converte to a paragraph but keep the bold')),
                        ('none', _('No change'))])

FONT_WEIGHT = OrderedDict([
                        ('trunc', _('Round the Weights value to the hundred')),
                        ('bold', _("Round to Bold (value 'bold')")),
                        ('none', _('Do not change the Weights')),
                        ('del', _('Delete Weights'))])
FONT_WEIGHT_ALT = _('Round to Bold (value 600)')

FORCE_JUSTIFY = OrderedDict([
                        ('all', _('Force the justification (replace "center" and "right")')),
                        ('empty', _('Justification for indeterminate text (keep "center" and "right")')),
                        ('none', _('No change')),
                        ('del', _('Delete all alignment'))])

LIST_ALIGN = OrderedDict([
                    ('keep', _("Use the 'Justification' setting")),
                    ('del', _('Delete the alignment in lists'))])

ID_CLASS = OrderedDict([
                        ('id', _('Delete "id" attribut')),
                        ('class', _('Delete "class" attribut')),
                        ('id_class', _('Delete "id" and "class" attribut')),
                        ('none', _('No change'))])


MARKDOWN = OrderedDict([
                        ('always', _('Convert in all comments (not recomanded)')),
                        ('try', _('Convert only from a plain text comment')),
                        ('none', _('No change'))])

DOUBLE_BR = OrderedDict([
                        ('empty', _('Create a empty paragraph')),
                        ('new', _('Create a new paragraph')),
                        ('none', _('No change'))])

SINGLE_BR = OrderedDict([
                        ('para', _('Create a new paragraph')),
                        ('space', _('Replace with space')),
                        ('none', _('No change'))])

EMPTY_PARA = OrderedDict([
                        ('merge', _('Merge in a single empty paragraph')),
                        ('none', _('No change')),
                        ('del', _('Delete empty paragraph'))])

IMG_TAG = OrderedDict([
                    ('keep', _('Keep images')),
                    ('del', _('Delete images'))])


# Set defaults
_defaults = {}
_defaults[KEY.KEEP_URL] = 'keep'
_defaults[KEY.HEADINGS] = 'none'
_defaults[KEY.FONT_WEIGHT] = 'bold'
_defaults[KEY.DEL_ITALIC] = False
_defaults[KEY.DEL_UNDER] = False
_defaults[KEY.DEL_STRIKE] = False
_defaults[KEY.FORCE_JUSTIFY] = 'empty'
_defaults[KEY.LIST_ALIGN] = 'del'
_defaults[KEY.ID_CLASS] = 'id_class'
_defaults[KEY.CSS_KEEP] = ''

_defaults[KEY.DEL_FORMATTING] = False

_defaults[KEY.MARKDOWN] = 'try'
_defaults[KEY.DOUBLE_BR] = 'new'
_defaults[KEY.SINGLE_BR] = 'none'
_defaults[KEY.EMPTY_PARA] = 'merge'
_defaults[KEY.IMG_TAG] = 'del'

# This is where all preferences for this plugin are stored
PREFS = PREFS_json()
PREFS.defaults = _defaults
PREFS.defaults[KEY.CUSTOM_COLUMN] = False
PREFS.defaults[KEY.NOTES_SETTINGS] = _defaults.copy()
PREFS.defaults[KEY.NOTES_SETTINGS][KEY.IMG_TAG] = 'keep'


#fix a imcompatibility betwen multiple Calibre version
CALIBRE_VERSIONS_BOLD = calibre_version < (4,0,0) or calibre_version >= (6,0,0)

if not CALIBRE_VERSIONS_BOLD:
    FONT_WEIGHT['bold'] = FONT_WEIGHT_ALT

if calibre_version >= (6,0,0):
    del FONT_WEIGHT['trunc']
    if PREFS[KEY.FONT_WEIGHT] == 'trunc':
        PREFS[KEY.FONT_WEIGHT] = 'bold'

try:
    import calibre.gui2.dialogs.edit_category_notes
    CALIBRE_HAS_NOTES = True
except:
    CALIBRE_HAS_NOTES = False


def css_clean_rules(css):
    #remove space and invalid character
    css = regex.loop(r'[.*!()?+<>\\]', r'', css.lower())
    css = regex.loop(r'(,|;|:|\n|\r|\s{2,})', r' ', css)
    css = regex.simple(r'^\s*(.*?)\s*$', r'\1', css)
    # split to table and remove duplicate
    css = list(set(css.split(' ')))
    # sort
    css = sorted(css)
    # join in a string
    css = ' '.join(css)
    return css


def _build_options_GroupBox(parent, layout, prefs):
    
    # -- options HTML --
    groupboxHTML = QGroupBox(' ', parent)
    layout.addWidget(groupboxHTML)
    
    grid_layoutHTML = QGridLayout()
    groupboxHTML.setLayout(grid_layoutHTML)
    
    
    grid_layoutHTML.addWidget(QLabel(_('Hyperlink:'), parent), 0, 0, 1, 2)
    parent.comboBoxKEEP_URL = KeyValueComboBox(parent, KEEP_URL, prefs[KEY.KEEP_URL])
    grid_layoutHTML.addWidget(parent.comboBoxKEEP_URL, 1, 0, 1, 2)
    
    grid_layoutHTML.addWidget(QLabel(_('Headings:'), parent), 0, 2, 1, 2)
    parent.comboBoxHEADINGS = KeyValueComboBox(parent, HEADINGS, prefs[KEY.HEADINGS])
    grid_layoutHTML.addWidget(parent.comboBoxHEADINGS, 1, 2, 1, 2)
    
    
    grid_layoutHTML.addWidget(QLabel(' ', parent), 4, 0)
    
    parent.comboBoxFONT_WEIGHT = KeyValueComboBox(parent, FONT_WEIGHT, prefs[KEY.FONT_WEIGHT])
    grid_layoutHTML.addWidget(parent.comboBoxFONT_WEIGHT, 5, 0, 1, 2)
    
    parent.checkBoxDEL_ITALIC = QCheckBox(_('Remove Italic'), parent)
    parent.checkBoxDEL_ITALIC.setChecked(prefs[KEY.DEL_ITALIC])
    grid_layoutHTML.addWidget(parent.checkBoxDEL_ITALIC, 5, 2, 1, 2)
    
    parent.checkBoxDEL_UNDER = QCheckBox(_('Remove Underline'), parent)
    parent.checkBoxDEL_UNDER.setChecked(prefs[KEY.DEL_UNDER])
    grid_layoutHTML.addWidget(parent.checkBoxDEL_UNDER, 6, 0, 1, 2)
    
    parent.checkBoxDEL_STRIKE = QCheckBox(_('Remove Strikethrough'), parent)
    parent.checkBoxDEL_STRIKE.setChecked(prefs[KEY.DEL_STRIKE])
    grid_layoutHTML.addWidget(parent.checkBoxDEL_STRIKE, 6, 2, 1, 2)
    
    grid_layoutHTML.addWidget(QLabel(' ', parent), 9, 0)
    
    
    grid_layoutHTML.addWidget(QLabel(_('Justification:'), parent), 10, 0, 1, 1)
    parent.comboBoxFORCE_JUSTIFY = KeyValueComboBox(parent, FORCE_JUSTIFY, prefs[KEY.FORCE_JUSTIFY])
    grid_layoutHTML.addWidget(parent.comboBoxFORCE_JUSTIFY, 10, 1, 1, 3)
    
    grid_layoutHTML.addWidget(QLabel(_('List alignment:'), parent), 11, 0, 1, 1)
    parent.comboBoxLIST_ALIGN = KeyValueComboBox(parent, LIST_ALIGN, prefs[KEY.LIST_ALIGN])
    grid_layoutHTML.addWidget(parent.comboBoxLIST_ALIGN, 11, 1, 1, 3)
    
    grid_layoutHTML.addWidget(QLabel(_('ID & CLASS attributs:'), parent), 12, 0, 1, 1)
    parent.comboBoxID_CLASS = KeyValueComboBox(parent, ID_CLASS, prefs[KEY.ID_CLASS])
    grid_layoutHTML.addWidget(parent.comboBoxID_CLASS, 12, 1, 1, 3)
    
    
    grid_layoutHTML.addWidget(QLabel(' ', parent))
    
    grid_layoutHTML.addWidget(QLabel(_('CSS rule to keep:'), parent), 20, 0, 1, 1)
    parent.lineEditCSS_KEEP = QLineEdit(parent)
    parent.lineEditCSS_KEEP.setText(prefs[KEY.CSS_KEEP])
    parent.lineEditCSS_KEEP.setToolTip(_('Custom CSS rules to keep in addition to the basic ones. Rules separated by a space.'))
    grid_layoutHTML.addWidget(parent.lineEditCSS_KEEP, 20, 1, 1, 3)
    
    def action_checkBoxDEL_FORMATTING(num):
        b = not parent.checkBoxDEL_FORMATTING.isChecked()
        
        parent.comboBoxKEEP_URL.setEnabled(b)
        parent.comboBoxHEADINGS.setEnabled(b)
        parent.comboBoxFONT_WEIGHT.setEnabled(b)
        parent.checkBoxDEL_ITALIC.setEnabled(b)
        parent.checkBoxDEL_UNDER.setEnabled(b)
        parent.checkBoxDEL_STRIKE.setEnabled(b)
        parent.comboBoxFORCE_JUSTIFY.setEnabled(b)
        parent.comboBoxLIST_ALIGN.setEnabled(b)
        parent.comboBoxID_CLASS.setEnabled(b)
        parent.lineEditCSS_KEEP.setEnabled(b)
    
    parent.checkBoxDEL_FORMATTING = QCheckBox(_('Remove all formatting'), parent)
    parent.checkBoxDEL_FORMATTING.stateChanged.connect(action_checkBoxDEL_FORMATTING)
    parent.checkBoxDEL_FORMATTING.setChecked(prefs[KEY.DEL_FORMATTING])
    layout.addWidget(parent.checkBoxDEL_FORMATTING)
    
    # -- options TEXT --
    groupboxTEXT = QGroupBox(' ', parent)
    layout.addWidget(groupboxTEXT)
    
    grid_layoutTEXT = QGridLayout()
    groupboxTEXT.setLayout(grid_layoutTEXT)
    
    grid_layoutTEXT.addWidget(QLabel(_('Markdown:'), parent), 1, 0, 1, 1)
    parent.comboBoxMARKDOWN = KeyValueComboBox(parent, MARKDOWN, prefs[KEY.MARKDOWN])
    grid_layoutTEXT.addWidget(parent.comboBoxMARKDOWN, 1, 1, 1, 2)
    parent.comboBoxMARKDOWN.setToolTip(_('Try to convert the Markdown strings to HTML'))
    
    grid_layoutTEXT.addWidget(QLabel(_("Multiple 'Line Return' in a paragraph:"), parent), 2, 0, 1, 1)
    parent.comboBoxDOUBLE_BR = KeyValueComboBox(parent, DOUBLE_BR, prefs[KEY.DOUBLE_BR])
    grid_layoutTEXT.addWidget(parent.comboBoxDOUBLE_BR, 2, 1, 1, 2)
    
    grid_layoutTEXT.addWidget(QLabel(_("Single 'Line Return' in a paragraph:"), parent), 3, 0, 1, 1)
    parent.comboBoxSINGLE_BR = KeyValueComboBox(parent, SINGLE_BR, prefs[KEY.SINGLE_BR])
    parent.comboBoxSINGLE_BR.setToolTip(_('This operation is applied after "Multiple \'Line Return\' in a paragraph"\n'+
                                          'and before "Multiple empty paragraph"'))
    grid_layoutTEXT.addWidget(parent.comboBoxSINGLE_BR, 3, 1, 1, 2)
    
    grid_layoutTEXT.addWidget(QLabel(_('Multiple empty paragraph:'), parent), 4, 0, 1, 1)
    parent.comboBoxEMPTY_PARA = KeyValueComboBox(parent, EMPTY_PARA, prefs[KEY.EMPTY_PARA])
    grid_layoutTEXT.addWidget(parent.comboBoxEMPTY_PARA, 4, 1, 1, 2)
    
    grid_layoutTEXT.addWidget(QLabel(_('Images:'), parent), 5, 0, 1, 1)
    parent.comboBoxIMG_TAG = KeyValueComboBox(parent, IMG_TAG, prefs[KEY.IMG_TAG])
    grid_layoutTEXT.addWidget(parent.comboBoxIMG_TAG, 5, 1, 1, 2)

def _retrive_option(parent, prefs):
    
    prefs[KEY.KEEP_URL] = parent.comboBoxKEEP_URL.selected_key()
    prefs[KEY.HEADINGS] = parent.comboBoxHEADINGS.selected_key()
    prefs[KEY.FONT_WEIGHT] = parent.comboBoxFONT_WEIGHT.selected_key()
    prefs[KEY.DEL_ITALIC] = parent.checkBoxDEL_ITALIC.isChecked()
    prefs[KEY.DEL_UNDER] = parent.checkBoxDEL_UNDER.isChecked()
    prefs[KEY.DEL_STRIKE] = parent.checkBoxDEL_STRIKE.isChecked()
    prefs[KEY.FORCE_JUSTIFY] = parent.comboBoxFORCE_JUSTIFY.selected_key()
    prefs[KEY.LIST_ALIGN] = parent.comboBoxLIST_ALIGN.selected_key()
    prefs[KEY.ID_CLASS] = parent.comboBoxID_CLASS.selected_key()
    
    prefs[KEY.CSS_KEEP] = css_clean_rules(parent.lineEditCSS_KEEP.text())
    
    prefs[KEY.DEL_FORMATTING] = parent.checkBoxDEL_FORMATTING.isChecked()
    
    prefs[KEY.MARKDOWN] = parent.comboBoxMARKDOWN.selected_key()
    prefs[KEY.DOUBLE_BR] = parent.comboBoxDOUBLE_BR.selected_key()
    prefs[KEY.SINGLE_BR] = parent.comboBoxSINGLE_BR.selected_key()
    prefs[KEY.EMPTY_PARA] = parent.comboBoxEMPTY_PARA.selected_key()
    prefs[KEY.IMG_TAG] = parent.comboBoxIMG_TAG.selected_key()
    
    return prefs


class ConfigWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        if calibre_version < (6,26,0):
            # Make dialog box scrollable (for smaller screens)
            scrollable = QScrollArea()
            scrollcontent = QWidget()
            scrollable.setWidget(scrollcontent)
            scrollable.setWidgetResizable(True)
            layout.addWidget(scrollable)
            
            layout = QVBoxLayout()
            scrollcontent.setLayout(layout)
        
        title_layout = ImageTitleLayout(self, PLUGIN_ICON, _('Comments Cleaner Options'))
        layout.addLayout(title_layout)
        
        # --- options ---
        _build_options_GroupBox(self, layout, PREFS)
        
        # --- Custom columns ---
        self.checkBoxCUSTOM_COLUMN = QCheckBox(_('Apply to others custom HTML columns'), self)
        self.checkBoxCUSTOM_COLUMN.setChecked(PREFS[KEY.CUSTOM_COLUMN])
        layout.addWidget(self.checkBoxCUSTOM_COLUMN)
        
        # --- Keyboard shortcuts ---
        if CALIBRE_HAS_NOTES:
            layout.addWidget(QLabel(' ', self))
            button_layout = QHBoxLayout()
            layout.addLayout(button_layout)
            
            button_layout.addStretch(1)
            button_layout.addWidget(NoteConfigDialogButton(self)) 
        
        # --- Keyboard shortcuts ---
        layout.addWidget(QLabel(' ', self))
        layout.addWidget(KeyboardConfigDialogButton(self))
        layout.addStretch(1)
    
    def save_settings(self):
        
        with PREFS:
            
            _retrive_option(self, PREFS)
            
            PREFS[KEY.CUSTOM_COLUMN] = self.checkBoxCUSTOM_COLUMN.isChecked()
        
        prefs = PREFS.copy()
        prefs.pop(KEY.NOTES_SETTINGS, None)
        
        debug_print('Save settings:', prefs, '\n')


# workaround to run one Calibre 2
try:
    from calibre.gui2.widgets2 import Dialog
except:
    class Dialog():
        pass

class NoteConfigDialogButton(QPushButton):
    
    def __init__(self, parent=None):
        QPushButton.__init__(self, get_icon(NOTES_ICON), _('Notes Cleaner Options'), parent)
        self.setToolTip(_('Edit the options for the notes cleaner action'))
        self.clicked.connect(self.edit_notes_options)

    def edit_notes_options(self):
        d = ConfigNotesDialog()
        d.exec()

class ConfigNotesDialog(Dialog):
    def __init__(self):
        Dialog.__init__(self,
            parent=GUI,
            title=_('Customize') + ' ' + _('Notes Cleaner'),
            name = 'plugin config dialog:User Action Interface:Notes Cleaner',
        )
    
    def setup_ui(self):
        v = QVBoxLayout(self)
        
        scrollable = QScrollArea()
        v.addWidget(scrollable)
        v.addWidget(self.bb)
        
        # Make dialog box scrollable (for smaller screens)
        scrollcontent = QWidget()
        scrollable.setWidget(scrollcontent)
        scrollable.setWidgetResizable(True)
        layout = QVBoxLayout()
        scrollcontent.setLayout(layout)
        
        
        title_layout = ImageTitleLayout(self, NOTES_ICON, _('Notes Cleaner Options'))
        layout.addLayout(title_layout)
        
        prefs = PREFS.defaults[KEY.NOTES_SETTINGS].copy()
        prefs.update(PREFS[KEY.NOTES_SETTINGS].copy())
        
        # --- options ---
        _build_options_GroupBox(self, layout, prefs)
        
        # --- Keyboard shortcuts ---
        layout.addWidget(QLabel(' ', self))
        layout.addWidget(KeyboardConfigDialogButton(self))
        layout.addStretch(1)
    
    def accept(self):
        
        with PREFS:
            prefs = _retrive_option(self, PREFS[KEY.NOTES_SETTINGS])
            PREFS[KEY.NOTES_SETTINGS] = prefs
        
        debug_print('Notes settings:', prefs, '\n')
        Dialog.accept(self)


class SelectNotesDialog(Dialog):
    def __init__(self, book_ids=[]):
        
        self.book_ids = book_ids
        self.selected_notes = {}
        
        Dialog.__init__(self,
            parent=GUI,
            title= _('Select Notes to clean'),
            name = 'plugin config dialog:User Action Interface:Select Notes to clean',
        )
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tree_view = SelectNotesWidget(book_ids=self.book_ids)
        layout.addWidget(self.tree_view)
        self.tree_view.update_texts(
            tooltip=_('Subset of Notes associate to the currently selected books'),
            zero_book=_('No books selected'),
            zero_values=_('No notes for {:d} selected books'),
            has_book_values=_('Notes for {:d} selected books'),
        )
        
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        button_layout.addWidget(NoteConfigDialogButton(self)) 
        button_layout.addStretch(1)
        
        layout.addWidget(self.bb)
    
    def accept(self):
        self.selected_notes = self.tree_view.get_selected()
        Dialog.accept(self)
