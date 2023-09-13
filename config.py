#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <un.pogaz@gmail.com>'
__docformat__ = 'restructuredtext en'

import copy
# python3 compatibility
from six.moves import range
from six import text_type as unicode

try:
    load_translations()
except NameError:
    pass # load_translations() added in calibre 1.9

from datetime import datetime
from collections import defaultdict, OrderedDict
from functools import partial

try:
    from qt.core import QWidget, QGridLayout, QScrollArea, QLabel, QPushButton, QGroupBox, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QObject
except ImportError:
    from PyQt5.Qt import QWidget, QGridLayout, QScrollArea, QLabel, QPushButton, QGroupBox, QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox, QObject

from calibre import prints
from calibre.gui2.ui import get_gui

from .common_utils import debug_print, get_icon, GUI, PREFS_json, regex, calibre_version
from .common_utils.dialogs import edit_keyboard_shortcuts
from .common_utils.widgets import ImageTitleLayout, KeyValueComboBox


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
                        ('bold', _('Round to Bold (value \'bold\')')),
                        ('none', _('Do not change the Weights')),
                        ('del', _('Delete Weights'))])
FONT_WEIGHT_ALT = _('Round to Bold (value 600)')

FORCE_JUSTIFY = OrderedDict([
                        ('all', _('Force the justification (replace "center" and "right")')),
                        ('empty', _('Justification for indeterminate text (keep "center" and "right")')),
                        ('none', _('No change')),
                        ('del', _('Delete all alignment'))])

