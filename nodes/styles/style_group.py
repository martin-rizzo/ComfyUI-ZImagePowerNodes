"""
File    : styles/base.py
Purpose : The base class and functions for styles handling.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""


def apply_style_to_prompt(prompt: str,
                          style : str,
                          /,*,
                          spicy_impact_booster: bool = False) -> str:
    """
    Applies a given style to a prompt with optional spicy content boost.

    Args:
        prompt (str): The input text prompt to be styled.
        style  (str): The template style into which the prompt will be inserted.
        spicy_impact_booster (optional): If True, adds spicy content to the output. Default is False.

    Returns:
        The final styled prompt ready for use.
    """
    spicy_content = ""
    if spicy_impact_booster:
        spicy_content = "attractive and spicy content, where any woman is sexy and provocative, with"

    result = style
    result = result.replace("{$spicy-content-with}", spicy_content) #< the secret spicy dressing
    result = result.replace("{$@}"                 , prompt       ) #< prompt to be styled
    result = result.replace("  ", " ")                              #< fix double spaces
    return result



class StyleGroup:

    def __init__(self,
                 styles       : dict[str, str] | None = None,
                 ordered_names: list[str] | None      = None,
                 category     : str                   = "",
                 version      : str                   = "",
                 ):

        self.category = category
        self.version  = version

        if styles is None:
            self._styles       = {}
            self._ordered_keys = []
            return

        if ordered_names is None:
            self._styles       = styles.copy()
            self._ordered_keys = list(styles.keys())
            return

        for name in ordered_names:
            if (name not in styles) or (name in self._styles):
                continue
            self._styles[name] = styles[name]
            self._ordered_keys.append(name)


    @classmethod
    def from_string(cls,
                    string   : str, /,*,
                    category : str = "",
                    version  : str = "",
                    ) -> "StyleGroup":
        style_group = StyleGroup(category=category, version=version)
        action  = None
        content = ""

        is_first_line = True
        for line in string.splitlines():
            is_shebang_line = is_first_line and line.startswith("#!")
            is_first_line   = False

            line = line.rstrip() #< trailing whitespaces are lost at the end of each line
            if ( is_shebang_line        or #< sheban "#!ZCONFIG"        (compatibility with Amazing Z-Image Workflow)
                 line.startswith("{#")  or #< variable definition       (compatibility with Amazing Z-Image Workflow)
                 line.startswith(">::") or #< action to modify workflow (compatibility with Amazing Z-Image Workflow)
                 line.startswith(">>>")    #< style definition !!
               ):
                # a new action is detected, so the previous pending one is processed
                if action and action.startswith(">>>"):
                    style_name = action[3:].strip()
                    style_group.add_style(style_name, content.strip())

                # the new action is stored as pending
                action, content = line, ""
            else:
                content += line + "\n"

        # before ending, process any pending action
        if action and action.startswith(">>>"):
            style_name = action[3:].strip()
            style_group.add_style(style_name, content.strip())

        return style_group


    def get_style(self, name: str, default: str = "") -> str:
        """Return the style content for a given name. If it doesn't exist, returns `default` or empty string."""
        # the name can be quoted with single or double quotes
        if(  ( name.startswith("'") and name.endswith("'") )  or
             ( name.startswith('"') and name.endswith('"') )  ):
            name = name[1:-1]
        return self._styles.get(name, default)


    def add_style(self, name, style_value):
        """Add a new style or update an existing one."""
        if name not in self._styles:
            self._ordered_keys.append(name)
        self._styles[name] = style_value


    def remove_style(self, name):
        """Remove a style by its name."""
        if name in self._styles:
            del self._styles[name]
            self._ordered_keys.remove(name)


    def get_names(self, /,*, quoted: bool | str = False) -> list[str]:
        """Return all keys in the order they were added.
        Args:
            quoted (optional):
                if True then each key is returned as a text with double quotes around it.
                if a string is passed then it's used as the quote char. Defaults to False.
        """
        if not quoted:
            return self._ordered_keys

        quote_char = quoted if isinstance(quoted, str) else '"'
        result = []
        for name in self.get_names():
            result.append(f'{quote_char}{name}{quote_char}')
        return result


    def __getitem__(self, key):
        """Allow indexing by style name."""
        if key not in self._styles:
            raise KeyError(f"Style '{key}' not found.")
        return self._styles[key]


    def __setitem__(self, key, value):
        """Allow setting a new style or updating an existing one using indexing."""
        self.add_style(key, value)


    def __delitem__(self, key):
        """Allow deleting a style by its name using the del keyword."""
        if key in self._styles:
            del self[key]
        else:
            raise KeyError(f"Style '{key}' not found.")


    def __len__(self):
        """Return the number of styles."""
        return len(self._styles)


    def __contains__(self, key):
        """Check if a style exists by its name."""
        return key in self._styles


