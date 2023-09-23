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
    from qt.core import (Qt, QAbstractItemView, QCheckBox, QGridLayout, QGroupBox,
                         QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
                         QSize, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
                        )
except ImportError:
    from PyQt5.Qt import (Qt, QAbstractItemView, QCheckBox, QGridLayout, QGroupBox,
                          QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
                          QSize, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
                        )

from calibre import prints
from calibre.gui2.ui import get_gui
from calibre.library.field_metadata import category_icon_map

from .common_utils import debug_print, get_icon, GUI, PREFS_json, regex, calibre_version
from .common_utils.dialogs import KeyboardConfigDialogButton
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

# This is where all preferences for this plugin are stored
PREFS = PREFS_json()
PREFS.defaults = _defaults
PREFS.defaults[KEY.CUSTOM_COLUMN] = False
PREFS.defaults[KEY.NOTES_SETTINGS] = _defaults.copy()


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


def _build_optionsHTML_GroupBox(parent, layout, prefs):
    rslt = QGroupBox(' ', parent)
    layout.addWidget(rslt)
    
    grid_layout = QGridLayout()
    rslt.setLayout(grid_layout)
    
    
    grid_layout.addWidget(QLabel(_('Hyperlink:'), parent), 0, 0, 1, 2)
    parent.comboBoxKEEP_URL = KeyValueComboBox(parent, KEEP_URL, prefs[KEY.KEEP_URL])
    grid_layout.addWidget(parent.comboBoxKEEP_URL, 1, 0, 1, 2)
    
    grid_layout.addWidget(QLabel(_('Headings:'), parent), 0, 2, 1, 2)
    parent.comboBoxHEADINGS = KeyValueComboBox(parent, HEADINGS, prefs[KEY.HEADINGS])
    grid_layout.addWidget(parent.comboBoxHEADINGS, 1, 2, 1, 2)
    
    
    grid_layout.addWidget(QLabel(' ', parent), 4, 0)
    
    parent.comboBoxFONT_WEIGHT = KeyValueComboBox(parent, FONT_WEIGHT, prefs[KEY.FONT_WEIGHT])
    grid_layout.addWidget(parent.comboBoxFONT_WEIGHT, 5, 0, 1, 2)
    
    parent.checkBoxDEL_ITALIC = QCheckBox(_('Remove Italic'), parent)
    parent.checkBoxDEL_ITALIC.setChecked(prefs[KEY.DEL_ITALIC])
    grid_layout.addWidget(parent.checkBoxDEL_ITALIC, 5, 2, 1, 2)
    
    parent.checkBoxDEL_UNDER = QCheckBox(_('Remove Underline'), parent)
    parent.checkBoxDEL_UNDER.setChecked(prefs[KEY.DEL_UNDER])
    grid_layout.addWidget(parent.checkBoxDEL_UNDER, 6, 0, 1, 2)
    
    parent.checkBoxDEL_STRIKE = QCheckBox(_('Remove Strikethrough'), parent)
    parent.checkBoxDEL_STRIKE.setChecked(prefs[KEY.DEL_STRIKE])
    grid_layout.addWidget(parent.checkBoxDEL_STRIKE, 6, 2, 1, 2)
    
    grid_layout.addWidget(QLabel(' ', parent), 9, 0)
    
    
    grid_layout.addWidget(QLabel(_('Justification:'), parent), 10, 0, 1, 1)
    parent.comboBoxFORCE_JUSTIFY = KeyValueComboBox(parent, FORCE_JUSTIFY, prefs[KEY.FORCE_JUSTIFY])
    grid_layout.addWidget(parent.comboBoxFORCE_JUSTIFY, 10, 1, 1, 3)
    
    grid_layout.addWidget(QLabel(_('List alignment:'), parent), 11, 0, 1, 1)
    parent.comboBoxLIST_ALIGN = KeyValueComboBox(parent, LIST_ALIGN, prefs[KEY.LIST_ALIGN])
    grid_layout.addWidget(parent.comboBoxLIST_ALIGN, 11, 1, 1, 3)
    
    grid_layout.addWidget(QLabel(_('ID & CLASS attributs:'), parent), 12, 0, 1, 1)
    parent.comboBoxID_CLASS = KeyValueComboBox(parent, ID_CLASS, prefs[KEY.ID_CLASS])
    grid_layout.addWidget(parent.comboBoxID_CLASS, 12, 1, 1, 3)
    
    
    grid_layout.addWidget(QLabel(' ', parent))
    
    grid_layout.addWidget(QLabel(_('CSS rule to keep:'), parent), 20, 0, 1, 1)
    parent.lineEditCSS_KEEP = QLineEdit(parent)
    parent.lineEditCSS_KEEP.setText(prefs[KEY.CSS_KEEP])
    parent.lineEditCSS_KEEP.setToolTip(_('Custom CSS rules to keep in addition to the basic ones. Rules separated by a space.'))
    grid_layout.addWidget(parent.lineEditCSS_KEEP, 20, 1, 1, 3)
    
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

