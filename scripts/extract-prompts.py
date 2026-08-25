"""
File    : extract-prompts.py
Purpose : Script to extract prompts & styles from Power Nodes generated images.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Mar 21, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import re
import os
import sys
import json
import argparse
import struct
from pathlib import Path
from typing  import NoReturn

# pillow is required only when the user asks for JPG conversion
try:                from PIL import Image
except ImportError: Image = None

# regular expressions for ???
_RE_DIGITS = re.compile(r"(\d+)")






# ANSI escape codes for colored terminal output
RED      = '\033[91m'
DKRED    = '\033[31m'
YELLOW   = '\033[93m'
DKYELLOW = '\033[33m'
GREEN    = '\033[92m'
CYAN     = '\033[96m'
DKGRAY   = '\033[90m'
RESET    = '\033[0m'

#============================= ERROR MESSAGES ==============================#

def disable_colors():
    global RED, DKRED, YELLOW, DKYELLOW, GREEN, CYAN, DKGRAY, RESET
    RED, DKRED, YELLOW, DKYELLOW, GREEN, CYAN, DKGRAY, RESET = "", "", "", "", "", "", "", ""


def message(msg: str, padding: int = 0, file=sys.stderr) -> None:
    """Displays a plain progress/status message to the specified stream.
    """
    print(f"{' ' * padding}{msg}", file=file)


def info(message: str, padding: int = 0, file=sys.stderr) -> None:
    """Displays an informational message to the error stream.
    """
    print(f"{" "*padding}{CYAN}\u24d8 {message}{RESET}", file=file)


def warning(message: str, *info_messages: str, padding: int = 0, file=sys.stderr) -> None:
    """Displays a warning message to the standard error stream.
    """
    print(f"{" "*padding}{CYAN}[{YELLOW}WARNING{CYAN}]{DKYELLOW} {message}{RESET}", file=file)
    for info_message in info_messages:
        if info_message:
            info(info_message, padding=padding, file=file)


def error(message: str, *info_messages: str, padding: int = 0, file=sys.stderr) -> None:
    """Displays an error message to the standard error stream.
    """
    print(f"{" "*padding}{DKRED}[{RED}ERROR!{DKRED}]{DKYELLOW} {message}{RESET}", file=file)
    for info_message in info_messages:
        if info_message:
            info(info_message, padding=padding, file=file)


def fatal_error(message: str, *info_messages: str, padding: int = 0, file=sys.stderr) -> NoReturn:
    """Displays a fatal error message to the standard error stream and exits with status code 1.
    """
    error(message, *info_messages, padding=padding, file=file)
    sys.exit(1)


#================================= HELPERS =================================#

def _human_key(text: str) -> list:
    """Convert a string into a tuple to be used as a key for sorting:
    'file2' -> ['file', 2], 'file100' -> ['file', 100]
    """
    return [int(token) if token.isdigit() else token.lower() for token in _RE_DIGITS.split(text)]


def sort_paths_by_filename(paths: list[Path]) -> list[Path]:
    """Sort a list of Path objects based on their filenames using a human-friendly approach.
    Args:
        paths: List of Path objects to be sorted.
    Returns:
        A new list of Path objects sorted by their filenames.
    """
    return sorted(paths, key=lambda p: _human_key(p.name))


def find_text_chunk(file_path: Path, text_chunk_name: str) -> str:
    """Search for a specific PNG text chunk and return its content as a UTF-8 string.
    Args:
        file_path      : Path to the PNG file.
        text_chunk_name: The name of the text chunk to search for.
    Returns:
        Decoded UTF-8 string if the chunk is found, otherwise an empty string.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not text_chunk_name:
        return ""

    name_bytes = text_chunk_name.encode("utf-8")
    with open(file_path, 'rb') as f:

        # verify PNG signature
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file")

        # iterate through chunks
        while True:
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break
            length, chunk_type = struct.unpack('>I4s', chunk_header)

            # skip non-text chunks
            if chunk_type != b"tEXt":
                f.seek(length + 4, 1)  #< skip data + CRC
                continue

             # read the entire tEXt chunk data
            chunk_data = f.read(length)

            # split keyword, null separator, and text
            keyword, null, content = chunk_data.partition(b"\x00")
            if keyword != name_bytes or null != b"\x00":
                f.seek(4, 1)  #< skip CRC
                continue

            # CHUNK FOUND!!
            # skip CRC and return the UTF-8 decoded text
            f.seek(4, 1)
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return ""

    return ""


def convert_png_to_jpg(path: Path,
                       *,
                       output_dir: Path | None = None,
                       quality   : int         = 95,
                       overwrite : bool        = False
                       ) -> Path | None:
    """
    Convert a PNG image to JPG format and save it in the specified output directory.

    The original PNG file remains unchanged. If no output directory is provided,
    the JPG file will be saved in the same directory as the PNG file. If the
    JPG already exists and overwrite is False, the function does nothing and
    and returns None.

    Args:
        path       : Path to the source PNG file.
        output_dir : Optional directory where the JPG file will be saved.
                     Defaults to the same directory as the PNG file.
        quality    : JPEG quality level (ranging from 1 to 100).
                     Defaults to 95.
        overwrite  : If True, allows overwriting the JPG files.
                     Defaults to False.

    Returns:
        Path to the newly created JPG file,
        or `None` if the file already exists and overwrite is False.
    """
    if Image is None:
        fatal_error("Pillow is required for JPG conversion.",
                    "Install it with: pip install Pillow")

    # default output directory is the same as the PNG
    if output_dir is None:
        output_dir = path.parent

    jpg_path = (output_dir / (path.stem + ".jpg")).resolve()

    # handle overwrite logic
    if jpg_path.exists() and not overwrite:
        warning(f'Cannot create "{jpg_path.name}", it already exists. ',
                 "use '--overwrite' to force overwrite")
        return None

    try:
        with Image.open(path) as image:
            rgb_image = image.convert("RGB")
            rgb_image.save(jpg_path, "JPEG", quality=quality)
    except Exception as exc:
        fatal_error(f"Failed to convert {path} to JPG: {exc}")

    return jpg_path


