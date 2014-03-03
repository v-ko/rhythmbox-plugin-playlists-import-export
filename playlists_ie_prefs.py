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

import rb, os
from gi.repository import RB, Gtk, Gio, GObject, PeasGtk, GConf

MY_GCONF_PREFIX = "/org/gnome/rhythmbox/plugins/playlists_ie/"
conf = GConf.Client.get_default()

class PlaylistsIOConfigureDialog (GObject.Object, PeasGtk.Configurable):
    __gtype_name__ = 'PlaylistsIOConfigureDialog'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)
#        conf = GConf.Client.get_default()
        folder = conf.get_string(MY_GCONF_PREFIX+"folder")
        if folder is None:
            conf.set_string(MY_GCONF_PREFIX+"folder",os.getcwd()+"playlists_import_export")

    def do_create_configure_widget(self):
        builder = Gtk.Builder()
        builder.add_from_file( os.path.abspath("./playlists_ie_prefs.ui") ) #rb.find_plugin_file(self,)

        self.config = builder.get_object("config")

        self.choose_button = builder.get_object("choose_button")
        self.path_display = builder.get_object("path_display")

        self.choose_button.connect("clicked", self.choose_callback)

#        conf = GConf.Client.get_default()

        folder = conf.get_string(MY_GCONF_PREFIX+"folder")
        self.path_display.set_text(folder)

        return self.config

    def choose_callback(self, widget):
        def response_handler(widget, response):
            if response == Gtk.ResponseType.OK:
                path = self.chooser.get_filename()
                self.chooser.destroy()
                self.path_display.set_text(path)
                conf.set_string(MY_GCONF_PREFIX+"folder",path)
            else:
                self.chooser.destroy()

        buttons = (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE,
                Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.chooser = Gtk.FileChooserDialog(title=_("Choose lyrics folder..."),
                    parent=None,
                    action=Gtk.FileChooserAction.SELECT_FOLDER,
                    buttons=buttons)
        self.chooser.connect("response", response_handler)
        self.chooser.set_modal(True)
        self.chooser.set_transient_for(self.config.get_toplevel())
        self.chooser.present()
