# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

# pylint: disable=too-many-lines
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals

"""Support for braille display output."""

from __future__ import annotations

import locale
import os
import queue
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Iterator, Sequence, TYPE_CHECKING, cast

from gi.repository import GLib

from . import debug
from . import script_manager
from . import settings
from . import text_attribute_manager

from .ax_event_synthesizer import AXEventSynthesizer
from .ax_hypertext import AXHypertext
from .ax_object import AXObject
from .ax_text import AXText, AXTextAttribute
from .orca_platform import tablesdir  # pylint: disable=import-error

try:
    import brlapi as BRLAPI
except (ImportError, OSError):
    BRLAPI = None
    _BRLAPI_AVAILABLE = False
else:
    _BRLAPI_AVAILABLE = True

try:
    from brlapi import OperationError as BrlapiOperationError
except (ImportError, OSError):
    BrlapiOperationError = None

_BRLAPI_OPERATION_ERROR: type[BaseException] | None = BrlapiOperationError

try:
    from brlapi import ConnectionError as BrlapiConnectionError
except (ImportError, OSError):
    BrlapiConnectionError = None

_BRLAPI_CONNECTION_ERROR: type[BaseException] | None = BrlapiConnectionError

try:
    import louis as LOUIS
except (ImportError, OSError):
    LOUIS = None
else:
    # TODO: Can we get the tablesdir info at runtime?
    if not tablesdir:
        LOUIS = None

if TYPE_CHECKING:
    from .input_event import BrailleEvent, InputEvent


_BRLAPI_ERRORS_LIST: list[type[BaseException]] = [
    OSError,
    RuntimeError,
    AttributeError,
    ValueError,
    TypeError,
]
if _BRLAPI_OPERATION_ERROR is not None:
    _BRLAPI_ERRORS_LIST.append(_BRLAPI_OPERATION_ERROR)
if _BRLAPI_CONNECTION_ERROR is not None:
    _BRLAPI_ERRORS_LIST.append(_BRLAPI_CONNECTION_ERROR)
BRLAPI_ERRORS: tuple[type[BaseException], ...] = tuple(_BRLAPI_ERRORS_LIST)
del _BRLAPI_ERRORS_LIST
CALLBACK_ERRORS = (
    AttributeError,
    KeyError,
    IndexError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
    GLib.GError,
)

_BRLAPI_RETRY_DELAY_MS = 2000
_BRLAPI_RETRY_MAX_DELAY_MS = 60000
_BRLAPI_CONNECT_TIMEOUT_MS = 5000
_BRLAPI_TASK_TIMEOUT_MS = 5000
_BRLAPI_DISPLAY_SIZE_POLL_MS = 500
_FLASH_EVENT_SOURCE_ID_INDEFINITE = -666

_BRLAPI_ATTR_NAMES = (
    "KEY_CMD_HWINLT",
    "KEY_CMD_FWINLT",
    "KEY_CMD_FWINLTSKIP",
    "KEY_CMD_HWINRT",
    "KEY_CMD_FWINRT",
    "KEY_CMD_FWINRTSKIP",
    "KEY_CMD_LNUP",
    "KEY_CMD_LNDN",
    "KEY_CMD_FREEZE",
    "KEY_CMD_TOP_LEFT",
    "KEY_CMD_BOT_LEFT",
    "KEY_CMD_HOME",
    "KEY_CMD_SIXDOTS",
    "KEY_CMD_ROUTE",
    "KEY_CMD_CUTBEGIN",
    "KEY_CMD_CUTLINE",
    "KEY_FLG_TOGGLE_ON",
    "KEY_TYPE_CMD",
    "rangeType_all",
    "rangeType_command",
    "PARAM_CLIENT_PRIORITY",
)

if BRLAPI is None:
    _BRLAPI_ATTRS: dict[str, Any | None] = {name: None for name in _BRLAPI_ATTR_NAMES}
else:
    _BRLAPI_ATTRS = {name: getattr(BRLAPI, name, None) for name in _BRLAPI_ATTR_NAMES}

BRLAPI_KEY_CMD_HWINLT = _BRLAPI_ATTRS["KEY_CMD_HWINLT"]
BRLAPI_KEY_CMD_FWINLT = _BRLAPI_ATTRS["KEY_CMD_FWINLT"]
BRLAPI_KEY_CMD_FWINLTSKIP = _BRLAPI_ATTRS["KEY_CMD_FWINLTSKIP"]
BRLAPI_KEY_CMD_HWINRT = _BRLAPI_ATTRS["KEY_CMD_HWINRT"]
BRLAPI_KEY_CMD_FWINRT = _BRLAPI_ATTRS["KEY_CMD_FWINRT"]
BRLAPI_KEY_CMD_FWINRTSKIP = _BRLAPI_ATTRS["KEY_CMD_FWINRTSKIP"]
BRLAPI_KEY_CMD_LNUP = _BRLAPI_ATTRS["KEY_CMD_LNUP"]
BRLAPI_KEY_CMD_LNDN = _BRLAPI_ATTRS["KEY_CMD_LNDN"]
BRLAPI_KEY_CMD_FREEZE = _BRLAPI_ATTRS["KEY_CMD_FREEZE"]
BRLAPI_KEY_CMD_TOP_LEFT = _BRLAPI_ATTRS["KEY_CMD_TOP_LEFT"]
BRLAPI_KEY_CMD_BOT_LEFT = _BRLAPI_ATTRS["KEY_CMD_BOT_LEFT"]
BRLAPI_KEY_CMD_HOME = _BRLAPI_ATTRS["KEY_CMD_HOME"]
BRLAPI_KEY_CMD_SIXDOTS = _BRLAPI_ATTRS["KEY_CMD_SIXDOTS"]
BRLAPI_KEY_CMD_ROUTE = _BRLAPI_ATTRS["KEY_CMD_ROUTE"]
BRLAPI_KEY_CMD_CUTBEGIN = _BRLAPI_ATTRS["KEY_CMD_CUTBEGIN"]
BRLAPI_KEY_CMD_CUTLINE = _BRLAPI_ATTRS["KEY_CMD_CUTLINE"]
BRLAPI_KEY_FLG_TOGGLE_ON = _BRLAPI_ATTRS["KEY_FLG_TOGGLE_ON"]
BRLAPI_KEY_TYPE_CMD = _BRLAPI_ATTRS["KEY_TYPE_CMD"]
BRLAPI_RANGE_TYPE_ALL = _BRLAPI_ATTRS["rangeType_all"]
BRLAPI_RANGE_TYPE_COMMAND = _BRLAPI_ATTRS["rangeType_command"]
BRLAPI_PARAM_CLIENT_PRIORITY = _BRLAPI_ATTRS["PARAM_CLIENT_PRIORITY"]

del _BRLAPI_ATTR_NAMES, _BRLAPI_ATTRS


# The size of the physical display (width, height).  The coordinate system of
# the display is set such that the upper left is (0,0), x values increase from
# left to right, and y values increase from top to bottom.
#
# TODO: Only a height of 1 is supported at this time.
DEFAULT_DISPLAY_SIZE = 32

# BRLAPI priority levels if Orca should have idle, normal or high priority
BRLAPI_PRIORITY_IDLE = 0
BRLAPI_PRIORITY_DEFAULT = 50
BRLAPI_PRIORITY_HIGH = 70


@dataclass(frozen=True)
class _LineInfo:
    """Rendered line string plus focus/mask/ranges used for viewport and output."""

    string: str
    focus_offset: int
    attribute_mask: str
    ranges: list[list[int]]


@dataclass(frozen=True)
class _TextInfo:
    """Focused text/caret snapshot used to keep cursor stable across refresh."""

    accessible: Any | None
    caret_offset: int
    line_offset: int
    cursor_cell: int


@dataclass(frozen=True)
class _RegionAtCell:
    """Result of mapping a cell to its region and in-region offset."""

    region: Region | None
    offset_in_region: int

    def __iter__(self) -> Iterator[Any]:
        yield self.region
        yield self.offset_in_region

    def __getitem__(self, index: int) -> Any:
        if index == 0:
            return self.region
        if index == 1:
            return self.offset_in_region
        raise IndexError(index)


@dataclass(frozen=True)
class _CaretContext:
    """Accessible and caret offset resolved from a braille routing event."""

    accessible: Any | None
    offset: int

    def __iter__(self) -> Iterator[Any]:
        yield self.accessible
        yield self.offset

    def __getitem__(self, index: int) -> Any:
        if index == 0:
            return self.accessible
        if index == 1:
            return self.offset
        raise IndexError(index)


@dataclass(frozen=True)
class _FlashState:
    """Saved lines/focus/viewport used to restore after a flash message."""

    lines: list[Line]
    region_with_focus: Region | None
    viewport: list[int]
    flash_time: int


@dataclass(frozen=True)
class _BrlapiTask:
    """Queued BrlAPI action with optional success/failure callbacks."""

    action: str
    func: Callable[[Any], None]
    brlapi: Any
    on_success: Callable[[], None] | None = None
    on_failure: Callable[[BaseException], None] | None = None


@dataclass
class _BrailleState:
    """Mutable runtime state for BrlAPI, lines, and viewport."""

    brlapi: Any = None
    brlapi_available: bool = False
    brlapi_running: bool = False
    brlapi_connecting: bool = False
    brlapi_connect_token: int = 0
    brlapi_session_token: int = 0
    brlapi_connect_timeout_source_id: int = 0
    brlapi_source_id: int = 0
    brlapi_retry_source_id: int = 0
    brlapi_retry_delay_ms: int = _BRLAPI_RETRY_DELAY_MS
    brlapi_display_size_poll_id: int = 0
    brlapi_queue: queue.Queue[_BrlapiTask | None] | None = None
    brlapi_worker: threading.Thread | None = None
    brlapi_inflight_action: str | None = None
    brlapi_inflight_since: float = 0.0
    brlapi_inflight_timer_id: int = 0
    brlapi_ready: bool = False
    display_size: list[int] = field(default_factory=lambda: [DEFAULT_DISPLAY_SIZE, 1])
    lines: list[Line] = field(default_factory=list)
    region_with_focus: Region | None = None
    last_text_info: _TextInfo = field(default_factory=lambda: _TextInfo(None, 0, 0, 0))
    viewport: list[int] = field(default_factory=lambda: [0, 0])
    callback: Callable[[Any], bool] | None = None
    end_is_showing: bool = False
    beginning_is_showing: bool = False
    cursor_cell: int = 0
    flash_event_source_id: int = 0
    saved: _FlashState | None = None
    idle: bool = False
    brlapi_current_priority: int = BRLAPI_PRIORITY_DEFAULT
    default_contraction_table: str | None = None
    pending_key_ranges: list[int] = field(default_factory=list)
    monitor_callback: Callable[[int, str, str | None, int], None] | None = None


