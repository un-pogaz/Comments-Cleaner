#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <>'
__docformat__ = 'restructuredtext en'

import os, sys, time

try:
	load_translations()
except NameError:
	pass # load_translations() added in calibre 1.9

from functools import partial
try:
	from PyQt5.Qt import Qt, QToolButton, QMenu, QProgressDialog, QTimer, QModelIndex
except ImportError:
	from PyQt4.Qt import Qt, QToolButton, QMenu, QProgressDialog, QTimer

from datetime import datetime

from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import error_dialog
from calibre.gui2.actions import InterfaceAction
from calibre.library import current_library_name

from calibre_plugins.comments_cleaner.config import PLUGIN_ICONS
from calibre_plugins.comments_cleaner.common_utils import set_plugin_icon_resources, get_icon, create_menu_action_unique, debug_print, debug_text, RegexSimple, RegexSearch, RegexLoop

from calibre_plugins.comments_cleaner.CommentsCleaner import *

class CommentCleanerAction(InterfaceAction):
	
	name = 'Comments Cleaner';
	# Create our top-level menu/toolbar action (text, icon_path, tooltip, keyboard shortcut)
	action_spec = ('Comments Cleaner', None, _('Remove the scraps CSS in HTML comments'), None);
	popup_type = QToolButton.MenuButtonPopup;
	action_type = 'current';
	dont_add_to = frozenset(['context-menu-device']);

	def genesis(self):
		self.is_library_selected = True;
		self.menu = QMenu(self.gui);
		self.menu_actions = [];
		
		# Read the plugin icons and store for potential sharing with the config widget
		icon_resources = self.load_resources(PLUGIN_ICONS);
		set_plugin_icon_resources(self.name, icon_resources);
		
		self.build_menus();
		
		# Assign our menu to this action and an icon
		self.qaction.setMenu(self.menu);
		self.qaction.setIcon(get_icon(PLUGIN_ICONS[0]));
		self.qaction.triggered.connect(self.toolbar_triggered);

	def build_menus(self):
		m = self.menu;
		m.clear();
		
		candidate = self.gui.library_path;
		db = LibraryDatabase (candidate);
		
		ac = create_menu_action_unique(self, m, _('&Clean the selecteds Comments'), PLUGIN_ICONS[0],
									triggered=partial(self._clean_comment),
									shortcut_name='Comments Cleaner')
		self.menu_actions.append (ac);
		
		self.menu.addSeparator();
		ac = create_menu_action_unique(self, m, _('&Customize plugin')+'...', 'config.png', shortcut=False, triggered=self.show_configuration);
		self.menu_actions.append (ac);
		
		self.gui.keyboard.finalize();

	def reactivate_menus(self):
		candidate = self.gui.library_path;
		db = LibraryDatabase (candidate);

	def toolbar_triggered(self):
		self._clean_comment();
		#self.show_configuration();


	def show_configuration(self):
		self.interface_action_base_plugin.do_user_config(self.gui);
		self.reactivate_menus();
		
	def _clean_comment(self):
		if not self.is_library_selected:
			return error_dialog(self.gui, _('No selected book'), _('No book selected for cleaning comments'), show=True);
			return;
		
		rows = self.gui.library_view.selectionModel().selectedRows();
		if not rows or len(rows) == 0:
			return error_dialog(self.gui, _('No selected book'), _('No book selected for cleaning comments'), show=True);
		book_ids = self.gui.library_view.get_selected_ids();
		
		cpgb = CleanerProgressDialog(self.gui, book_ids);
		if cpgb.wasCanceled():
			debug_print('Cleaning comments as cancelled. No change.');
		else:
			cpgb._update_comments_field();
			debug_print('Cleaning launched for '+ str(cpgb.maximum()) +' book.');
			debug_print('Cleaning performed for '+ str(cpgb.books_clean) +' comments.\n');
		
		cpgb.close();
		cpgb = None;
		



class CleanerProgressDialog(QProgressDialog):
	
	def __init__(self, gui, book_ids):
		
		# DB API
		self.dbA = gui.current_db;
		# liste of book id
		self.book_ids = book_ids;
		# book comment dic
		self.books_dic = {};
		# Count of cleaned comments
		self.books_clean = 0;
		
		
		QProgressDialog.__init__(self, '', _('Cancel'), 0, len(self.book_ids), gui);
		self.gui = gui;
		
		self.setValue(0);
		self.setMinimumWidth(500);
		
		self.setWindowTitle(_('Comments Cleaner Progress'));
		self.setWindowIcon(get_icon(PLUGIN_ICONS[0]));
		self.setAutoClose(True);
		self.setAutoReset(False);
		
		self.hide();
		debug_print('Launch cleaning for '+ str(self.maximum()) +' book.');
		
		QTimer.singleShot(0, self._do_clean_comments);
		self.exec_();
		

	def close(self):
		self.dbA = None;
		self.book_ids = None;
		self.books_dic = None;
		self.books_clean = None;
		super(CleanerProgressDialog, self).close();

	def _do_clean_comments(self):
		
		# set value and label
		self.setValue(self.value() + 1);
		self.setLabelText(_('Book %d of %d') % (self.value(), self.maximum()));
		
		if self.maximum() > 50:
			self.show();
		else:
			self.hide();
		
		
		# get the current book id
		book_id = self.book_ids[self.value()-1]
		
		# get the comment
		miA = self.dbA.get_metadata(book_id, index_is_id=True, get_cover=False);
		comment = miA.get('comments');
		
		if self.wasCanceled():
			self.close();
			return;
			
		# process the comment
		if comment is not None:
			debug_text('Text in (book: '+str(self.value())+'/'+str(self.maximum())+')[id: '+str(book_id)+']', comment);
			comment_out = CleanHTML(comment);
			if comment == comment_out:
				debug_print('Unchanged text :::\n');
			else:
				debug_text('Text out', comment_out);
				self.books_dic[book_id] = comment_out;
		
		## If the number of books cleaned is too large,
		## update the DB and create a new dictionary.
		#if len(self.books_dic) > 0 and len(self.books_dic) % 5000 == 0:
		#	self._update_comments_field();
		#	self.books_dic = {};
		
		if self.value() >= self.maximum():
			self.hide();
		else:
			QTimer.singleShot(0, self._do_clean_comments);

	def _update_comments_field(self):
		if len(self.books_dic) > 0:
			if len(self.books_dic) > 1000:
				debug_print('Update the database for '+str(len(self.books_dic))+' books...');
			
			self.books_clean += len(self.books_dic);
			self.dbA.new_api.set_field('comments', {id:self.books_dic[id] for id in self.books_dic.keys()});
			self.gui.iactions['Edit Metadata'].refresh_gui(self.books_dic.keys(), covers_changed=False);
			