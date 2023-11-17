#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <un.pogaz@gmail.com>'
__docformat__ = 'restructuredtext en'


try:
    load_translations()
except NameError:
    pass # load_translations() added in calibre 1.9

from collections import defaultdict, OrderedDict
from functools import partial
from typing import Any

try:
    from qt.core import (
        Qt, QCheckBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
        QVBoxLayout, QWidget,
    )
except ImportError:
    from PyQt5.Qt import (
        Qt, QCheckBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
        QVBoxLayout, QWidget,
    )

from calibre.gui2.widgets2 import Dialog

from .common_utils import debug_print, get_icon, GUI, PREFS_json, regex, CALIBRE_VERSION
from .common_utils.dialogs import KeyboardConfigDialogButton
from .common_utils.widgets import ImageTitleLayout, KeyValueComboBox, SelectNotesWidget


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
PREFS.defaults = _defaults.copy()
PREFS.defaults[KEY.CUSTOM_COLUMN] = False
PREFS.defaults[KEY.NOTES_SETTINGS] = _defaults.copy()
PREFS.defaults[KEY.NOTES_SETTINGS][KEY.IMG_TAG] = 'keep'
PREFS.defaults[KEY.NOTES_SETTINGS][KEY.CSS_KEEP] = 'float'


#fix a imcompatibility betwen multiple Calibre version
CALIBRE_VERSIONS_BOLD = CALIBRE_VERSION < (4,0,0) or CALIBRE_VERSION >= (6,0,0)

if not CALIBRE_VERSIONS_BOLD:
    FONT_WEIGHT['bold'] = FONT_WEIGHT_ALT

if CALIBRE_VERSION >= (6,0,0):
    del FONT_WEIGHT['trunc']
    if PREFS[KEY.FONT_WEIGHT] == 'trunc':
        PREFS[KEY.FONT_WEIGHT] = 'bold'

if CALIBRE_VERSION >= (7,0,0):
    CALIBRE_HAS_NOTES = True
else:
    CALIBRE_HAS_NOTES = False


def css_clean_rules(css: str) -> str:
    #remove space and invalid character
    css = regex.loop(r'[.*!()?+<>\\]', r'', css.lower())
    css = regex.loop(r'([,;:\n\r]|\s{2,})', r' ', css)
    css = regex.simple(r'^\s*(.*?)\s*$', r'\1', css)
    # split to table and remove duplicate
    css = list(set(css.split(' ')))
    # sort
    css = sorted(css)
    # join in a string
    css = ' '.join(css)
    return css