_STATE = _BrailleState(brlapi_available=_BRLAPI_AVAILABLE)


def set_monitor_callback(callback: Callable[[int, str, str | None, int], None] | None) -> None:
    """Sets the callback for updating the braille monitor display."""

    _STATE.monitor_callback = callback


def _log_brlapi_unavailable(resource: str, error: BaseException | None = None) -> None:
    """Log why a BrlAPI resource/constructor is unavailable."""

    if error is None:
        msg = f"BRAILLE: BrlAPI {resource} is unavailable."
    else:
        msg = f"BRAILLE: BrlAPI {resource} is unavailable ({type(error).__name__}): {error}"
    debug.print_message(debug.LEVEL_WARNING, msg, True)


def _create_brlapi_write_struct() -> Any | None:
    """Returns a BrlAPI write struct instance when available."""

    if BRLAPI is None:
        _log_brlapi_unavailable("WriteStruct")
        return None
    try:
        return BRLAPI.WriteStruct()
    except (AttributeError, TypeError) as error:
        _log_brlapi_unavailable("WriteStruct", error)
        return None


def _create_brlapi_connection() -> Any | None:
    """Returns a BrlAPI connection instance when available."""

    if BRLAPI is None:
        _log_brlapi_unavailable("Connection")
        return None
    try:
        return BRLAPI.Connection()  # pylint: disable=c-extension-no-member
    except BRLAPI_ERRORS as error:
        _log_brlapi_unavailable("Connection", error)
        return None


def _empty_text_info() -> _TextInfo:
    """Return a zeroed TextInfo placeholder with no focused text."""

    return _TextInfo(None, 0, 0, 0)


def _reset_last_text_info() -> None:
    """Reset cached text info to the empty placeholder."""

    _STATE.last_text_info = _empty_text_info()


def _stop_brlapi_worker() -> None:
    """Signal and clear the BrlAPI worker thread/queue."""

    if _STATE.brlapi_queue is not None:
        _STATE.brlapi_queue.put(None)
    _STATE.brlapi_queue = None
    _STATE.brlapi_worker = None


def _mark_brlapi_dead() -> None:
    """Reset BrlAPI state after failure and schedule a reconnect."""

    if _STATE.brlapi_running:
        _STATE.brlapi_running = False
    if _STATE.brlapi_source_id:
        GLib.source_remove(_STATE.brlapi_source_id)
        _STATE.brlapi_source_id = 0
    _STATE.brlapi = None
    _STATE.idle = False
    _STATE.brlapi_ready = False
    _STATE.brlapi_session_token += 1
    if _STATE.brlapi_inflight_timer_id:
        GLib.source_remove(_STATE.brlapi_inflight_timer_id)
        _STATE.brlapi_inflight_timer_id = 0
    _STATE.brlapi_inflight_action = None
    _STATE.brlapi_inflight_since = 0.0
    if _STATE.brlapi_connect_timeout_source_id:
        GLib.source_remove(_STATE.brlapi_connect_timeout_source_id)
        _STATE.brlapi_connect_timeout_source_id = 0
    if _STATE.brlapi_display_size_poll_id:
        GLib.source_remove(_STATE.brlapi_display_size_poll_id)
        _STATE.brlapi_display_size_poll_id = 0
    _STATE.brlapi_retry_delay_ms = _BRLAPI_RETRY_DELAY_MS
    _stop_brlapi_worker()
    _schedule_brlapi_retry()


def _handle_brlapi_failure(token: int, action: str, error: BaseException) -> bool:
    """Log a BrlAPI failure and reset state for this session."""

    if token != _STATE.brlapi_session_token:
        return False
    msg = f"BRAILLE: {action} failed ({type(error).__name__}): {error}"
    debug.print_message(debug.LEVEL_WARNING, msg, True)
    _mark_brlapi_dead()
    return False


def _run_brlapi_callback(token: int, callback: Callable[..., None], *args: Any) -> bool:
    """Invoke a callback if the session token still matches."""

    if token != _STATE.brlapi_session_token:
        return False
    callback(*args)
    return False


def _note_brlapi_task_started(token: int, action: str) -> bool:
    """Record an inflight task and arm its timeout timer."""

    if token != _STATE.brlapi_session_token:
        return False
    _STATE.brlapi_inflight_action = action
    _STATE.brlapi_inflight_since = time.monotonic()
    if _STATE.brlapi_inflight_timer_id:
        GLib.source_remove(_STATE.brlapi_inflight_timer_id)
    _STATE.brlapi_inflight_timer_id = GLib.timeout_add(
        _BRLAPI_TASK_TIMEOUT_MS, _brlapi_task_timeout
    )
    return False


def _note_brlapi_task_finished(token: int) -> bool:
    """Clear inflight task tracking and cancel the timeout."""

    if token != _STATE.brlapi_session_token:
        return False
    _STATE.brlapi_inflight_action = None
    _STATE.brlapi_inflight_since = 0.0
    if _STATE.brlapi_inflight_timer_id:
        GLib.source_remove(_STATE.brlapi_inflight_timer_id)
        _STATE.brlapi_inflight_timer_id = 0
    return False


def _brlapi_task_timeout() -> bool:
    """Handle an inflight BrlAPI task timeout."""

    _STATE.brlapi_inflight_timer_id = 0
    action = _STATE.brlapi_inflight_action
    if action is None:
        return False
    elapsed = time.monotonic() - _STATE.brlapi_inflight_since
    msg = f"BRAILLE: BrlAPI action timed out after {elapsed:.1f}s: {action}"
    debug.print_message(debug.LEVEL_INFO, msg, True)
    _mark_brlapi_dead()
    return False


def _brlapi_worker_loop(token: int, task_queue: queue.Queue[_BrlapiTask | None]) -> None:
    """Process queued BrlAPI tasks on the worker thread."""

    while True:
        task = task_queue.get()
        if task is None:
            return
        GLib.idle_add(_note_brlapi_task_started, token, task.action)
        try:
            task.func(task.brlapi)
        except BRLAPI_ERRORS as error:
            GLib.idle_add(_note_brlapi_task_finished, token)
            callback = task.on_failure
            if callback is None:
                GLib.idle_add(_handle_brlapi_failure, token, task.action, error)
            else:
                GLib.idle_add(_run_brlapi_callback, token, callback, error)
        else:
            GLib.idle_add(_note_brlapi_task_finished, token)
            if task.on_success is not None:
                GLib.idle_add(_run_brlapi_callback, token, task.on_success)


def _enqueue_brlapi_task(
    action: str,
    func: Callable[[Any], None],
    on_success: Callable[[], None] | None = None,
    on_failure: Callable[[BaseException], None] | None = None,
) -> bool:
    """Queue a BrlAPI task if the connection/worker is ready."""

    if not _STATE.brlapi_running:
        msg = f"BRAILLE: Cannot {action}: BrlAPI not running."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False
    brlapi = _STATE.brlapi
    if brlapi is None:
        msg = f"BRAILLE: Cannot {action}: BrlAPI connection unavailable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False
    if _STATE.brlapi_queue is None:
        msg = f"BRAILLE: Cannot {action}: BrlAPI worker unavailable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False
    if _STATE.brlapi_worker is None or not _STATE.brlapi_worker.is_alive():
        msg = f"BRAILLE: Cannot {action}: BrlAPI worker not running."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        _mark_brlapi_dead()
        return False
    _STATE.brlapi_queue.put(_BrlapiTask(action, func, brlapi, on_success, on_failure))
    return True


def _cancel_brlapi_retry() -> None:
    """Cancel any scheduled BrlAPI reconnect attempt."""

    if _STATE.brlapi_retry_source_id:
        GLib.source_remove(_STATE.brlapi_retry_source_id)
        _STATE.brlapi_retry_source_id = 0


def _cancel_brlapi_connect_timeout() -> None:
    """Cancel the pending BrlAPI connect timeout."""

    if _STATE.brlapi_connect_timeout_source_id:
        GLib.source_remove(_STATE.brlapi_connect_timeout_source_id)
        _STATE.brlapi_connect_timeout_source_id = 0


def _cancel_brlapi_display_size_poll() -> None:
    """Cancel polling for a nonzero BrlAPI display size."""

    if _STATE.brlapi_display_size_poll_id:
        GLib.source_remove(_STATE.brlapi_display_size_poll_id)
        _STATE.brlapi_display_size_poll_id = 0


def _schedule_brlapi_display_size_poll() -> None:
    """Schedule polling until the device reports a nonzero display size."""

    if _STATE.brlapi_display_size_poll_id:
        return
    _STATE.brlapi_display_size_poll_id = GLib.timeout_add(
        _BRLAPI_DISPLAY_SIZE_POLL_MS, _poll_brlapi_display_size
    )


def _poll_brlapi_display_size() -> bool:
    """Request display size from BrlAPI asynchronously."""

    _STATE.brlapi_display_size_poll_id = 0
    if not _STATE.brlapi_running or _STATE.brlapi_queue is None:
        return False

    def _read_display_size(brlapi: Any) -> None:
        """Read display size from BrlAPI and post update to main loop."""

        size = brlapi.displaySize
        GLib.idle_add(_update_brlapi_display_size, size)

    if not _enqueue_brlapi_task("check display size", _read_display_size):
        return False
    return False


def _update_brlapi_display_size(size: tuple[int, int]) -> bool:
    """Apply display size and mark the device ready if valid."""

    if size[0] <= 0:
        _schedule_brlapi_display_size_poll()
        return False

    _STATE.display_size = [size[0], 1]
    _STATE.brlapi_ready = True
    _cancel_brlapi_display_size_poll()
    refresh(True)
    return False


def _schedule_brlapi_connect_timeout() -> None:
    """Arm the BrlAPI connection timeout timer."""

    _cancel_brlapi_connect_timeout()
    _STATE.brlapi_connect_timeout_source_id = GLib.timeout_add(
        _BRLAPI_CONNECT_TIMEOUT_MS, _brlapi_connect_timeout
    )


