import gradio as gr

from datetime import datetime
from modules.shared import opts

def d_print(text):
    timestamp = datetime.now().strftime('%H:%M:%S:%f')[:-3]
    print(f"\033[94m[Model Manager ({timestamp})]\033[0m {text}")

def d_warn(text):
    timestamp = datetime.now().strftime('%H:%M:%S:%f')[:-3]
    if opts.mm_print_warnings:
        print(f"\033[93m[Model Manager ({timestamp})]\033[0m {text}")
    gr.Warning(text)

def d_error(text):
    timestamp = datetime.now().strftime('%H:%M:%S:%f')[:-3]
    if opts.mm_print_errors:
        print(f"\033[91m[Model Manager ({timestamp})]\033[0m {text}")
    gr.Error(text)

def d_info(text):
    timestamp = datetime.now().strftime('%H:%M:%S:%f')[:-3]
    print(f"\033[92m[Model Manager ({timestamp})]\033[0m {text}")
    gr.Info(text)