# License : GPLv2 , google it

#TODO: import on startup (there's a bug - we have to wait for stuff to load first) 
#      autoexport on runtime playlist changes
#      skip automatic playlists

import os, re, rb, logging
from gi.repository import Gio, GObject, Peas, RB

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
        pl_man = shell.props.playlist_manager
        
        count = 0
        
        for playlist in pl_man.get_playlists():
            count = count + 1
            if( isinstance(playlist, RB.AutoPlaylistSource) ):
                if( playlist.props.name == "Unnamed playlist" ):
                    playlist.props.name = "Unnamed playlist_"
            else :            
                #logging.error("deleting " + playlist.props.name)
                pl_man.delete_playlist(playlist.props.name)

        print(count)
        
        for plfile in os.listdir("/sync/Music/playlists"):
            if plfile.endswith(".m3u"):
                pl_name = plfile[:-4]
                pl_uri = "file:///sync/Music/playlists/"+plfile
                pl_man.parse_file(pl_uri)
                #logging.error("importing "+pl_name)  
                
                #add a dummy playlist, because the last imported will 
                #pl_man.new_playlist("dummy_dummy_dummy")            
                
                for playlist in pl_man.get_playlists():
                    if(playlist.props.name == "Unnamed playlist"):
                        playlist.props.name = pl_name
                
                #pl_man.delete_playlist("dummy_dummy_dummy")

    def export_playlists(self, action, parameter, shell):
        pl_man = shell.props.playlist_manager

        for playlist in pl_man.get_playlists():
            if( isinstance(playlist, RB.StaticPlaylistSource) ):
                pl_name = playlist.props.name
                pl_uri = "file:///sync/Music/playlists/" + pl_name
                pl_uri = pl_uri + ".m3u"
                #logging.error("exporting "+pl_name) 
                pl_man.export_playlist(pl_name,pl_uri,1);
            

#connect to changes in playl

