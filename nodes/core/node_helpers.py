"""
File    : node_helpers.py
Purpose : Functions to help with ComfyUI nodes data extraction.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 24, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

There are two types of structures that store the nodes in ComfyUI:
  - "workflow" : This is a dictionary containing all nodes, groups, and
                 connections as they are presented visually in the editor.
  - "prompt"   : This is a dictionary with information for the backend and
                 contains a summary of the nodes with only selected values
                 and essential data.

In general, the functions in this file operate on the "prompt" structure.

"""

def get_class_type(node: dict) -> str:
    """Returns the class name of a node."""
    class_type = node.get("class", "") if isinstance(node ,dict) else ""
    class_type = class_type.partition(" //")[0]  #< Z-Image Power Nodes has a special format for class names.
    return class_type


def get_input_int(node: dict, input_name: str, /, *, default: int = 0) -> int:
    """
    Retrieves the integer value of an input from a given node.

    If `input_name` does not exist in the node or is a connection to
    another node, this function returns the specified `default` value.

    Args:
        node        (dict): The node from which to retrieve the input value.
        input_name   (str): The name of the input to look up.
        default (optional): The default integer value to return if the input
                            is not found or is a connection. Defaults to 0.

    Returns:
        The integer representation of the input value
        or the provided default integer value if it cannot be converted.
    """
    inputs = node.get("inputs")     if isinstance(node  , dict) else None
    value  = inputs.get(input_name) if isinstance(inputs, dict) else None

    if isinstance(value, (int,float)):
        return int(value)
    elif isinstance(value, str):
        try   : return int(value)
        except: pass
    return int(default) if isinstance(default,(int,float)) else 0


def get_input_float(node: dict, input_name: str, /, *, default: float = 0.0) -> float:
    """
    Retrieves the floating-point value of an input from a given node.

    If `input_name` does not exist in the node or is a connection to
    another node, this function returns the specified `default` value.

    Args:
        node        (dict): The node from which to retrieve the input value.
        input_name   (str): The name of the input to look up.
        default (optional): The default float value to return if the input
                            is not found or is a connection. Defaults to 0.0.

    Returns:
        The floating-point representation of the input value
        or the provided default float value if it cannot be converted.
    """
    inputs = node.get("inputs")     if isinstance(node  , dict) else None
    value  = inputs.get(input_name) if isinstance(inputs, dict) else None

    if isinstance(value, (float, int)):
        return float(value)
    elif isinstance(value, str):
        try   : return float(value)
        except: pass
    return float(default) if isinstance(default,(float,int)) else 0.0


def get_input_string(node: dict, input_name: str, *, default: str = "") -> str:
    """
    Retrieves the string value of an input from a given node.

    If `input_name` does not exist in the node or is a connection to
    another node, this function returns the specified `default` value.

    Args:
        node        (dict): The node from which to retrieve the input value.
        input_name   (str): The name of the input to look up.
        default (optional): The default string value to return if the input is not found or is a connection.
                            Defaults to an empty string.

    Returns:
        The string representation of the input value or the provided default string value.
    """
    inputs = node  .get("inputs"  ) if isinstance(node  ,dict) else None
    value  = inputs.get(input_name) if isinstance(inputs,dict) else None
    if isinstance(value, (float,int)):
        return str(value)
    if isinstance(value, str):
        return value
    return default


def get_input_node(node: dict, input_name: str, *, nodes: dict) -> dict:
    """
    Retrieves the connected node for a given input connection.

    Args:
        node      (dict): The base node from which to retrieve the connected node.
        input_name (str): Name of the connection to look up.
        nodes     (dict): Dictionary containing all nodes (prompt structure)

    Returns:
        A dictionary representing the connected node,
        or an empty dictionary if no such connection exists.
    """
    inputs        = node.get("inputs")          if isinstance(node  , dict)              else None
    wire          = inputs.get(input_name)      if isinstance(inputs, dict)              else None
    input_node_id = wire[0]                     if isinstance(wire,list) and len(wire)>0 else None
    input_node    = nodes.get(input_node_id)    if isinstance(input_node_id , str)       else None
    return input_node if isinstance(input_node,dict) else {}


def find_prompt(node: dict, type: str, *, nodes: dict, depth: int = 0) -> str:
    """
    Returns the text prompt from a given node searching through its inputs.
    Args:
        node (dict): The current node under consideration.
        type       : The specific type of prompt to retrieve ('positive' or 'negative').
        nodes      : A dictionary containing all nodes in the workflow.
        depth (optional): Internal parameter to track the recursion depth.
    """
    if not isinstance(node,dict) or not node or depth >= 8:
        return ""

    # in the first step of recursion, check if the `type` param is valid
    if depth==0 and type not in ["positive","negative"]:
        raise ValueError(f"Type must be 'positive' or 'negative', not '{type}'")

    # in the first step of recursion, node can be a sampler node with positive/negative inputs
    if depth==0:
        prompt_node = get_input_node(node, type, nodes=nodes)
        if prompt_node:
            return find_prompt(prompt_node, type, nodes=nodes, depth=depth+1)

    #--------------------------------------------
    # from this point, what we do is to traverse the connection chain until reaching a prompt

    class_type = node.get("class_type", "")

    if class_type == "ControlNetApply" or class_type == "FluxGuidance":
        conditioning_node = get_input_node( node,"conditioning", nodes=nodes )
        return find_prompt(conditioning_node, type, nodes=nodes, depth=depth+1)

    text_node = get_input_node( node,"text", nodes=nodes )
    if text_node:
        return find_prompt(text_node, type, nodes=nodes, depth=depth+1)

    # finally check if we are in a node that contains prompt
    TEXT_NAMES = ("text", "text_g", f"text_{type}", "populated_text")
    for name in TEXT_NAMES:
        prompt: str = get_input_string(node, name)
        if prompt:
            return prompt

    return ""