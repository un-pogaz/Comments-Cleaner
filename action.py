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
from datetime import datetime
try:
    from PyQt5.Qt import QToolButton, QMenu, QProgressDialog, QTimer
except ImportError:
    from PyQt4.Qt import QToolButton, QMenu, QProgressDialog, QTimer

from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import error_dialog
from calibre.gui2.actions import InterfaceAction
from calibre.library import current_library_name

from calibre_plugins.comments_cleaner.config import PLUGIN_ICONS, PREFS
from calibre_plugins.comments_cleaner.common_utils import set_plugin_icon_resources, get_icon, create_menu_action_unique, debug_print, debug_text

from calibre_plugins.comments_cleaner.CommentsCleaner import CleanHTML

class CommentCleanerAction(InterfaceAction):
    
    name = 'Comments Cleaner'
    # Create our top-level menu/toolbar action (text, icon_path, tooltip, keyboard shortcut)
    action_spec = ('Comments Cleaner', None, _('Remove the scraps CSS in HTML comments'), None)
    popup_type = QToolButton.MenuButtonPopup
    action_type = 'current'
    dont_add_to = frozenset(['context-menu-device'])
    
    def genesis(self):
        self.is_library_selected = True
        self.menu = QMenu(self.gui)
        self.menu_actions = []
        
        # Read the plugin icons and store for potential sharing with the config widget
        icon_resources = self.load_resources(PLUGIN_ICONS)
        set_plugin_icon_resources(self.name, icon_resources)
        
        self.build_menus()
        
        # Assign our menu to this action and an icon
        self.qaction.setMenu(self.menu)
        self.qaction.setIcon(get_icon(PLUGIN_ICONS[0]))
        self.qaction.triggered.connect(self.toolbar_triggered)
    
    def build_menus(self):
        m = self.menu
        m.clear()
        
        ac = create_menu_action_unique(self, m, _('&Clean the selecteds Comments'), PLUGIN_ICONS[0],
                                             triggered=partial(self._clean_comment),
                                             shortcut_name='Comments Cleaner')
        self.menu_actions.append(ac)
        
        self.menu.addSeparator()
        ac = create_menu_action_unique(self, m, _('&Customize plugin...'), 'config.png',
                                             triggered=self.show_configuration,
                                             shortcut=False)
        self.menu_actions.append(ac)
        
        self.gui.keyboard.finalize()
    
    def toolbar_triggered(self):
        self._clean_comment()
        #self.show_configuration()
    
    
    def show_configuration(self):
        self.interface_action_base_plugin.do_user_config(self.gui)
        
    def _clean_comment(self):
        if not self.is_library_selected:
            return error_dialog(self.gui, _('No selected book'), _('No book selected for cleaning comments'), show=True)
            return
        
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, _('No selected book'), _('No book selected for cleaning comments'), show=True)
        book_ids = self.gui.library_view.get_selected_ids()
        
        cpgb = CleanerProgressDialog(self.gui, book_ids)
        cpgb.close()
        cpgb = None
        


class CleanerProgressDialog(QProgressDialog):
    
    def __init__(self, gui, book_ids):
        
        # DB API
        self.dbA = gui.current_db.new_api
        # liste of book id
        self.book_ids = book_ids
        # Count book
        self.book_count = len(self.book_ids)
        # book comment dic
        self.books_dic = {}
        # Count of cleaned comments
        self.books_clean = 0
        
        
        QProgressDialog.__init__(self, '', _('Cancel'), 0, self.book_count, gui)
        self.gui = gui
        
        self.setWindowTitle(_('Comments Cleaner Progress'))
        self.setWindowIcon(get_icon(PLUGIN_ICONS[0]))
        
        self.setValue(0)
        self.setMinimumWidth(500)
        self.setMinimumDuration(100)
        
        self.setAutoClose(True)
        self.setAutoReset(False)
        
        self.hide()
        debug_print('Launch cleaning for {0} book.'.format(self.book_count))
        debug_print(str(PREFS)+'\n')
        
        QTimer.singleShot(0, self._run_clean_comments)
        self.exec_()
        
        if self.wasCanceled():
            debug_print('Cleaning comments as cancelled. No change.')
        else:
            debug_print('Cleaning launched for {0} book.'.format(self.book_count))
            debug_print('Cleaning performed for {0} comments.'.format(self.books_clean))
            debug_print('Settings: {0}\n'.format(PREFS))
    
    def close(self):
        self.dbA = None
        self.books_dic = None
        super(CleanerProgressDialog, self).close()
    
    def _run_clean_comments(self):
        
        self.setValue(0)
        
        for num, book_id in enumerate(self.book_ids, start=1):
            
            # update Progress
            self.setValue(num)
            self.setLabelText(_('Book {0} of {1}').format(num, self.book_count))
            
            if self.book_count < 100:
                self.hide()
            else:
                self.show()
            
            # get the comment
            miA = self.dbA.get_metadata(book_id, get_cover=False, get_user_categories=False)
            comment = miA.get('comments')
            
            if self.wasCanceled():
                self.close()
                return
            
            # book_info = "title" (author & author) [book: num/book_count]{id: book_id}
            book_info = '"'+miA.get('title')+'" ('+' & '.join(miA.get('authors'))+') [book: '+str(num)+'/'+str(self.book_count)+']{id: '+str(book_id)+'}'
            
            # process the comment
            if comment is not None:
                debug_text('Comment for '+book_info, comment)
                comment_out = CleanHTML(comment)
                if comment == comment_out:
                    debug_print('Unchanged comment :::\n')
                else:
                    debug_text('Comment out', comment_out)
                    self.books_dic[book_id] = comment_out
            
            else:
                debug_print('Empty comment '+book_info+':::\n')
            
        
        books_dic_count = len(self.books_dic)
        if books_dic_count > 0:
            
            debug_print('Update the database for {0} books...\n'.format(books_dic_count))
            self.setLabelText(_('Update the library for {0} books...').format(books_dic_count))
            
            self.books_clean += len(self.books_dic)
            self.dbA.set_field('comments', {id:self.books_dic[id] for id in self.books_dic.keys()})
            self.gui.iactions['Edit Metadata'].refresh_gui(self.books_dic.keys(), covers_changed=False)
        
        self.hide()
        return
