#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import rb
from gi.repository import RB, Gtk, Gio, GObject, PeasGtk


class PlaylistsIOConfigureDialog (GObject.Object, PeasGtk.Configurable):
    __gtype_name__ = 'PlaylistsIOConfigureDialog'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)
        self.config = None
        self.chooser = None
        self.choose_button = None
        self.path_display = None
        self.import_skip_box = None

    def do_create_configure_widget(self):
        builder = Gtk.Builder()
        builder.add_from_file(rb.find_plugin_file(self, "playlists_ie_prefs.ui"))

        self.config = builder.get_object("config")

        self.choose_button = builder.get_object("choose_button")
        self.path_display = builder.get_object("path_display")
        self.import_skip_box = builder.get_object("import_skip_check")

        self.choose_button.connect("clicked", self.choose_callback)
        self.path_display.connect("changed", self.path_changed_callback)
        self.import_skip_box.connect("toggled", self.import_skip_box_callback)

        settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.playlists_ie")
        folder = settings.get_string("ie-folder")  # get the import-export folder
        importskip = settings.get_boolean("import-skip")  # get import-skip boolean from settings

        self.path_display.set_text(folder)
        self.import_skip_box.set_active(importskip)

        return self.config

    def choose_callback(self, widget):
        def response_handler(responsewidget, response):
            if response == Gtk.ResponseType.OK:
                path = self.chooser.get_filename()
                self.chooser.destroy()
                self.path_display.set_text(path)

            else:
                self.chooser.destroy()

        buttons = (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE,
                   Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.chooser = Gtk.FileChooserDialog(title="Choose folder for import/export...",
                                             parent=None,
                                             action=Gtk.FileChooserAction.SELECT_FOLDER,
                                             buttons=buttons)
        self.chooser.connect("response", response_handler)
        self.chooser.set_modal(True)
        self.chooser.set_transient_for(self.config.get_toplevel())
        self.chooser.present()

    def path_changed_callback(self, widget):
        path = self.path_display.get_text()

        settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.playlists_ie")
        settings.set_string("ie-folder", path)  # get the import-export folder

    def import_skip_box_callback(self, widget):
        active = self.import_skip_box.get_active()

        settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.playlists_ie")
        settings.set_boolean("import-skip", active)  # set the import-skip status
