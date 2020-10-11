#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Grant Drake <grant.drake@gmail.com>'
__docformat__ = 'restructuredtext en'

from collections import OrderedDict
from PyQt5.Qt import QWidget, QGridLayout, QLabel, QPushButton, QGroupBox, QVBoxLayout, QLineEdit
from calibre.utils.config import JSONConfig

from calibre_plugins.comments_cleaner.common_utils import KeyValueComboBox, KeyboardConfigDialog, ImageTitleLayout, get_library_uuid, debug_print, RegexSimple, RegexSearch, RegexLoop, CSS_CleanRules

import copy, os

PLUGIN_ICONS = ['images/plugin.png']

class KEY:
	KEEP_URL = 'KeepUrl';
	FORCE_JUSTIFY = 'ForceJustify';
	FONT_WEIGHT = 'FontWeight';
	CSS_KEEP = 'CSStoKeep';
	DOUBLE_BR = 'DoubleBR';

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
						('new', _('Create a new paragraph')),
						('none', _('No change'))])


CSS_KEEP_TIP = _('Custom CSS rules to keep in addition to the basic ones. Rules separated by a space.')


# This is where all preferences for this plugin are stored
PREFS = JSONConfig('plugins/Comment Cleaner')

# Set defaults
PREFS.defaults[KEY.KEEP_URL] = 'keep'
PREFS.defaults[KEY.FORCE_JUSTIFY] = 'empty'
PREFS.defaults[KEY.FONT_WEIGHT] = 'bold'
PREFS.defaults[KEY.DOUBLE_BR] = 'new'
PREFS.defaults[KEY.CSS_KEEP] = ''

class ConfigWidget(QWidget):

	def __init__(self, plugin_action):
		QWidget.__init__(self);
		
		self.plugin_action = plugin_action;
		layout = QVBoxLayout(self);
		self.setLayout(layout);
		
		title_layout = ImageTitleLayout(self, PLUGIN_ICONS[0], _('Comments Cleaner Options'));
		layout.addLayout(title_layout);
		
		
		# --- options ---
		options_group_box = QGroupBox(_(' '), self);
		layout.addWidget(options_group_box);
		options_group_box_layout = QGridLayout();
		options_group_box.setLayout(options_group_box_layout);
		
		options_group_box_layout.addWidget(QLabel(_('Hyperlink:'), self), 1, 1);
		self.showCombo1 = KeyValueComboBox(self, KEEP_URL, PREFS[KEY.KEEP_URL]);
		options_group_box_layout.addWidget(self.showCombo1, 2, 1);
		
		options_group_box_layout.addWidget(QLabel(_('Justification:'), self), 3, 1);
		self.showCombo2 = KeyValueComboBox(self, FORCE_JUSTIFY, PREFS[KEY.FORCE_JUSTIFY]);
		options_group_box_layout.addWidget(self.showCombo2, 4, 1);
		
		options_group_box_layout.addWidget(QLabel(_('Weights:'), self), 5, 1);
		self.showCombo3 = KeyValueComboBox(self, FONT_WEIGHT, PREFS[KEY.FONT_WEIGHT]);
		options_group_box_layout.addWidget(self.showCombo3, 6, 1);
		
		options_group_box_layout.addWidget(QLabel(_('Multiple Line Return in a paragraph:'), self), 7, 1);
		self.showCombo4 = KeyValueComboBox(self, DOUBLE_BR, PREFS[KEY.DOUBLE_BR]);
		options_group_box_layout.addWidget(self.showCombo4, 8, 1);
		
		
		
		options_group_box_layout.addWidget(QLabel(_(' '), self), 19, 1);
		
		options_group_box_layout.addWidget(QLabel(_('CSS rule to keep:'), self), 20, 1);
		self.keepCSS = QLineEdit(self);
		self.keepCSS.setText(PREFS[KEY.CSS_KEEP]);
		self.keepCSS.setToolTip(CSS_KEEP_TIP);
		options_group_box_layout.addWidget(self.keepCSS, 21, 1);
		
		# --- Keyboard shortcuts ---
		keyboard_shortcuts_button = QPushButton(_('Keyboard shortcuts...'), self);
		keyboard_shortcuts_button.setToolTip(_('Edit the keyboard shortcuts associated with this plugin'));
		keyboard_shortcuts_button.clicked.connect(self.edit_shortcuts);
		layout.addWidget(keyboard_shortcuts_button);
		layout.addStretch(1);

	def save_settings(self):
		
		PREFS[KEY.KEEP_URL] = self.showCombo1.selected_key();
		PREFS[KEY.FORCE_JUSTIFY] = self.showCombo2.selected_key();
		PREFS[KEY.FONT_WEIGHT] = self.showCombo3.selected_key();
		PREFS[KEY.DOUBLE_BR] = self.showCombo4.selected_key();
		
		PREFS[KEY.CSS_KEEP] = CSS_CleanRules(self.keepCSS.text());
		

	def edit_shortcuts(self):
		self.save_settings();
		self.plugin_action.build_menus();
		d = KeyboardConfigDialog(self.plugin_action.gui, self.plugin_action.action_spec[0]);
		if d.exec_() == d.Accepted:
			self.plugin_action.gui.keyboard.finalize();
