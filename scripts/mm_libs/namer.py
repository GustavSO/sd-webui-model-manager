import decimal
import gradio as gr
from modules.shared import opts
import re
from scripts.mm_libs.model import Model
from scripts.mm_libs.debug import *

# TODO: Should detect on a per-OS basis
IILEGAL_WIN_CHARS = re.compile(r'[<>:"/|?*\\]')

# Mapping for the alphabet filtering
alphabet_mapping = {
    "Chinese": r"[\u4E00-\u9FFF\u3400-\u4DBF\U00020000-\U0002A6DF\U0002A700-\U0002B73F\U0002B740-\U0002B81F\U0002B820-\U0002CEAF\U0002CEB0-\U0002EBEF]",  # Basic Multilingual Plane, Extension A, Extension B, Extension C, Extension D, Extension E
    "Cyrillic": r"[\u0400-\u04ff]",  # Cyrillic
    "Japanese": r"[\u3040-\u30ff]",  # Hiragana and Katakana (should maybe also include Kanji)
    "Latin": r"[a-zA-Z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF]",  # Latin Letters, Latin-1 Supplement (excluding × [U+00D7] and ÷ [U+00F7]),
    "Korean": r"[\u3131-\u3163\uac00-\ud7a3]",  # Hangul Jamo, Hangul Syllables /TODO: Validate
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
def vaidate_filename(filename: str):
    # This will only happen if the user have turned off the auto trim illegal characters setting
    if IILEGAL_WIN_CHARS.search(filename):
        d_error("Invalid Filename: Illegal characters detected. Remove them or enable 'Trim Illegal Characters' in settings")
        return False

    if not filename:
        d_error("Invalid Filename: Filename cannot be empty")
        return False

    return True


# Remove excluded words from the filename
# Ignore case
def remove_excluded_words(filename: str):
    excluded_words = (
        opts.mm_excluded_words_or_phrases.split(",")
        if opts.mm_excluded_words_or_phrases
        else []
    )
    for word in excluded_words:
        word = word.strip()
        filename = re.sub(rf"\b{word}\b", "", filename, flags=re.IGNORECASE)

    return filename


def format_filename(format: str, model: Model):
    if not format:
        return remove_excluded_words(f"{model.name})")

    for key, value in name_mapping.items():
        eval_value = str(eval(value))
        if key in ["model_name", "model_version"]:
            eval_value = remove_excluded_words(eval_value)
            if key == "model_version":
                if opts.mm_decimalize_versioning:
                    d_print("Decimalizing versioning")
                    d_print(f"Before: {eval_value}")
                    eval_value = decimalize_versioning(eval_value)
                    d_print(f"After: {eval_value}")
                if opts.mm_capatalize_versioning:
                    d_print("Capatalizing versioning")
                    d_print(f"Before: {eval_value}")
                    eval_value = capatalize_versioning(eval_value)
                    d_print(f"After: {eval_value}")


        format = format.replace(key, eval_value)

    return format


def adjust_filename(filename: str):
    if opts.mm_auto_trim_illegal_chars:
        filename = trim_illegal_chars(filename)

    if opts.mm_filter_alphabet:
        alphabets = opts.mm_filter_alphabet
        filename = filter_alphabet(filename, alphabets)

    if opts.mm_auto_fit_brackets:
        filename = auto_fit_brackets(filename)

    if opts.mm_remove_empty_brackets:
        filename = remove_empty_brackets(filename)

    if opts.mm_capatalize:
        filename = capatalize(filename)

    # if opts.mm_capatalize_versioning:
    #     filename = re.sub(r"v(\d+)", lambda x: f"V{x.group(1)}", filename)

    # if opts.mm_decimalize_versioning:
    #     filename = re.sub(r"V(\d+)(?!\.\d+)", lambda x: f"V{x.group(1)}.0", filename)

    if opts.mm_auto_trim_whitespace:
        filename = trim_whitespace(filename)

    return filename.strip()


def trim_illegal_chars(filename: str):
    return IILEGAL_WIN_CHARS.sub("", filename)


def filter_alphabet(filename: str, alphabets: list):
    for alphabet in alphabets:
        filename = re.sub(alphabet_mapping[alphabet], "", filename)
    return filename


# TODO: Gotta be a better way to do this
# Removes whitespaces on the inside of brackets
def auto_fit_brackets(filename: str):
    return re.sub(
        r"([\[(\{])\s*([^)\]}]+?)\s*([\])}])",
        lambda x: f"{x.group(1)}{x.group(2).strip()}{x.group(3)}",
        filename,
    )

def remove_empty_brackets(filename):
    filename = re.sub(r"[\[(\{]\s*[\])}]", "", filename)
    return filename


def capatalize(filename):
    filename = re.sub(r"\b\w", lambda x: x.group().upper(), filename)
    return filename


def trim_whitespace(filename):
    filename = re.sub(" +", " ", filename)
    return filename

def capatalize_versioning(version):
    return re.sub(r"v(\d+)", lambda x: f"V{x.group(1)}", version)

def decimalize_versioning(version):
    pattern = r"[Vv](\d+)(,|\.)?(\d*)"
    
    def replace_version(match):
        # If the version number includes a comma, replace it with a dot
        if match.group(2) == ',':
            return f"V{match.group(1)}.{match.group(3)}"
        # If the version number lacks a decimal point, append `.0`
        elif not match.group(2):
            return f"V{match.group(1)}.0"
        # If the version number already includes a dot, return it unchanged
        else:
            return f"V{match.group(1)}.{match.group(3)}"
    
    return re.sub(pattern, replace_version, version)