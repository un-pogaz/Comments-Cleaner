#!/usr/bin/env python

__license__   = 'GPL v3'
__copyright__ = '2020, un_pogaz <un.pogaz@gmail.com>'


try:
    load_translations()
except NameError:
    pass  # load_translations() added in calibre 1.9

from collections import defaultdict
from typing import List

try:
    from qt.core import QMenu, QTimer, QToolButton
except ImportError:
    from PyQt5.Qt import QMenu, QTimer, QToolButton

from calibre.gui2.actions import InterfaceAction

from .comments_cleaner import clean_comment, normalize_comment
from .common_utils import GUI, PLUGIN_NAME, debug_print, get_icon
from .common_utils.columns import get_html
from .common_utils.dialogs import ProgressDialog, custom_exception_dialog
from .common_utils.librarys import get_BookIds_selected
from .common_utils.menus import create_menu_action_unique
from .config import CALIBRE_HAS_NOTES, KEY, NOTES_ICON, PLUGIN_ICON, PREFS, SelectNotesDialog


class CommentsCleanerAction(InterfaceAction):
    
    name = PLUGIN_NAME
    # Create our top-level menu/toolbar action (text, icon_path, tooltip, keyboard shortcut)
    action_spec = (PLUGIN_NAME, None, _('Remove the scraps CSS in HTML comments'), None)
    popup_type = QToolButton.MenuButtonPopup
    action_type = 'current'
    dont_add_to = frozenset(['context-menu-device'])
    accepts_drops = True

    def genesis(self):
        self.menu = QMenu(GUI)
        self.qaction.setMenu(self.menu)
        self.qaction.setIcon(get_icon(PLUGIN_ICON))
        self.qaction.triggered.connect(self.toolbar_triggered)
        self.rebuild_menus()
    
    def initialization_complete(self):
        return
    
    def rebuild_menus(self):
        m = self.menu
        m.clear()
        
        create_menu_action_unique(self, m, _('Clean the selected &comments'), PLUGIN_ICON,
                                        triggered=self.clean_comments,
                                        unique_name='Clean the selected &comments')
        
        if CALIBRE_HAS_NOTES:
            create_menu_action_unique(self, m, _('Clean category &notes'), NOTES_ICON,
                                        triggered=self.clean_notes,
                                        unique_name='Clean category &notes')
        
        self.menu.addSeparator()
        create_menu_action_unique(self, m, _('&Customize plugin…'), 'config.png',
                                        triggered=self.show_configuration,
                                        unique_name='&Customize plugin',
                                        shortcut=False)
        
        GUI.keyboard.finalize()
    
    def toolbar_triggered(self):
        self.clean_comments()
    
    def show_configuration(self):
        self.interface_action_base_plugin.do_user_config(GUI)
    
    mime = 'application/calibre+from_library'
    
    def accept_enter_event(self, event, mime_data):
        if mime_data.hasFormat(self.mime):
            return True
        return False
    
    def accept_drag_move_event(self, event, mime_data):
        if mime_data.hasFormat(self.mime):
            return True
        return False
    
    def drop_event(self, event, mime_data):
        if mime_data.hasFormat(self.mime):
            self.dropped_ids = tuple(map(int, mime_data.data(self.mime).data().split()))
            QTimer.singleShot(1, self.do_drop)
            return True
        return False
    
    def do_drop(self):
        book_ids = self.dropped_ids
        del self.dropped_ids
        if book_ids:
            self._clean_comments(book_ids)
    
    def clean_comments(self):
        self._clean_comments(get_BookIds_selected(show_error=True))
    
    def clean_notes(self):
        self._clean_notes(get_BookIds_selected(show_error=False))
    
    def _clean_comments(self, book_ids: List[int]):
        CleanerProgressDialog(book_ids)
    
    def _clean_notes(self, book_ids: List[int]):
        d = SelectNotesDialog(book_ids)
        if d.exec():
            notes_lst = d.selected_notes
        else:
            debug_print('Cleaning notes aborted. Selection dialog closed.')
            return
        
        CleanerNoteProgressDialog(notes_lst)


def debug_text(pre, text=None):
    debug_print(pre+':::')
    if text:
        debug_print(text, pre=None)
    print()