def _brlapi_connect_timeout() -> bool:
    """Handle connect timeout and schedule a retry."""

    _STATE.brlapi_connect_timeout_source_id = 0
    if not _STATE.brlapi_connecting:
        return False
    msg = f"BRAILLE: BrlAPI connection timed out after {_BRLAPI_CONNECT_TIMEOUT_MS} ms."
    debug.print_message(debug.LEVEL_INFO, msg, True)
    _STATE.brlapi_connecting = False
    _STATE.brlapi_connect_token += 1
    _schedule_brlapi_retry()
    return False


def _schedule_brlapi_retry() -> None:
    """Schedule a reconnect attempt with backoff."""

    if _STATE.brlapi_retry_source_id or not settings.enableBraille:
        return
    delay_ms = _STATE.brlapi_retry_delay_ms
    msg = f"BRAILLE: Scheduling BrlAPI retry in {delay_ms} ms."
    debug.print_message(debug.LEVEL_INFO, msg, True)
    _STATE.brlapi_retry_source_id = GLib.timeout_add(delay_ms, _retry_brlapi_connection)


def _retry_brlapi_connection() -> bool:
    """Retry connecting to BrlAPI if conditions permit."""

    _STATE.brlapi_retry_source_id = 0
    if not settings.enableBraille or _STATE.brlapi_running or _STATE.brlapi_connecting:
        return False
    _STATE.brlapi_retry_delay_ms = min(_STATE.brlapi_retry_delay_ms * 2, _BRLAPI_RETRY_MAX_DELAY_MS)
    _start_brlapi_connection()
    return False


def _start_brlapi_connection() -> None:
    """Kick off asynchronous BrlAPI connection setup."""

    if _STATE.brlapi_running or _STATE.brlapi_connecting or not settings.enableBraille:
        return
    _cancel_brlapi_retry()
    _schedule_brlapi_connect_timeout()
    _STATE.brlapi_connecting = True
    _STATE.brlapi_connect_token += 1
    token = _STATE.brlapi_connect_token
    msg = "BRAILLE: Attempting connection with BrlAPI."
    debug.print_message(debug.LEVEL_INFO, msg, True)
    _STATE.brlapi_queue = queue.Queue()
    thread = threading.Thread(
        target=_brlapi_connect_worker,
        args=(token, _STATE.brlapi_queue),
        daemon=True,
    )
    _STATE.brlapi_worker = thread
    thread.start()


def _brlapi_connect_worker(token: int, task_queue: queue.Queue[_BrlapiTask | None]) -> None:
    """Worker thread body for establishing a BrlAPI connection."""

    connection: Any | None = None
    display_size: tuple[int, int] | None = None
    error: BaseException | None = None

    try:
        connection = _create_brlapi_connection()
        if connection is None:
            error = RuntimeError("BrlAPI connection unavailable.")
        else:
            msg = "BRAILLE: Attempting to enter TTY mode."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            connection.enterTtyModeWithPath()
            msg = "BRAILLE: TTY mode entered."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            display_size = connection.displaySize
            if display_size[0] == 0:
                msg = "BRAILLE: Display size reported 0 cells; device not ready."
                debug.print_message(debug.LEVEL_INFO, msg, True)
    except (GLib.GError, OSError, RuntimeError, AttributeError, ValueError, TypeError) as err:
        error = err
    except BRLAPI_ERRORS as err:
        error = err

    GLib.idle_add(_finish_brlapi_connection, token, connection, display_size, error)
    if error is not None or connection is None or display_size is None:
        return

    _brlapi_worker_loop(token, task_queue)


def _finish_brlapi_connection(
    token: int,
    connection: Any | None,
    display_size: tuple[int, int] | None,
    error: BaseException | None,
) -> bool:
    """Finalize a connection attempt on the main thread and init state."""

    if token != _STATE.brlapi_connect_token:
        return False

    _STATE.brlapi_connecting = False
    _cancel_brlapi_connect_timeout()

    if error is not None or connection is None or display_size is None:
        msg = (
            f"WARNING: Braille initialization failed: {error}"
            if error
            else ("WARNING: Braille initialization failed.")
        )
        debug.print_message(debug.LEVEL_WARNING, msg, True)

        _STATE.brlapi_running = False
        _STATE.brlapi = None
        _STATE.brlapi_worker = None
        _STATE.brlapi_queue = None
        _schedule_brlapi_retry()
        return False

    _cancel_brlapi_retry()
    _STATE.brlapi = connection
    _STATE.brlapi_running = True
    _STATE.idle = False
    _STATE.brlapi_session_token += 1
    _STATE.brlapi_retry_delay_ms = _BRLAPI_RETRY_DELAY_MS

    tokens = ["BRAILLE: Connection established with BrlAPI:", _STATE.brlapi]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    (x, y) = display_size
    msg = f"BRAILLE: Display size: ({x},{y})"
    debug.print_message(debug.LEVEL_INFO, msg, True)

    if x > 0:
        _STATE.display_size = [x, 1]
        _STATE.brlapi_ready = True
        _cancel_brlapi_display_size_poll()
    else:
        _STATE.display_size = [DEFAULT_DISPLAY_SIZE, 1]
        _STATE.brlapi_ready = False
        _schedule_brlapi_display_size_poll()

    _STATE.brlapi_source_id = GLib.io_add_watch(
        connection.fileDescriptor, GLib.PRIORITY_DEFAULT, GLib.IO_IN, _brlapi_key_reader
    )

    if _STATE.pending_key_ranges:
        _apply_key_ranges(list(_STATE.pending_key_ranges))

    if not _STATE.lines:
        _clear()
    refresh(True)

    msg = "BRAILLE: Initialized"
    debug.print_message(debug.LEVEL_INFO, msg, True)
    return False


def _get_default_table() -> str:
    """Returns the default braille translation table for the current locale."""

    user_locale = locale.getlocale(locale.LC_MESSAGES)[0]
    user_locale_tokens = ["BRAILLE: User locale is", user_locale]
    debug.print_tokens(debug.LEVEL_INFO, user_locale_tokens, True)

    if not user_locale or user_locale == "C":
        msg = "BRAILLE: Locale cannot be determined. Falling back on 'en-us'"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        language = "en-us"
    else:
        language = "-".join(user_locale.split("_")).lower()

    try:
        tables = [x for x in os.listdir(tablesdir) if x[-4:] in (".utb", ".ctb")]
    except OSError:
        tokens = ["BRAILLE: Exception calling os.listdir for", tablesdir]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return ""

    # Some of the tables are probably not a good choice for default table....
    exclude = ["interline", "mathtext"]

    # Some of the tables might be a better default than others. For instance, someone who
    # can read grade 2 braille presumably can read grade 1; the reverse is not necessarily
    # true. Literary braille might be easier for some users to read than computer braille.
    # We can adjust this based on user feedback, but in general the goal is a sane default
    # for the largest group of users; not the perfect default for all users.
    prefer = ["g1", "g2", "comp6", "comp8"]

    def is_candidate(t: str) -> bool:
        """Return True for locale-matching table candidates."""
        return t.startswith(language) and not any(e in t for e in exclude)

    tables = list(filter(is_candidate, tables))
    candidate_tokens: list[Any] = [
        "BRAILLE:",
        len(tables),
        "candidate tables for locale found:",
        ", ".join(tables),
    ]
    debug.print_tokens(debug.LEVEL_INFO, candidate_tokens, True)

    if not tables:
        return ""

    for p in prefer:
        for table in tables:
            if p in table:
                return os.path.join(tablesdir, table)

    # If we couldn't find a preferred match, just go with the first match for the locale.
    return os.path.join(tablesdir, tables[0])


if LOUIS:
    _STATE.default_contraction_table = _get_default_table()
    default_table_tokens = [
        "BRAILLE: Default contraction table is:",
        _STATE.default_contraction_table,
    ]
    debug.print_tokens(debug.LEVEL_INFO, default_table_tokens, True)


class Region:
    """Base braille region with optional contraction and cursor tracking."""

    def __init__(self, string: str, cursor_offset: int = 0, expand_on_cursor: bool = False) -> None:
        if not string:
            string = ""

        # If LOUIS is None, then we don't go into contracted mode.
        self._contracted = settings.enableContractedBraille and LOUIS is not None
        self._expand_on_cursor = expand_on_cursor

        # The uncontracted string for the line.
        self._raw_line = string.strip("\n")

        if self._contracted:
            self._contraction_table = (
                settings.brailleContractionTable or _STATE.default_contraction_table
            )
            if string.strip():
                tokens = ["BRAILLE: Contracting '", string, "' with table", self._contraction_table]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            self.string, self._in_position, self._out_position, self.cursor_offset = (
                self._contract_line(self._raw_line, cursor_offset, self._expand_on_cursor)
            )
        else:
            if string.strip():
                if not settings.enableContractedBraille:
                    msg = (
                        f"BRAILLE: Not contracting '{string}' "
                        f"because contracted braille is not enabled."
                    )
                    debug.print_message(debug.LEVEL_INFO, msg, True)
                else:
                    tokens = [
                        "BRAILLE: Not contracting '",
                        string,
                        "' due to problem with liblouis.",
                    ]
                    debug.print_tokens(debug.LEVEL_WARNING, tokens, True)

            self.string = self._raw_line
            self.cursor_offset = cursor_offset

    def __str__(self) -> str:
        return f"REGION: '{self.string}', cursor offset:{self.cursor_offset}"

    def process_routing_key(self, offset: int) -> None:
        """Handle a routing key press relative to this region."""

        msg = f"BRAILLE REGION: Process routing key. Offset: {offset}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_attribute_mask(self, _indicate_links: bool = True) -> str:
        """Return the attrOr mask for this region."""

        return "\x00" * len(self.string)

    def reposition_cursor(self) -> bool:
        """Recompute contracted text and cursor mapping after caret movement."""

        if not self._contracted:
            return False

        self.string, self._in_position, self._out_position, self.cursor_offset = (
            self._contract_line(self._raw_line, self.cursor_offset, self._expand_on_cursor)
        )
        return True

    def _contract_line(
        self, line: str, cursor_offset: int = 0, expand_on_cursor: bool = False
    ) -> tuple[str, list[int], list[int], int]:
        """Contracts and returns the given line."""

        try:
            cursor_on_space = line[cursor_offset] == " "
        except IndexError:
            cursor_on_space = False

        if not expand_on_cursor or cursor_on_space:
            mode = 0
        else:
            if settings.enableComputerBrailleAtCursor:
                mode = LOUIS.compbrlAtCursor
            else:
                mode = 0

        contracted, in_position, out_position, cursor_position = LOUIS.translate(
            [self._contraction_table], line, cursorPos=cursor_offset, mode=mode
        )

        # Make sure the cursor is at a realistic spot.
        # Note that if cursor_offset is beyond the end of the buffer,
        # a spurious value is returned by liblouis in cursorPos.
        if cursor_offset >= len(line):
            cursor_position = len(contracted)
        else:
            cursor_position = min(cursor_position, len(contracted))

        return contracted, in_position, out_position, cursor_position

    def _display_to_buffer_offset(self, display_offset: int) -> int:
        """Map a display cell offset to a raw string offset."""

        try:
            offset = self._in_position[display_offset]
        except IndexError:
            # Off the chart, we just place the cursor at the end of the line.
            offset = len(self._raw_line)
        except AttributeError:
            # Not in contracted mode.
            offset = display_offset

        return offset

    def set_contracted_braille(self, contracted: bool) -> None:
        """Apply contracted or uncontracted mode to this region."""

        if contracted:
            self._contraction_table = (
                settings.brailleContractionTable or _STATE.default_contraction_table
            )
            self._contract_region()
        else:
            self._expand_region()

    def _contract_region(self) -> None:
        """Contracts this region if not already contracted."""
        if self._contracted:
            return
        self.string, self._in_position, self._out_position, self.cursor_offset = (
            self._contract_line(self._raw_line, self.cursor_offset, self._expand_on_cursor)
        )
        self._contracted = True

    def _expand_region(self) -> None:
        """Expands this region if currently contracted."""
        if not self._contracted:
            return
        self.string = self._raw_line
        try:
            self.cursor_offset = self._in_position[self.cursor_offset]
        except IndexError:
            self.cursor_offset = len(self.string)
        self._contracted = False


