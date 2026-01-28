# Style String Injector
![text](/docs/style_string_injector.jpg)

Injects a selected style into your prompt. This node takes an input string containing
the raw prompt (composition, characters, etc.) and modifies it with the chosen style.

## Inputs

### string
Through this connection, provide the plain text of your prompt, including composition,
characters, or other details, without specifying any particular style.

### category
The category of the style you want to apply. Changing this option updates the list of
available styles in `style_to_apply` to show only those that match.
Currently, there are 4 categories:
  * __photo__       : Contains photographic and realistic styles
  * __illustration__: Contains illustration, drawing, comic, anime, etc.
  * __other__       : Styles that don't fit into the previous groups
  * __custom__      : Free styles for user configuration

### style
Selects the desired style to inject or "none" if you prefer the output to be identical to
the input prompt without any modifications


## Outputs

### string
A string with the text of your original prompt with the selected style seamlessly
integrated into it.

