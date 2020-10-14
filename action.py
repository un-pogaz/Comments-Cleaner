#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
						print_function)

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <>'
__docformat__ = 'restructuredtext en'

from datetime import datetime
from functools import partial
try:
	from PyQt5.Qt import Qt, QToolButton, QMenu, QProgressDialog, QModelIndex
except ImportError:
	from PyQt4.Qt import Qt, QToolButton, QMenu, QProgressDialog


from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import error_dialog
from calibre.gui2.actions import InterfaceAction
from calibre.library import current_library_name

from calibre_plugins.comments_cleaner.config import PLUGIN_ICONS
from calibre_plugins.comments_cleaner.common_utils import set_plugin_icon_resources, get_icon, create_menu_action_unique, debug_print, debug_text, RegexSimple, RegexSearch, RegexLoop

from calibre_plugins.comments_cleaner.CommentsCleaner import *

import os, sys, time

try:
	debug_print("Comments Cleaner::action.py - loading translations")
	load_translations()
except NameError:
	debug_print("Comments Cleaner::action.py - exception when loading translations")
	pass # load_translations() added in calibre 1.9

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
			return
		
		rows = self.gui.library_view.selectionModel().selectedRows();
		if not rows or len(rows) == 0 :
			return error_dialog(self.gui, _('No selected book'), _('No book selected for cleaning comments'), show=True);
		book_ids = self.gui.library_view.get_selected_ids();
		
		self._do_clean_text (book_ids);

	def _do_clean_text(self, book_ids):
		
		self.dbA = self.gui.current_db;
		
		books_dic = {};
		
		# Count of cleaned comments
		books_clean = 0;
		
		debug_print('Launch cleaning for '+ str(len(book_ids)) +' book.');
		
		# For each book, clean the comments
		for book_id in book_ids:
			
			miA = self.dbA.get_metadata(book_id, index_is_id=True, get_cover=False);
			comment = miA.get('comments');
			
			if comment is not None:
				debug_text('Text in ['+str(book_id)+']', comment);
				comment_out = CleanHTML(comment);
				if comment == comment_out:
					debug_print('Unchanged text :::\n');
				else:
					debug_text('Text out', comment_out);
					books_dic[book_id] = comment_out;
			
			# If the number of books cleaned is too large,
			# update the DB and create a new dictionary.
			if ((len(books_dic) > 0) and (len(books_dic) % 2500 == 0)):
				books_clean += len(books_dic);
				self._update_comments_field(books_dic);
				books_dic = {};
			
		
		books_clean += len(books_dic);
		self._update_comments_field(books_dic);
		debug_print('Cleaning performed for '+ str(books_clean) +' book.\n');
		self.dbA = None;
		

	def _update_comments_field(self, books_dic):
		if len(books_dic) > 0:
			debug_print('Update the database for '+str(len(books_dic))+' books.');
			self.dbA.new_api.set_field('comments', {id:books_dic[id] for id in books_dic.keys()});
			self.gui.iactions['Edit Metadata'].refresh_gui(books_dic.keys(), covers_changed=False);