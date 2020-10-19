#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Grant Drake <grant.drake@gmail.com>'
__docformat__ = 'restructuredtext en'

import copy, os, distutils.util as util

try:
	load_translations()
except NameError:
	pass # load_translations() added in calibre 1.9

from collections import OrderedDict
from PyQt5.Qt import QWidget, QGridLayout, QLabel, QPushButton, QGroupBox, QVBoxLayout, QLineEdit, QCheckBox, QObject
from calibre.utils.config import JSONConfig

from calibre_plugins.comments_cleaner.common_utils import KeyValueComboBox, KeyboardConfigDialog, ImageTitleLayout, get_library_uuid, debug_print, RegexSimple, RegexSearch, RegexLoop, CSS_CleanRules


PLUGIN_ICONS = ['images/plugin.png']

class KEY:
	KEEP_URL = 'KeepUrl';
	FORCE_JUSTIFY = 'ForceJustify';
	FONT_WEIGHT = 'FontWeight';
	CSS_KEEP = 'CSStoKeep';
	DOUBLE_BR = 'DoubleBR';
	EMPTY_PARA = 'EmptyParagraph';
	HEADINGS = 'Headings';
	ID_CLASS = 'ID_Class';
	MARKDOWN = 'Markdown';
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
						('trunc', _('Truncate the value to the hundred')),
						('bold', _('Rounded to Bold (value 600)')),
						('none', _('No change'))])

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
PREFS.defaults[KEY.DOUBLE_BR] = 'new'
PREFS.defaults[KEY.EMPTY_PARA] = 'merge'
PREFS.defaults[KEY.CSS_KEEP] = ''
PREFS.defaults[KEY.HEADINGS] = 'none'
PREFS.defaults[KEY.ID_CLASS] = 'id_class'
PREFS.defaults[KEY.MARKDOWN] = 'try'
PREFS.defaults[KEY.FORMATTING] = 'false'

