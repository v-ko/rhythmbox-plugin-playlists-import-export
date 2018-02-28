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

import os, rb, logging, time
from gi.repository import Gio, GObject, Peas, RB, Gtk

from playlists_ie_prefs import PlaylistsIOConfigureDialog

class PlaylistLoadSavePlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'PlaylistLoadSavePlugin'
    object = GObject.property(type=GObject.Object)

    def __init__ (self):
        GObject.Object.__init__ (self)

    def do_activate (self):
        #self.import_playlists()
        shell = self.object
        app = shell.props.application
        self.window = shell.props.window

        self.action1 = Gio.SimpleAction.new("import-playlists", None)
        self.action1.connect("activate", self.import_playlists, shell)
        self.action2 = Gio.SimpleAction.new("export-playlists", None)
        self.action2.connect("activate", self.export_playlists, shell)
        self.action3 = Gio.SimpleAction(name="update-playlist")
        self.action3.connect("activate", self.update_playlist, shell)

        self.window.add_action(self.action1)
        self.window.add_action(self.action2)
        self.window.add_action(self.action3)

        item1 = Gio.MenuItem.new(label="Import playlists", detailed_action="win.import-playlists")
        item2 = Gio.MenuItem.new(label="Export playlists", detailed_action="win.export-playlists")
        item3 = Gio.MenuItem.new(label="Update this playlist", detailed_action="win.update-playlist")

        app.add_plugin_menu_item("tools", "import-playlists", item1)
        app.add_plugin_menu_item("tools", "export-playlists", item2)
        app.add_plugin_menu_item("tools", "update-playlist", item3)

    def do_deactivate (self):
        shell = self.object
        app = shell.props.application
        app.remove_plugin_menu_item("view", "import-playlists")
        app.remove_plugin_menu_item("view", "export-playlists")
        app.remove_action("import-playlists")
        app.remove_action("export-playlists")
        self.action1 = None
        self.action2 = None

    def import_playlists(self, action, parameter, shell):
        settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.playlists_ie")
        folder = settings.get_string("ie-folder") #get the import-export folder
        if (os.path.isdir(folder)!=True):
            self.warn_for_no_present_dir()
            return

        self.create_progress_bar_win()
        pl_man = shell.props.playlist_manager
        pl_list = pl_man.get_playlists()
        pl_count = len(pl_list)
        processed_pl_count=0

        for playlist in pl_list:

            while Gtk.events_pending():
                Gtk.main_iteration()

            if( isinstance(playlist, RB.AutoPlaylistSource) ): #keep only auto playlists
                if( playlist.props.name == "Unnamed playlist" ): #this name is used for the newly imported playlists
                    playlist.props.name = "Unnamed playlist_"
            else :
                #logging.error("deleting " + playlist.props.name)
                pl_man.delete_playlist(playlist.props.name)

            processed_pl_count=processed_pl_count+1
            self.update_fraction(1-processed_pl_count/pl_count)

        pl_file_count=0
        processed_pl_files=0

        for pl_file in os.listdir(folder):

            if pl_file.endswith(".m3u"):
                pl_file_count=pl_file_count+1

        for pl_file in os.listdir(folder):

            while Gtk.events_pending():
                Gtk.main_iteration()

            if pl_file.endswith(".m3u"):
                pl_name = pl_file[:-4]
                pl_uri = os.path.join(folder,pl_name)
                pl_uri = "file://"+ pl_uri + ".m3u"
                pl_man.parse_file(pl_uri)
                #logging.error("importing "+pl_uri)

                for playlist in pl_man.get_playlists():
                    if(playlist.props.name == "Unnamed playlist"): #that's the one we imported last , so set it's name
                        playlist.props.name = pl_name

                processed_pl_files=processed_pl_files+1
                self.update_fraction(processed_pl_files/pl_file_count)

        self.progress_window.destroy()

    def import_single_playlist(self, playlist, shell):
        settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.playlists_ie")
        folder = settings.get_string("ie-folder")  # get the import-export folder
        if not os.path.isdir(folder):
            self.warn_for_no_present_dir()
            return

        pl_man = shell.props.playlist_manager

        pl_file_count = 0
        processed_pl_files = 0

        for pl_file in os.listdir(folder):

            if pl_file.lower().endswith(".m3u") and pl_file[:-4] == playlist:
                pl_file_count = pl_file_count + 1

        self.create_progress_bar_win()
        for pl_file in os.listdir(folder):
            while Gtk.events_pending():
                Gtk.main_iteration()

            if pl_file.lower().endswith(".m3u") and pl_file[:-4] == playlist:
                pl_man.delete_playlist(playlist)
                pl_name = pl_file[:-4]
                pl_uri = os.path.join(folder, pl_name)
                pl_uri = "file://" + pl_uri + ".m3u"
                pl_man.parse_file(pl_uri)
                logging.info("importing " + pl_uri)

                for playlist in pl_man.get_playlists():
                    if playlist.props.name == "Unnamed playlist":  # that's the one we imported last , so set it's name
                        playlist.props.name = pl_name

                processed_pl_files = processed_pl_files + 1

        self.progress_window.destroy()

    def update_playlist(self, action, parameter, shell):
        """ get your currently seleced playlist and run import_single_playlist """
        page = shell.props.selected_page
        if not hasattr(page, "get_entry_view"):
            return
        pagetype = shell.props.selected_page.get_name()
        playlist = shell.props.selected_page.get_property('name')
        # self.process_selection(selection)
        if pagetype == 'RBStaticPlaylistSource':
            self.import_single_playlist(playlist, shell)
        else:
            self.warn_not_a_playlist()
        return

    def export_playlists(self, action, parameter, shell):
        settings = Gio.Settings.new("org.gnome.rhythmbox.plugins.playlists_ie")
        folder = settings.get_string("ie-folder") #get the import-export folder
        if (os.path.isdir(folder)!=True):
            self.warn_for_no_present_dir()
            return

        pl_man = shell.props.playlist_manager
        self.create_progress_bar_win()

        pl_list = pl_man.get_playlists()
        pl_count = len(pl_list)
        processed_pl_count=0

        for playlist in pl_list:

            while Gtk.events_pending():
                Gtk.main_iteration()

            if( isinstance(playlist, RB.StaticPlaylistSource) ):
                pl_name = playlist.props.name
                pl_uri = os.path.join(folder,pl_name)
                pl_uri = "file://"+ pl_uri + ".m3u"
                #logging.error("exporting "+pl_name)
                pl_man.export_playlist(pl_name,pl_uri,1);

                processed_pl_count=processed_pl_count+1
                self.update_fraction(processed_pl_count/pl_count)

        self.progress_window.destroy()

    def warn_not_a_playlist(self):

        logging.error("Not viewing a playlist")
        self.messagedialog = Gtk.MessageDialog(parent=self.window,
                                               flags=Gtk.DialogFlags.MODAL,
                                               type=Gtk.MessageType.WARNING,
                                               buttons=Gtk.ButtonsType.OK,
                                               message_format="Please select a static playlist to update")
        self.messagedialog.connect("response", self.destroy_warning)
        self.messagedialog.show()

    def warn_for_no_present_dir(self):

        #logging.error("reached warning for dir")
        messagedialog = Gtk.MessageDialog(parent=self.window,
                                          flags=Gtk.DialogFlags.MODAL,
                                          type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK,
                                          message_format="Please first select a valid directory. (Plugins->Preferences)")
        messagedialog.connect("response", self.destroy_warning)
        messagedialog.show()

    def destroy_warning(arg1,widget,arg3):
        widget.destroy()

    def create_progress_bar_win(self):

        self.progress_window = Gtk.Dialog(title="Import/export progress",
                                          parent=self.window)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_window.get_content_area().add(self.progress_bar)
        self.progress_window.get_action_area().set_size_request(1,-1)

        #self.progress_window.set_transient_for(self.window)
        self.progress_window.set_modal(True)
        self.progress_window.resize(500,30)
        self.progress_window.show_all()


    def update_fraction(self, fraction):

        self.progress_bar.pulse()
        self.progress_bar.set_fraction(fraction)
