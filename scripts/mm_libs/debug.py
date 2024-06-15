import inspect
import os
import gradio as gr

from datetime import datetime
from enum import Enum
from modules.shared import opts

class Color(Enum):
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    END = "\033[0m"


def _d_print(text, color, show_time, details=None):
    """Prints a message in the specified color."""
    timestamp = datetime.now().strftime('%H:%M:%S:%f')[:-3]
    prefix = f"[Model Manager ({timestamp})] " if show_time else "[Model Manager] "
    if details:
        prefix += f"@ [{details}] "
    print(f"{color.value}{prefix}{Color.END.value}{text}")

def d_message(text):
    """Prints a message in blue color."""
    show_time = opts.mm_show_timestamp
    _d_print(text, Color.BLUE, show_time)

def d_warn(text):
    """Shows a gradio warning. Prints a warning in yellow color if enabled."""
    show_time=opts.mm_show_timestamp
    if opts.mm_print_warnings:
        _d_print(text, Color.YELLOW, show_time)
    gr.Warning(text)

def d_error(text):
    """Shows a gradio error. Prints an error in red color if enabled."""
    show_time = opts.mm_show_timestamp
    if opts.mm_print_errors:
        _d_print(text, Color.RED, show_time)
    gr.Error(text)

def d_info(text):
    """Shows a gradio info. Prints an info message in green color if enabled."""
    show_time=opts.mm_show_timestamp
    if opts.mm_print_info:
        _d_print(text, Color.GREEN, show_time)
    gr.Info(text)

def d_debug(text, color=Color.CYAN):
    """Prints a debug message in cyan color. Always shows the timestamp."""
    if not opts.mm_print_debug if hasattr(opts, "mm_print_debug") else False:
        return
    
    details = None
    if opts.mm_debug_stacktrace if hasattr(opts, "mm_debug_stacktrace") else False:
        caller_frame = inspect.stack()[1]
        caller_name = os.path.basename(caller_frame.filename)
        caller_function = caller_frame.function
        caller_line = caller_frame.lineno
        details = f"{caller_name}::{caller_function}::{caller_line}"

    _d_print(text, color, True, details)