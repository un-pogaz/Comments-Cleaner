#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Grant Drake <grant.drake@gmail.com>'
__docformat__ = 'restructuredtext en'

import copy, os

try:
	load_translations()
except NameError:
	pass # load_translations() added in calibre 1.9

from collections import OrderedDict
from PyQt5.Qt import QWidget, QGridLayout, QLabel, QPushButton, QGroupBox, QVBoxLayout, QLineEdit, QCheckBox, QObject
from calibre.utils.config import JSONConfig

from calibre_plugins.comments_cleaner.common_utils import KeyValueComboBox, KeyboardConfigDialog, ImageTitleLayout, get_library_uuid, debug_print, RegexSimple, RegexSearch, RegexLoop, CSS_CleanRules, strtobool


PLUGIN_ICONS = ['images/plugin.png']

class KEY:
	KEEP_URL = 'KeepUrl';
	FORCE_JUSTIFY = 'ForceJustify';
	FONT_WEIGHT = 'FontWeight';
	DEL_ITALIC = 'RemoveItalic';
	DEL_UNDER = 'RemoveUnderline';
	DEL_STRIKE = 'RemoveStrikethrough';
	CSS_KEEP = 'CSStoKeep';
	HEADINGS = 'Headings';
	ID_CLASS = 'ID_Class';
	MARKDOWN = 'Markdown';
	
	DOUBLE_BR = 'DoubleBR';
	EMPTY_PARA = 'EmptyParagraph';
	
	FORMATTING = 'RemoveFormatting';

KEEP_URL = OrderedDict([
					('keep', _('Keep URL')),
					('del', _('Delete URL'))])

FORCE_JUSTIFY = OrderedDict([
						('all', _('Force the justification (ecrase "center" and "right")')),
						('empty', _('Justification for indeterminate text (keep "center" and "right")')),
						('none', _('No change')),
						('del', _('Delete all align'))])

FONT_WEIGHT = OrderedDict([
						('trunc', _('Truncate the Weights value to the hundred')),
						('bold', _('Rounded to Bold (value 600)')),
						('none', _('Do not change the Weights')),
						('del', _('Delete Weights'))])

DOUBLE_BR = OrderedDict([
						('empty', _('Create a empty paragraph')),
						('new', _('Create a new paragraph')),
						('none', _('No change'))])

EMPTY_PARA = OrderedDict([
						('merge', _('Merge in a single empty paragraph')),
						('none', _('No change')),
						('del', _('Delete empty paragraph'))])

HEADINGS = OrderedDict([
						('conv', _('Converte to a paragraph')),
						('bolder', _('Converte to a paragraph but keep the bold')),
						('none', _('No change'))])

ID_CLASS = OrderedDict([
						('id', _('Delete "id" attribut')),
						('class', _('Delete "class" attribut')),
						('id_class', _('Delete "id" and "class" attribut')),
						('none', _('No change'))])

MARKDOWN = OrderedDict([
						('always', _('Convert in all comments (not recomanded)')),
						('try', _('Convert only from a plain text comment')),
						('none', _('No change'))])


# This is where all preferences for this plugin are stored
PREFS = JSONConfig('plugins/Comment Cleaner')

# Set defaults
PREFS.defaults[KEY.KEEP_URL] = 'keep'
PREFS.defaults[KEY.FORCE_JUSTIFY] = 'empty'
PREFS.defaults[KEY.FONT_WEIGHT] = 'bold'
PREFS.defaults[KEY.DEL_ITALIC] = 'false'
PREFS.defaults[KEY.DEL_UNDER] = 'false'
PREFS.defaults[KEY.DEL_STRIKE] = 'false'
PREFS.defaults[KEY.HEADINGS] = 'none'
PREFS.defaults[KEY.ID_CLASS] = 'id_class'
PREFS.defaults[KEY.CSS_KEEP] = ''

PREFS.defaults[KEY.FORMATTING] = 'false'

PREFS.defaults[KEY.MARKDOWN] = 'try'
PREFS.defaults[KEY.DOUBLE_BR] = 'new'
PREFS.defaults[KEY.EMPTY_PARA] = 'merge'

