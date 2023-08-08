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
    from qt.core import QToolButton, QMenu, QProgressDialog, QTimer
except ImportError:
    from PyQt5.Qt import QToolButton, QMenu, QProgressDialog, QTimer

from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import error_dialog
from calibre.gui2.actions import InterfaceAction
from calibre.gui2.ui import get_gui
from calibre.library import current_library_name

from .config import PLUGIN_ICON, PREFS, KEY
from .comments_cleaner import CleanComment
from .common_utils import debug_print, get_icon, PLUGIN_NAME, GUI, current_db, load_plugin_resources
from .common_utils.dialogs import ProgressDialog
from .common_utils.librarys import get_BookIds_selected
from .common_utils.menus import create_menu_action_unique
from .common_utils.columns import get_html


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
        load_plugin_resources(self.plugin_path)
        
        self.rebuild_menus()
        
        # Assign our menu to this action and an icon
        self.qaction.setMenu(self.menu)
        self.qaction.setIcon(get_icon(PLUGIN_ICON))
        self.qaction.triggered.connect(self.toolbar_triggered)
    
    def initialization_complete(self):
        return
    
    def rebuild_menus(self):
        m = self.menu
        m.clear()
        
        create_menu_action_unique(self, m, _('&Clean the selected comments'), PLUGIN_ICON,
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
        book_ids = get_BookIds_selected(show_error=True)
        
        CleanerProgressDialog(book_ids)


def debug_text(pre, text):
    debug_print(pre+':::\n'+text+'\n')

class CleanerProgressDialog(ProgressDialog):
    
    def setup_progress(self, **kvargs):
        # book comment dic
        self.books_dic = {}
        # book custom columns dic
        self.custom_columns_dic = {}
        if PREFS[KEY.CUSTOM_COLUMN]:
            for cc in get_html(True):
                self.custom_columns_dic[cc] = {}
        # Count of cleaned comments
        self.books_clean = 0
        # Exception
        self.exception = None
    
    def end_progress(self):
        
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
    
    def job_progress(self):
        
        debug_print('Launch Comments Cleaner for {:d} books.'.format(self.book_count))
        debug_print(PREFS)
        
        try:
            
            for book_id in self.book_ids:
                
                # update Progress
                num = self.increment()
                
                # get the comment
                miA = self.dbAPI.get_proxy_metadata(book_id)
                comment = miA.get('comments')
                
                if self.wasCanceled():
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
                
                for cc_html in self.custom_columns_dic:
                    comment = miA.get(cc_html)
                    if comment is not None:
                        debug_text(cc_html+' for '+book_info, comment)
                        comment_out = CleanComment(comment)
                        if comment == comment_out:
                            debug_print('Unchanged '+cc_html+' :::\n')
                        else:
                            debug_text(cc_html+' out', comment_out)
                            
                            if book_id not in self.custom_columns_dic[cc_html]:
                                self.custom_columns_dic[cc_html][book_id] = comment_out
                    
                    else:
                        debug_print('Empty comment '+book_info+':::\n')
            
            
            ids = set(self.books_dic.keys())
            for ccbv in self.custom_columns_dic.values():
                ids.update(ccbv.keys())
            books_edit_count = len(ids)
            if books_edit_count > 0:
                
                debug_print('Update the database for {0} books...\n'.format(books_edit_count))
                self.set_value(-1, text=_('Update the library for {:d} books...').format(books_edit_count))
                
                self.books_clean = books_edit_count
                self.dbAPI.set_field('comments', self.books_dic)
                for cck,ccbv in self.custom_columns_dic.items():
                    if ccbv:
                        self.dbAPI.set_field(cck, ccbv)
                GUI.iactions['Edit Metadata'].refresh_gui(ids, covers_changed=False)
            
        except Exception as e:
            self.exception = e
        
