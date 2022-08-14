#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <un.pogaz@gmail.com>'
__docformat__ = 'restructuredtext en'

import copy, time
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
    from qt.core import QToolButton, QMenu, QProgressDialog, QTimer
except ImportError:
    from PyQt5.Qt import QToolButton, QMenu, QProgressDialog, QTimer

from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import error_dialog
from calibre.gui2.actions import InterfaceAction
from calibre.gui2.ui import get_gui
from calibre.library import current_library_name

from .config import PLUGIN_ICONS, PREFS
from .comments_cleaner import CleanComment
from .common_utils import (debug_print, get_icon, PLUGIN_NAME, current_db, get_BookIds_selected, load_plugin_resources,
                            create_menu_action_unique, has_restart_pending)

GUI = get_gui()

class CommentsCleanerAction(InterfaceAction):
    
    name = PLUGIN_NAME
    # Create our top-level menu/toolbar action (text, icon_path, tooltip, keyboard shortcut)
    action_spec = (PLUGIN_NAME, None, _('Remove the scraps CSS in HTML comments'), None)
    popup_type = QToolButton.MenuButtonPopup
    action_type = 'current'
    dont_add_to = frozenset(['context-menu-device'])
    
    def genesis(self):
        self.is_library_selected = True
        self.menu = QMenu(GUI)
        
        # Read the plugin icons and store for potential sharing with the config widget
        load_plugin_resources(self.plugin_path, PLUGIN_ICONS)
        
        self.rebuild_menus()
        
        # Assign our menu to this action and an icon
        self.qaction.setMenu(self.menu)
        self.qaction.setIcon(get_icon(PLUGIN_ICONS[0]))
        self.qaction.triggered.connect(self.toolbar_triggered)
    
    def initialization_complete(self):
        return
    
    def rebuild_menus(self):
        m = self.menu
        m.clear()
        
        ac = create_menu_action_unique(self, m, _('&Clean the selected comments'), PLUGIN_ICONS[0],
                                             triggered=self._clean_comment,
                                             shortcut_name=PLUGIN_NAME)
        
        self.menu.addSeparator()
        create_menu_action_unique(self, m, _('&Customize plugin...'), 'config.png',
                                             triggered=self.show_configuration,
                                             shortcut=False)
        
        GUI.keyboard.finalize()
    
    def toolbar_triggered(self):
        self._clean_comment()
        #self.show_configuration()
    
    
    def show_configuration(self):
        self.interface_action_base_plugin.do_user_config(GUI)
        
    def _clean_comment(self):
        book_ids = get_BookIds_selected()
        
        cpgb = CleanerProgressDialog(book_ids)
        cpgb.close()
        del cpgb
        


def debug_text(pre, text):
    debug_print(pre+':::\n'+text+'\n')

class CleanerProgressDialog(QProgressDialog):
    def __init__(self, book_ids):
        
        # DB
        self.db = current_db()
        # DB API
        self.dbAPI = self.db.new_api
        
        # liste of book id
        self.book_ids = book_ids
        # Count book
        self.book_count = len(self.book_ids)
        # book comment dic
        self.books_dic = {}
        # Count of cleaned comments
        self.books_clean = 0
        # Exception
        self.exception = None
        
        self.time_execut = 0
        
        
        QProgressDialog.__init__(self, '', _('Cancel'), 0, self.book_count, GUI)
        
        self.setWindowTitle(_('Comments Cleaner progress').format(PLUGIN_NAME))
        self.setWindowIcon(get_icon(PLUGIN_ICONS[0]))
        
        self.setValue(0)
        self.setMinimumWidth(500)
        self.setMinimumDuration(100)
        
        self.setAutoClose(True)
        self.setAutoReset(False)
        
        self.hide()
        debug_print('Launch cleaning for {0} books.'.format(self.book_count))
        debug_print(str(PREFS)+'\n')
        
        QTimer.singleShot(0, self._run_clean_comments)
        self.exec_()
        
        if self.wasCanceled():
            debug_print('Cleaning comments as cancelled. No change.')
        elif self.exception:
            debug_print('Cleaning comments as cancelled. An exception has occurred:')
            debug_print(self.exception)
        else:
            debug_print('Settings: {0}\n'.format(PREFS))
            debug_print('Cleaning launched for {0} books.'.format(self.book_count))
            debug_print('Cleaning performed for {0} comments.'.format(self.books_clean))
            debug_print('Cleaning execute in {:0.3f} seconds.\n'.format(self.time_execut))
    
    def close(self):
        QProgressDialog.close(self)
    
    def _run_clean_comments(self):
        
        start = time.time()
        try:
            self.setValue(0)
            
            for num, book_id in enumerate(self.book_ids, start=1):
                
                # update Progress
                self.setValue(num)
                self.setLabelText(_('Book {:d} of {:d}').format(num, self.book_count))
                
                if self.book_count < 100:
                    self.hide()
                else:
                    self.show()
                
                # get the comment
                miA = self.dbAPI.get_proxy_metadata(book_id)
                comment = miA.get('comments')
                
                if self.wasCanceled():
                    self.close()
                    return
                
                # book_info = "title" (author & author) [book: num/book_count]{id: book_id}
                book_info = '"'+miA.get('title')+'" ('+' & '.join(miA.get('authors'))+') [book: '+str(num)+'/'+str(self.book_count)+']{id: '+str(book_id)+'}'
                
                # process the comment
                if comment is not None:
                    debug_text('Comment for '+book_info, comment)
                    comment_out = CleanComment(comment)
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
                self.setLabelText(_('Update the library for {:d} books...').format(books_dic_count))
                
                self.books_clean += len(self.books_dic)
                self.dbAPI.set_field('comments', {id:self.books_dic[id] for id in self.books_dic.keys()})
                GUI.iactions['Edit Metadata'].refresh_gui(self.books_dic.keys(), covers_changed=False)
            
        except Exception as e:
            self.exception = e
        
        self.time_execut = round(time.time() - start, 3)
        self.db.clean()
        self.hide()
        return