class Component(Region):
    """Region tied to an accessible object and routing actions."""

    def __init__(
        self,
        accessible: Any,
        string: str,
        cursor_offset: int = 0,
        indicator: str = "",
        expand_on_cursor: bool = False,
    ) -> None:
        Region.__init__(self, string, cursor_offset, expand_on_cursor)
        if indicator:
            if self.string:
                self.string = indicator + " " + self.string
            else:
                self.string = indicator

        self.accessible = accessible

    def __str__(self) -> str:
        return f"COMPONENT: '{self.string}', cursor offset:{self.cursor_offset}"

    def get_caret_offset(self, _offset: int) -> int:
        """Return caret offset for a routing position, or -1 if not applicable."""

        return -1

    def process_routing_key(self, offset: int) -> None:
        """Activate or focus this accessible for a routing key press."""

        msg = f"BRAILLE COMPONENT: Process routing key. Offset: {offset}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        script = script_manager.get_manager().get_active_script()
        if script and script.utilities.grab_focus_before_routing(self.accessible):
            AXObject.grab_focus(self.accessible)

        if AXObject.do_action(self.accessible, 0):
            return

        # Do a mouse button 1 click if we have to. For example, page tabs don't have any actions
        # but we want to be able to select them with the cursor routing key.
        try:
            result = AXEventSynthesizer.click_object(self.accessible, 1)
        except (GLib.GError, AttributeError, RuntimeError, TypeError) as error:
            tokens = ["ERROR: Could not process routing key:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        else:
            if not result:
                msg = "INFO: Processing routing key failed"
                debug.print_message(debug.LEVEL_INFO, msg, True)


class Link(Component):
    """Component representing a hyperlink."""

    def __init__(self, accessible: Any, string: str, cursor_offset: int = 0) -> None:
        super().__init__(accessible, string, cursor_offset, "", True)

    def __str__(self) -> str:
        return f"LINK: '{self.string}', cursor offset:{self.cursor_offset}"

    def get_attribute_mask(self, _indicate_links: bool = True) -> str:
        """Return an attrOr mask that marks link cells."""

        return chr(settings.brailleLinkIndicator) * len(self.string)


class Text(Region):
    """Region backed by accessible text with caret routing support."""

    def __init__(
        self,
        accessible: Any,
        label: str = "",
        eol: str = "",
        start_offset: int | None = None,
        end_offset: int | None = None,
        caret_offset: int | None = None,
    ) -> None:
        tokens = [
            "BRAILLE: Creating text region for",
            accessible,
            f"label:'{label}', offsets: {start_offset}-{end_offset}, caret: {caret_offset}",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.accessible = accessible
        self._eol = eol
        string = ""
        self.caret_offset = 0
        self.line_offset = 0
        if self.accessible:
            if caret_offset is not None:
                self.caret_offset = caret_offset
            else:
                self.caret_offset = AXText.get_caret_offset(self.accessible)
            if start_offset is not None:
                self.caret_offset = max(start_offset, self.caret_offset)
            string, self.line_offset = AXText.get_line_at_offset(
                self.accessible, self.caret_offset
            )[0:2]
            string = string.replace("\ufffc", " ")

        if end_offset is None:
            self._end_offset = len(string)
        else:
            self._end_offset = end_offset - self.line_offset

        if start_offset is None:
            self._start_offset = 0
        else:
            self._start_offset = start_offset - self.line_offset

        string = string[self._start_offset : self._end_offset]
        self.caret_offset -= self._start_offset
        cursor_offset = min(self.caret_offset - self.line_offset, len(string))
        self._max_caret_offset = self.line_offset + len(string)

        if label and label != string:
            self._label = label + " "
        else:
            self._label = ""

        string = self._label + string
        cursor_offset += len(self._label)
        super().__init__(string, cursor_offset, True)

        if not self._contracted and not settings.disableBrailleEOL:
            self.string += self._eol
        elif settings.disableBrailleEOL:
            # Ensure there is a place to click on at the end of a line so the user can route the
            # caret there.
            self.string += " "

    def __str__(self) -> str:
        return (
            f"TEXT: '{self.string}', cursor offset:{self.cursor_offset} "
            f"start offset:{self._start_offset}, line offset:{self.line_offset}"
        )

    def reposition_cursor(self) -> bool:
        """Update caret/cursor when the caret moves within the same line."""

        if not _STATE.region_with_focus:
            return False

        string, line_offset = AXText.get_line_at_offset(self.accessible)[0:2]
        caret_offset = AXText.get_caret_offset(self.accessible)
        cursor_offset = min(caret_offset - line_offset, len(string))

        if line_offset != self.line_offset:
            return False

        self.caret_offset = caret_offset
        self.line_offset = line_offset

        cursor_offset += len(self._label)

        if self._contracted:
            self.string, self._in_position, self._out_position, cursor_offset = self._contract_line(
                self._raw_line, cursor_offset, True
            )

        self.cursor_offset = cursor_offset

        return True

    def get_caret_offset(self, offset: int) -> int:
        """Map a display offset to an accessible caret offset."""

        offset = self._display_to_buffer_offset(offset)
        if offset < 0:
            return -1

        return min(self.line_offset + offset, self._max_caret_offset)

    def process_routing_key(self, offset: int) -> None:
        """Route the caret in accessible text for the given display offset."""

        msg = f"BRAILLE TEXT: Process routing key. Offset: {offset}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        caret_offset = self.get_caret_offset(offset)
        if caret_offset < 0:
            return

        script = script_manager.get_manager().get_active_script()
        if script is None:
            msg = "BRAILLE: Cannot set caret offset without active script."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return
        script.utilities.set_caret_offset(self.accessible, caret_offset)

    def get_attribute_mask(self, indicate_links: bool = True) -> str:
        """Return the attrOr mask for links, attributes, and selections."""

        if AXText.is_whitespace_or_empty(self.accessible):
            return ""

        script = script_manager.get_manager().get_active_script()
        if script is None:
            msg = "BRAILLE: Cannot get attribute mask without active script."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        string_length = len(self._raw_line) - len(self._label)
        line_end_offset = self.line_offset + string_length
        region_mask = [settings.BRAILLE_UNDERLINE_NONE] * string_length

        attr_indicator = settings.textAttributesBrailleIndicator
        selection_indicator = settings.brailleSelectorIndicator
        link_indicator = settings.brailleLinkIndicator

        if indicate_links and link_indicator != settings.BRAILLE_UNDERLINE_NONE:
            links = AXHypertext.get_all_links(self.accessible)
            for link in links:
                start_offset = AXHypertext.get_link_start_offset(link)
                end_offset = AXHypertext.get_link_end_offset(link)
                mask_start = max(start_offset - self.line_offset, 0)
                mask_end = min(end_offset - self.line_offset, string_length)
                for i in range(mask_start, mask_end):
                    region_mask[i] |= link_indicator

        if attr_indicator:
            enabled = text_attribute_manager.get_manager().get_attributes_to_braille()
            offset = self.line_offset
            while offset < line_end_offset:
                attributes, start_offset, end_offset = AXText.get_text_attributes_at_offset(
                    self.accessible, offset
                )
                if end_offset <= offset:
                    break
                mask = settings.BRAILLE_UNDERLINE_NONE
                offset = end_offset
                for attrib in attributes:
                    if attrib not in enabled:
                        continue
                    ax_text_attr = AXTextAttribute.from_string(attrib)
                    if ax_text_attr and not ax_text_attr.value_is_default(attributes[attrib]):
                        mask = attr_indicator
                        break
                if mask != settings.BRAILLE_UNDERLINE_NONE:
                    mask_start = max(start_offset - self.line_offset, 0)
                    mask_end = min(end_offset - self.line_offset, string_length)
                    for i in range(mask_start, mask_end):
                        region_mask[i] |= attr_indicator

        if selection_indicator:
            selections = AXText.get_selected_ranges(self.accessible)
            for start_offset, end_offset in selections:
                mask_start = max(start_offset - self.line_offset, 0)
                mask_end = min(end_offset - self.line_offset, string_length)
                for i in range(mask_start, mask_end):
                    region_mask[i] |= selection_indicator

        if self._contracted:
            contracted_mask = [0] * len(self._raw_line)
            out_position = self._out_position[len(self._label) :]
            if self._label:
                out_position = [offset - len(self._label) - 1 for offset in out_position]
            for i, m in enumerate(region_mask):
                try:
                    contracted_mask[out_position[i]] |= m
                except IndexError:
                    continue
            region_mask = contracted_mask[: len(self.string)]

        # Add empty mask characters for the EOL character as well as for the label.
        region_mask += [0] * len(self._eol)
        if self._label:
            region_mask = [0] * len(self._label) + region_mask

        return "".join(map(chr, region_mask))

    def _contract_line(
        self, line: str, cursor_offset: int = 0, expand_on_cursor: bool = True
    ) -> tuple[str, list[int], list[int], int]:
        """Contracts and returns the given line."""

        contracted, in_position, out_position, cursor_position = super()._contract_line(
            line, cursor_offset, expand_on_cursor
        )
        return contracted + self._eol, in_position, out_position, cursor_position

    def _display_to_buffer_offset(self, display_offset: int) -> int:
        """Map a display cell offset to an underlying text offset."""

        offset = super()._display_to_buffer_offset(display_offset)
        offset += self._start_offset
        offset -= len(self._label)
        return offset

    def set_contracted_braille(self, contracted: bool) -> None:
        """Apply contracted mode and maintain EOL handling."""
        super().set_contracted_braille(contracted)
        if not contracted:
            self.string += self._eol


class ReviewComponent(Component):
    """Component used to present flat review content."""

    def __init__(self, accessible: Any, string: str, cursor_offset: int, zone: Any) -> None:
        super().__init__(accessible, string, cursor_offset, expand_on_cursor=True)
        self.zone = zone

    def __str__(self) -> str:
        return f"ReviewComponent: {self.zone}, {self.cursor_offset}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ReviewComponent)
            and self.accessible == other.accessible
            and self.zone == other.zone
            and self.string == other.string
            and self.cursor_offset == other.cursor_offset
        )


class ReviewText(Region):
    """Text region used for flat review mode."""

    def __init__(self, accessible: Any, string: str, line_offset: int, zone: Any) -> None:
        super().__init__(string, expand_on_cursor=True)
        self.accessible = accessible
        self.line_offset = line_offset
        self.zone = zone

    def __str__(self) -> str:
        return f"ReviewText: {self.zone}, {self.cursor_offset}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, ReviewText)
            and self.accessible == other.accessible
            and self.line_offset == other.line_offset
            and self.zone == other.zone
            and self.string == other.string
        )

    def get_caret_offset(self, offset: int) -> int:
        """Map a display offset to a flat review caret offset."""

        offset = self._display_to_buffer_offset(offset)

        if offset < 0:
            return -1

        return self.line_offset + offset

    def process_routing_key(self, offset: int) -> None:
        """Route caret for flat review based on the display offset."""

        msg = f"BRAILLE REVIEW TEXT: Process routing key. Offset: {offset}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        caret_offset = self.get_caret_offset(offset)
        script = script_manager.get_manager().get_active_script()
        if script is None:
            msg = "BRAILLE: Cannot set caret offset without active script."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return
        script.utilities.set_caret_offset(self.accessible, caret_offset)