LIST_ALIGN = OrderedDict([
                    ('keep', _('Use the \'Justification\' setting')),
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


# Set defaults
defaults = {}
defaults[KEY.KEEP_URL] = 'keep'
defaults[KEY.HEADINGS] = 'none'
defaults[KEY.FONT_WEIGHT] = 'bold'
defaults[KEY.DEL_ITALIC] = False
defaults[KEY.DEL_UNDER] = False
defaults[KEY.DEL_STRIKE] = False
defaults[KEY.FORCE_JUSTIFY] = 'empty'
defaults[KEY.LIST_ALIGN] = 'del'
defaults[KEY.ID_CLASS] = 'id_class'
defaults[KEY.CSS_KEEP] = ''

defaults[KEY.DEL_FORMATTING] = False

defaults[KEY.MARKDOWN] = 'try'
defaults[KEY.DOUBLE_BR] = 'new'
defaults[KEY.SINGLE_BR] = 'none'
defaults[KEY.EMPTY_PARA] = 'merge'

# This is where all preferences for this plugin are stored
PREFS = PREFS_json()
PREFS.defaults = defaults
PREFS.defaults[KEY.CUSTOM_COLUMN] = False
PREFS.defaults[KEY.NOTES_SETTINGS] = defaults.copy()


#fix a imcompatibility betwen multiple Calibre version
CalibreVersions_Bold = calibre_version < (4,0,0) or calibre_version >= (6,0,0)

if not CalibreVersions_Bold:
    FONT_WEIGHT['bold'] = FONT_WEIGHT_ALT

if calibre_version >= (6,0,0):
    del FONT_WEIGHT['trunc']
    if PREFS[KEY.FONT_WEIGHT] == 'trunc':
        PREFS[KEY.FONT_WEIGHT] = 'bold'

CalibreHasNotes = False
try:
    import calibre.gui2.dialogs.edit_category_notes
    CalibreHasNotes = True
except:
    pass


def CSS_CleanRules(css):
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


def build_optionsHTML_GroupBox(parent, layout, prefs):
    rslt = QGroupBox(' ', parent)
    layout.addWidget(rslt)
    
    optionsHTML_GridLayout = QGridLayout()
    rslt.setLayout(optionsHTML_GridLayout)
    
    
    optionsHTML_GridLayout.addWidget(QLabel(_('Hyperlink:'), parent), 0, 0, 1, 2)
    parent.comboBoxKEEP_URL = KeyValueComboBox(parent, KEEP_URL, prefs[KEY.KEEP_URL])
    optionsHTML_GridLayout.addWidget(parent.comboBoxKEEP_URL, 1, 0, 1, 2)
    
    optionsHTML_GridLayout.addWidget(QLabel(_('Headings:'), parent), 0, 2, 1, 2)
    parent.comboBoxHEADINGS = KeyValueComboBox(parent, HEADINGS, prefs[KEY.HEADINGS])
    optionsHTML_GridLayout.addWidget(parent.comboBoxHEADINGS, 1, 2, 1, 2)
    
    
    optionsHTML_GridLayout.addWidget(QLabel(' ', parent), 4, 0)
    
    parent.comboBoxFONT_WEIGHT = KeyValueComboBox(parent, FONT_WEIGHT, prefs[KEY.FONT_WEIGHT])
    optionsHTML_GridLayout.addWidget(parent.comboBoxFONT_WEIGHT, 5, 0, 1, 2)
    
    parent.checkBoxDEL_ITALIC = QCheckBox(_('Remove Italic'), parent)
    parent.checkBoxDEL_ITALIC.setChecked(prefs[KEY.DEL_ITALIC])
    optionsHTML_GridLayout.addWidget(parent.checkBoxDEL_ITALIC, 5, 2, 1, 2)
    
    parent.checkBoxDEL_UNDER = QCheckBox(_('Remove Underline'), parent)
    parent.checkBoxDEL_UNDER.setChecked(prefs[KEY.DEL_UNDER])
    optionsHTML_GridLayout.addWidget(parent.checkBoxDEL_UNDER, 6, 0, 1, 2)
    
    parent.checkBoxDEL_STRIKE = QCheckBox(_('Remove Strikethrough'), parent)
    parent.checkBoxDEL_STRIKE.setChecked(prefs[KEY.DEL_STRIKE])
    optionsHTML_GridLayout.addWidget(parent.checkBoxDEL_STRIKE, 6, 2, 1, 2)
    
    optionsHTML_GridLayout.addWidget(QLabel(' ', parent), 9, 0)
    
    
    optionsHTML_GridLayout.addWidget(QLabel(_('Justification:'), parent), 10, 0, 1, 1)
    parent.comboBoxFORCE_JUSTIFY = KeyValueComboBox(parent, FORCE_JUSTIFY, prefs[KEY.FORCE_JUSTIFY])
    optionsHTML_GridLayout.addWidget(parent.comboBoxFORCE_JUSTIFY, 10, 1, 1, 3)
    
    optionsHTML_GridLayout.addWidget(QLabel(_('List alignment:'), parent), 11, 0, 1, 1)
    parent.comboBoxLIST_ALIGN = KeyValueComboBox(parent, LIST_ALIGN, prefs[KEY.LIST_ALIGN])
    optionsHTML_GridLayout.addWidget(parent.comboBoxLIST_ALIGN, 11, 1, 1, 3)
    
    optionsHTML_GridLayout.addWidget(QLabel(_('ID & CLASS attributs:'), parent), 12, 0, 1, 1)
    parent.comboBoxID_CLASS = KeyValueComboBox(parent, ID_CLASS, prefs[KEY.ID_CLASS])
    optionsHTML_GridLayout.addWidget(parent.comboBoxID_CLASS, 12, 1, 1, 3)
    
    
    optionsHTML_GridLayout.addWidget(QLabel(' ', parent))
    
    optionsHTML_GridLayout.addWidget(QLabel(_('CSS rule to keep:'), parent), 20, 0, 1, 1)
    parent.lineEditCSS_KEEP = QLineEdit(parent)
    parent.lineEditCSS_KEEP.setText(prefs[KEY.CSS_KEEP])
    parent.lineEditCSS_KEEP.setToolTip(_('Custom CSS rules to keep in addition to the basic ones. Rules separated by a space.'))
    optionsHTML_GridLayout.addWidget(parent.lineEditCSS_KEEP, 20, 1, 1, 3)
    
    return rslt

def build_optionsDEL_FORMATTING(parent, layout, prefs):
    parent.checkBoxDEL_FORMATTING = QCheckBox(_('Remove all formatting'), parent)
    parent.checkBoxDEL_FORMATTING.stateChanged.connect(partial(action_checkBox_click, parent))
    parent.checkBoxDEL_FORMATTING.setChecked(prefs[KEY.DEL_FORMATTING])
    layout.addWidget(parent.checkBoxDEL_FORMATTING)

def build_optionsTEXT_GroupBox(parent, layout, prefs):
        optionsTEXT_GroupBox = QGroupBox(' ', parent)
        layout.addWidget(optionsTEXT_GroupBox)
        
        optionsTEXT_GridLayout = QGridLayout()
        optionsTEXT_GroupBox.setLayout(optionsTEXT_GridLayout)
        
        optionsTEXT_GridLayout.addWidget(QLabel(_('Markdown:'), parent), 1, 0, 1, 1)
        parent.comboBoxMARKDOWN = KeyValueComboBox(parent, MARKDOWN, prefs[KEY.MARKDOWN])
        optionsTEXT_GridLayout.addWidget(parent.comboBoxMARKDOWN, 1, 1, 1, 2)
        parent.comboBoxMARKDOWN.setToolTip(_('Try to convert the Markdown strings to HTML'))
        
        optionsTEXT_GridLayout.addWidget(QLabel(_('Multiple \'Line Return\' in a paragraph:'), parent), 2, 0, 1, 1)
        parent.comboBoxDOUBLE_BR = KeyValueComboBox(parent, DOUBLE_BR, prefs[KEY.DOUBLE_BR])
        optionsTEXT_GridLayout.addWidget(parent.comboBoxDOUBLE_BR, 2, 1, 1, 2)
        
        optionsTEXT_GridLayout.addWidget(QLabel(_('Single \'Line Return\' in a paragraph:'), parent), 3, 0, 1, 1)
        parent.comboBoxSINGLE_BR = KeyValueComboBox(parent, SINGLE_BR, prefs[KEY.SINGLE_BR])
        parent.comboBoxSINGLE_BR.setToolTip(_('This operation is applied after "Multiple \'Line Return\' in a paragraph"\n'+
                                             'and before "Multiple empty paragraph"'))
        optionsTEXT_GridLayout.addWidget(parent.comboBoxSINGLE_BR, 3, 1, 1, 2)
        
        optionsTEXT_GridLayout.addWidget(QLabel(_('Multiple empty paragraph:'), parent), 4, 0, 1, 1)
        parent.comboBoxEMPTY_PARA = KeyValueComboBox(parent, EMPTY_PARA, prefs[KEY.EMPTY_PARA])
        optionsTEXT_GridLayout.addWidget(parent.comboBoxEMPTY_PARA, 4, 1, 1, 2)

def action_checkBox_click(parent, num):
    
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


class ConfigWidget(QWidget):
    def __init__(self, plugin_action):
        QWidget.__init__(self)
        
        self.plugin_action = plugin_action
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
        build_optionsHTML_GroupBox(self, layout, PREFS)
        build_optionsDEL_FORMATTING(self, layout, PREFS)
        build_optionsTEXT_GroupBox(self, layout, PREFS)
        
        # --- Custom columns ---
        self.checkBoxCUSTOM_COLUMN = QCheckBox(_('Apply to others custom HTML columns'), self)
        self.checkBoxCUSTOM_COLUMN.setChecked(PREFS[KEY.CUSTOM_COLUMN])
        layout.addWidget(self.checkBoxCUSTOM_COLUMN)
        
        # --- Keyboard shortcuts ---
        if CalibreHasNotes:
            layout.addWidget(QLabel(' ', self))
            button_layout = QHBoxLayout()
            layout.addLayout(button_layout)
            
            notes_options_button = QPushButton(get_icon(NOTES_ICON), _('Notes Cleaner Options'), self)
            notes_options_button.setToolTip(_('Edit the options for the notes cleaner action'))
            notes_options_button.clicked.connect(self.edit_notes_options)
            button_layout.addStretch(1)
            button_layout.addWidget(notes_options_button)
        
        # --- Keyboard shortcuts ---
        layout.addWidget(QLabel(' ', self))
        keyboard_shortcuts_button = QPushButton(_('Keyboard shortcuts')+'...', self)
        keyboard_shortcuts_button.setToolTip(_('Edit the keyboard shortcuts associated with this plugin'))
        keyboard_shortcuts_button.clicked.connect(self.edit_shortcuts)
        layout.addWidget(keyboard_shortcuts_button)
        layout.addStretch(1)
    
    def save_settings(self):
        
        with PREFS:
            PREFS[KEY.KEEP_URL] = self.comboBoxKEEP_URL.selected_key()
            PREFS[KEY.HEADINGS] = self.comboBoxHEADINGS.selected_key()
            PREFS[KEY.FONT_WEIGHT] = self.comboBoxFONT_WEIGHT.selected_key()
            PREFS[KEY.DEL_ITALIC] = self.checkBoxDEL_ITALIC.isChecked()
            PREFS[KEY.DEL_UNDER] = self.checkBoxDEL_UNDER.isChecked()
            PREFS[KEY.DEL_STRIKE] = self.checkBoxDEL_STRIKE.isChecked()
            PREFS[KEY.FORCE_JUSTIFY] = self.comboBoxFORCE_JUSTIFY.selected_key()
            PREFS[KEY.LIST_ALIGN] = self.comboBoxLIST_ALIGN.selected_key()
            PREFS[KEY.ID_CLASS] = self.comboBoxID_CLASS.selected_key()
            
            PREFS[KEY.CSS_KEEP] = CSS_CleanRules(self.lineEditCSS_KEEP.text())
            
            PREFS[KEY.DEL_FORMATTING] = self.checkBoxDEL_FORMATTING.isChecked()
            
            PREFS[KEY.MARKDOWN] = self.comboBoxMARKDOWN.selected_key()
            PREFS[KEY.DOUBLE_BR] = self.comboBoxDOUBLE_BR.selected_key()
            PREFS[KEY.SINGLE_BR] = self.comboBoxSINGLE_BR.selected_key()
            PREFS[KEY.EMPTY_PARA] = self.comboBoxEMPTY_PARA.selected_key()
            
            PREFS[KEY.CUSTOM_COLUMN] = self.checkBoxCUSTOM_COLUMN.isChecked()
        
        prefs = PREFS.copy()
        prefs.pop(KEY.NOTES_SETTINGS, None)
        
        debug_print('Save settings: {0}\n'.format(prefs))
        
    
    def edit_shortcuts(self):
        edit_keyboard_shortcuts(self.plugin_action)
    
    def edit_notes_options(self):
        d = ConfigNotesDialog()
        d.exec_()


# workaround to run one Calibre 2
try:
    from calibre.gui2.widgets2 import Dialog
except:
    class Dialog():
        pass

class ConfigNotesDialog(Dialog):
    
    def __init__(self):
        Dialog.__init__(self,
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
        
        
        prefs = PREFS[KEY.NOTES_SETTINGS]
        
        # --- options ---
        build_optionsHTML_GroupBox(self, layout, prefs)
        build_optionsDEL_FORMATTING(self, layout, prefs)
        build_optionsTEXT_GroupBox(self, layout, prefs)
        layout.addStretch(1)
    
    def accept(self):
        
        with PREFS:
            prefs = PREFS[KEY.NOTES_SETTINGS]
            
            prefs[KEY.KEEP_URL] = self.comboBoxKEEP_URL.selected_key()
            prefs[KEY.HEADINGS] = self.comboBoxHEADINGS.selected_key()
            prefs[KEY.FONT_WEIGHT] = self.comboBoxFONT_WEIGHT.selected_key()
            prefs[KEY.DEL_ITALIC] = self.checkBoxDEL_ITALIC.isChecked()
            prefs[KEY.DEL_UNDER] = self.checkBoxDEL_UNDER.isChecked()
            prefs[KEY.DEL_STRIKE] = self.checkBoxDEL_STRIKE.isChecked()
            prefs[KEY.FORCE_JUSTIFY] = self.comboBoxFORCE_JUSTIFY.selected_key()
            prefs[KEY.LIST_ALIGN] = self.comboBoxLIST_ALIGN.selected_key()
            prefs[KEY.ID_CLASS] = self.comboBoxID_CLASS.selected_key()
            
            prefs[KEY.CSS_KEEP] = CSS_CleanRules(self.lineEditCSS_KEEP.text())
            
            prefs[KEY.DEL_FORMATTING] = self.checkBoxDEL_FORMATTING.isChecked()
            
            prefs[KEY.MARKDOWN] = self.comboBoxMARKDOWN.selected_key()
            prefs[KEY.DOUBLE_BR] = self.comboBoxDOUBLE_BR.selected_key()
            prefs[KEY.SINGLE_BR] = self.comboBoxSINGLE_BR.selected_key()
            prefs[KEY.EMPTY_PARA] = self.comboBoxEMPTY_PARA.selected_key()
            
            PREFS[KEY.NOTES_SETTINGS] = prefs
        
        debug_print('Notes settings: {0}\n'.format(prefs))
        Dialog.accept(self)