import io
import math
import gi
from threading import RLock
from PIL import Image
from gi.repository import GdkPixbuf, GLib

from .tools import set_text_widget_permission, set_label

gi.require_version("Gtk", "3.0")


verrou_tags = RLock()
verrou_mbz = RLock()


class View:
    def __init__(self):
        """
        Here, we initialise the widget we are going to use in the future.
        """

        self.tree_view = None
        self.title = None
        self.album = None
        self.artist = None
        self.genre = None
        self.cover = None
        self.track = None
        self.year = None
        self.length = None
        self.size = None

        # size of the cover
        self.cover_width = 250
        self.cover_height = 250
        self.last_cover = ""

        self.title_mbz = None
        self.album_mbz = None
        self.artist_mbz = None
        self.genre_mbz = None
        self.cover_mbz = None
        self.track_mbz = None
        self.year_mbz = None

    def show_mbz(self, data_scrapped):
        with verrou_mbz:

            # We show the tag currently in tag_dico
            self.title_mbz.set_text(data_scrapped["title"])
            self.track_mbz.set_text(data_scrapped["track"])
            self.genre_mbz.set_text(data_scrapped["genre"])
            self.album_mbz.set_text(data_scrapped["album"])
            self.artist_mbz.set_text(data_scrapped["artist"])
            self.year_mbz.set_text(data_scrapped["year"])

            if data_scrapped["cover"] != "":
                with Image.open(io.BytesIO(data_scrapped["cover"])) as img:

                    try:
                        glib_bytes = GLib.Bytes.new(img.tobytes())
                        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
                            glib_bytes,
                            GdkPixbuf.Colorspace.RGB,
                            False,
                            8,
                            img.width,
                            img.height,
                            len(img.getbands()) * img.width,
                        )

                        pixbuf = pixbuf.scale_simple(
                            250, 250, GdkPixbuf.InterpType.BILINEAR
                        )

                        self.cover_mbz.set_from_pixbuf(pixbuf)
                    except TypeError:
                        self.cover_mbz.set_from_icon_name("emblem-music-symbolic", 6)
            else:
                self.cover_mbz.set_from_icon_name("emblem-music-symbolic", 6)

    def erase(self):
        """
        We erase value written in the GtkEntry of each of those tags
        """
        self.genre.set_text("")
        self.album.set_text("")
        self.title.set_text("")
        self.artist.set_text("")
        self.year.set_text("")
        self.track.set_text("")
        self.cover.set_from_icon_name("emblem-music-symbolic", 6)
        self.last_cover = ""
        self.show_mbz(
            {
                "title": "",
                "track": "",
                "album": "",
                "genre": "",
                "artist": "",
                "cover": "",
                "year": "",
            }
        )

    def show_cover_from_bytes(self, bytes_file):
        with Image.open(io.BytesIO(bytes_file)) as img:
            glib_bytes = GLib.Bytes.new(img.tobytes())

            width = img.width  # The best fix i could find for the moment
            height = img.height
            if glib_bytes.get_size() < width * height * 3:
                width = math.sqrt(glib_bytes.get_size() / 3)
                height = math.sqrt(glib_bytes.get_size() / 3)

            pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
                glib_bytes,
                GdkPixbuf.Colorspace.RGB,
                False,
                8,
                width,
                height,
                len(img.getbands()) * img.width,
            )

            pixbuf = pixbuf.scale_simple(
                self.cover_width, self.cover_height, GdkPixbuf.InterpType.BILINEAR
            )

            self.cover.set_from_pixbuf(pixbuf)

    def show_cover_from_file(self, name_file):
        with Image.open(name_file) as img:
            glib_bytes = GLib.Bytes.new(img.tobytes())

            pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
                glib_bytes,
                GdkPixbuf.Colorspace.RGB,
                False,
                8,
                img.width,
                img.height,
                len(img.getbands()) * img.width,
            )

            pixbuf = pixbuf.scale_simple(
                self.cover_width, self.cover_height, GdkPixbuf.InterpType.BILINEAR
            )

            self.cover.set_from_pixbuf(pixbuf)

    def show_tags(self, tags_dict, multiple_rows):
        with verrou_tags:
            # We show those tags uniquely if there is only one row selected
            set_text_widget_permission(self.title, multiple_rows, tags_dict["title"])
            set_text_widget_permission(self.track, multiple_rows, tags_dict["track"])

            # TODO show size and length for the concatenation of songs
            set_label(self.size, multiple_rows, tags_dict["size"])
            set_label(self.length, multiple_rows, tags_dict["length"])

            # We show the tag currently in tags_dict
            self.genre.set_text(tags_dict["genre"])
            self.album.set_text(tags_dict["album"])
            self.artist.set_text(tags_dict["artist"])
            self.year.set_text(tags_dict["year"])

            # A test to handle if there is a cover
            if tags_dict["cover"] != "":
                if tags_dict["cover"] != self.last_cover:
                    # A test to detect bytes file
                    if isinstance(tags_dict["cover"], bytes):
                        self.show_cover_from_bytes(tags_dict["cover"])
                        self.last_cover = tags_dict["cover"]
                    else:
                        self.show_cover_from_file(tags_dict["cover"])
                        self.last_cover = tags_dict["cover"]
                else:
                    pass
            else:

                self.cover.set_from_icon_name("emblem-music-symbolic", 6)
                self.last_cover = ""


VIEW = View()