class Line:
    """Braille line composed of sequential regions."""

    def __init__(self, region: Region | None = None) -> None:
        self._regions: list[Region] = []
        self._info_cache: dict[bool, _LineInfo] = {}
        if region:
            self._regions.append(region)
            self.invalidate_cache_internal()

    def get_regions(self) -> tuple[Region, ...]:
        """Return regions in display order."""

        return tuple(self._regions)

    def invalidate_cache_internal(self) -> None:
        """Clear cached line info for this line."""
        self._info_cache.clear()

    def add_regions(self, regions: Iterable[Region]) -> None:
        """Append multiple regions to this line."""

        self._regions.extend(regions)
        self.invalidate_cache_internal()

    def get_info(self, indicate_links: bool = True) -> _LineInfo:
        """Compute rendered line info used for display and panning."""

        cached = self._info_cache.get(indicate_links)
        if cached is not None:
            return cached

        string = ""
        focus_offset = -1
        attribute_mask = ""
        for region in self._regions:
            if region == _STATE.region_with_focus:
                focus_offset = len(string)
            if region.string:
                string += region.string
            mask = region.get_attribute_mask(indicate_links)
            attribute_mask += mask

        ranges = _compute_ranges(string, focus_offset, _STATE.display_size[0])
        info = _LineInfo(string, focus_offset, attribute_mask, ranges)
        self._info_cache[indicate_links] = info
        return info

    def get_region_at_offset(self, offset: int) -> _RegionAtCell:
        """Return the region and offset for a 0-based cell index."""

        # Translate the cursor offset for this line into a cursor offset for a region, and then
        # pass the event off to the region for handling.
        focused_region = None
        string = ""
        pos = 0
        for region in self._regions:
            focused_region = region
            string = string + region.string
            if len(string) > offset:
                break
            pos = len(string)

        if offset >= len(string):
            return _RegionAtCell(None, -1)
        return _RegionAtCell(focused_region, offset - pos)

    def process_routing_key(self, offset: int) -> None:
        """Dispatch a routing key press to the region at the given offset."""

        msg = f"BRAILLE LINE: Process routing key. Offset: {offset}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

        region_info = self.get_region_at_offset(offset)
        if region_info.region:
            region_info.region.process_routing_key(region_info.offset_in_region)

    def set_contracted_braille(self, contracted: bool) -> None:
        """Apply contracted mode to all regions in this line."""
        for region in self._regions:
            region.set_contracted_braille(contracted)
        self.invalidate_cache_internal()


def _compute_ranges(string: str, focus_offset: int, display_width: int) -> list[list[int]]:
    """Compute word-wrap ranges for a line given display width."""

    # TODO: The way words are being combined here can result in incorrect range groupings.
    # For instance, if we generate the full ancestry of a multiline text object and the
    # line begins with whitespace, we'll wind up with a single range that contains the
    # last word of the ancestor followed by the whitespace and the first word, e.g.
    # "frame      Hello". We probably should not be creating a single string which we then
    # split into words.

    words = [word.span() for word in re.finditer(r"(^\s+|\S+\s*)", string)]
    ranges: list[list[int]] = []
    span: list[int] = []
    for start, end in words:
        if span and end - span[0] > display_width:
            ranges.append(span)
            span = []
        if not span:
            # Subdivide long words that exceed the display width.
            word_length = end - start
            if word_length > display_width:
                display_widths = word_length // display_width
                if display_widths:
                    for i in range(display_widths):
                        ranges.append([start + i * display_width, start + (i + 1) * display_width])
                    if word_length % display_width:
                        span = [start + display_widths * display_width, end]
                    else:
                        continue
            else:
                span = [start, end]
        else:
            span[1] = end
        if end == focus_offset:
            ranges.append(span)
            span = []
    if span:
        ranges.append(span)

    return ranges


def get_region_at_cell(cell: int) -> _RegionAtCell:
    """Map a 1-based cell to the current region and in-region offset."""

    if len(_STATE.lines) > 0:
        offset = (cell - 1) + _STATE.viewport[0]
        line_number = _STATE.viewport[1]
        return _STATE.lines[line_number].get_region_at_offset(offset)
    return _RegionAtCell(None, -1)


def get_caret_context(event: BrailleEvent) -> _CaretContext:
    """Return accessible and caret offset for a routing key event."""

    offset = event.event["argument"]
    region_info = get_region_at_cell(offset + 1)
    if region_info.region and isinstance(region_info.region, (Text, ReviewText)):
        accessible = region_info.region.accessible
        caret_offset = region_info.region.get_caret_offset(region_info.offset_in_region)
    else:
        accessible = None
        caret_offset = -1

    return _CaretContext(accessible, caret_offset)


def _clear() -> None:
    """Clears the logical structure, but keeps the Braille display as-is (until it's refreshed)."""

    _STATE.lines = []
    _STATE.region_with_focus = None
    _STATE.viewport = [0, 0]


def clear_display() -> None:
    """Clear braille state and refresh the display."""

    _clear()
    refresh(True)


def _set_lines(lines: Sequence[Line]) -> None:
    """Replaces the list of lines displayed on the braille device."""
    _STATE.lines = list(lines)
    _invalidate_line_caches()


def display_line(
    line: Line,
    focused_region: Region | None,
    pan_to_cursor: bool = True,
    indicate_links: bool = True,
    stop_flash: bool = True,
) -> None:
    """Display a single braille line and optional focus region."""

    _clear()
    _set_lines([line])
    _set_focus(focused_region, pan_to_focus=pan_to_cursor, indicate_links=indicate_links)
    refresh(pan_to_cursor=pan_to_cursor, indicate_links=indicate_links, stop_flash=stop_flash)


def try_reposition_cursor(accessible: Any) -> bool:
    """Try to reposition the cursor for an accessible without rebuilding lines."""

    if not _STATE.lines:
        return False

    line = _STATE.lines[_STATE.viewport[1]]
    for region in line.get_regions():
        if isinstance(region, Text) and region.accessible == accessible:
            if region.reposition_cursor():
                refresh(True)
                return True
            break

    return False


def is_beginning_showing() -> bool:
    """Return True if the viewport shows the line start."""
    return _STATE.beginning_is_showing


def is_end_showing() -> bool:
    """Return True if the viewport shows the line end."""
    return _STATE.end_is_showing


def _set_focus(
    region: Region | None, pan_to_focus: bool = True, indicate_links: bool = True
) -> None:
    """Specifies the region with focus.  This region will be positioned
    at the home position if pan_to_focus is True.

    Arguments:
    - region: the given region, which must be in a line that has been
      added to the logical display, or None to clear focus
    - pan_to_focus: whether or not to position the region at the home
      position
    - indicate_links: Whether or not we should take the time to get the
      attributeMask for links. Reasons we might not want to include
      knowing that we will fail and/or it taking an unreasonable
      amount of time (AKA Gecko).
    """

    _STATE.region_with_focus = region
    focused_region = _STATE.region_with_focus
    _invalidate_line_caches()

    if not (pan_to_focus and focused_region):
        return

    # Adjust the _STATE.viewport according to the new region with focus.
    # The goal is to have the first cell of the region be in the
    # home position, but we will give priority to make sure the
    # cursor for the region is on the display.  For example, when
    # faced with a long text area, we'll show the position with
    # the caret vs. showing the beginning of the region.

    line_number = 0
    done = False
    for line in _STATE.lines:
        for reg in line.get_regions():
            if reg == focused_region:
                _STATE.viewport[1] = line_number
                done = True
                break
        if done:
            break
        line_number += 1

    line = _STATE.lines[_STATE.viewport[1]]
    line_info = line.get_info(indicate_links)
    offset = line_info.focus_offset

    # If the cursor is too far right, we scroll the _STATE.viewport
    # so the cursor will be on the last cell of the display.
    if focused_region.cursor_offset >= _STATE.display_size[0]:
        offset += focused_region.cursor_offset - _STATE.display_size[0] + 1

    _STATE.viewport[0] = max(0, offset)


