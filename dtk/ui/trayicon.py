#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from theme import ui_theme
from dtk.ui.window import Window
import gtk

def menu_grab_transfer_window_get(menu):
    event_window = gtk.gdk.Window(
        parent=menu.get_root_window(),
        x = -100,
        y = -100,
        width = 10,
        height = 10,
        window_type = gtk.gdk.WINDOW_TEMP,
        wclass = gtk.gdk.INPUT_ONLY,
        override_redirect = True,
        event_mask = 0
        )
    event_window.set_user_data(menu)
    event_window.show()
    return event_window

def menu_grab_transfer_window_destroy(gdk_window):
    if gdk_window:
        gdk_window.set_user_data(None);
        gdk_window.destroy()    

def popup_grab_on_window (gdk_window, activate_time, grab_keyboard=False):
    if (gtk.gdk.pointer_grab(gdk_window, 
                             True,
                             gtk.gdk.POINTER_MOTION_MASK 
                             | gtk.gdk.BUTTON_PRESS_MASK 
                             | gtk.gdk.BUTTON_RELEASE_MASK 
                             | gtk.gdk.ENTER_NOTIFY_MASK 
                             | gtk.gdk.LEAVE_NOTIFY_MASK, 
                             None, 
                             None, 
                             activate_time)):

        if ((not grab_keyboard) 
            or gtk.gdk.keyboard_grab(gdk_window, True, activate_time) == 0):
            return True
        else:
            gtk.gdk.pointer_ungrab(gtk.gdk.CURRENT_TIME)
            return False
    return False
    



class TrayIcon(Window):
    def __init__(self,
                 y_padding=15,
                 tray_icon_to_screen_width=10,
                 align_size=10,
                 show_pixbuf=None,
                 hide_pixbuf=None
                 ):
        Window.__init__(self, 
                        window_type=gtk.WINDOW_POPUP
                        )
        # Init values.        
        self.y_padding = y_padding
        self.tray_icon_to_screen_width = tray_icon_to_screen_width
        self.align_size = align_size
        self.show_pixbuf = show_pixbuf
        self.hide_pixbuf = hide_pixbuf
        # Init setting.
        self.set_title("Linux Deepin Desktop Trayicon")
        self.set_can_focus(True)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        # Init event.
        self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.connect("show", self.init_menu)
        self.connect("destroy", lambda w : gtk.main_quit()) 
        self.connect("button-press-event", self.menu_grab_window_button_press)
        # Init trayicon.
        self.init_tray_icon()        
        # Init frame.
        self.init_tray_alignment()
        # Init root and screen.
        self.root = self.get_root_window()
        self.screen = self.root.get_screen()        
        self.hide_all()        
            
    def init_menu(self, widget):
        gtk.gdk.pointer_grab(
            self.window,
            True,
            gtk.gdk.POINTER_MOTION_MASK
            | gtk.gdk.BUTTON_PRESS_MASK
            | gtk.gdk.BUTTON_RELEASE_MASK
            | gtk.gdk.ENTER_NOTIFY_MASK
            | gtk.gdk.LEAVE_NOTIFY_MASK,
            None,
            None,
            gtk.gdk.CURRENT_TIME)
        gtk.gdk.keyboard_grab(self.window, owner_events=False, time=gtk.gdk.CURRENT_TIME)
        self.grab_add()        
        
    def init_tray_alignment(self):    
        self.main_ali = gtk.Alignment(0, 0, 1, 1)
        self.main_ali.set_padding(self.align_size, 
                                  self.align_size, 
                                  self.align_size, 
                                  self.align_size)
        self.window_frame.pack_start(self.main_ali, True, True)
        
    def add_widget(self, widget):    
        self.main_ali.add(widget)
                        
    def menu_grab_window_button_press(self, widget, event):        
        if not ((widget.allocation.x <= event.x <= widget.allocation.width) 
           and (widget.allocation.y <= event.y <= widget.allocation.height)):
            self.hide_all()
            self.grab_remove()
            # self.destroy_event_window(event)
        
    def destroy_event_window(self, event):    
        popup_grab_on_window(self.event_window, event.time, True)
        menu_grab_transfer_window_destroy(self.event_window)
        
    def init_tray_icon(self):
        self.tray_icon = gtk.StatusIcon()
        self.tray_icon.set_visible(True)
        # init events.
        self.tray_icon.connect("activate", self.tray_icon_activate)
        self.tray_icon.connect('popup-menu', self.tray_icon_popup_menu)
         
    def set_from_pixbuf(self, icon_pixbuf=None):
        if icon_pixbuf:
            self.tray_icon.set_from_pixbuf(icon_pixbuf.get_pixbuf())
        
    def set_from_file(self, icon_path=None):    
        if icon_path:
            self.tray_icon.set_from_file(icon_path)                
        
    def tray_icon_activate(self, status_icon):
        self.show_menu()
        
    def tray_icon_popup_menu(self, 
                             status_icon, 
                             button, 
                             activate_time
                             ):
        self.show_menu()
        #
        # self.create_event_window(activate_time)
        
    def create_event_window(self, activate_time):    
        self.event_window = menu_grab_transfer_window_get(self)
        popup_grab_on_window(self.event_window, activate_time)
        
    def show_menu(self):    
        metry = self.tray_icon.get_geometry()
        tray_icon_rect = metry[1]        
        # get screen height and width. 
        screen_h = self.screen.get_height()            
        # tray_icon_rect[0]: x tray_icon_rect[1]: y t...t[2]: width t...t[3]: height
        if (screen_h / 2) <= tray_icon_rect[1] <= screen_h: # bottom trayicon show.
            y_padding = 10 + self.y_padding
            self.move(tray_icon_rect[0] + tray_icon_rect[2]/2 - self.get_size_request()[0]/2, 
                      tray_icon_rect[1] - tray_icon_rect[3]  + y_padding - self.get_size_request()[1])
        else: # top trayicon show.
            y_padding = 15 - self.y_padding
            x = tray_icon_rect[0] + tray_icon_rect[2]/2 - self.get_size_request()[0]/2
            y = tray_icon_rect[1] + tray_icon_rect[3] + y_padding
            x -= self.set_max_show_menu(x)
            self.move(x, y)                      
        #   
        self.show_all()
        
    def set_max_show_menu(self, x):        
        screen_w = self.screen.get_width()        
        screen_rect_width = x + self.get_size_request()[0]
        if (screen_rect_width) > screen_w:
            return screen_rect_width - screen_w + self.tray_icon_to_screen_width
        else:
            return 0
        
        
if __name__ == "__main__":
    tray_icon = TrayIcon(y_padding=15)
    tray_icon.set_opacity(0.95)
    tray_icon.set_size_request(200, 100)
    vbox = gtk.VBox()
    tray_icon.add_widget(vbox)
    gtk.main()