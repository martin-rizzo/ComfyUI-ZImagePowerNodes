"""
File    : styles/style_group.py
Purpose : A class for managing and retrieving style templates based on their names.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""

class StyleGroup:
    """
    A group of style templates indexed by name.

    A class for managing and retrieving style templates based on their names.
    The indexation is case-insensitive and when indexing the names can be provided quoted or not.

    Args:
        category              (str): The category of the style group. Defaults to an empty string.
        version               (str): The version of the style group. Defaults to an empty string.
        styles        (dict | None): A dictionary mapping style names to their template. Defaults to None.
        ordered_names (list | None): The ordered list of style names. Defaults to None.

    Attributes:
        category (str): The category of the style group.
        version  (str): The version of the style group.
    """

    def __init__(self,
                 category     : str = "",
                 version      : str = "",
                 styles       : dict[str, str] | None = None,
                 ordered_names: list[str]      | None = None,
                 ):

        self.category = category
        self.version  = version
        self._templates_by_lowername = {}
        self._names_by_lowername     = {}
        self._ordered_names          = []

        # if no styles are provided then leave everything empty and do nothing
        if styles is None:
            return

        # if no ordered names are provided then add styles unordered from the dictionary
        if ordered_names is None:
            for name, template in styles.items():
                self.add_style(name, template)
            return

        # we have the ordered list of names then add styles in order
        for name in ordered_names:
            if name in styles:
                self.add_style(name, styles[name])


    @classmethod
    def from_string(cls,
                    string : str,
                    /,*,
                    category : str = "",
                    version  : str = "",
                    ) -> "StyleGroup":
        """
        Creates a StyleGroup instance from a string containing style definitions.

        Args:
            string   (str): The input string containing style definitions.
            category (str): The category of the style group. Defaults to an empty string.
            version  (str): The version of the style group. Defaults to an empty string.

        Returns:
            A new instance of `StyleGroup` parsed from the input string.
        """
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

    @staticmethod
    def apply_style_template(prompt        : str,
                             style_template: str,
                             /,*,
                             spicy_impact_booster: bool = False) -> str:
        """
        Applies a given style template to a prompt with optional spicy content boost.

        Args:
            prompt         (str): The input text prompt to be styled.
            style_template (str): The template style into which the prompt will be inserted.
                                  This is a string template that should contain "{$@}" and
                                  can be obtained with `style_group.get_style_template(name)`
            spicy_impact_booster (optional): If True, adds spicy content to the output. Default is False.

        Returns:
            The final styled prompt ready for use.
        """
        spicy_content = ""
        if spicy_impact_booster:
            spicy_content = "attractive and spicy content, where any woman is sexy and provocative, with"

        result = style_template
        result = result.replace("{$spicy-content-with}", spicy_content) #< the secret spicy dressing
        result = result.replace("{$@}"                 , prompt       ) #< prompt to be styled
        result = result.replace("  ", " ")                              #< fix double spaces
        return result



    def contains(self, name: str) -> bool:
        """Check whether the group contains a given style or not."""
        return name.lower() in self._templates_by_lowername


    def get_style_template(self, name: str, default: str = "") -> str:
        """Return the style template for a given name. If it doesn't exist, returns `default` or empty string."""
        name = name.strip()
        # the name can be quoted with single or double quotes
        if(  ( name.startswith("'") and name.endswith("'") )  or
             ( name.startswith('"') and name.endswith('"') )  ):
            name = name[1:-1]
        lowername = name.lower()
        return self._templates_by_lowername.get(lowername, default)


    def add_style(self, name: str, template: str):
        """Add a new style or update an existing one."""
        lowername = name.lower()
        # if the style already exists, then it is only updated
        if lowername in self._templates_by_lowername:
            self._templates_by_lowername[lowername] = template
            return
        # adds a new style
        self._templates_by_lowername[lowername] = template
        self._names_by_lowername[lowername] = name
        self._ordered_names.append(name)


    def remove_style(self, name: str):
        """Remove a style by its name."""
        lowername = name.lower()
        if lowername not in self._templates_by_lowername:
            return
        name = self._names_by_lowername[lowername] or name
        del self._templates_by_lowername[lowername]
        del self._names_by_lowername[lowername]
        self._ordered_names.remove(name)


    def update(self, style_group: "StyleGroup"):
        """Update this style group with another one."""
        for name in style_group.get_names():
            self.add_style(name, style_group.get_style_template(name))


    def get_names(self, /,*, quoted: bool | str = False) -> list[str]:
        """
        Returns a list of all style names.
        Args:
            quoted (optional):
                if True then each key is returned as a text with double quotes around it.
                if a string is passed then it's used as the quote char. Defaults to False.
        """
        if not quoted:
            return self._ordered_names
        quote_char = quoted if isinstance(quoted, str) else '"'
        return [ f'{quote_char}{x}{quote_char}' for x in self.get_names() ]


    def __getitem__(self, name: str):
        """Allow indexing by style name."""
        if not self.contains(name):
            raise KeyError(f"Style '{name}' not found.")
        return self.get_style_template(name)


    def __setitem__(self, name: str, template: str):
        """Allow setting a new style or updating an existing one using indexing."""
        self.add_style(name, template)


    def __delitem__(self, name):
        """Allow deleting a style by its name using the `del` keyword."""
        if not self.contains(name):
            raise KeyError(f"Style '{name}' not found.")
        self.remove_style(name)


    def __len__(self):
        """Return the number of styles."""
        return len(self._templates_by_lowername)


    def __contains__(self, name):
        """Check if a style exists by its name."""
        return self.contains(name)


    def __str__(self) -> str:
        return f"StyleGroup({len(self._templates_by_lowername)} styles)"