def _idle_braille() -> bool:
    """Try to hand off control to other screen readers without shutting down the connection."""

    if not _STATE.idle:
        if BRLAPI_PARAM_CLIENT_PRIORITY is None:
            msg = "BRAILLE: Cannot idle braille: BrlAPI priority parameter unavailable."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return _STATE.idle
        msg = "BRAILLE: Attempting to idle braille."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        def _on_success() -> None:
            """Mark braille as idle after a successful request."""

            _STATE.idle = True
            msg = "BRAILLE: Idling braille succeeded."
            debug.print_message(debug.LEVEL_INFO, msg, True)

        def _on_failure(error: BaseException) -> None:
            """Log a failure to idle braille."""

            msg = f"BRAILLE: Idling braille failed: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        queued = _enqueue_brlapi_task(
            "idle braille",
            lambda brlapi: brlapi.setParameter(
                BRLAPI_PARAM_CLIENT_PRIORITY, 0, False, BRLAPI_PRIORITY_IDLE
            ),
            on_success=_on_success,
            on_failure=_on_failure,
        )
        if queued:
            return True

    return _STATE.idle


def _clear_braille() -> None:
    """Clear the display and then try to hand off control to other screen readers."""

    if not _STATE.brlapi_running:
        # We do want to try to clear the output we left on the device
        init(_STATE.callback)

    if _STATE.brlapi_running:
        if not _enqueue_brlapi_task("clear braille", lambda brlapi: brlapi.writeText("", 0)):
            msg = "BRAILLE: Cannot clear braille: BrlAPI connection unavailable."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            _mark_brlapi_dead()
            return
        _idle_braille()


def _enable_braille() -> None:
    """Re-enable Braille output after making it idle or clearing it"""

    tokens = ["BRAILLE: Enabling braille. BrlAPI running:", _STATE.brlapi_running]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    if not _STATE.brlapi_running:
        msg = "BRAILLE: Need to initialize first."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        init(_STATE.callback)

    if _STATE.brlapi_running:
        if _STATE.idle:
            msg = "BRAILLE: Is running, but idling."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            if BRLAPI_PARAM_CLIENT_PRIORITY is None:
                msg = "BRAILLE: could not restore priority: BrlAPI parameter unavailable."
                debug.print_message(debug.LEVEL_WARNING, msg, True)
                return
            msg = "BRAILLE: Attempting to de-idle braille."
            debug.print_message(debug.LEVEL_INFO, msg, True)

            def _on_success() -> None:
                """Mark braille as active after restoring priority."""

                _STATE.idle = False
                msg = "BRAILLE: De-idle succeeded."
                debug.print_message(debug.LEVEL_INFO, msg, True)

            def _on_failure(error: BaseException) -> None:
                """Log a failure to restore braille priority."""

                msg = f"BRAILLE: could not restore priority: {error}"
                debug.print_message(debug.LEVEL_WARNING, msg, True)

            queued = _enqueue_brlapi_task(
                "restore braille priority",
                lambda brlapi: brlapi.setParameter(
                    BRLAPI_PARAM_CLIENT_PRIORITY, 0, False, _STATE.brlapi_current_priority
                ),
                on_success=_on_success,
                on_failure=_on_failure,
            )
            if queued:
                return


def disable_braille() -> None:
    """Idle or shut down braille output if enabled."""

    tokens = ["BRAILLE: Disabling braille. BrlAPI running:", _STATE.brlapi_running]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    if not settings.enableBraille:
        _cancel_brlapi_retry()
        if _STATE.brlapi_connecting:
            _STATE.brlapi_connect_token += 1
            _STATE.brlapi_connecting = False
        _cancel_brlapi_connect_timeout()
        _cancel_brlapi_display_size_poll()

    if _STATE.brlapi_running and not _STATE.idle:
        msg = "BRAILLE: BrlApi running and not idle."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        if not _idle_braille() and not settings.enableBraille:
            # BrlAPI before 0.8 and we really want to shut down
            msg = "BRAILLE: could not go idle, completely shut down"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            shutdown()


def check_braille_setting() -> None:
    """Disable braille if settings turn it off."""

    msg = "BRAILLE: Checking braille setting."
    debug.print_message(debug.LEVEL_INFO, msg, True)

    if not settings.enableBraille:
        disable_braille()


def _invalidate_line_caches() -> None:
    """Clear cached LineInfo for all lines."""

    for line in _STATE.lines:
        line.invalidate_cache_internal()


def _prepare_refresh(stop_flash: bool) -> bool:
    """Validate braille state and decide if refresh should proceed."""

    if stop_flash:
        kill_flash(restore_saved=False)

    from . import braille_presenter  # pylint: disable=import-outside-toplevel

    braille_enabled = braille_presenter.get_presenter().use_braille()

    # TODO - JD: This should be taken care of in orca.py.
    if not braille_enabled:
        if _STATE.brlapi_running:
            msg = "BRAILLE: FIXME - Braille disabled, but not properly shut down."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            shutdown()
        _reset_last_text_info()
        return False

    if not _STATE.lines:
        _clear_braille()
        _reset_last_text_info()
        return False

    return True


def _get_current_text_info() -> _TextInfo:
    """Build TextInfo for the currently focused Text region."""

    region = _STATE.region_with_focus
    if isinstance(region, Text):
        return _TextInfo(
            region.accessible,
            region.caret_offset,
            region.line_offset,
            0,
        )
    return _empty_text_info()


def _is_same_line(last_text_info: _TextInfo, current_text_info: _TextInfo) -> bool:
    """Return True if both TextInfo instances refer to the same line."""

    return (
        current_text_info.accessible is not None
        and current_text_info.accessible == last_text_info.accessible
        and current_text_info.line_offset == last_text_info.line_offset
    )


def _compute_cursor_offset(line_info: _LineInfo, region: Region | None) -> int:
    """Compute the absolute cursor offset in the line string."""

    if line_info.focus_offset < 0 or region is None:
        return -1
    return line_info.focus_offset + region.cursor_offset


def _set_cursor_cell(cursor_offset: int, start_position: int) -> None:
    """Set the 1-based cursor cell for the current viewport."""

    _STATE.cursor_cell = cursor_offset - start_position
    if (_STATE.cursor_cell < 0) or (_STATE.cursor_cell >= _STATE.display_size[0]):
        _STATE.cursor_cell = 0
    else:
        _STATE.cursor_cell += 1  # Normalize to 1-based offset


def _update_last_text_info_from_focus() -> None:
    """Cache TextInfo from the current focus region after refresh."""

    region = _STATE.region_with_focus
    if isinstance(region, Text):
        _STATE.last_text_info = _TextInfo(
            region.accessible,
            region.caret_offset,
            region.line_offset,
            _STATE.cursor_cell,
        )
    else:
        _reset_last_text_info()


def _compute_target_cursor_cell(
    pan_to_cursor: bool,
    target_cursor_cell: int,
    last_text_info: _TextInfo,
    current_text_info: _TextInfo,
    on_same_line: bool,
) -> int:
    """Choose target cursor cell based on caret movement and history."""

    if target_cursor_cell < 0:
        target_cursor_cell = _STATE.display_size[0] + target_cursor_cell + 1
        msg = f"BRAILLE: Adjusted target_cursor_cell to: {target_cursor_cell}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    if pan_to_cursor and target_cursor_cell == 0 and on_same_line:
        if last_text_info.cursor_cell == 0:
            msg = "BRAILLE: Not adjusting target_cursor_cell. User panned caret out of view."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif last_text_info.caret_offset == current_text_info.caret_offset:
            target_cursor_cell = last_text_info.cursor_cell
            msg = "BRAILLE: Setting target_cursor_cell to previous value. Caret hasn't moved."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        elif last_text_info.caret_offset < current_text_info.caret_offset:
            new_location = last_text_info.cursor_cell + (
                current_text_info.caret_offset - last_text_info.caret_offset
            )
            if new_location <= _STATE.display_size[0]:
                msg = f"BRAILLE: Setting target_cursor_cell based on offset: {new_location}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                target_cursor_cell = new_location
            else:
                msg = "BRAILLE: Setting target_cursor_cell to end of display."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                target_cursor_cell = _STATE.display_size[0]
        elif last_text_info.caret_offset > current_text_info.caret_offset:
            new_location = last_text_info.cursor_cell - (
                last_text_info.caret_offset - current_text_info.caret_offset
            )
            if new_location >= 1:
                msg = f"BRAILLE: Setting target_cursor_cell based on offset: {new_location}"
                debug.print_message(debug.LEVEL_INFO, msg, True)
                target_cursor_cell = new_location
            else:
                msg = "BRAILLE: Setting target_cursor_cell to start of display."
                debug.print_message(debug.LEVEL_INFO, msg, True)
                target_cursor_cell = 1

    return target_cursor_cell


def _update_viewport_for_cursor(
    pan_to_cursor: bool, target_cursor_cell: int, cursor_offset: int, line_string: str
) -> None:
    """Adjust the viewport offset to keep the cursor visible."""

    if not (pan_to_cursor and cursor_offset >= 0):
        return

    if len(line_string) <= _STATE.display_size[0] and cursor_offset < _STATE.display_size[0]:
        msg = f"BRAILLE: Not adjusting offset {_STATE.viewport[0]}. Cursor offset fits on display."
        debug.print_message(debug.LEVEL_INFO, msg, True)
    elif target_cursor_cell:
        _STATE.viewport[0] = max(0, cursor_offset - target_cursor_cell + 1)
        msg = f"BRAILLE: Adjusting offset to {_STATE.viewport[0]} based on target_cursor_cell."
        debug.print_message(debug.LEVEL_INFO, msg, True)
    elif cursor_offset < _STATE.viewport[0]:
        _STATE.viewport[0] = max(0, cursor_offset)
        msg = f"BRAILLE: Adjusting offset to {_STATE.viewport[0]} (cursor on left)"
        debug.print_message(debug.LEVEL_INFO, msg, True)
    elif cursor_offset >= (_STATE.viewport[0] + _STATE.display_size[0]):
        _STATE.viewport[0] = max(0, cursor_offset - _STATE.display_size[0] + 1)
        msg = f"BRAILLE: Adjusting offset to {_STATE.viewport[0]} (cursor beyond display end)"
        debug.print_message(debug.LEVEL_INFO, msg, True)
    else:
        range_for_offset = _get_range_for_offset(cursor_offset)
        _STATE.viewport[0] = max(0, range_for_offset[0])
        msg = f"BRAILLE: Adjusting offset to {_STATE.viewport[0]} (unhandled condition)"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if cursor_offset >= (_STATE.viewport[0] + _STATE.display_size[0]):
            _STATE.viewport[0] = max(0, cursor_offset - _STATE.display_size[0] + 1)
            msg = f"BRAILLE: Readjusting offset to {_STATE.viewport[0]} (cursor beyond display end)"
            debug.print_message(debug.LEVEL_INFO, msg, True)