class CommonOptions(QWidget):
    def __init__(self, prefs: dict, parent: QWidget=None):
        QWidget.__init__(self, parent=parent)
        
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        # -- options HTML --
        groupboxHTML = QGroupBox(self)
        layout.addWidget(groupboxHTML)
        
        layoutHTML = QVBoxLayout(groupboxHTML)
        groupboxHTML.setLayout(layoutHTML)
        
        layout_gridHTML = QGridLayout()
        layoutHTML.addLayout(layout_gridHTML)
        
        layout_gridHTML.addWidget(QLabel(_('Hyperlink:'), self), 0, 0)
        self.comboBoxKEEP_URL = KeyValueComboBox(KEEP_URL, prefs[KEY.KEEP_URL], parent=groupboxHTML)
        layout_gridHTML.addWidget(self.comboBoxKEEP_URL, 1, 0)
        
        layout_gridHTML.addWidget(QLabel(_('Headings:'), self), 0, 1)
        self.comboBoxHEADINGS = KeyValueComboBox(HEADINGS, prefs[KEY.HEADINGS], parent=groupboxHTML)
        layout_gridHTML.addWidget(self.comboBoxHEADINGS, 1, 1)
        
        layout_gridHTML.addWidget(QLabel(' ', self), 2, 0)
        
        self.comboBoxFONT_WEIGHT = KeyValueComboBox(FONT_WEIGHT, prefs[KEY.FONT_WEIGHT], parent=groupboxHTML)
        layout_gridHTML.addWidget(self.comboBoxFONT_WEIGHT, 3, 0)
        
        self.checkBoxDEL_ITALIC = QCheckBox(_('Remove Italic'), groupboxHTML)
        self.checkBoxDEL_ITALIC.setChecked(prefs[KEY.DEL_ITALIC])
        layout_gridHTML.addWidget(self.checkBoxDEL_ITALIC, 3, 1)
        
        self.checkBoxDEL_UNDER = QCheckBox(_('Remove Underline'), groupboxHTML)
        self.checkBoxDEL_UNDER.setChecked(prefs[KEY.DEL_UNDER])
        layout_gridHTML.addWidget(self.checkBoxDEL_UNDER, 4, 0)
        
        self.checkBoxDEL_STRIKE = QCheckBox(_('Remove Strikethrough'), groupboxHTML)
        self.checkBoxDEL_STRIKE.setChecked(prefs[KEY.DEL_STRIKE])
        layout_gridHTML.addWidget(self.checkBoxDEL_STRIKE, 4, 1)
        
        
        layoutHTML.addWidget(QLabel(' ', groupboxHTML))
        
        
        layout_formHTML = QFormLayout()
        layout_formHTML.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        layout_formHTML.setFormAlignment(Qt.AlignRight)
        layoutHTML.addLayout(layout_formHTML)
        
        self.comboBoxFORCE_JUSTIFY = KeyValueComboBox(FORCE_JUSTIFY, prefs[KEY.FORCE_JUSTIFY], parent=groupboxHTML)
        layout_formHTML.addRow(_('Justification:'), self.comboBoxFORCE_JUSTIFY)
        self.comboBoxFORCE_JUSTIFY.setSizePolicy(size_policy)
        
        self.comboBoxLIST_ALIGN = KeyValueComboBox(LIST_ALIGN, prefs[KEY.LIST_ALIGN], parent=groupboxHTML)
        layout_formHTML.addRow(_('List alignment:'), self.comboBoxLIST_ALIGN)
        self.comboBoxLIST_ALIGN.setSizePolicy(size_policy)
        
        self.comboBoxID_CLASS = KeyValueComboBox(ID_CLASS, prefs[KEY.ID_CLASS], parent=groupboxHTML)
        layout_formHTML.addRow(QLabel(_('ID & CLASS attributs:')), self.comboBoxID_CLASS)
        self.comboBoxID_CLASS.setSizePolicy(size_policy)
        
        layout_formHTML.addWidget(QLabel(' ', self))
        
        self.lineEditCSS_KEEP = QLineEdit(groupboxHTML)
        layout_formHTML.addRow(_('CSS rule to keep:'), self.lineEditCSS_KEEP)
        self.lineEditCSS_KEEP.setText(prefs[KEY.CSS_KEEP])
        self.lineEditCSS_KEEP.setToolTip(_('Custom CSS rules to keep in addition to the basic ones. Rules separated by a space.'))
        self.lineEditCSS_KEEP.setSizePolicy(size_policy)
        
        def action_checkBoxDEL_FORMATTING(num):
            b = not self.checkBoxDEL_FORMATTING.isChecked()
            
            self.comboBoxKEEP_URL.setEnabled(b)
            self.comboBoxHEADINGS.setEnabled(b)
            self.comboBoxFONT_WEIGHT.setEnabled(b)
            self.checkBoxDEL_ITALIC.setEnabled(b)
            self.checkBoxDEL_UNDER.setEnabled(b)
            self.checkBoxDEL_STRIKE.setEnabled(b)
            self.comboBoxFORCE_JUSTIFY.setEnabled(b)
            self.comboBoxLIST_ALIGN.setEnabled(b)
            self.comboBoxID_CLASS.setEnabled(b)
            self.lineEditCSS_KEEP.setEnabled(b)
        
        self.checkBoxDEL_FORMATTING = QCheckBox(_('Remove all formatting'), self)
        self.checkBoxDEL_FORMATTING.stateChanged.connect(action_checkBoxDEL_FORMATTING)
        self.checkBoxDEL_FORMATTING.setChecked(prefs[KEY.DEL_FORMATTING])
        layout.addWidget(self.checkBoxDEL_FORMATTING)
        
        # ------
        layout.addWidget(QLabel(' ', self))
        
        # -- options TEXT --
        groupboxTEXT = QGroupBox(self)
        layout.addWidget(groupboxTEXT)
        
        layoutTEXT = QFormLayout(groupboxTEXT)
        layoutTEXT.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        layoutTEXT.setFormAlignment(Qt.AlignRight)
        groupboxTEXT.setLayout(layoutTEXT)
        
        self.comboBoxMARKDOWN = KeyValueComboBox(MARKDOWN, prefs[KEY.MARKDOWN], parent=groupboxTEXT)
        layoutTEXT.addRow(_('Markdown:'), self.comboBoxMARKDOWN)
        self.comboBoxMARKDOWN.setToolTip(_('Try to convert the Markdown strings to HTML'))
        self.comboBoxMARKDOWN.setSizePolicy(size_policy)
        
        self.comboBoxDOUBLE_BR = KeyValueComboBox(DOUBLE_BR, prefs[KEY.DOUBLE_BR], parent=groupboxTEXT)
        layoutTEXT.addRow(_("Multiple 'Line Return' in a paragraph:"), self.comboBoxDOUBLE_BR)
        self.comboBoxDOUBLE_BR.setSizePolicy(size_policy)
        
        self.comboBoxSINGLE_BR = KeyValueComboBox(SINGLE_BR, prefs[KEY.SINGLE_BR])
        layoutTEXT.addRow(_("Single 'Line Return' in a paragraph:"), self.comboBoxSINGLE_BR)
        self.comboBoxSINGLE_BR.setToolTip(_('This operation is applied after "Multiple \'Line Return\' in a paragraph"\n'+
                                              'and before "Multiple empty paragraph"'))
        self.comboBoxSINGLE_BR.setSizePolicy(size_policy)
        
        self.comboBoxEMPTY_PARA = KeyValueComboBox(EMPTY_PARA, prefs[KEY.EMPTY_PARA], parent=groupboxTEXT)
        layoutTEXT.addRow(_('Multiple empty paragraph:'), self.comboBoxEMPTY_PARA)
        self.comboBoxEMPTY_PARA.setSizePolicy(size_policy)
        
        self.comboBoxIMG_TAG = KeyValueComboBox(IMG_TAG, prefs[KEY.IMG_TAG], parent=groupboxTEXT)
        layoutTEXT.addRow(_('Images:'), self.comboBoxIMG_TAG)
        self.comboBoxIMG_TAG.setSizePolicy(size_policy)
    
    def get_option(self) -> dict:
        
        prefs = {}
        
        prefs[KEY.KEEP_URL] = self.comboBoxKEEP_URL.selected_key()
        prefs[KEY.HEADINGS] = self.comboBoxHEADINGS.selected_key()
        prefs[KEY.FONT_WEIGHT] = self.comboBoxFONT_WEIGHT.selected_key()
        prefs[KEY.DEL_ITALIC] = self.checkBoxDEL_ITALIC.isChecked()
        prefs[KEY.DEL_UNDER] = self.checkBoxDEL_UNDER.isChecked()
        prefs[KEY.DEL_STRIKE] = self.checkBoxDEL_STRIKE.isChecked()
        prefs[KEY.FORCE_JUSTIFY] = self.comboBoxFORCE_JUSTIFY.selected_key()
        prefs[KEY.LIST_ALIGN] = self.comboBoxLIST_ALIGN.selected_key()
        prefs[KEY.ID_CLASS] = self.comboBoxID_CLASS.selected_key()
        
        prefs[KEY.CSS_KEEP] = css_clean_rules(self.lineEditCSS_KEEP.text())
        
        prefs[KEY.DEL_FORMATTING] = self.checkBoxDEL_FORMATTING.isChecked()
        
        prefs[KEY.MARKDOWN] = self.comboBoxMARKDOWN.selected_key()
        prefs[KEY.DOUBLE_BR] = self.comboBoxDOUBLE_BR.selected_key()
        prefs[KEY.SINGLE_BR] = self.comboBoxSINGLE_BR.selected_key()
        prefs[KEY.EMPTY_PARA] = self.comboBoxEMPTY_PARA.selected_key()
        prefs[KEY.IMG_TAG] = self.comboBoxIMG_TAG.selected_key()
        
        return prefs


class ConfigWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        if CALIBRE_VERSION < (6,26,0):
            # Make dialog box scrollable (for smaller screens)
            scrollable = QScrollArea()
            scrollcontent = QWidget()
            scrollable.setWidget(scrollcontent)
            scrollable.setWidgetResizable(True)
            layout.addWidget(scrollable)
            
            layout = QVBoxLayout()
            scrollcontent.setLayout(layout)
        
        title_layout = ImageTitleLayout(PLUGIN_ICON, _('Comments Cleaner Options'))
        layout.addLayout(title_layout)
        
        # --- options ---
        self.options = CommonOptions(PREFS, parent=self)
        layout.addWidget(self.options)
        
        # --- Custom columns ---
        self.checkBoxCUSTOM_COLUMN = QCheckBox(_('Apply to others custom HTML columns'), self)
        self.checkBoxCUSTOM_COLUMN.setChecked(PREFS[KEY.CUSTOM_COLUMN])
        layout.addWidget(self.checkBoxCUSTOM_COLUMN)
        
        # --- Buttons ---
        layout.addWidget(QLabel(' ', self))
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        button_layout.addWidget(KeyboardConfigDialogButton(parent=self))
        
        if CALIBRE_HAS_NOTES:
            button_layout.addWidget(NoteConfigDialogButton(self)) 
        
        button_layout.addStretch(-1)
        
        layout.addStretch(-1)
    
    def save_settings(self):
        with PREFS:
            prefs = self.options.get_option()
            prefs[KEY.CUSTOM_COLUMN] = self.checkBoxCUSTOM_COLUMN.isChecked()
            PREFS.update(prefs)
        
        debug_print('Save settings:', prefs, '\n')


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
            title=_('Customize') + ' ' + _('Notes Cleaner'),
            name='plugin config dialog:User Action Interface:Notes Cleaner',
            parent=GUI,
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
        
        
        title_layout = ImageTitleLayout(NOTES_ICON, _('Notes Cleaner Options'))
        layout.addLayout(title_layout)
        
        prefs = PREFS[KEY.NOTES_SETTINGS].copy()
        
        # --- options ---
        self.options = CommonOptions(prefs, parent=self)
        layout.addWidget(self.options)
        
        # --- Keyboard shortcuts ---
        layout.addWidget(QLabel(' ', self))
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        button_layout.addWidget(KeyboardConfigDialogButton(parent=self))
        button_layout.addStretch(-1)
        layout.addStretch(-1)
    
    def accept(self):
        with PREFS:
            prefs = self.options.get_option()
            PREFS[KEY.NOTES_SETTINGS].update(prefs)
        
        debug_print('Notes settings:', prefs, '\n')
        Dialog.accept(self)


class SelectNotesDialog(Dialog):
    def __init__(self, book_ids=[]):
        self.book_ids = book_ids
        self.selected_notes = {}
        
        Dialog.__init__(self,
            title=_('Select Notes to clean'),
            name='plugin config dialog:User Action Interface:Select Notes to clean',
            parent=GUI,
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
        button_layout.addStretch(-1)
        
        layout.addWidget(self.bb)
    
    def accept(self):
        self.selected_notes = self.tree_view.get_selected()
        Dialog.accept(self)