def _build_optionsTEXT_GroupBox(parent, layout, prefs):
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

def _build_optionsNOTES_Button(parent, layout):
    
    def edit_notes_options():
        d = ConfigNotesDialog()
        d.exec_()
    
    rslt = QPushButton(get_icon(NOTES_ICON), _('Notes Cleaner Options'), parent)
    rslt.setToolTip(_('Edit the options for the notes cleaner action'))
    
    rslt.clicked.connect(edit_notes_options)
    layout.addWidget(rslt)

class ConfigWidget(QWidget):
    def __init__(self, plugin_action):
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
        _build_optionsHTML_GroupBox(self, layout, PREFS)
        _build_optionsTEXT_GroupBox(self, layout, PREFS)
        
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
            _build_optionsNOTES_Button(self, button_layout)
        
        # --- Keyboard shortcuts ---
        layout.addWidget(QLabel(' ', self))
        layout.addWidget(KeyboardConfigDialogButton(self))
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
            
            PREFS[KEY.CSS_KEEP] = css_clean_rules(self.lineEditCSS_KEEP.text())
            
            PREFS[KEY.DEL_FORMATTING] = self.checkBoxDEL_FORMATTING.isChecked()
            
            PREFS[KEY.MARKDOWN] = self.comboBoxMARKDOWN.selected_key()
            PREFS[KEY.DOUBLE_BR] = self.comboBoxDOUBLE_BR.selected_key()
            PREFS[KEY.SINGLE_BR] = self.comboBoxSINGLE_BR.selected_key()
            PREFS[KEY.EMPTY_PARA] = self.comboBoxEMPTY_PARA.selected_key()
            
            PREFS[KEY.CUSTOM_COLUMN] = self.checkBoxCUSTOM_COLUMN.isChecked()
        
        prefs = PREFS.copy()
        prefs.pop(KEY.NOTES_SETTINGS, None)
        
        debug_print('Save settings: {0}\n'.format(prefs))
        
    


# workaround to run one Calibre 2
try:
    from calibre.gui2.widgets2 import Dialog
except:
    class Dialog():
        pass

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
        
        prefs = PREFS[KEY.NOTES_SETTINGS]
        
        # --- options ---
        _build_optionsHTML_GroupBox(self, layout, prefs)
        _build_optionsTEXT_GroupBox(self, layout, prefs)
        
        # --- Keyboard shortcuts ---
        layout.addWidget(QLabel(' ', self))
        layout.addWidget(KeyboardConfigDialogButton(self))
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
            
            prefs[KEY.CSS_KEEP] = css_clean_rules(self.lineEditCSS_KEEP.text())
            
            prefs[KEY.DEL_FORMATTING] = self.checkBoxDEL_FORMATTING.isChecked()
            
            prefs[KEY.MARKDOWN] = self.comboBoxMARKDOWN.selected_key()
            prefs[KEY.DOUBLE_BR] = self.comboBoxDOUBLE_BR.selected_key()
            prefs[KEY.SINGLE_BR] = self.comboBoxSINGLE_BR.selected_key()
            prefs[KEY.EMPTY_PARA] = self.comboBoxEMPTY_PARA.selected_key()
            
            PREFS[KEY.NOTES_SETTINGS] = prefs
        
        debug_print('Notes settings: {0}\n'.format(prefs))
        Dialog.accept(self)