def _paint_display(line_info: _LineInfo, start_position: int, end_position: int) -> bool:
    """Render the current viewport segment to device and monitor."""

    log_line = f"BRAILLE LINE:  '{line_info.string}'"
    debug.print_message(debug.LEVEL_INFO, log_line, True)
    log_line = (
        f"     VISIBLE:  '{line_info.string[start_position:end_position]}', "
        f"cursor={_STATE.cursor_cell}"
    )
    debug.print_message(debug.LEVEL_INFO, log_line, True)

    substring = line_info.string[start_position:end_position]
    if line_info.attribute_mask:
        submask = line_info.attribute_mask[start_position:end_position]
    else:
        submask = ""

    submask += "\x00" * (len(substring) - len(submask))

    if settings.enableBraille:
        _enable_braille()

    if settings.enableBraille and _STATE.brlapi_running and _STATE.brlapi_ready:
        region_size = len(substring)
        cursor_cell = _STATE.cursor_cell
        has_attr_mask = bool(line_info.attribute_mask)
        while region_size < _STATE.display_size[0]:
            substring += " "
            if has_attr_mask:
                submask += "\x00"
            region_size += 1

        def _write_braille(brlapi: Any) -> None:
            """Write the current line segment to BrlAPI."""

            write_struct = _create_brlapi_write_struct()
            if write_struct is None:
                raise RuntimeError("BrlAPI WriteStruct unavailable.")
            write_struct.regionBegin = 1
            write_struct.regionSize = region_size
            write_struct.text = substring
            write_struct.cursor = cursor_cell
            if has_attr_mask:
                write_struct.attrOr = submask
            brlapi.write(write_struct)

        if not _enqueue_brlapi_task("write braille", _write_braille):
            msg = "BRAILLE: Cannot write: BrlAPI connection unavailable."
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

    if _STATE.monitor_callback is not None:
        if line_info.attribute_mask:
            sub_mask = line_info.attribute_mask[start_position:end_position]
        else:
            sub_mask = None
        _STATE.monitor_callback(_STATE.cursor_cell, substring, sub_mask, _STATE.display_size[0])

    _STATE.beginning_is_showing = start_position == 0
    _STATE.end_is_showing = end_position >= len(line_info.string)
    return True


def refresh(
    pan_to_cursor: bool = True,
    target_cursor_cell: int = 0,
    indicate_links: bool = True,
    stop_flash: bool = True,
) -> None:
    """Render current lines to braille with panning and link indicators."""

    msg = f"BRAILLE: Refresh. Pan: {pan_to_cursor} target: {target_cursor_cell}"
    debug.print_message(debug.LEVEL_INFO, msg, True)

    if not _prepare_refresh(stop_flash):
        return

    last_text_info = _STATE.last_text_info
    tokens = [
        "BRAILLE: Last text object:",
        last_text_info.accessible,
        (
            f"(Caret: {last_text_info.caret_offset}, Line: {last_text_info.line_offset}, "
            f"Cell: {last_text_info.cursor_cell})"
        ),
    ]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    current_text_info = _get_current_text_info()
    on_same_line = _is_same_line(last_text_info, current_text_info)

    tokens = [
        "BRAILLE: Current text object:",
        current_text_info.accessible,
        (
            f"(Caret: {current_text_info.caret_offset}, Line: {current_text_info.line_offset}). "
            "On same line:"
        ),
        on_same_line,
    ]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    target_cursor_cell = _compute_target_cursor_cell(
        pan_to_cursor,
        target_cursor_cell,
        last_text_info,
        current_text_info,
        bool(on_same_line),
    )

    line = _STATE.lines[_STATE.viewport[1]]
    line_info = line.get_info(indicate_links)
    msg = (
        f"BRAILLE: Line {_STATE.viewport[1]}: '{line_info.string}' focusOffset: "
        f"{line_info.focus_offset} {line_info.ranges}"
    )
    debug.print_message(debug.LEVEL_INFO, msg, True)

    cursor_offset = _compute_cursor_offset(line_info, _STATE.region_with_focus)
    if cursor_offset >= 0:
        msg = f"BRAILLE: Cursor offset in line string is: {cursor_offset}"
        debug.print_message(debug.LEVEL_INFO, msg, True)

    _update_viewport_for_cursor(pan_to_cursor, target_cursor_cell, cursor_offset, line_info.string)

    start_position, end_position = _adjust_for_word_wrap(target_cursor_cell, line_info.ranges)
    _STATE.viewport[0] = start_position

    # Now normalize the cursor position to BrlTTY, which uses 1 as
    # the first cursor position as opposed to 0.
    _set_cursor_cell(cursor_offset, start_position)

    if not _paint_display(line_info, start_position, end_position):
        return

    # Remember the text information we were presenting (if any)
    _update_last_text_info_from_focus()


def _flash_callback() -> bool:
    """Restore saved state when a flash message expires."""

    if _STATE.flash_event_source_id and _STATE.saved:
        _STATE.lines = _STATE.saved.lines
        _STATE.region_with_focus = _STATE.saved.region_with_focus
        _STATE.viewport = _STATE.saved.viewport
        _invalidate_line_caches()
        msg = "BRAILLE: Flash message callback"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        refresh(pan_to_cursor=False, stop_flash=False)
        _STATE.flash_event_source_id = 0

    return False


def kill_flash(restore_saved: bool = True) -> None:
    """Stop any active flash and optionally restore previous content."""

    msg = "BRAILLE: Kill flash message"
    debug.print_message(debug.LEVEL_INFO, msg, True, True)
    if _STATE.flash_event_source_id:
        if _STATE.flash_event_source_id > 0:
            GLib.source_remove(_STATE.flash_event_source_id)
        if restore_saved and _STATE.saved:
            _STATE.lines = _STATE.saved.lines
            _STATE.region_with_focus = _STATE.saved.region_with_focus
            _STATE.viewport = _STATE.saved.viewport
            _invalidate_line_caches()
            refresh(pan_to_cursor=False, stop_flash=False)
        _STATE.flash_event_source_id = 0


def _reset_flash_timer() -> None:
    """Resets the flash timer if a flash is currently active."""

    if _STATE.flash_event_source_id > 0 and _STATE.saved:
        GLib.source_remove(_STATE.flash_event_source_id)
        _STATE.flash_event_source_id = GLib.timeout_add(_STATE.saved.flash_time, _flash_callback)


def _init_flash(flash_time: int) -> None:
    """Sets up / clears the state needed to flash a message."""

    msg = f"BRAILLE: Initializing flash: Source ID: {_STATE.flash_event_source_id}"
    debug.print_message(debug.LEVEL_INFO, msg, True)

    if _STATE.flash_event_source_id:
        if _STATE.flash_event_source_id > 0:
            GLib.source_remove(_STATE.flash_event_source_id)
        _STATE.flash_event_source_id = 0
    else:
        _STATE.saved = _FlashState(
            _STATE.lines, _STATE.region_with_focus, _STATE.viewport, flash_time
        )

    if flash_time > 0:
        _STATE.flash_event_source_id = GLib.timeout_add(flash_time, _flash_callback)
    elif flash_time < 0:
        _STATE.flash_event_source_id = _FLASH_EVENT_SOURCE_ID_INDEFINITE


def display_message(message: str, flash_time: int = 0) -> None:
    """Display a message for the specified amount of time."""

    msg = f"BRAILLE: Display message: '{message}' (flash_time: {flash_time})"
    debug.print_message(debug.LEVEL_INFO, msg, True)

    _init_flash(flash_time)
    region = Region(message, -1)
    line = Line(region)
    display_line(line, region, stop_flash=False)


def _adjust_for_word_wrap(target_cursor_cell: int, ranges: Sequence[list[int]]) -> tuple[int, int]:
    """Adjust viewport boundaries to word-wrap ranges."""

    start_position = _STATE.viewport[0]
    end_position = start_position + _STATE.display_size[0]
    msg = (
        f"BRAILLE: Current range: ({start_position}, {end_position}). "
        f"Target cell: {target_cursor_cell}"
    )
    debug.print_message(debug.LEVEL_INFO, msg, True)

    if not _STATE.lines or not settings.enableBrailleWordWrap:
        return start_position, end_position

    ranges = list(filter(lambda x: x[0] <= start_position + target_cursor_cell < x[1], ranges))
    if ranges:
        msg = f"BRAILLE: Adjusted range: ({ranges[0][0]}, {ranges[-1][1]})"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        if ranges[-1][1] - ranges[0][0] > _STATE.display_size[0]:
            msg = "BRAILLE: Not adjusting range which is greater than display size"
            debug.print_message(debug.LEVEL_INFO, msg, True)
        else:
            start_position, end_position = ranges[0][0], ranges[-1][1]

    return start_position, end_position


def _get_range_for_offset(offset: int) -> list[int]:
    """Return the word-wrap range containing the given offset."""

    line_info = _STATE.lines[_STATE.viewport[1]].get_info()
    for r in line_info.ranges:
        if r[0] <= offset < r[1]:
            return r
    for r in line_info.ranges:
        if offset == r[1]:
            return r

    return [0, 0]


def pan_left(pan_amount: int = 0) -> bool:
    """Pan the viewport left and return True if it moved."""

    old_x = _STATE.viewport[0]
    if pan_amount == 0:
        old_start, _old_end = _get_range_for_offset(old_x)
        new_start, _new_end = _get_range_for_offset(old_start - _STATE.display_size[0])
        pan_amount = max(0, min(old_start - new_start, _STATE.display_size[0]))

    _STATE.viewport[0] = max(0, _STATE.viewport[0] - pan_amount)
    msg = f"BRAILLE: Panning left. Amount: {pan_amount} (from {old_x} to {_STATE.viewport[0]})"
    debug.print_message(debug.LEVEL_INFO, msg, True)
    _reset_flash_timer()
    return old_x != _STATE.viewport[0]