class CleanerProgressDialog(ProgressDialog):
    
    def setup_progress(self, **kvargs):
        
        self.used_prefs = PREFS.copy()
        self.used_prefs.pop(KEY.NOTES_SETTINGS, None)
        
        # book comment map
        self.books_comments_map = {'comments':{}}
        # book custom columns dic
        if self.used_prefs[KEY.CUSTOM_COLUMN]:
            self.books_comments_map.update({cc:{} for cc in get_html(True)})
        
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
            custom_exception_dialog(self.exception)
        else:
            debug_print('Settings:', self.used_prefs, '\n')
            debug_print(f'Cleaning launched for {self.book_count} books.')
            debug_print(f'Cleaning performed for {self.books_clean} comments.')
            debug_print(f'Cleaning execute in {self.time_execut:0.3f} seconds.\n')
    
    def job_progress(self):
        
        debug_print(f'Launch Comments Cleaner for {self.book_count} books.')
        debug_print(self.used_prefs)
        print()
        
        try:
            
            for book_id in self.book_ids:
                
                if self.wasCanceled():
                    return
                
                # update Progress
                num = self.increment()
                
                # get the comment
                
                miA = self.dbAPI.get_proxy_metadata(book_id)
                
                # book_info = "title" (author & author) [book: num/book_count]{id: book_id}
                book_info = '"{title}" ({authors}) [book: {num}/{book_count}]{{id: {book_id}}}'.format(
                    title=miA.get('title'),
                    authors=' & '.join(miA.get('authors')),
                    num=num,
                    book_count=self.book_count,
                    book_id=book_id,
                )
                
                # process the comments
                for field in self.books_comments_map.keys():
                    comment = miA.get(field)
                    if comment is not None:
                        debug_text(field+' for '+book_info, comment)
                        comment_norm = normalize_comment(comment)
                        comment_out = clean_comment(comment_norm, self.used_prefs)
                        if comment == comment_out:
                            debug_text('Unchanged '+field)
                        else:
                            if comment != comment_norm:
                                debug_text('Normalize ' + field)
                            if comment_norm != comment_out:
                                debug_text(field+' out', comment_out)
                            self.books_comments_map[field][book_id] = comment_out
                    
                    else:
                        debug_text('Empty '+field+' '+book_info)
            
            ids = set()
            for ccbv in self.books_comments_map.values():
                ids.update(ccbv.keys())
            
            books_edit_count = len(ids)
            if books_edit_count > 0:
                
                debug_print(f'Update the database for {books_edit_count} books…\n')
                self.set_value(-1, text=_('Update the library for {:d} books…').format(books_edit_count))
                
                self.books_clean = books_edit_count
                
                with self.dbAPI.backend.conn:
                    for field,id_val in self.books_comments_map.items():
                        self.dbAPI.set_field(field,id_val)
                
                GUI.iactions['Edit Metadata'].refresh_gui(ids, covers_changed=False)
            else:
                debug_print('No book to update inside the database.\n')
            
        except Exception as e:
            self.exception = e


class CleanerNoteProgressDialog(ProgressDialog):
    
    icon = NOTES_ICON
    title = _('{PLUGIN_NAME} progress').format(PLUGIN_NAME='Notes Cleaner')
    
    def setup_progress(self, **kvargs):
        
        self.used_prefs = PREFS[KEY.NOTES_SETTINGS].copy()
        
        self.note_src = self.book_ids
        self.note_count = []
        for v in self.note_src.values():
            self.note_count.extend(v)
        
        self.note_count = len(self.note_count)
        
        self.note_clean = 0
        self.field_id_notes = defaultdict(dict)
        
        # Exception
        self.exception = None
        
        return self.note_count
    
    def progress_text(self):
        return _('Note {:d} of {:d}').format(self.value(), self.note_count)
    
    def end_progress(self):
        
        if self.wasCanceled():
            debug_print('Cleaning notes as cancelled. No change.')
        elif self.exception:
            debug_print('Cleaning notes as cancelled. An exception has occurred:')
            debug_print(self.exception)
            custom_exception_dialog(self.exception)
        else:
            debug_print('Settings:', self.used_prefs,'\n')
            debug_print(f'Cleaning launched for {self.note_count} notes.')
            debug_print(f'Cleaning performed for {self.note_clean} notes.')
            debug_print(f'Cleaning execute in {self.time_execut:0.3f} seconds.\n')
    
    def job_progress(self):
        debug_print(f'Launch Notes Cleaner for {self.note_count} notes.')
        debug_print(self.used_prefs)
        print()
        
        try:
            
            for field,items in self.note_src.items():
                for (value, item_id) in items:
                    
                    if self.wasCanceled():
                        return
                    
                    # update Progress
                    num = self.increment()
                    
                    # get the note
                    item_name = self.dbAPI.get_item_name(field, item_id)
                    note_data = self.dbAPI.notes_data_for(field, item_id)
                    note = note_data.get('doc', None)
                    
                    note_info = field+':'+item_name+' [note: '+str(num)+'/'+str(self.note_count)+']'
                    
                    # process the note
                    if note is not None:
                        debug_text('Note for '+note_info, note)
                        note_norm = normalize_comment(note)
                        note_out = clean_comment(note_norm, self.used_prefs)
                        if note == note_out:
                            debug_text('Unchanged note')
                        else:
                            if note != note_norm:
                                debug_text('Normalize note')
                            if note_norm != note_out:
                                debug_text('Note out', note_out)
                            note_data['doc'] = note_out
                            self.field_id_notes[field][item_id] = note_data
                    
                    else:
                        debug_text('Empty note '+note_info)
            
            ids = []
            for v in self.field_id_notes.values():
                ids.extend(v)
            note_edit_count = len(ids)
            if note_edit_count > 0:
                
                debug_print(f'Update the database for {note_edit_count} notes…\n')
                self.set_value(-1, text=_('Update the library for {:d} notes…').format(note_edit_count))
                
                with self.dbAPI.backend.conn:
                    for field,values in self.field_id_notes.items():
                        for item_id,note_data in values.items():
                            self.dbAPI.set_notes_for(
                                field, item_id,
                                note_data['doc'],
                                searchable_text=note_data['searchable_text'],
                                resource_hashes=note_data['resource_hashes'],
                            )
                
                self.note_clean = note_edit_count
            
        except Exception as e:
            self.exception = e
