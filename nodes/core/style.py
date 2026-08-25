"""
File    : style.py
Purpose : Core classes for working with visual styles.
           `Style`   : A class for storing information about a visual style.
           `StyleSet`: A container for storing multiple styles.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Apr 30, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
from __future__ import annotations
import re
import unicodedata
from   typing          import Iterator
from   collections.abc import KeysView
from   .palette        import Palette
from   .system         import logger
VersionTuple = tuple[int, int, int]
CommandTuple = tuple[str,str,str,str]

# Pattern used to remove non-alphanumeric characters.
_CLEAN_PATTERN = re.compile(r"[^a-z0-9_]")

# Pattern used to extract the command name from a string.
_COMMAND_NAME_PATTERN = re.compile(r'[a-zA-Z0-9.@*#+-]+')

# Pattern used to extract 'cheat-codes' from template or prompts.
_CHEATCODE_PATTERN = re.compile(r"[@*#+-]+")


# For undefined order, we use a tuple with two very high values.
_UNDEFINED_ORDER = (999_999, 999_999)



#=============================== Style CLASS ===============================#

class Style:
    """
    Represents a visual style with its name, template, description, and tags.

    Attributes:
        name        : The name of the style.
        template    : A string with the template to be injected into the prompt.
        description : A string with the description for the style.
        tags        : A string containing tags associated with the style.
        category    : A string with the category name to which this style belongs.
        version     : A string indicating the version to which this style belongs, e.g. "2.1.0"
        order       : An optional tuple used to determine the order of the styles;
                      This attribute is used internally by the `StyleSet` class
                      when sorting the styles and should not be set by the user.

    Properties:
        version_tuple : Returns the version as a tuple of three integers.
        quoted_name   : A string containing the style's name but surrounded by double quotes.
        slug          : A string with the slug version of the style's name for URL use.

    Example:
        >>> style = Style( "cinematic",
        ...     template    = "{$@}, rendered in epic cinematic lighting",
        ...     description = "Ultra-realistic blockbuster look",
        ...     tags        = "photoreal, movie, 8k",
        ...     category    = "photo",
        ...     version     = "1.0.0"
        ... )
        >>> style.quoted_name
        '"cinematic"'
    """
    def __init__(self,
                 name       : str,
                 *,
                 template   : str | list[str],
                 description: str                        = "",
                 tags       : str                        = "",
                 category   : str                        = "",
                 version    : str | VersionTuple         = (0, 0, 0),
                 order      : tuple[int, int]            = _UNDEFINED_ORDER,
                 ):
        self.name       : str             = name.strip()
        self.template   : str             = ""
        self.description: str             = description.strip()
        self.tags       : str             = tags.strip()
        self.category   : str             = category.strip()
        self.order      : tuple[int, int] = order
        self._versiontup: VersionTuple    = (0, 0, 0)

        # convert template to string if necessary
        if isinstance(template, str):
            self.template = template.strip()
        elif isinstance(template, (list,tuple)):
            self.template = "\n".join(template).strip()
        else:
            raise ValueError("Invalid template format. Expected a string or a list/tuple of strings.")

        # convert version to tuple if necessary
        if isinstance(version, str):
            self._versiontup = Style.make_version_tuple(version)
        elif isinstance(version, tuple) and len(version) == 3:
            self._versiontup = version
        else:
            raise ValueError("Invalid version format. Expected a string or a tuple of 3 integers.")

        # transform the template into easy-to-process commands
        self._commands = self._parse_commands(self.template)



    def apply_to_prompt(self,
                        prompt : str, *,
                        palette: Palette | None = None,
                        ) -> str:
        """
        Applies the style to a given prompt, optionally resolving palette variables
        and handling conditional cheat codes.

        Args:
            prompt : The input text prompt to be styled.
            palette: Optional `Palette` object used to resolve color-related variables
                     within the style template. If not provided, fallback values are used.

        Returns:
            A string containing the fully processed and styled prompt.
        """
        result    = []
        prompt    = prompt.strip()
        cheatcode = ""

        # extract any cheat-code from the user prompt
        if prompt.startswith("**"):
            match = _CHEATCODE_PATTERN.match(prompt, pos=2)
            if match:
                cheatcode = match.group()
                prompt    = prompt[match.end():]

        # process the template commands one by one
        for command in self._commands:
            command_name, command_extra, param1, param2 = command

            if command_name == "STR":
                result.append( param1 )

            elif command_name == "IFPAL":
                if palette: result.append( palette.resolve_variables( param1 ) )
                else      : result.append( param2 )

            elif command_name == "CHEAT":
                if command_extra in cheatcode: result.append( param1 )
                else                         : result.append( param2 )

            elif command_name == "PROMPT" or command_name == "@":
                result.append( param1 + prompt + param2 )

        return "".join(result)

    @property
    def version(self) -> str:
        """Returns the version formatted as a semantic version string 'X.Y.Z'."""
        return '.'.join(map(str, self._versiontup))

    @property
    def version_tuple(self) -> VersionTuple:
        """Returns the version as a tuple of three integers."""
        return self._versiontup

    @property
    def quoted_name(self) -> str:
        """A string containing the style's name but surrounded by double quotes."""
        return f'"{self.name}"'


    @property
    def slug(self) -> str:
        """A string with the slug version of the style's name for URL use."""
        return self.canonicalize_name(self.name)


    @staticmethod
    def canonicalize_name(name: str) -> str:
        """
        Normalize the style name.

        The transformation pipeline is:
          1. Return empty string immediately if the name is empty.
          2. Unicode NFD normalization removing diacritics such as accents, tildes, etc.
          3. Lower-case, strip surrounding whitespace.
          4. Replace spaces and hyphens with underscores.
          5. Remove quotation (`'`, `"`)
          6. Guard against null cases ("-", "none", empty string).
          7. Replace any remaining non-alphanumeric character with "x".

        Args:
            name: The style name to canonicalize.

        Returns:
            The canonicalized style name, that contains only lowercase ASCII
            letters, digits, and underscores; suitable for use in URLs, ids, etc;
            or empty string if the input name is invalid or empty.

        Examples:
            >>> Style.canonicalize_name("Cinematic Look")
            'cinematic_look'
            >>> Style.canonicalize_name("8k PHOTO STYLE")
            '8k_photo_style'
            >>> Style.canonicalize_name("Fotográfico")
            'fotografico'
            >>> Style.canonicalize_name("")
            ''
            >>> Style.canonicalize_name("None")
            ''
        """
        if not isinstance(name, str) or not name:
            return ""

        # step 1: unicode normalization
        # strip the combining marks to remove accents, tildes, etc.
        name = unicodedata.normalize("NFD", name)
        name = "".join(c for c in name if not unicodedata.combining(c))

        # step 2: case normalization, whitespace cleanup,
        # map spaces and hyphens to underscores, then drop quote characters
        name = name.lower().strip().replace(" ", "_").replace("-", "_")
        name = re.sub(r"['\"`]", "", name)

        # step 3: Reject invalid or null names.
        if name in ("", "-", "none", "null"):
            return ""

        # step 4: any character not in [a-z 0-9 _] becomes "x".
        return _CLEAN_PATTERN.sub("x", name)


    @staticmethod
    def make_version_tuple(version_str: str) -> VersionTuple:
        """
        Parses a version string into a tuple of three integers (major, minor, and patch).

        The version string can be in one of the following formats:
          - Compact format    : 'v20' or '81' which are interpreted as (2, 0, 0) and (8, 1, 0).
          - Traditional format: '2.0.4' or 'v8.1' which are interpreted as (2, 0, 4) and (8, 1, 0).
        The leading 'v' or 'V' character is optional and will be stripped from the string.

        Args:
            version_str (str): The version string to parse.
        Returns:
            VersionTuple: A tuple of three integers (X, Y, Z) representing
                          the major, minor, and patch versions.
                          Returns (0, 0, 0) if parsing fails.
        """
        if not isinstance(version_str, str) or not version_str:
            return (0, 0, 0)

        # remove leading 'v' or 'V' characters
        clean_str = version_str.strip().lstrip('vV')

        if '.' in clean_str:
            # split by '.' and convert to integers if possible
            # '1.2.3' -> ['1', '2', '3']
            digits = [int(p) for p in clean_str.split('.') if p.isdigit()]
        else:
            # for compact format, split into individual digits
            # '123' -> [1, 2, 3] || '92' -> [9, 2]
            digits = [int(char) for char in clean_str if char.isdigit()]

        # ensure there are at least three elements by padding with zeros and return
        digits = digits + [0, 0, 0]
        return (digits[0], digits[1], digits[2])


    @staticmethod
    def _extract_command_and_params(input_string: str, pos: int) -> tuple[int, str, str, str, str]:
        """
        Extract keyword and value using index pointers to minimize string allocations.

        Args:
            input_string : The source string to parse.
            index        : The starting position in the string.

        Returns:
            A tuple of (keyword, value).
        """
        command = ""
        params  = ["", ""]

        # Use re.finditer or match with pos to avoid slicing the input_string
        match = _COMMAND_NAME_PATTERN.match(input_string, pos=pos)
        if match:
            command = match.group()
            pos     = match.end()

        for idx in range(len(params)):

            # skip whitespaces if any
            while pos < len(input_string) and input_string[pos].isspace():
                pos += 1

            if pos >= len(input_string):
                break

            first_char = input_string[pos]

            # if end-of-comand is reached, break the parameter loop
            if first_char == '}':
                pos += 1
                break

            # if end-of-param is reached, the parameter is empty
            elif first_char == '|':
                pos += 1
                continue

            # if the param starts with quotes, extract everything enclosed in quotes
            elif first_char in ('"', "'"):
                quote_char = first_char
                end_pos    = input_string.find(quote_char, pos+1)
                if end_pos == -1:
                    raise ValueError(f"Missing closing quotes: {quote_char}")
                params[idx] = input_string[pos+1:end_pos]
                pos  = end_pos+1

            # if the parameter is not quoted, extract until the first pipe "|" or "}"
            else:
                endparam   = input_string.find('|', pos)
                endcommand = input_string.find('}', pos)
                end_pos = min( endparam if endparam>=0 else 99999, endcommand if endcommand>=0 else 99999 )
                if end_pos == 99999:
                    raise ValueError(f"Could not find end of parameter in IFPAL template tag")
                params[idx] = input_string[pos:end_pos].strip()
                pos = end_pos+1
                if end_pos == endcommand:
                    break

        command_name, _, command_extra = command.partition('.')
        return pos, command_name.upper(), command_extra, params[0], params[1]


    @staticmethod
    def _parse_commands(input_text: str) -> list[CommandTuple]:
        """
        Parses a string into a list of tuples, distinguishing between command blocks 
        and plain text segments.

        Args:
            input_text : The raw string containing text and command patterns '{$...}'.

        Returns:
            A list of tuples:
            - If command: ('COMMAND_NAME', 'param1', 'param2') 
            (Note: for now, keeping the inner content as the command name).
            - If plain text: ('TEXT', 'actual text segment', '')
        """
        pos = 0
        commands: list[CommandTuple] = []
        while True:

            # find the next command, break the loop if no command found
            command_pos = input_text.find("{$", pos)
            if command_pos<0:
                break

            # command found!
            # add as simple "STRING" everything that's there until the beginning of the command
            if command_pos>pos:
                commands.append(( "STR", "", input_text[pos:command_pos], "" ))
                pos = command_pos

            # extract the whole information of the command,
            end_pos, command_name, command_extra, param1, param2 = Style._extract_command_and_params(input_text, pos+2)

            # convert abreviated forms into valid commands
            if command_name == "@":
                command_name, command_extra  = "PROMPT", ""
            elif command_name.startswith("**"):
                command_name, command_extra = "CHEAT", command_name[2:]

            # but if it is not recognized as a command then add it as simple "STRING"
            if not command_name in ("@", "IFPAL", "CHEAT", "PROMPT"):
                logger.debug(f"Invalid command '({command_name})' in style template")
                commands.append(( "STR", "", input_text[pos:end_pos], "" ))
                pos = end_pos
                continue

            # finally add the found command and advance
            commands.append(( command_name, command_extra, param1, param2 ))
            pos = end_pos


        # add any remaining text as a simple "STRING"
        if pos<len(input_text):
            commands.append(( "STR", "", input_text[pos:], "" ))

        return commands


    def __repr__(self) -> str:
        """Return an unambiguous string representation of the Style instance that can be used to recreate it."""
        return (
            f"Style({self.name!r}, "
            f"template={self.template!r}, "
            f"description={self.description!r}, "
            f"tags={self.tags!r}, "
            f"version={self.version!r})"
        )