def pan_right(pan_amount: int = 0) -> bool:
    """Pan the viewport right and return True if it moved."""

    old_x = _STATE.viewport[0]
    if pan_amount == 0:
        old_start, old_end = _get_range_for_offset(old_x)
        new_start, _new_end = _get_range_for_offset(old_end)
        pan_amount = max(0, min(new_start - old_start, _STATE.display_size[0]))

    if len(_STATE.lines) > 0:
        line_number = _STATE.viewport[1]
        new_x = _STATE.viewport[0] + pan_amount
        line_info = _STATE.lines[line_number].get_info()
        if new_x < len(line_info.string):
            _STATE.viewport[0] = new_x

    msg = f"BRAILLE: Panning right. Amount: {pan_amount} (from {old_x} to {_STATE.viewport[0]})"
    debug.print_message(debug.LEVEL_INFO, msg, True)
    _reset_flash_timer()
    return old_x != _STATE.viewport[0]


def return_to_region_with_focus(_input_event: Any | None = None) -> bool:
    """Pan so the region with focus is visible."""

    _set_focus(_STATE.region_with_focus)
    refresh(True)

    return True


def _next_contracted_braille_setting(event: InputEvent | None) -> bool:
    """Derive the contracted braille setting from event flags or toggle."""

    current = settings.enableContractedBraille
    if event is None or event.type != "braille":
        msg = (
            "BRAILLE: Toggling contracted braille from non-braille event. "
            f"Current: {current} New: {not current}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return not current

    if BRLAPI_KEY_FLG_TOGGLE_ON is None:
        msg = "BRAILLE: Cannot toggle contracted braille: BrlAPI flag unavailable."
        debug.print_message(debug.LEVEL_WARNING, msg, True)
        msg = (
            "BRAILLE: Toggling contracted braille without BrlAPI flag. "
            f"Current: {current} New: {not current}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return not current

    braille_event = cast(Any, event)
    enabled = (braille_event.event["flags"] & BRLAPI_KEY_FLG_TOGGLE_ON) != 0
    msg = (
        "BRAILLE: Contracted braille flag from display. "
        f"Flags: {braille_event.event['flags']} Enabled: {enabled}"
    )
    debug.print_message(debug.LEVEL_INFO, msg, True)
    return enabled


def toggle_contracted_braille(event: InputEvent | None) -> None:
    """Toggle contracted braille based on the incoming event."""

    settings.enableContractedBraille = _next_contracted_braille_setting(event)
    for line in _STATE.lines:
        line.set_contracted_braille(settings.enableContractedBraille)
    refresh()


def process_routing_key(event: BrailleEvent) -> bool:
    """Handle a routing key BrailleEvent and dispatch to the line."""

    msg = f"BRAILLE: Process routing key. Source ID: {_STATE.flash_event_source_id}"
    debug.print_message(debug.LEVEL_INFO, msg, True)

    if _STATE.flash_event_source_id:
        kill_flash()
        return True

    cell = event.event["argument"]

    if len(_STATE.lines) > 0:
        cursor = cell + _STATE.viewport[0]
        line_number = _STATE.viewport[1]
        _STATE.lines[line_number].process_routing_key(cursor)

    return True


def _process_braille_event(event: Any) -> bool:
    """Processes a BrailleEvent, calling the callback if it exists."""

    tokens = ["BRAILLE: Processing event", event]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
    consumed = False
    if _STATE.callback:
        try:
            consumed = _STATE.callback(event)
        except CALLBACK_ERRORS as error:
            msg = f"WARNING: Could not process braille event: {error}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            consumed = False

    return consumed


def _brlapi_key_reader(_source: Any, _condition: Any) -> bool:
    """Method to read a key from the BrlAPI bindings."""

    brlapi = _STATE.brlapi
    if brlapi is None:
        msg = "WARNING: BrlAPI connection unavailable; cannot read key."
        debug.print_message(debug.LEVEL_WARNING, msg, True)
        _mark_brlapi_dead()
        return False
    try:
        key = brlapi.readKey(False)
    except BRLAPI_ERRORS as error:
        msg = f"WARNING: Could not read BrlApi key: {error}"
        debug.print_message(debug.LEVEL_WARNING, msg, True)
        _mark_brlapi_dead()
        return False
    if key:
        _process_braille_event(brlapi.expandKeyCode(key))
    return _STATE.brlapi_running


def _apply_key_ranges(keys: Sequence[int]) -> None:
    """Send ignore/accept key ranges to BrlAPI."""

    if (
        BRLAPI_RANGE_TYPE_ALL is None
        or BRLAPI_RANGE_TYPE_COMMAND is None
        or BRLAPI_KEY_TYPE_CMD is None
        or BRLAPI_KEY_CMD_ROUTE is None
    ):
        msg = "BRAILLE: Not setting up key ranges: BrlAPI constants unavailable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return

    msg = "BRAILLE: Ignoring all key ranges."
    debug.print_message(debug.LEVEL_INFO, msg, True)
    if not _enqueue_brlapi_task(
        "ignore key ranges",
        lambda brlapi: brlapi.ignoreKeys(BRLAPI_RANGE_TYPE_ALL, [0]),
    ):
        msg = "BRAILLE: Not setting up key ranges: BrlAPI connection unavailable."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return

    key_set = [BRLAPI_KEY_TYPE_CMD | BRLAPI_KEY_CMD_ROUTE]

    msg = "BRAILLE: Enabling commands:"
    debug.print_message(debug.LEVEL_INFO, msg, True)

    for key in keys:
        key_set.append(BRLAPI_KEY_TYPE_CMD | key)

    msg = "BRAILLE: Sending keys to BrlAPI."
    debug.print_message(debug.LEVEL_INFO, msg, True)
    _enqueue_brlapi_task(
        "accept key ranges",
        lambda brlapi: brlapi.acceptKeys(BRLAPI_RANGE_TYPE_COMMAND, key_set),
    )

    msg = "BRAILLE: Key ranges set up."
    debug.print_message(debug.LEVEL_INFO, msg, True)


def setup_key_ranges(keys: Iterable[int]) -> None:
    """Configure BrlTTY key ranges for readKey filtering."""

    msg = "BRAILLE: Setting up key ranges."
    debug.print_message(debug.LEVEL_INFO, msg, True)

    _STATE.pending_key_ranges = list(keys)

    if not _STATE.brlapi_running:
        init(_STATE.callback)

    if not _STATE.brlapi_running:
        msg = "BRAILLE: Not setting up key ranges: BrlAPI not running."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return

    _apply_key_ranges(_STATE.pending_key_ranges)


def set_brlapi_priority(level: int = BRLAPI_PRIORITY_DEFAULT) -> None:
    """Set the current BrlAPI priority level."""

    if not _STATE.brlapi_available or not _STATE.brlapi_running or not settings.enableBraille:
        return

    if _STATE.idle:
        msg = "BRAILLE: Braille is idle, don't change _STATE.brlapi priority."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        _STATE.brlapi_current_priority = level
        return

    if BRLAPI_PARAM_CLIENT_PRIORITY is None:
        msg = "BRAILLE: Cannot set priority: BrlAPI parameter unavailable."
        debug.print_message(debug.LEVEL_WARNING, msg, True)
        return

    tokens = ["BRAILLE: Setting priority to:", level]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    def _on_success() -> None:
        """Update cached priority after a successful set."""

        msg = "BRAILLE: Priority set."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        _STATE.brlapi_current_priority = level

    def _on_failure(error: BaseException) -> None:
        """Log a failure to set the BrlAPI priority."""

        msg = f"BRAILLE: Cannot set priority: {error}"
        debug.print_message(debug.LEVEL_WARNING, msg, True)

    _enqueue_brlapi_task(
        "set priority",
        lambda brlapi: brlapi.setParameter(BRLAPI_PARAM_CLIENT_PRIORITY, 0, False, level),
        on_success=_on_success,
        on_failure=_on_failure,
    )


def init(callback: Callable[[Any], bool] | None = None) -> bool:
    """Initialize braille and start an asynchronous BrlAPI connection."""

    if not settings.enableBraille:
        return False

    tokens = ["BRAILLE: Initializing. Callback:", callback]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    if BRLAPI is None:
        msg = "BRAILLE: Initialization failed: BrlApi is not defined."
        debug.print_message(debug.LEVEL_WARNING, msg, True)
        return False

    if _STATE.brlapi_running:
        msg = "BRAILLE: BrlAPI is already running."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    _STATE.callback = callback
    if _STATE.brlapi_connecting:
        msg = "BRAILLE: BrlAPI connection already in progress."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    tokens = ["BRAILLE: WINDOWPATH=", os.environ.get("WINDOWPATH")]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    tokens = ["BRAILLE: XDG_VTNR=", os.environ.get("XDG_VTNR")]
    debug.print_tokens(debug.LEVEL_INFO, tokens, True)

    _start_brlapi_connection()
    return True


def shutdown() -> bool:
    """Shut down braille and return True if it ran."""

    msg = "BRAILLE: Attempting braille shutdown."
    debug.print_message(debug.LEVEL_INFO, msg, True)

    _cancel_brlapi_retry()
    if _STATE.brlapi_connecting:
        _STATE.brlapi_connect_token += 1
        _STATE.brlapi_connecting = False
    _cancel_brlapi_connect_timeout()
    _cancel_brlapi_display_size_poll()
    if _STATE.brlapi_inflight_timer_id:
        GLib.source_remove(_STATE.brlapi_inflight_timer_id)
        _STATE.brlapi_inflight_timer_id = 0
    _STATE.brlapi_inflight_action = None
    _STATE.brlapi_inflight_since = 0.0

    if _STATE.brlapi_running:
        msg = "BRAILLE: Removing BrlAPI Source ID."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        GLib.source_remove(_STATE.brlapi_source_id)
        _STATE.brlapi_source_id = 0

        brlapi = _STATE.brlapi
        if brlapi is not None and _STATE.brlapi_queue is not None:
            _STATE.brlapi_queue.put(
                _BrlapiTask("leave TTY mode", lambda api: api.leaveTtyMode(), brlapi)
            )
            _STATE.brlapi_queue.put(
                _BrlapiTask("close connection", lambda api: api.closeConnection(), brlapi)
            )
            _STATE.brlapi_queue.put(None)

        _STATE.brlapi_running = False
        _STATE.brlapi = None
        _STATE.brlapi_session_token += 1
        _STATE.brlapi_queue = None
        _STATE.brlapi_worker = None
        _STATE.idle = False

        _STATE.display_size = [DEFAULT_DISPLAY_SIZE, 1]
    else:
        msg = "BRAILLE: Braille was not running."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return False

    msg = "BRAILLE: Braille shutdown complete."
    debug.print_message(debug.LEVEL_INFO, msg, True)
    return True
