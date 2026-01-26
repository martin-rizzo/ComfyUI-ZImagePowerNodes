"""
File    : core/system.py
Purpose : System-level functions for the ComfyUI-ZImagePowerNodes project.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import sys
import logging
# ANSI colors
_GREEN     = "\033[0;32m"
_BLUE      = "\033[0;34m"
_YELLOW    = "\033[0;33m"
_RED       = "\033[0;31m"
_LIGHT_RED = "\033[1;31m"
_RESET     = "\033[0m"   # reset to default color

class _CustomFormatter(logging.Formatter):
    """Custom formatter for the logger."""
    EMOJI      : str = "\U0001F4AA"  # emoji shown before the log message
    NAME_COLOR : str = _YELLOW       # logger name color
    LEVEL_COLORS = {
        logging.INFO    : _GREEN,
        logging.DEBUG   : _BLUE,
        logging.WARNING : _YELLOW,
        logging.ERROR   : _RED,
        logging.CRITICAL: _LIGHT_RED,
    }

    def format(self, record):
        """Override the default format method."""
        # set color based on the log level and add an emoji before the logger name
        level_color = self.LEVEL_COLORS.get(record.levelno, _RESET)
        record.name      = f"{self.EMOJI}{self.NAME_COLOR}{record.name}{_RESET}"
        record.levelname = f"{level_color}{record.levelname}{_RESET}"
        return super().format(record)


#====================== THE MAIN Z-IMAGE NODES LOGGER ======================#

logger: logging.Logger = logging.getLogger()

def setup_logger(name      : str,
                 emoji     : str,
                 log_level : str  = "INFO",
                 use_stdout: bool = False
                 ):
    global logger
    if logger is not None:
        logger.warning("Logger already set up. Skipping setup_logger().")

    logger = logging.getLogger(name)
    logger.propagate = False
    if not logger.handlers:
        formatter = _CustomFormatter("[%(name)s %(levelname)s] %(message)s")
        formatter.EMOJI = emoji

        handler = logging.StreamHandler(sys.stdout if use_stdout else sys.stderr)
        handler.setFormatter( formatter )
        logger.addHandler(handler)

    logger.setLevel(log_level)
    if log_level=="DEBUG" or log_level==logging.DEBUG:
        logger.debug("Debug logging enabled.")