#============================= COMFY WORKFLOWS =============================#

def extract_api_workflow(path: Path) -> dict[str, dict]:
    """Extract the ComfyUI workflow stored in the 'prompt' PNG chunk.
    Args:
        path: Path to the PNG file.
    Returns:
        Dictionary of workflow nodes.
        Returns an empty dictionary if no prompt chunk is found.
    """
    chunk_content = find_text_chunk(path, 'prompt')
    if not chunk_content:
        return {}
    try:
        workflow_data = json.loads(chunk_content)
    except json.JSONDecodeError:
        workflow_data = {}

    return workflow_data


def extract_style_and_prompt(path: Path) -> tuple[str,str]:
    """Extract style and prompt from a the workflow stored in a PNG file.
    Args:
        path: Path to the PNG file.
    Returns:
        A tuple containing the style and prompt strings,
        or a tuple with empty strings if the prompt is not found.
    """
    for node in extract_api_workflow(path).values():
        class_type = node.get("class_type", "")
        if class_type.startswith("StylePromptEncode"):
            inputs = node.get("inputs") or {}
            style  = inputs.get("style", "")
            if not isinstance(style,str):
                style = "???"
            prompt = inputs.get("text" , "")
            if not isinstance(prompt,str):
                prompt = "???"
            return style.strip(), prompt.strip()

    return ("", "")


def format_prompt(path: Path, style: str, prompt: str) -> str:
    """
    Format the prompt string to include the style and prompt.
    Args:
       path   : The path to the image file from which the prompt was extracted.
       style  : The "Power Nodes" style of the image.
       prompt : The "Power Nodes" prompt for the image.
    Returns:
       The formatted prompt string.
    """
    return f'Prompt {path.stem} - Style "{style}"\n{prompt}'


#===========================================================================#
#////////////////////////////////// MAIN ///////////////////////////////////#
#===========================================================================#


def main(args=None, parent_script=None):
    """
    Main entry point for the script.
    Args:
        args          (optional): List of arguments to parse. Default is None, which will use the command line arguments.
        parent_script (optional): The name of the calling script if any. Used for customizing help output.
    """
    prog = None
    if parent_script:
        prog = parent_script + " " + os.path.basename(__file__).split('.')[0]

    # set up argument parser for the script
    parser = argparse.ArgumentParser(
        prog            = prog,
        description     = "Extract prompts from Power Nodes generated images.",
        formatter_class = argparse.RawTextHelpFormatter,
#        epilog          = """Environment Variables:
#  VAR_NAME = Description.
#  """
    )
    parser.add_argument('-j', '--jpg', action='store_true',
                        help="Convert every found PNG to JPG, storing the JPGs in the current directory.")
    parser.add_argument('-q', '--quality', type=int, metavar='1-100', default=95,
                        help="JPEG quality when using --jpg (default: 95).")
    parser.add_argument('-w', '--overwrite', action='store_true',
                        help="Allow overwriting existing JPG files when using --jpg.")
    parser.add_argument('--no-color' , action='store_true',
                        help="Disable colored output.")
    parser.add_argument('paths', nargs='*', default=['.'],
                        help='Files or directories to scan for PNG images. '
                             'If a directory is given, all PNGs inside are included. '
                             'Default is current directory.')

    args = parser.parse_args(args=args)

    # if the user requested to disable colors, call disable_colors()
    if args.no_color:
        disable_colors()

    # collect all PNG files from the given paths
    png_paths = []
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_dir():
            png_paths.extend(path.glob('*.[pP][nN][gG]'))
        elif path.is_file() and path.suffix.lower() == '.png':
            png_paths.append(path)

    if not png_paths:
        fatal_error("No PNG files found.")

    # show message to the user explaining that this could be a unsafe script
    info("This script was written for personal use only, use at your own risk.")

    # extract style and prompt from each PNG file
    number_of_prompts = 0
    for path in sort_paths_by_filename(png_paths):
        style, prompt = extract_style_and_prompt(path)
        if style and prompt:
            text = format_prompt(path, style, prompt)
            print()
            print(text)
            number_of_prompts += 1
    message(f"{GREEN} ✓ Extracted {number_of_prompts} prompts from {len(png_paths)} PNG files.{RESET}")

    # if the user requested to convert PNGs to JPGs, do so
    if args.jpg:
        output_dir = Path.cwd()
        if not (1 <= args.quality <= 100):
            fatal_error("Quality must be between 1 and 100.")
        for path in png_paths:
            jpg_path = convert_png_to_jpg(path,
                                          output_dir = output_dir,
                                          quality    = args.quality,
                                          overwrite  = args.overwrite,
                                          )
            if jpg_path:
                message(f'{GREEN} ✓ Converted "{path}" → "{jpg_path.name}"{RESET}')

if __name__ == "__main__":
    main()
