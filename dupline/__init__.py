# -*- coding: utf-8 -*-

#  Copyright (C) 2014 - Ignacio Casal Quinteiro
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with This program. If not, see <http://www.gnu.org/licenses/>.


from gi.repository import GObject, Gio, Gdk, Gtk, Gedit

class DupLineAppActivatable(GObject.Object, Gedit.AppActivatable):

    app = GObject.property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.app.set_accels_for_action("win.dupline-up", ["<Super><Alt>Up"])
        self.app.set_accels_for_action("win.dupline-down", ["<Super><Alt>Down"])

    def do_deactivate(self):
        self.app.set_accels_for_action("win.dupline-up", None)
        self.app.set_accels_for_action("win.dupline-down", None)


class DupLineWindowActivatable(GObject.Object, Gedit.WindowActivatable):

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        action = Gio.SimpleAction(name="dupline-up")
        action.connect('activate', self.on_dupline_up_activate)
        self.window.add_action(action)

        action = Gio.SimpleAction(name="dupline-down")
        action.connect('activate', self.on_dupline_down_activate)
        self.window.add_action(action)

    def do_deactivate(self):
        self.window.remove_action("dupline-up")
        self.window.remove_action("dupline-down")

    def do_update_state(self):
        self.window.lookup_action("dupline-up").set_enabled(self.window.get_active_document() != None)
        self.window.lookup_action("dupline-down").set_enabled(self.window.get_active_document() != None)

    def get_view_activatable(self, view):
        if not hasattr(view, "dupline_view_activatable"):
            return None
        return view.dupline_view_activatable

    def call_view_activatable(self, cb):
        view = self.window.get_active_view()

        if view:
            cb(self.get_view_activatable(view))

    # Menu activate handlers
    def on_dupline_up_activate(self, action, parameter, user_data=None):
        self.call_view_activatable(lambda va: va.dupline_up())

    def on_dupline_down_activate(self, action, parameter, user_data=None):
        self.call_view_activatable(lambda va: va.dupline_down())


class DupLineViewActivatable(GObject.Object, Gedit.ViewActivatable):

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.view.dupline_view_activatable = self

    def do_deactivate(self):
        delattr(self.view, "dupline_view_activatable")

    def do_update_state(self):
        pass

    def dupline_up(self):
        buf = self.view.get_buffer()
        insert = buf.get_insert()
        start = buf.get_iter_at_mark(insert)
        start.set_line_offset(0)
        end = start.copy()

        end.forward_line()
        text = buf.get_slice(start, end, True)
        if text is not None and text != "":
            add_newline = False
            if end.is_end():
                add_newline = True

            buf.begin_user_action()
            buf.insert(start, text)
            if add_newline:
                buf.insert(start, "\n")
            buf.end_user_action()

    def dupline_down(self):
        buf = self.view.get_buffer()
        insert = buf.get_insert()
        start = buf.get_iter_at_mark(insert)
        start.set_line_offset(0)
        end = start.copy()

        end.forward_line()
        text = buf.get_slice(start, end, True)
        if text is not None and text != "":
            forwarded = start.forward_line()

            buf.begin_user_action()
            if not forwarded:
                buf.insert(start, "\n")
            buf.insert(start, text)
            buf.end_user_action()

# ex:ts=4:et:
