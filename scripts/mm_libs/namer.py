import gradio as gr
from modules.shared import opts
import re
from scripts.mm_libs.model import Model

# TODO: Should detect on a per-OS basis
IILEGAL_WIN_CHARS = re.compile(r'[<>:"/|?*\\]')

# Mapping for the alphabet filtering
alphabet_mapping = {
    "Chinese": r"[\u4E00-\u9FFF\u3400-\u4DBF\U00020000-\U0002A6DF\U0002A700-\U0002B73F\U0002B740-\U0002B81F\U0002B820-\U0002CEAF\U0002CEB0-\U0002EBEF]", # Basic Multilingual Plane, Extension A, Extension B, Extension C, Extension D, Extension E
    "Cyrillic": r"[\u0400-\u04ff]", # Cyrillic
    "Japanese": r"[\u3040-\u30ff]", # Hiragana and Katakana (should maybe also include Kanji)
    "Latin": r"[a-zA-Z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF]", # Latin Letters, Latin-1 Supplement (excluding × [U+00D7] and ÷ [U+00F7]),
    "Korean": r"[\u3131-\u3163\uac00-\ud7a3]" # Hangul Jamo, Hangul Syllables /TODO: Validate
}

# Mapping for the filename formatting
name_mapping = {
    "model_name": "model.name",
    "model_version": "model.version",
    "model_base": "model.metadata['sd version']",
    "model_creator": "model.creator",
    "model_type": "model.type",
}

# Validate the filename for illegal characters and empty strings
def vaidate_filename(filename : str):
    if IILEGAL_WIN_CHARS.search(filename):
        gr.Warning("Invalid Filename: Illegal characters detected. Remove them or enable 'Trim Illegal Characters' in settings")
        return

    if filename == "":
        gr.Warning("Invalid Filename: Filename cannot be empty")
        return

    return filename

def remove_excluded_words(filename : str, excluded_words : list):
    for word in excluded_words:
        filename = re.sub(rf"\b{word}\b", "", filename)

    return filename

def format_filename(format : str, excluded_words : list, model: Model):
    for key, value in name_mapping.items():
        eval_value = str(eval(value))
        if key in ['model_name', 'model_version']:
            eval_value = remove_excluded_words(eval_value, excluded_words)
        format = format.replace(key, eval_value)

    return format

def adjust_filename(filename : str):
    if opts.mm_auto_trim_illegal_chars:
        filename = IILEGAL_WIN_CHARS.sub('', filename)

    alphabets = opts.mm_filter_alphabet
    for alphabet in alphabets:
        filename = re.sub(alphabet_mapping[alphabet], "", filename)

    if opts.mm_auto_fit_brackets:
        filename = re.sub(r"([\[(\{])\s*([^)\]}]+?)\s*([\])}])", lambda x: f"{x.group(1)}{x.group(2).strip()}{x.group(3)}", filename)

    if opts.mm_remove_empty_brackets:
        filename = re.sub(r"[\[(\{]\s*[\])}]", "", filename)

    if opts.mm_capatalize:
        filename = re.sub(r"\b\w", lambda x: x.group().upper(), filename)

    if opts.mm_capatalize_versioning:
        filename = re.sub(r"v(\d+)", lambda x: f"V{x.group(1)}", filename)
    
    if opts.mm_decimalize_versioning:
        filename = re.sub(r"V(\d+)(?!\.\d+)", lambda x: f"V{x.group(1)}.0", filename)

    if opts.mm_auto_trim_whitespace:
        filename = re.sub(" +", " ", filename)

    return filename.strip()