class ConfigWidget(QWidget):

	def __init__(self, plugin_action):
		QWidget.__init__(self);
		
		self.plugin_action = plugin_action;
		layout = QVBoxLayout(self);
		self.setLayout(layout);
		
		title_layout = ImageTitleLayout(self, PLUGIN_ICONS[0], _('Comments Cleaner Options'));
		layout.addLayout(title_layout);
		
		
		# --- options HTML ---
		optionsHTML_GroupBox = QGroupBox(' ', self);
		layout.addWidget(optionsHTML_GroupBox);
		optionsHTML_GridLayout = QGridLayout();
		optionsHTML_GroupBox.setLayout(optionsHTML_GridLayout);
		
		
		optionsHTML_GridLayout.addWidget(QLabel(_('Hyperlink:'), self), 0, 0);
		self.comboBoxKEEP_URL = KeyValueComboBox(self, KEEP_URL, PREFS[KEY.KEEP_URL]);
		optionsHTML_GridLayout.addWidget(self.comboBoxKEEP_URL, 1, 0);
		
		optionsHTML_GridLayout.addWidget(QLabel(_('Headings:'), self), 0, 1);
		self.comboBoxHEADINGS = KeyValueComboBox(self, HEADINGS, PREFS[KEY.HEADINGS]);
		optionsHTML_GridLayout.addWidget(self.comboBoxHEADINGS, 1, 1);
		
		
		optionsHTML_GridLayout.addWidget(QLabel(' ', self), 4, 0);
		
		self.comboBoxFONT_WEIGHT = KeyValueComboBox(self, FONT_WEIGHT, PREFS[KEY.FONT_WEIGHT]);
		optionsHTML_GridLayout.addWidget(self.comboBoxFONT_WEIGHT, 5, 0);
		
		self.checkBoxDEL_ITALIC = QCheckBox(_('Remove Italic'), self);
		self.checkBoxDEL_ITALIC.setChecked(strtobool(PREFS[KEY.DEL_ITALIC]));
		optionsHTML_GridLayout.addWidget(self.checkBoxDEL_ITALIC, 5, 1);
		
		self.checkBoxDEL_UNDER = QCheckBox(_('Remove Underline'), self);
		self.checkBoxDEL_UNDER.setChecked(strtobool(PREFS[KEY.DEL_UNDER]));
		optionsHTML_GridLayout.addWidget(self.checkBoxDEL_UNDER, 6, 0);
		
		self.checkBoxDEL_STRIKE = QCheckBox(_('Remove Strikethrough'), self);
		self.checkBoxDEL_STRIKE.setChecked(strtobool(PREFS[KEY.DEL_STRIKE]));
		optionsHTML_GridLayout.addWidget(self.checkBoxDEL_STRIKE, 6, 1);
		
		optionsHTML_GridLayout.addWidget(QLabel(' ', self), 9, 0);
		
		
		optionsHTML_GridLayout.addWidget(QLabel(_('Justification:'), self), 10, 0);
		self.comboBoxFORCE_JUSTIFY = KeyValueComboBox(self, FORCE_JUSTIFY, PREFS[KEY.FORCE_JUSTIFY]);
		optionsHTML_GridLayout.addWidget(self.comboBoxFORCE_JUSTIFY, 11, 0, 1, 2);
		
		optionsHTML_GridLayout.addWidget(QLabel(_('ID & CLASS attributs:'), self), 12, 0);
		self.comboBoxID_CLASS = KeyValueComboBox(self, ID_CLASS, PREFS[KEY.ID_CLASS]);
		optionsHTML_GridLayout.addWidget(self.comboBoxID_CLASS, 13, 0, 1, 2);
		
		
		optionsHTML_GridLayout.addWidget(QLabel(' ', self));
		
		optionsHTML_GridLayout.addWidget(QLabel(_('CSS rule to keep:'), self), 20, 0);
		self.lineEditCSS_KEEP = QLineEdit(self);
		self.lineEditCSS_KEEP.setText(PREFS[KEY.CSS_KEEP]);
		self.lineEditCSS_KEEP.setToolTip(_('Custom CSS rules to keep in addition to the basic ones. Rules separated by a space.'));
		optionsHTML_GridLayout.addWidget(self.lineEditCSS_KEEP, 21, 0, 1, 2);
		
		# --- formatting ---
		
		self.checkBoxCLEAN_ALL = QCheckBox(_('Remove all formatting'), self);
		self.checkBoxCLEAN_ALL.stateChanged.connect(self.checkBox_click);
		self.checkBoxCLEAN_ALL.setChecked(strtobool(PREFS[KEY.FORMATTING]));
		layout.addWidget(self.checkBoxCLEAN_ALL);
		
		
		# --- options TEXT ---
		optionsTEXT_GroupBox = QGroupBox(' ', self);
		layout.addWidget(optionsTEXT_GroupBox);
		optionsTEXT_GridLayout = QGridLayout();
		optionsTEXT_GroupBox.setLayout(optionsTEXT_GridLayout);
		
		optionsTEXT_GridLayout.addWidget(QLabel(_('Markdown:'), self));
		self.comboBoxMARKDOWN = KeyValueComboBox(self, MARKDOWN, PREFS[KEY.MARKDOWN]);
		optionsTEXT_GridLayout.addWidget(self.comboBoxMARKDOWN);
		self.comboBoxMARKDOWN.setToolTip(_('Try to convert any Markdown strings to HTML.'));
		
		optionsTEXT_GridLayout.addWidget(QLabel(_('Multiple Line Return in a paragraph:'), self));
		self.comboBoxDOUBLE_BR = KeyValueComboBox(self, DOUBLE_BR, PREFS[KEY.DOUBLE_BR]);
		optionsTEXT_GridLayout.addWidget(self.comboBoxDOUBLE_BR);
		
		optionsTEXT_GridLayout.addWidget(QLabel(_('Multiple empty paragraph:'), self));
		self.comboBoxEMPTY_PARA = KeyValueComboBox(self, EMPTY_PARA, PREFS[KEY.EMPTY_PARA]);
		optionsTEXT_GridLayout.addWidget(self.comboBoxEMPTY_PARA);
		
		
		# --- Keyboard shortcuts ---
		layout.addWidget(QLabel(' ', self));
		keyboard_shortcuts_button = QPushButton(_('Keyboard shortcuts...'), self);
		keyboard_shortcuts_button.setToolTip(_('Edit the keyboard shortcuts associated with this plugin'));
		keyboard_shortcuts_button.clicked.connect(self.edit_shortcuts);
		layout.addWidget(keyboard_shortcuts_button);
		layout.addStretch(1);

	def save_settings(self):
		
		PREFS[KEY.KEEP_URL] = self.comboBoxKEEP_URL.selected_key();
		PREFS[KEY.FORCE_JUSTIFY] = self.comboBoxFORCE_JUSTIFY.selected_key();
		PREFS[KEY.FONT_WEIGHT] = self.comboBoxFONT_WEIGHT.selected_key();
		PREFS[KEY.DEL_ITALIC] = str(self.checkBoxDEL_ITALIC.checkState() > 0).lower()
		PREFS[KEY.DEL_UNDER] = str(self.checkBoxDEL_UNDER.checkState() > 0).lower()
		PREFS[KEY.DEL_STRIKE] = str(self.checkBoxDEL_STRIKE.checkState() > 0).lower()
		PREFS[KEY.HEADINGS] = self.comboBoxHEADINGS.selected_key();
		PREFS[KEY.ID_CLASS] = self.comboBoxID_CLASS.selected_key();
		
		PREFS[KEY.CSS_KEEP] = CSS_CleanRules(self.lineEditCSS_KEEP.text());
		
		
		PREFS[KEY.FORMATTING] = str(self.checkBoxCLEAN_ALL.checkState() > 0).lower()
		
		
		PREFS[KEY.MARKDOWN] = self.comboBoxMARKDOWN.selected_key();
		PREFS[KEY.DOUBLE_BR] = self.comboBoxDOUBLE_BR.selected_key();
		PREFS[KEY.EMPTY_PARA] = self.comboBoxEMPTY_PARA.selected_key();
		
		
		debug_print('Save settings: {0}\n'.format(PREFS));
		

	def edit_shortcuts(self):
		self.save_settings();
		self.plugin_action.build_menus();
		d = KeyboardConfigDialog(self.plugin_action.gui, self.plugin_action.action_spec[0]);
		if d.exec_() == d.Accepted:
			self.plugin_action.gui.keyboard.finalize();


	def checkBox_click(self, num):
		
		if self.checkBoxCLEAN_ALL.checkState():
			self.comboBoxKEEP_URL.setEnabled(False);
			self.comboBoxFORCE_JUSTIFY.setEnabled(False);
			self.comboBoxFONT_WEIGHT.setEnabled(False);
			self.checkBoxDEL_ITALIC.setEnabled(False);
			self.checkBoxDEL_UNDER.setEnabled(False);
			self.checkBoxDEL_STRIKE.setEnabled(False);
			self.comboBoxHEADINGS.setEnabled(False);
			self.comboBoxID_CLASS.setEnabled(False);
			self.lineEditCSS_KEEP.setEnabled(False);
		else:
			self.comboBoxKEEP_URL.setEnabled(True);
			self.comboBoxFORCE_JUSTIFY.setEnabled(True);
			self.comboBoxFONT_WEIGHT.setEnabled(True);
			self.checkBoxDEL_ITALIC.setEnabled(True);
			self.checkBoxDEL_UNDER.setEnabled(True);
			self.checkBoxDEL_STRIKE.setEnabled(True);
			self.comboBoxHEADINGS.setEnabled(True);
			self.comboBoxID_CLASS.setEnabled(True);
			self.lineEditCSS_KEEP.setEnabled(True);