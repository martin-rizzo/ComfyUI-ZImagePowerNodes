
def apply_style_to_prompt(prompt: str,
                          style : str,
                          /,*,
                          spicy_impact_booster: False) -> str:
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



class Styles:

    def __init__(self, styles: dict[str, str] = None, ordered_names: list[str] = None, ):

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
    def from_config(cls, config: str) -> "Styles":
        styles  = Styles()
        action  = None
        content = ""

        is_first_line = True
        for line in config.splitlines():
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
                    styles.add_style(style_name, content.strip())

                # the new action is stored as pending
                action, content = line, ""
            else:
                content += line + "\n"

        return styles


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


    def get_style_names(self):
        """Return all keys in the order they were added."""
        return self._ordered_keys


    def get(self, name, default=None):
        """Return the style content for a given name. If it doesn't exist, returns default."""
        return self._styles.get(name, default)


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