class SelectNotesDialog(Dialog):
    def __init__(self, book_ids=[]):
        
        self.dbAPI = GUI.current_db.new_api
        self.book_ids = book_ids
        self.select_notes = {}
        self.all_possible_notes = self.dbAPI.get_all_items_that_have_notes()
        
        Dialog.__init__(self,
            parent=GUI,
            title= _('Select Notes to clean'),
            name = 'plugin config dialog:User Action Interface:Select Notes to clean',
        )
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tree_view = QTreeWidget(self)
        layout.addWidget(self.tree_view)
        
        self.tree_view.setIconSize(QSize(20, 20))
        self.tree_view.header().hide()
        self.tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
        self.tree_view.itemChanged.connect(self.tree_item_changed)
        self._is_internal_item_changed = False
        
        self.select_book_item = None
        
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        _build_optionsNOTES_Button(self, button_layout)
        button_layout.addStretch(1)
        
        layout.addWidget(self.bb)
        
        self._populate_tree(self.all_possible_notes, self.book_ids)
    
    def _populate_tree(self, map_fields_notes, book_ids=[]):
        self.select_book_item = None
        self.tree_view.takeTopLevelItem(-1)
        
        category_icons = {}
        category_icons.update({k:get_icon(v) for k,v in category_icon_map.items()})
        category_icons.update(GUI.tags_view.model().category_custom_icons)
        
        
        def create_tree_item(parent, text, data, icon):
            rslt = QTreeWidgetItem(parent)
            rslt.setText(0, text)
            rslt.setData(0, Qt.UserRole, data)
            rslt.setFlags(Qt.ItemIsEnabled|Qt.ItemIsUserCheckable)
            rslt.setCheckState(0, Qt.Unchecked)
            rslt.setIcon(0, icon)
            return rslt
        
        def create_root_item(parent, field, items):
            icon = category_icons.get(field, category_icons['custom:'])
            name = self.dbAPI.field_metadata[field]['name']
            rslt = create_tree_item(parent, '{name} ({field})'.format(name=name, field=field), field, icon)
            
            for id in items:
                ch = create_tree_item(rslt, self.dbAPI.get_item_name(field, id), id, icon)
                rslt.addChild(ch)
            
            rslt.sortChildren(0, Qt.AscendingOrder)
            return rslt
        
        book_fields_ids = {}
        for book_id in book_ids:
            mi = self.dbAPI.get_metadata(book_id, get_user_categories=False)
            
            for field,items_ids in self.all_possible_notes.items():
                values = mi.get(field)
                if not isinstance(values, list):
                    values = [values]
                
                for v in values:
                    id = self.dbAPI.get_item_id(field, v)
                    if id in items_ids:
                        if field not in book_fields_ids:
                            book_fields_ids[field] = set()
                        book_fields_ids[field].add(id)
        
        if map_fields_notes:
            self.select_book_item = QTreeWidgetItem(self.tree_view)
            self.select_book_item.setFlags(Qt.ItemIsEnabled)
            self.select_book_item.setIcon(0, get_icon('book.png'))
            self.select_book_item.setToolTip(0, _('Subset of notes for the current selected books'))
            
            if not book_ids:
                msg = _('No books selected')
            elif not book_fields_ids:
                msg = _('{:d} books selected (no note)').format(len(book_ids))
            else:
                msg = _('{:d} books selected').format(len(book_ids))
            self.select_book_item.setText(0, msg)
            self.tree_view.addTopLevelItem(self.select_book_item)
        
        for field,items_ids in book_fields_ids.items():
            if items_ids:
                self.select_book_item.addChild(create_root_item(self.select_book_item, field, items_ids))
        
        separator = QTreeWidgetItem(self.tree_view)
        separator.setFlags(Qt.NoItemFlags)
        if map_fields_notes:
            self.tree_view.addTopLevelItem(self.select_book_item)
            separator.setText(0, '--------------')
        else:
            separator.setText(0, _('No notes'))
        self.tree_view.addTopLevelItem(separator)
        
        for field in (self.dbAPI.pref('tag_browser_category_order') or sorted(self.dbAPI.backend.notes.allowed_fields)):
            items_ids = map_fields_notes.get(field, None)
            if items_ids:
                self.tree_view.addTopLevelItem(create_root_item(self.tree_view, field, items_ids))
    
    def tree_item_changed(self, item, column):
        if not self._is_internal_item_changed:
            self._is_internal_item_changed = True
            
            parent = item.parent()
            if isinstance(parent, QTreeWidgetItem) and parent.data(0, Qt.UserRole):
                state = False
                for idx in range(parent.childCount()):
                    if parent.child(idx).checkState(column) == Qt.CheckState.Checked:
                        state = True
                        break
                parent.setCheckState(column, Qt.CheckState.PartiallyChecked if state else Qt.CheckState.Unchecked)
            else:
                if item.checkState(column) == Qt.CheckState.Checked:
                    state = Qt.ItemIsUserCheckable
                else:
                    state = Qt.ItemIsEnabled|Qt.ItemIsUserCheckable
                for idx in range(item.childCount()):
                    item.child(idx).setFlags(state)
            
            self._is_internal_item_changed = False
    
    def accept(self):
        self.select_notes = {}
        
        def parse_tree_item(item):
            item_text, field = item.text(0), item.data(0, Qt.UserRole)
            all_field = False
            if item.checkState(0) == Qt.CheckState.Checked:
                all_field = True
            
            for idx in range(item.childCount()):
                child = item.child(idx)
                if all_field or child.checkState(0) == Qt.CheckState.Checked:
                    if field not in self.select_notes:
                        self.select_notes[field] = set()
                    self.select_notes[field].add(child.data(0, Qt.UserRole))
        
        for idx in range(self.tree_view.topLevelItemCount()):
            item = self.tree_view.topLevelItem(idx)
            
            if item.data(0, Qt.UserRole):
                parse_tree_item(item)
            else:
                for idx in range(item.childCount()):
                    ch = item.child(idx)
                    parse_tree_item(ch)
        
        Dialog.accept(self)
