"""
File    : predefined_styles.py
Purpose : Provides access to all predefined styles through the `PREDEFINED_STYLES` object
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Apr 30, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
from pathlib     import Path
from collections import defaultdict
from .style      import Style, StyleSet


#============================== StyleLibrary ===============================#
#             this class represents the full style library                  #

class StyleLibrary:
    """
    A central repository that stores every registered Style object.

    Styles are internally grouped by version, and callers can obtain a `StyleSet`
    that contains only targets belonging to a specific release.
    """
    def __init__(self) -> None:
        self._styles_by_version: dict[tuple[int,int,int], StyleSet] = defaultdict(StyleSet)


    def load_from_directory(self,
                            directory: Path | str
                            ) -> tuple[int, int]:
        """
        Load style definitions from all compatible files within a directory.

        This method scans the specified directory for text files whose names
        follow the naming convention `styles_<version>_<category>.txt` (e.g.,
        "styles_v1_illustration.txt"). Each matching file is parsed and its
        styles are added to the library under the extracted category and version.

        Args:
            directory: Path to the directory containing style definition files.
                       Can be a `str` or `pathlib.Path`.
        Returns:
            A tuple containing:
                - The number of files that were successfully processed.
                - The total number of styles loaded from those files.
        """
        # force `directory` to be a path
        if isinstance(directory, str):
            directory = Path(directory)

        # recorrer todos los archivos que hay dentro del directorio
        num_loaded_files  = 0
        num_loaded_styles = 0
        for file_path in directory.iterdir():

            # only files whose names have a format like "styles_*.txt"
            if file_path.suffix != ".txt":
                continue
            name_parts = file_path.stem.replace('_',' ').replace('.',' ').split()
            if len(name_parts) != 3 or name_parts[0] != 'styles':
                continue

            # extract version and category from the file name
            version  = _normalize_version( name_parts[1].strip() )
            category = name_parts[2].strip()
            if version and category:
                num_loaded_files  += 1
                num_loaded_styles += self.load_from_string(file_path.read_text(encoding='utf-8'),
                                                           category = category,
                                                           version  = version)
        return num_loaded_files, num_loaded_styles



    def load_from_string(self,
                         string : str,
                         /,*,
                         category : str                  = "",
                         version  : str | tuple[int,...] = "0.0.0",
                         ) -> int:
        """
        Loads style definitions from a string into the style library.

        For more information about the input string format,
        refer to `StyleSet.load_from_string()`.

        Args:
            string  : The input string containing style definitions to be loaded.
            category: Default category assigned to styles that do not specify one.
            version : Default version string assigned to styles that do not specify one.

        Returns:
            The total number of styles that were successfully parsed and added to
            the style set. Returns 0 if the string was empty or contained markers
            not related to style definitions.
        """
        styles = StyleSet.from_string(string, category=category, version=version)
        return self.add_many_styles( styles )


    def add_style(self, style: Style) -> bool:
        """Add a Style into the library."""
        return self._styles_by_version[style.version].add_style(style)


    def add_many_styles(self, styles: StyleSet | list[Style]) -> int:
        """Convenience wrapper to bulk-register styles.
        Args:
            styles: Iterable of Style objects to be stored.
        Returns:
            The number of styles successfully added.
        """
        added_count = 0
        for style in styles:
            if self.add_style(style):
                added_count += 1
        return added_count


    def by_version(self, version: str | tuple[int,int,int]) -> StyleSet:
        """Returns a StyleSet that contains every style tagged with `version`.
        Args:
            version: A semantic version string such as "1.0.0".
        Returns:
            A `StyleSet` instance holding styles for the given version.
            If no such version exists, an empty `StyleSet` is returned.
        """
        normalized_version = Style.normalize_version(version)
        if normalized_version not in self._styles_by_version:
            return StyleSet()
        return self._styles_by_version[normalized_version]



    def versions(self) -> list[str]:
        """Returns all versions currently represented inside the library.
        Returns:
            A list of all versions currently represented inside the library.
        """
        return [".".join(map(str, version)) for version in self._styles_by_version.keys()]


    def __len__(self) -> int:
        """Returns the number of styles currently stored inside the library."""
        return sum( len(styles) for styles in self._styles_by_version.values() )



    def __repr__(self) -> str:
        return (
            f"StyleLibrary(versions={len(self._styles_by_version)}, total_styles={len(self)})"
        )



#================================= HELPERS =================================#

def _normalize_version(version_str: str) -> str:
    """
    Convert a compact version string to standard semver format (X.Y.Z).

    Args:
        version_str: A string starting with 'v' followed by digits.
                     Examples: 'v08', 'v1', 'v201', 'V42'
    Returns:
        A version string with exactly 3 components, padded with zeros if needed.
        Examples: '0.8.0', '1.0.0', '2.0.1', '4.2.0'
        Returns an empty string if the input doesn't start with 'v' or 'V'.
    """
    # Return empty string if it doesn't start with 'v' or 'V'
    if not version_str or (version_str[0] != 'v' and version_str[0] != 'V'):
        return ''

    # remove the leading 'v' (case insensitive)
    version_part = version_str.lstrip('vV')

    # extract all digits from the remaining string
    # and pad with zeros to ensure exactly 3 components
    digits = [c for c in version_part if c.isdigit()]
    if len(digits) < 3:
        digits.extend(['0', '0', '0'])

    # take only the first 3 digits
    return '.'.join(digits[:3])


#======================= 'PREDEFINED_STYLES' OBJECT ========================#

from typing import Final
from .helpers import get_project_root

PREDEFINED_STYLES: Final = StyleLibrary()
PREDEFINED_STYLES.load_from_directory( get_project_root() / "styles" )

