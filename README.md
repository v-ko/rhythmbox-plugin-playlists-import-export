Playlists import/export
==========================
A Rhythmbox plugin to export all of your playlists with one click or to import them back (BEWARE THIS DELETES THE EXISTING ONES FROM RB, so export first) again in one click. This allows for synchronizing across computres (with any sync program), and backing up.
Some details:
- Automatic playlists are not affected (only static ones)

Installation
--------------------
- Just get all the files and drop them in /home/user/.local/share/rhythmbox/plugins
- Then restart Rhythmbox

Usage
--------------------
- In the RB menu click Plugins, select the plugin, click Preferences and choose the directory you want to import from or export to. (the default one is /home/user/playlists_import_export)
- Use the 'Import/Export playlists' buttons in the Tools menu

TODO
--------------------
- Warning on first import that existing static playlists will be deleted
- import on startup (there's a bug - we have to wait for stuff to load first) 
- autoexport on runtime playlist changes (+switch autoexport on/off)
      
Change log
--------------------
1.0.0 Initial release
1.0.1 Bugfix: finding the .ui file on some runs was failing