class ConfigWidget(QWidget):

	def __init__(self, plugin_action):		
		QWidget.__init__(self);
		
		self.plugin_action = plugin_action;
		layout = QVBoxLayout(self);
		self.setLayout(layout);
		
		title_layout = ImageTitleLayout(self, PLUGIN_ICONS[0], _('Comments Cleaner Options'));
		layout.addLayout(title_layout);
		
		
		# --- options ---
		options_group_box = QGroupBox(' ', self);
		layout.addWidget(options_group_box);
		options_group_box_layout = QGridLayout();
		options_group_box.setLayout(options_group_box_layout);
		
		
		options_group_box_layout.addWidget(QLabel(_('Hyperlink:'), self));
		self.comboBoxKEEP_URL = KeyValueComboBox(self, KEEP_URL, PREFS[KEY.KEEP_URL]);
		options_group_box_layout.addWidget(self.comboBoxKEEP_URL);
		
		options_group_box_layout.addWidget(QLabel(_('Headings:'), self));
		self.comboBoxHEADINGS = KeyValueComboBox(self, HEADINGS, PREFS[KEY.HEADINGS]);
		options_group_box_layout.addWidget(self.comboBoxHEADINGS);
		
		options_group_box_layout.addWidget(QLabel(_('Weights:'), self));
		self.comboBoxFONT_WEIGHT = KeyValueComboBox(self, FONT_WEIGHT, PREFS[KEY.FONT_WEIGHT]);
		options_group_box_layout.addWidget(self.comboBoxFONT_WEIGHT);
		
		options_group_box_layout.addWidget(QLabel(_('Justification:'), self));
		self.comboBoxFORCE_JUSTIFY = KeyValueComboBox(self, FORCE_JUSTIFY, PREFS[KEY.FORCE_JUSTIFY]);
		options_group_box_layout.addWidget(self.comboBoxFORCE_JUSTIFY);
		
		options_group_box_layout.addWidget(QLabel(_('Multiple Line Return in a paragraph:'), self));
		self.comboBoxDOUBLE_BR = KeyValueComboBox(self, DOUBLE_BR, PREFS[KEY.DOUBLE_BR]);
		options_group_box_layout.addWidget(self.comboBoxDOUBLE_BR);
		
		options_group_box_layout.addWidget(QLabel(_('Multiple empty paragraph:'), self));
		self.comboBoxEMPTY_PARA = KeyValueComboBox(self, EMPTY_PARA, PREFS[KEY.EMPTY_PARA]);
		options_group_box_layout.addWidget(self.comboBoxEMPTY_PARA);
		
		options_group_box_layout.addWidget(QLabel(_('ID & CLASS attributs:'), self));
		self.comboBoxID_CLASS = KeyValueComboBox(self, ID_CLASS, PREFS[KEY.ID_CLASS]);
		options_group_box_layout.addWidget(self.comboBoxID_CLASS);
		
		options_group_box_layout.addWidget(QLabel(_('Markdown:'), self));
		self.comboBoxMARKDOWN = KeyValueComboBox(self, MARKDOWN, PREFS[KEY.MARKDOWN]);
		options_group_box_layout.addWidget(self.comboBoxMARKDOWN);
		self.comboBoxMARKDOWN.setToolTip(_('Try to convert any Markdown strings to HTML.'));
		
		
		options_group_box_layout.addWidget(QLabel(' ', self));
		
		options_group_box_layout.addWidget(QLabel(_('CSS rule to keep:'), self));
		self.lineEditCSS_KEEP = QLineEdit(self);
		self.lineEditCSS_KEEP.setText(PREFS[KEY.CSS_KEEP]);
		self.lineEditCSS_KEEP.setToolTip(_('Custom CSS rules to keep in addition to the basic ones. Rules separated by a space.'));
		options_group_box_layout.addWidget(self.lineEditCSS_KEEP);
		
		
		self.checkBoxCLEAN_ALL = QCheckBox(_('Remove all formatting'), self);
		self.checkBoxCLEAN_ALL.stateChanged.connect(self.checkBox_click);
		self.checkBoxCLEAN_ALL.setChecked(util.strtobool(PREFS[KEY.FORMATTING]));
		layout.addWidget(self.checkBoxCLEAN_ALL);
		
		layout.addWidget(QLabel(' ', self));
		
		
		# --- Keyboard shortcuts ---
		keyboard_shortcuts_button = QPushButton(_('Keyboard shortcuts...'), self);
		keyboard_shortcuts_button.setToolTip(_('Edit the keyboard shortcuts associated with this plugin'));
		keyboard_shortcuts_button.clicked.connect(self.edit_shortcuts);
		layout.addWidget(keyboard_shortcuts_button);
		layout.addStretch(1);

	def save_settings(self):
		
		PREFS[KEY.KEEP_URL] = self.comboBoxKEEP_URL.selected_key();
		PREFS[KEY.FORCE_JUSTIFY] = self.comboBoxFORCE_JUSTIFY.selected_key();
		PREFS[KEY.FONT_WEIGHT] = self.comboBoxFONT_WEIGHT.selected_key();
		PREFS[KEY.DOUBLE_BR] = self.comboBoxDOUBLE_BR.selected_key();
		PREFS[KEY.EMPTY_PARA] = self.comboBoxEMPTY_PARA.selected_key();
		PREFS[KEY.HEADINGS] = self.comboBoxHEADINGS.selected_key();
		PREFS[KEY.ID_CLASS] = self.comboBoxID_CLASS.selected_key();
		PREFS[KEY.MARKDOWN] = self.comboBoxMARKDOWN.selected_key();
		
		PREFS[KEY.CSS_KEEP] = CSS_CleanRules(self.lineEditCSS_KEEP.text());
		
		PREFS[KEY.FORMATTING] = str(self.checkBoxCLEAN_ALL.checkState() > 0).lower()
		
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
			self.comboBoxDOUBLE_BR.setEnabled(False);
			self.comboBoxEMPTY_PARA.setEnabled(False);
			self.comboBoxHEADINGS.setEnabled(False);
			self.comboBoxID_CLASS.setEnabled(False);
			self.comboBoxMARKDOWN.setEnabled(False);
			self.lineEditCSS_KEEP.setEnabled(False);
		else:
			self.comboBoxKEEP_URL.setEnabled(True);
			self.comboBoxFORCE_JUSTIFY.setEnabled(True);
			self.comboBoxFONT_WEIGHT.setEnabled(True);
			self.comboBoxDOUBLE_BR.setEnabled(True);
			self.comboBoxEMPTY_PARA.setEnabled(True);
			self.comboBoxHEADINGS.setEnabled(True);
			self.comboBoxID_CLASS.setEnabled(True);
			self.comboBoxMARKDOWN.setEnabled(True);
			self.lineEditCSS_KEEP.setEnabled(True);