#============================= StyleSet CLASS ==============================#

class StyleSet:
    """
    A class representing a set of visual styles.
    """

    # Order for categories, lower values come first.
    # (unlisted categories will be placed after these, order = 999)
    CATEGORY_SORT_ORDER = {
        "photo"       : 0,
        "illustration": 1,
        "wild"        : 2
    }

    def __init__(self,
                 styles: StyleSet | None = None,
                 ) -> None:
        """
        Initialize the StyleSet with an optional dictionary of styles.

        Args:
            styles: An optional StyleSet instance to copy from,
                    or None to start with an empty set.
        """
        self._styles_by_canonical: dict[str, Style]   = {}
        self._sorted_list        : list[Style] | None = None
        self._sequence_index     : int                = 0

        if styles is None:
            pass

        elif isinstance(styles, StyleSet):
            # copy the internal dictionary directly (it always is canonicalized)
            self._styles_by_canonical = dict(styles._styles_by_canonical)
            self._sorted_list         = list(styles._sorted_list) if styles._sorted_list is not None else None

        else:
            raise TypeError("Invalid type for styles argument.")


    @property
    def sorted_list(self) -> list[Style]:
        """
        Returns a list of styles sorted by its order property.
        """
        if  self._sorted_list is None:
            self._sorted_list = sorted(
                self._styles_by_canonical.values(),
                key = lambda style: style.order
                )
        return self._sorted_list


    @classmethod
    def from_string(cls,
                    string  : str | list[str],
                    category: str                = "",
                    version : str | VersionTuple = (0,0,0),
                    ) -> StyleSet:
        """
        Create a new StyleSet instance from a multi-line string containing style definitions.

        Args:
           string: A multi-line string containing style definitions.
        Returns:
           A new `StyleSet` instance with styles loaded from the provided string.
        """
        style_set = cls()
        style_set.add_styles_from_string(string, category=category, version=version)
        return style_set


    def add_styles_from_string(self,
                               string : str | list[str],
                               /,*,
                               category: str                = "",
                               version : str | VersionTuple = (0,0,0),
                               ) -> int:
        """
        Parses style definitions from a multi-line string and adds them into the style set.

        This method scans the input string for special marker prefixes that
        delimit style definitions.

        Marker Reference:
            ">>>" - Style definition marker.
                    Indicates the start of a new style. Everything that follows
                    (lines, blank lines, etc.) belongs to this style's definition
                    until another style marker is encountered.
                    The text immediately after ">>>" becomes the style name.
                    Example: ">>>Minimalist Dark" -> creates a style named "Minimalist Dark"
            ">##" - Comment/Metadata marker.
                    All lines that start with ">##" are treated as comments unless
                    they contain a metadata definition (e.g., @DESCRIPTION).
            "@"   - File identifier (must be the first line of the input string).
                    The identifier line is ignored during parsing.
                    Example: "@STYLES"

        Automatic Fallback Behavior:
            If the input string contains NO ">>>" markers, the entire string is
            treated as a single style called "Custom 1".

        Args:
            string   : The input string (or list of lines) containing style definitions.
            category : The default category to assign to styles if not specified.
            version  : Default version assigned to styles that do not specify one.

        Returns:
            The total number of styles that were successfully parsed and added
            to the style set. Returns 0 if the string was empty or contained
            no valid style definitions.

        Example:
            >>> input_string = '''
            ... @STYLES
            ...
            ... >>>Phone Photo
            ... Your photographs has android phone cam-quality.
            ... YOUR PHOTO: {$@}
            ...
            ... >>>Selfie
            ... The subject takes a selfie with their limb outstretched.
            ... THE SELFIE: {$@}
            ... '''
            >>> style_set = StyleSet()
            >>> count = style_set.add_styles_from_string(input_string)
            # Adds 2 styles: "Phone Photo" and "Selfie"
        """
        all_lines = string.strip().splitlines() if isinstance(string,str) else string

        # skip file identifier line if present (must be the first line)
        if all_lines and all_lines[0].startswith("#!"):
            all_lines.pop(0)

        # if the input string does not contain any explicit style definitions (>>>),
        # it is assumed to be plain text and automatically assigned to a default
        # style "Custom 1".
        if not any(line.startswith(">>>") for line in all_lines):
            all_lines.insert(0, ">>>Custom 1")

        # add sentinel element to force processing of last style
        all_lines.append(">>>EOF")

        load_count      : int                = 0
        pending_marker  : str                = ""
        pending_content : list[str]          = []
        pending_desc    : str                = ""
        pending_tags    : str                = ""
        pending_category: str                = category
        pending_version : str | VersionTuple = version

        for line in all_lines:
            line = line.rstrip()  #< trailing whitespaces are lost at the end of each line

            # if the line is a comment:
            #   - if the comment starts with '@', attempt to extract the parameter
            #   - otherwise, skip the line completely
            if line.startswith(">##"):
                comment = line[3:].strip()
                if comment.startswith("@"):
                    param, _, value = line[3:].partition(":")
                    param = param.strip().upper()
                    value = value.strip()
                    if   param == "@DESCRIPTION": pending_desc     = value
                    elif param == "@DESC"       : pending_desc     = value
                    elif param == "@TAGS"       : pending_tags     = value
                    elif param == "@CATEGORY"   : pending_category = value
                    elif param == "@VERSION"    : pending_version  = value

            # when a new style marker is detected,
            # the previous pending style/content must be processed
            elif line.startswith(">>>"):
                if pending_marker:
                    style = Style(pending_marker[3:],
                                  template    = pending_content,
                                  description = pending_desc,
                                  tags        = pending_tags,
                                  category    = pending_category,
                                  version     = pending_version)
                    if self.add_style(style):
                        load_count += 1

                # reset values to default
                pending_marker   = line
                pending_content  = []
                pending_desc     = ""
                pending_tags     = ""
                pending_category = category
                pending_version  = version

            # the line does not contain any marker,
            # it is text that must be added to the pending content
            else:
                pending_content.append(line)

        return load_count


    def add_style(self, style: Style) -> bool:
        """
        Adds a new Style object to the set.

        The style is indexed by its canonical name internally.
        If the canonical name is empty (invalid style name), the style is silently rejected.

        Args:
            style: The `Style` object to be added.
        Returns:
            True if the style was added, False otherwise.
        """
        canonical_name = Style.canonicalize_name(style.name)
        # reject styles with invalid names or with empty templates
        if not canonical_name or not style.template:
            return False

        # retrieve the order assigned to the style category (defaults to 999)
        category_order = self.CATEGORY_SORT_ORDER.get(style.category, 999)

        # style.order is a tuple = (category_order, sequence_index)
        # this ensures that styles are grouped by category first,
        # and then sorted by their addition time
        if style.order == _UNDEFINED_ORDER:
            style.order = (category_order, self._sequence_index)
        self._styles_by_canonical[canonical_name] = style

        # reset sorted list cache and increment the sequence index
        self._sorted_list = None
        self._sequence_index += 1
        return True


    def get(self, style_name: str, default: Style | None = None) -> Style | None:
        """
        Retrieves a style by name, returning a default value if not found.

        This is a safe alternative to indexing with [] that won't raise a
        KeyError when the style name is missing.

        Args:
            style_name: The name of the style to retrieve.
            default   : Optional value to return if the style is not found.
        Returns:
            The `Style` object if found, otherwise the default value of None.

        Example:
            >>> # Get a non-existing style with default (returns default)
            >>> default_style = Style("fallback")
            >>> style_set = StyleSet()
            >>> style = style_set.get("nonexistent", default_style)
            >>> style.name
            'fallback'
            >>>
            >>> # Get a non-existing style without default (returns None)
            >>> result = style_set.get("nonexistent")
            >>> result is None
            True
        """
        canonical_name = Style.canonicalize_name(style_name)
        if not canonical_name:
            return default
        return self._styles_by_canonical.get(canonical_name, default)


    def by_version(self, version: str | VersionTuple) -> StyleSet:
        """
        Returns a StyleSet that contains every style tagged with `version`.

        Args:
            version: A semantic version string such as "1.0.0".
        Returns:
            A `StyleSet` instance holding styles for the given version.
            If no such version exists, an empty `StyleSet` is returned.
        """
        version_tuple = Style.make_version_tuple(version) if isinstance(version, str) else version
        styles = StyleSet()
        for style in self._styles_by_canonical.values():
            if style.version_tuple == version_tuple:
                styles.add_style(style)
        return styles


    def by_category(self, category: str) -> StyleSet:
        """
        Returns a StyleSet that contains every style with the specified category.

        Args:
            category: The category string used to filter styles.
        Returns:
            A `StyleSet` instance holding styles for the given category.
            If no such category exists, an empty `StyleSet` is returned.
        """
        styles = StyleSet()
        for style in self._styles_by_canonical.values():
            if style.category == category:
                styles.add_style(style)
        return styles


    def names(self) -> list[str]:
        """
        Return a list of all style names stored in the set.

        Returns:
            A list of style names sorted by the style order attribute.

        Example:
            >>> for name in style_set.names():
            ...     print(name)
        """
        return [style.name for style in self.sorted_list]


    def quoted_names(self) -> list[str]:
        """
        Return a list of all quoted style names stored in the set.

        Returns:
            A list of quoted style names sorted by the style order attribute.

        Example:
            >>> for quoted_name in style_set.quoted_names():
            ...     print(quoted_name)
        """
        return [style.quoted_name for style in self.sorted_list]


    def canonical_names(self) -> KeysView[str]:
        """
        Return a dynamic view of all canonical style names stored in the set.

        Canonical names are normalized versions of the style names.
        They are converted to lowercase with:
          - spaces replaced by underscores
          - accent marks removed
          - rare characters converted to 'x'

        Important:
            The returned view is **NOT** sorted by style order attribute.

        Returns:
            A view object containing all canonical style names.

        Example:
            >>> for canonical_name in style_set.canonical_names():
            ...     print(canonical_name)
        """
        return self._styles_by_canonical.keys()


    def categories(self) -> list[str]:
        """
        Returns a list of all categories of the styles stored in the set.
        """
        # get unique categories
        unique_cats = {style.category for style in self._styles_by_canonical.values()}

        # sort using the CATEGORY_SORT_ORDER map,
        # default 999 ensures unlisted categories appear at the end.
        return sorted(
            unique_cats,
            key=lambda c: (self.CATEGORY_SORT_ORDER.get(c, 999), c)
        )


    def __getitem__(self, style_name: str) -> Style:
        """
        Enables access to a specific style by its name.

        The input name is canonicalized before lookup.
        Example usage: `style_set["cinematic_look"]`
        """
        canonical_name = Style.canonicalize_name(style_name)
        return self._styles_by_canonical[canonical_name]


    def __delitem__(self, style_name: str) -> None:
        """
        Removes a style from the set by its name.

        The input name is canonicalized before deletion.
        Example usage: `del style_set["cinematic_look"]`
        """
        canonical_name = Style.canonicalize_name(style_name)
        del self._styles_by_canonical[canonical_name]


    def __contains__(self, style_name: str) -> bool:
        """
        Checks if a specific style exists in the set.

        The input name is canonicalized before checking.
        Example usage: `"oil_painting" in style_set`
        """
        canonical_name = Style.canonicalize_name(style_name)
        return canonical_name in self._styles_by_canonical


    def __len__(self) -> int:
        """
        Returns the number of styles currently stored in the set.

        Example usage: `len(style_set)`
        """
        return len(self._styles_by_canonical)


    def __iter__(self) -> Iterator[Style]:
        """
        Allows iteration over the Style objects within this set.

        Example usage: `for style in style_set:`
        """
        return iter(self.sorted_list)


    def __repr__(self) -> str:
        """
        Provides a string representation of the StyleSet instance.
        """
        return f"StyleSet(styles={list(self._styles_by_canonical.keys())})"


