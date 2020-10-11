#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Grant Drake <grant.drake@gmail.com>'
__docformat__ = 'restructuredtext en'

from collections import OrderedDict
from PyQt5.Qt import QWidget, QGridLayout, QLabel, QPushButton, QGroupBox, QVBoxLayout
from calibre.utils.config import JSONConfig

from calibre_plugins.comments_cleaner.common_utils import KeyValueComboBox, KeyboardConfigDialog, ImageTitleLayout, get_library_uuid, debug_print, RegexSimple, RegexSearch, RegexLoop

import copy, os


PLUGIN_ICONS = ['images/plugin.png']

KEY_KEEP_URL = 'KeepUrl';
KEY_FORCE_JUSTIFY = 'ForceJustify';
KEY_FONT_WEIGHT = 'FontWeight';

# This is where all preferences for this plugin are stored
prefs = JSONConfig('plugins/Comment Cleaner')

# Set defaults
prefs.defaults[KEY_KEEP_URL] = 'keep'
prefs.defaults[KEY_FORCE_JUSTIFY] = 'empty'
prefs.defaults[KEY_FONT_WEIGHT] = 'bold'


SHOW_URL = OrderedDict([('keep', _('Keep URL')),
						('none', _('Delete URL'))])

FORCE_JUSTIFY = OrderedDict([('all', _('Forced justification (ecrase "center" and "right")')),
							('empty', _('Justification for indeterminate text')),
							('none', _('No change')),
							('del', _('Delete all align'))])

FONT_WEIGHT = OrderedDict([
						('trunc', _('Truncate the value to the hundred')),
						('bold', _('Rounded to Bold (value 600)')),
						('none', _('No change'))])

class ConfigWidget(QWidget):

	def __init__(self, plugin_action):
		QWidget.__init__(self)
		
		self.plugin_action = plugin_action
		layout = QVBoxLayout(self)
		self.setLayout(layout)
		
		title_layout = ImageTitleLayout(self, PLUGIN_ICONS[0], _('Comments Cleaner Options'))
		layout.addLayout(title_layout)
		
		
		# --- options ---
		options_group_box = QGroupBox(_(' '), self)
		layout.addWidget(options_group_box)
		options_group_box_layout = QGridLayout()
		options_group_box.setLayout(options_group_box_layout)
		
		options_group_box_layout.addWidget(QLabel(_('URL:'), self), 1, 1)
		self.showCombo1 = KeyValueComboBox(self, SHOW_URL, prefs[KEY_KEEP_URL])
		options_group_box_layout.addWidget(self.showCombo1, 2, 1)
		
		options_group_box_layout.addWidget(QLabel(_('Justification:'), self), 3, 1)
		self.showCombo2 = KeyValueComboBox(self, FORCE_JUSTIFY, prefs[KEY_FORCE_JUSTIFY])
		options_group_box_layout.addWidget(self.showCombo2, 4, 1)
		
		options_group_box_layout.addWidget(QLabel(_('Weights:'), self), 5, 1)
		self.showCombo3 = KeyValueComboBox(self, FONT_WEIGHT, prefs[KEY_FONT_WEIGHT])
		options_group_box_layout.addWidget(self.showCombo3, 6, 1)

		# --- Keyboard shortcuts ---
		keyboard_shortcuts_button = QPushButton(_('Keyboard shortcuts...'), self)
		keyboard_shortcuts_button.setToolTip(_(
					'Edit the keyboard shortcuts associated with this plugin'))
		keyboard_shortcuts_button.clicked.connect(self.edit_shortcuts)
		layout.addWidget(keyboard_shortcuts_button)
		layout.addStretch(1)

	def save_settings(self):
		
		prefs[KEY_KEEP_URL] = self.showCombo1.selected_key()
		prefs[KEY_FORCE_JUSTIFY] = self.showCombo2.selected_key()
		prefs[KEY_FONT_WEIGHT] = self.showCombo3.selected_key()

	def edit_shortcuts(self):
		self.save_settings ()
		self.plugin_action.build_menus ()
		d = KeyboardConfigDialog(self.plugin_action.gui, self.plugin_action.action_spec[0])
		if d.exec_() == d.Accepted:
			self.plugin_action.gui.keyboard.finalize()
