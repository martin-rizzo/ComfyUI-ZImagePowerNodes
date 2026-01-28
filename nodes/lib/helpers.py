"""
File    : helpers.py
Purpose : Helpers functions
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 24, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import re
import time
import torch


def ireplace(text: str, old: str, new: str, count: int = 0) -> str:
    """
    Replaces occurrences of a substring in a case-insensitive manner.

    Args:
        text : The original string.
        old  : The substring to be replaced.
        new  : The replacement substring.
        count (optional): Maximum number of replacements.
                          Defaults to 0, which means replace all occurrences.

    Returns:
        A copy of the original string with specified replacements made.
    """
    pattern = re.compile(re.escape(old), re.IGNORECASE)
    return pattern.sub(new, text, count=count)



def expand_date_and_vars(string: str,
                         /,*,
                         vars: dict[str,str] = {}
                         ) -> str:
    """
    Expands date variables and substitutes user-defined variables in a string.

    ### Variable Syntax
    Variables must be enclosed in percentage signs (`%variable_name%`).
      - If the content between `%` contains spaces, it will be treated as literal text and not as a variable.
      - To include a literal percentage sign, use `%%`.

    ### Supported Time Variables (Case-Insensitive)
      - `%year%`   : Current year (e.g., 2023)
      - `%month%`  : Current month with two digits (01-12)
      - `%day%`    : Current day with two digits (01-31)
      - `%hour%`   : Current hour in 24-hour format (00-23)
      - `%minute%` : Current minute (00-59)
      - `%second%` : Current second (00-59)

    ### Custom Date Format
    You can use the `date:` prefix followed by a specific format: `%date:FORMAT%`.
    Within the format, the following tokens are substituted:
      - `yyyy` : Year with 4 digits (e.g., 2023)
      - `yy`   : Year with 2 digits (e.g., 23)
      - `MM`   : Month with two digits (01-12) - **Case-Sensitive**
      - `dd`   : Day with two digits (01-31)
      - `hh`   : Hour with two digits (00-23)
      - `mm`   : Minute with two digits (00-59) - **Case-Sensitive**
      - `ss`   : Second with two digits (00-59)

    *Note: `MM` and `mm` distinguish between month and minute respectively.*

    ### User Variables
    Any key present in the `vars` dictionary will be substituted with its value.
    User values are limited to the first 16 characters.

    Args:
        string         : The input string containing potential variable names.
        vars (optional): A dictionary of custom variable name-value pairs.
                         Defaults to an empty dictionary.

    Returns:
        The expanded and substituted string with all recognized variables replaced by their values.
    """
    now: time.struct_time = time.localtime()

    def get_var_value(name: str) -> str | None:
            """Returns the value for a given variable name or None if the variable name is not defined."""
            case_name = name
            name      = case_name.lower()
            if name == "":
                return "%"
            # try to resolve time variables
            elif name == "year"  : return str(now.tm_year)
            elif name == "month" : return str(now.tm_mon ).zfill(2)
            elif name == "day"   : return str(now.tm_mday).zfill(2)
            elif name == "hour"  : return str(now.tm_hour).zfill(2)
            elif name == "minute": return str(now.tm_min ).zfill(2)
            elif name == "second": return str(now.tm_sec ).zfill(2)
            # try to resolve full date variable
            elif name.startswith("date:"):
                value = case_name[5:]
                value = ireplace(value, "yyyy", str(now.tm_year))
                value = ireplace(value, "yy"  , str(now.tm_year)[-2:])
                value = value.replace(  "MM"  , str(now.tm_mon ).zfill(2))
                value = ireplace(value, "dd"  , str(now.tm_mday).zfill(2))
                value = ireplace(value, "hh"  , str(now.tm_hour).zfill(2))
                value = value.replace(  "mm"  , str(now.tm_min ).zfill(2))
                value = ireplace(value, "ss"  , str(now.tm_sec ).zfill(2))
                return value
            elif name in vars:
               value = str(vars[name])[:16]
            return None

    output = ""
    next_token_is_var = False
    for token in string.split("%"):
        current_token_is_var = next_token_is_var
        last_token_was_text  = current_token_is_var

        # if the token contains spaces then it's not a variable name
        if ' ' in token:
            current_token_is_var = False

        var_value = get_var_value(token) if current_token_is_var else None
        if var_value is not None:
            # current token is a variable and the next token is text
            output += var_value
            next_token_is_var = False
        else:
            # current token is text, and the next token could be a variable
            output += ("%" if last_token_was_text else "") + token
            next_token_is_var = True

    return output



def normalize_images(images: torch.Tensor,
                     /,*,
                     max_channels  : int        = 3,
                     max_batch_size: int | None = None,
                     ) -> torch.Tensor:
    """
    Normalizes a batch of images to default ComfyUI format.

    This function ensures that the input image tensor has a consistent shape
    of [batch_size, height, width, channels].

    Args:
        images           (Tensor): A tensor representing a batch of images.
        max_channels   (optional): The maximum number of color channels allowed. Defaults to 3.
        max_batch_size (optional): The maximum batch size allowed. Defaults to None (no limit).
    Returns:
        A normalized image tensor with shape [batch_size, height, width, channels].
    """
    images_dimension = len(images.shape)

    # if 'images' is a single image, add a batch_size dimension to it
    if images_dimension == 3:
        images = images.unsqueeze(0)

    # if 'images' has more than 4 dimensions,
    # colapse the extra dimensions into the batch_size dimension
    if images_dimension > 4:
        images = images.reshape(-1, *images.shape[-3:])

    # limit the number of color channels to 'max_channels'
    if isinstance(max_channels,int) and images.shape[-1] > max_channels:
        images = images[ : , : , : , 0:max_channels ]

    # limit the number of batch elements to 'max_batch_size'
    if isinstance(max_batch_size,int) and images.shape[0] > max_batch_size:
        images = images[ 0:max_batch_size , : , : , : ]

    return images

