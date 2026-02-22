# Orca
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Provides a graphical speech monitor, mainly for development tasks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from . import guilabels

if TYPE_CHECKING:
    from collections.abc import Callable

MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 72
ZOOM_STEP = 2


class SpeechMonitor(Gtk.Window):  # pylint: disable=too-many-instance-attributes
    """Displays a GUI speech monitor showing a scrolling log of spoken text."""

    _shared_css_provider: Gtk.CssProvider | None = None

    # pylint: disable-next=too-many-statements
    def __init__(
        self,
        font_size: int = 14,
        foreground: str = "#ffffff",
        background: str = "#000000",
        on_close: Callable[[], None] | None = None,
    ) -> None:
        """Create a new SpeechMonitor."""

        # pylint: disable=no-member

        super().__init__()
        self._on_close = on_close
        self._font_size = font_size
        self._default_font_size = font_size
        self._foreground = foreground
        self._background = background
        self.set_title(guilabels.SPEECH_MONITOR)
        self.set_default_size(1000, 400)
        self.set_icon_name("orca")

        titlebar = Gtk.Box()
        self.set_titlebar(titlebar)

        self._close_icon = Gtk.Image.new_from_icon_name(
            "window-close-symbolic",
            Gtk.IconSize.LARGE_TOOLBAR,
        )
        close_btn = Gtk.Button()
        close_btn.set_image(self._close_icon)
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        close_btn.connect("clicked", self._on_close_clicked)

        title_label = Gtk.Label(label=guilabels.SPEECH_MONITOR)
        title_label.set_halign(Gtk.Align.CENTER)

        drag_bar = Gtk.EventBox()
        drag_bar.add(title_label)
        drag_bar.connect("button-press-event", self._on_drag_bar_press)

        close_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        close_row.pack_start(drag_bar, True, True, 0)
        close_row.pack_end(close_btn, False, False, 0)

        self._text_view = Gtk.TextView()
        self._text_view.set_editable(False)
        self._text_view.set_cursor_visible(True)
        self._text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._text_view.set_left_margin(6)
        self._text_view.set_right_margin(6)
        self._text_view.set_top_margin(6)
        self._text_view.set_bottom_margin(6)
        self._buffer = self._text_view.get_buffer()
        self._end_mark = self._buffer.create_mark("end", self._buffer.get_end_iter(), False)
        self._line_count = 0

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self._text_view)

        border_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        border_box.pack_start(close_row, False, False, 0)
        border_box.pack_start(scrolled, True, True, 0)
        self.add(border_box)

        self.get_style_context().add_class("speech-monitor")
        titlebar.get_style_context().add_class("speech-monitor-titlebar")
        title_label.get_style_context().add_class("speech-monitor-title")
        close_btn.get_style_context().add_class("speech-monitor-close")
        border_box.get_style_context().add_class("speech-monitor-border")
        self._text_view.get_style_context().add_class("speech-monitor-text")

        if SpeechMonitor._shared_css_provider is None:
            SpeechMonitor._shared_css_provider = Gtk.CssProvider()
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),  # pylint: disable=no-value-for-parameter
                SpeechMonitor._shared_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
        self._apply_css()

        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        self.set_focus(self._text_view)
        self.connect("notify::is-active", self._on_window_activated)
        self.connect("delete-event", self._on_delete_event)
        self.connect("key-press-event", self._on_key_press)

    def _on_window_activated(self, _window: Gtk.Window, _pspec: Any) -> None:
        """Grab focus on the text view whenever the window becomes active."""

        if self.is_active():
            self._text_view.grab_focus()

    def _on_close_clicked(self, _button: Gtk.Button) -> None:
        """Handle the close button click."""

        if self._on_close is not None:
            self._on_close()

    def _on_drag_bar_press(self, _widget: Gtk.Widget, event: Gdk.EventButton) -> bool:
        """Initiate a window move when the drag bar is clicked."""

        # pylint: disable=no-member
        if event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
            return True
        return False

    def _on_delete_event(self, _window: Gtk.Window, _event: Gdk.Event) -> bool:
        """Intercept the close request to toggle the monitor off."""

        if self._on_close is not None:
            self._on_close()
        return True

    def _on_key_press(self, _window: Gtk.Window, event: Gdk.EventKey) -> bool:
        """Handle Ctrl+Plus/Minus/0 for zoom."""

        if not event.state & Gdk.ModifierType.CONTROL_MASK:
            return False

        if event.keyval in (Gdk.KEY_plus, Gdk.KEY_equal, Gdk.KEY_KP_Add):
            self._font_size = min(MAX_FONT_SIZE, self._font_size + ZOOM_STEP)
            self._apply_css()
            return True
        if event.keyval in (Gdk.KEY_minus, Gdk.KEY_KP_Subtract):
            self._font_size = max(MIN_FONT_SIZE, self._font_size - ZOOM_STEP)
            self._apply_css()
            return True
        if event.keyval in (Gdk.KEY_0, Gdk.KEY_KP_0):
            self._font_size = self._default_font_size
            self._apply_css()
            return True

        return False

    def set_font_size(self, size: int) -> None:
        """Updates the font size and reapplies CSS."""

        self._font_size = size
        self._apply_css()

    def reapply_css(
        self,
        foreground: str | None = None,
        background: str | None = None,
    ) -> None:
        """Reapplies CSS styling (e.g. after color changes)."""

        if foreground is not None:
            self._foreground = foreground
        if background is not None:
            self._background = background
        self._apply_css()

    def _apply_css(self) -> None:
        """Apply CSS styling for background color, text color, font size, and border."""

        bg = self._background
        fg = self._foreground
        close_px = max(16, self._font_size * 2)
        css = (
            f".speech-monitor {{ background-color: {bg}; }}\n"
            f".speech-monitor-titlebar {{ min-height: 0; padding: 0; margin: 0; "
            f"background-color: {bg}; border: none; box-shadow: none; }}\n"
            f".speech-monitor decoration {{ box-shadow: none; "
            f"border: none; }}\n"
            f".speech-monitor-title {{ color: {fg}; font-weight: bold; }}\n"
            f".speech-monitor-close {{ min-height: {close_px}px; min-width: {close_px}px; "
            f"padding: 2px; margin: 0; color: {fg}; }}\n"
            f".speech-monitor-close:hover {{ opacity: 0.7; }}\n"
            f".speech-monitor-border {{ border: 3px solid {fg}; }}\n"
            f".speech-monitor-text {{ font-size: {self._font_size}pt; }}\n"
            f".speech-monitor-text text {{ color: {fg}; background-color: {bg}; }}"
        )
        self._close_icon.set_pixel_size(close_px)
        if SpeechMonitor._shared_css_provider is not None:
            SpeechMonitor._shared_css_provider.load_from_data(css.encode())

    def clear(self) -> None:
        """Clears the speech monitor display."""

        self._buffer.set_text("")
        self._line_count = 0

    def _append_text(self, text: str) -> None:
        """Appends text, trims excess lines, and scrolls to the bottom."""

        self._buffer.insert(self._buffer.get_end_iter(), text)
        self._line_count += text.count("\n")
        if self._line_count > 500:
            excess = self._line_count - 500
            start = self._buffer.get_start_iter()
            cut_point = self._buffer.get_iter_at_line(excess)
            self._buffer.delete(start, cut_point)
            self._line_count = 500

        self._buffer.place_cursor(self._buffer.get_end_iter())
        self._text_view.scroll_mark_onscreen(self._end_mark)

    def write_text(self, text: str) -> None:
        """Appends spoken text to the monitor."""

        self._append_text(f"{text}\n")

    def write_key_event(self, key_description: str) -> None:
        """Appends a formatted key event entry to the monitor."""

        self._append_text(f"[key: {key_description}]\n")

    def write_character(self, character: str) -> None:
        """Appends a formatted character entry to the monitor."""

        self._append_text(f"[char: {character}]\n")
