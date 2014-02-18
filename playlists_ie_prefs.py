

from os import system, path

import rb
from gi.repository import RB, Gtk, Gio, GObject, PeasGtk

import gettext
gettext.install('rhythmbox', RB.locale_dir())

class PlaylistsIOConfigureDialog (GObject.Object, PeasGtk.Configurable):
	__gtype_name__ = 'PlaylistsIOConfigureDialog'
	object = GObject.property(type=GObject.Object)

	def __init__(self):
		GObject.Object.__init__(self)
		self.settings = Gio.Settings("org.gnome.rhythmbox.plugins.playlists_ie")

	def do_create_configure_widget(self):
		builder = Gtk.Builder()
		builder.add_from_file(rb.find_plugin_file(self, "playlists_ie_prefs.ui"))

		self.config = builder.get_object("config")

		self.choose_button = builder.get_object("choose_button")
		self.path_display = builder.get_object("path_display")

		self.choose_button.connect("clicked", self.choose_callback)

		self.folder = self.get_prefs()
		if self.folder is None:
			self.folder = '~/.playlists_ie'
		self.path_display.set_text(self.folder)

		return self.config

	def choose_callback(self, widget):
		def response_handler(widget, response):
			if response == Gtk.ResponseType.OK:
				path = self.chooser.get_filename()
				self.chooser.destroy()
				self.path_display.set_text(path)
				self.settings['folder'] = path
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

	def get_prefs (self):
		folder = self.settings['folder']

		print("playlists_ie folder: " + folder)
		return (folder)
