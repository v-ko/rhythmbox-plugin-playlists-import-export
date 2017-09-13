Playlists import/export
==========================
A Rhythmbox plugin to export all of your playlists with one click or to import them back again in one click. This allows for synchronizing across computres (with any sync program), and backing up.
Some details:
- Automatic playlists are not affected (only static ones)

Installation
--------------------
- Pull the project and run the install.sh . If you are on RB 2.XX check the "install.sh -h"
- Then restart Rhythmbox

Usage
--------------------
- In the RB menu click Plugins, select the plugin, click Preferences and choose the directory you want to import from or export to. (the default one is /home/user/playlists_import_export)
- Use the 'Import/Export playlists' buttons in the Tools menu

Change log
--------------------
- 1.0.0 Initial release
- 1.0.1 Bugfix: finding the .ui file on some runs was failing
- 1.1.0 Bugfixes + added warning and progress bar
