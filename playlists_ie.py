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

import os, rb, logging
from gi.repository import Gio, GObject, Peas, RB, GConf

from playlists_ie_prefs import PlaylistsIOConfigureDialog

MY_GCONF_PREFIX = "/org/gnome/rhythmbox/plugins/playlists_ie/"
conf = GConf.Client.get_default()

class PlaylistLoadSavePlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'PlaylistLoadSavePlugin'
    object = GObject.property(type=GObject.Object)

    def __init__ (self):
        GObject.Object.__init__ (self)
        folder = conf.get_string(MY_GCONF_PREFIX+"folder")
        if folder is None:
            conf.set_string(MY_GCONF_PREFIX+"folder",os.getcwd()+"playlists_import_export")

    def do_activate (self):
        #self.import_playlists()
        shell = self.object    
        app = shell.props.application
        window = shell.props.window        
        
        self.action1 = Gio.SimpleAction.new("import-playlists", None)
        self.action1.connect("activate", self.import_playlists, shell)
        self.action2 = Gio.SimpleAction.new("export-playlists", None)
        self.action2.connect("activate", self.export_playlists, shell)
        
        window.add_action(self.action1)
        window.add_action(self.action2)
        
        item1 = Gio.MenuItem.new(label=_("Import playlists"), detailed_action="win.import-playlists")
        item2 = Gio.MenuItem.new(label=_("Export playlists"), detailed_action="win.export-playlists")
        
        app.add_plugin_menu_item("tools","import-playlists",item1)
        app.add_plugin_menu_item("tools","export-playlists",item2)

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
        folder = conf.get_string(MY_GCONF_PREFIX+"folder")
        pl_man = shell.props.playlist_manager
        
        for playlist in pl_man.get_playlists():

            if( isinstance(playlist, RB.AutoPlaylistSource) ):
                if( playlist.props.name == "Unnamed playlist" ):
                    playlist.props.name = "Unnamed playlist_"
            else :            
                #logging.error("deleting " + playlist.props.name)
                pl_man.delete_playlist(playlist.props.name)
        
        for plfile in os.listdir(folder):
            if plfile.endswith(".m3u"):
                pl_name = plfile[:-4]
                pl_uri = os.path.join(folder,pl_name)
                pl_uri = "file://"+ pl_uri + ".m3u"
                pl_man.parse_file(pl_uri)
                #logging.error("importing "+pl_uri)  
                
                for playlist in pl_man.get_playlists():
                    if(playlist.props.name == "Unnamed playlist"):
                        playlist.props.name = pl_name

    def export_playlists(self, action, parameter, shell):
        folder = conf.get_string(MY_GCONF_PREFIX+"folder")
        pl_man = shell.props.playlist_manager

        for playlist in pl_man.get_playlists():
            if( isinstance(playlist, RB.StaticPlaylistSource) ):
                pl_name = playlist.props.name
                pl_uri = os.path.join(folder,pl_name)
                pl_uri = "file://"+ pl_uri + ".m3u"
                #logging.error("exporting "+pl_name) 
                pl_man.export_playlist(pl_name,pl_uri,1);