#================================= HELPERS =================================#

def remove_style_from_text(text: str, name: str) -> str:
    """
    Removes a style definition from the given text.

    Args:
        text: The original text containing multiple style definitions.
        name: The name of the style to be removed.

    Returns:
        The modified text with the specified style removed.
    """
    name_to_find = Style.canonicalize_name(name)
    if not name_to_find:
        return text

    lines = text.splitlines()

    # find the beginning of the style definition
    start = None
    for i, line in enumerate(lines):
        if line.startswith(">>>") and Style.canonicalize_name(line[3:]) == name_to_find:
            start = i
            break
    else:
        return text #<< loop finished without break: name not found

    # find the end of the style definition
    end = None
    for i, line in enumerate(lines[start + 1:], start=start + 1):
        if line.startswith((">>>", ">::", "{#")):
            end = i
            break

    # remove the style block (inclusive start, exclusive end)
    kept_lines = lines[:start] if end is None else lines[:start] + lines[end:]
    return "\n".join(kept_lines)


def append_style_to_text(text: str, name: str, template: str) -> str:
    """
    Appends a style definition to the given text.
    Args:
        text    : The original text to which the style will be added.
        name    : The name of the new style.
        template: The content defining the new style.
    Returns:
        The modified text with the new style appended.
    """
    return f"{text}>>>{name}\n{template}\n\n\n"



