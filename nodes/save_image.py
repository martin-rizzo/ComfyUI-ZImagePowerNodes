"""
File    : save_image.py
Purpose : Node for saving a generated images to disk injecting CivitAI compatible metadata.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 18, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

The V3 schema documentation can be found here:
 - https://docs.comfy.org/custom-nodes/v3_migration

Code for the metadata extraction process used by CivitAI:
 - https://github.com/civitai/civitai/blob/main/src/utils/metadata/comfy.metadata.ts

"""
import os
import time
import json
import numpy as np
import torch
import folder_paths
from PIL                 import Image
from PIL.PngImagePlugin  import PngInfo
from comfy_api.latest    import io


class SaveImage(io.ComfyNode):
    xTITLE         = "Save Image"
    xCATEGORY      = ""
    xCOMFY_NODE_ID = ""
    xDEPRECATED    = False

    # these were instance variables
    # but now in V3 schema everything is @classmethod
    xTYPE          = "output"
    xCOMPRESS_LVL  = 4  # 4 when xType == "output", otherwise 0
    xEXTRA_PREFIX  = ""
    xOUTPUT_DIR    = ""

    #__ INPUT / OUTPUT ____________________________________
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            display_name   = cls.xTITLE,
            category       = cls.xCATEGORY,
            node_id        = cls.xCOMFY_NODE_ID,
            is_deprecated  = cls.xDEPRECATED,
            is_output_node = True,
            description    = (
                ""
            ),
            inputs=[
                io.Image.Input  ("images",
                                 tooltip="The images to save.",
                                ),
                io.String.Input ("filename_prefix", default="ZImage",
                                 tooltip="The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or %Empty Latent Image.width% to include values from nodes",
                                ),
                io.Boolean.Input("civitai_compatible_metadata", default=True,
                                 tooltip="Whether to save the image in a CivitAI compatible format. If checked, this will modify the metadata de forma que el prompt y demas parametros puedan ser leidos por CivitAI.",
                                ),
            ],
            hidden=[
                io.Hidden.prompt,
                io.Hidden.extra_pnginfo,
            ]
        )

    #__ FUNCTION __________________________________________
    @classmethod
    def execute(cls, images, filename_prefix: str, civitai_compatible_metadata: bool):

        output_dir     = cls.xOUTPUT_DIR if cls.xOUTPUT_DIR else folder_paths.get_output_directory()
        images         = cls.normalize_images(images)
        image_width    = images[0].shape[1]
        image_height   = images[0].shape[0]
        extra_pnginfo  = cls.hidden.extra_pnginfo

        prompt_nodes   = cls.hidden.prompt
        workflow_nodes = extra_pnginfo.get("workflow") if extra_pnginfo else None

        # solve the `filename_prefix`` entered by the user and get the full path
        filename_prefix = \
            cls.solve_filename_variables( f"{filename_prefix}{cls.xEXTRA_PREFIX}" )
        full_output_folder, name, counter, subfolder, filename_prefix \
            = folder_paths.get_save_image_path(filename_prefix,
                                               output_dir,
                                               image_width,
                                               image_height
                                               )

        # try to inject CivitAI compatible metadata
        if civitai_compatible_metadata:
            initial_sampler, seed, steps, cfg, sampler_name = cls.find_initial_sampler(nodes=prompt_nodes)
            if initial_sampler:
                positive, negative = cls.get_positive_negative(initial_sampler, nodes=prompt_nodes)
                prompt_nodes = cls.inject_civitai_nodes(prompt_nodes,
                                                        positive     = positive,
                                                        negative     = negative,
                                                        seed         = seed,
                                                        steps        = steps,
                                                        cfg          = cfg,
                                                        sampler_name = sampler_name)

        # create PNG info containing ComfyUI metadata (+CivitAI injection)
        pnginfo = PngInfo()

        if prompt_nodes:
            prompt_json = json.dumps(prompt_nodes)
            pnginfo.add_text("prompt", prompt_json)

        if workflow_nodes:
            workflow_json = json.dumps(workflow_nodes)
            pnginfo.add_text("workflow", workflow_json)

        if extra_pnginfo:
            for info_name, info_dict in extra_pnginfo.items():
                if info_name not in ("parameters", "prompt", "workflow"):
                    pnginfo.add_text(info_name, json.dumps(info_dict))


        # iterate over each image in batch to save it
        image_locations = []
        for batch_number, image in enumerate(images):
            batch_name = name.replace("%batch_num%", str(batch_number))

            # convert to PIL Image
            image = np.clip( image.numpy(force=True) * 255, 0, 255 ) # <- numpy
            image = Image.fromarray( image.astype(np.uint8) )        # <- PIL

            # generate the full file path to save the image
            filename  = f"{batch_name}_{counter+batch_number:05}_.png"
            file_path =  os.path.join(full_output_folder, filename)

            image.save(file_path,
                       pnginfo        = pnginfo,
                       compress_level = cls.xCOMPRESS_LVL)
            image_locations.append({"filename" : filename,
                                    "subfolder": subfolder,
                                    "type"     : cls.xTYPE
                                    })

        return { "ui": { "images": image_locations } }




    #__ internal functions ________________________________

    @classmethod
    def solve_filename_variables(cls,
                                 filename : str,
                                 ) -> str:
        """
        Solve the filename variables and return a string containing the solved filename.
        Args:
            filename    : The filename to solve.
            genparams   : A GenParams dictionary containing all the generation parameters.
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
                    value = cls.ireplace(value, "yyyy", str(now.tm_year))
                    value = cls.ireplace(value, "yy"  , str(now.tm_year)[-2:])
                    value = value.replace(  "MM"  , str(now.tm_mon ).zfill(2))
                    value = cls.ireplace(value, "dd"  , str(now.tm_mday).zfill(2))
                    value = cls.ireplace(value, "hh"  , str(now.tm_hour).zfill(2))
                    value = value.replace(  "mm"  , str(now.tm_min ).zfill(2))
                    value = cls.ireplace(value, "ss"  , str(now.tm_sec ).zfill(2))
                    return value
                #elif name in extra_vars:
                #    value = str(extra_vars[name])[:16]
                return None

        output = ""
        next_token_is_var = False
        for token in filename.split("%"):
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



    @staticmethod
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

        if (max_channels is not None) and images.shape[-1] > max_channels:
            images = images[ : , : , : , 0:max_channels ]

        if (max_batch_size is not None) and images.shape[0] > max_batch_size:
            images = images[ 0:max_batch_size , : , : , : ]

        return images



    @staticmethod
    def ireplace(text: str, old: str, new: str, count: int = -1) -> str:
        """
        Replaces all occurrences of `old` in `text` with `new`, case-insensitive.
        If count is given, only the first `count` occurrences are replaced.
        """
        lower_text , lower_old = text.lower(), old.lower()
        index_start, index_end = 0, lower_text.find(lower_old, 0)
        if index_end == -1 or len(lower_text) != len(text):
            return text

        output = ""
        lower_old_length = len(lower_old)
        while index_end != -1 and count != 0:
            output += text[index_start:index_end] + new
            index_start = index_end + lower_old_length
            index_end   = lower_text.find(lower_old, index_start)
            if count > 0:
                count -= 1
        return output + text[index_start:]


    #__ nodes related functions ___________________________

    CIVITAI_NODES="""{

  "$1": {
    "inputs": {
      "text": "",
      "clip": [ "$5", 1 ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": { "title": "CLIP Text Encode (Positive Prompt)" }
  },

  "$2": {
    "inputs": {
      "text": "",
      "clip": [ "$5", 1 ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": { "title": "CLIP Text Encode (Negative Prompt)" }
  },

  "$3": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptySD3LatentImage",
    "_meta": { "title": "EmptySD3LatentImage" }
  },

  "$4": {
    "inputs": {
      "seed": 550110717236789,
      "steps": 20,
      "cfg": 1.0,
      "sampler_name": "euler",
      "scheduler": "simple",
      "denoise": 1.0,
      "model": [ "$5", 0 ],
      "positive": [ "$6", 0 ],
      "negative": [ "$2", 0 ],
      "latent_image": [ "$3", 0 ]
    },
    "class_type": "KSampler",
    "_meta": { "title": "KSampler"  }
  },


  "$5": {
    "inputs": {
      "ckpt_name": "z-image_turbo_.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": { "title": "Load Checkpoint"  }
  },

  "$6": {
    "inputs": {
      "guidance": 8.15,
      "conditioning": [ "$1", 0 ]
    },
    "class_type": "FluxGuidance",
    "_meta": { "title": "FluxGuidance" }
  }
}
"""
    @classmethod
    def find_civitai_nodes(cls,
                           nodes : dict[ str, dict ],
                           ) -> int:
        """
        Searches for existing CivitAI-injected nodes in the given node dictionary.

        This method looks through the provided nodes to check if it have been
        previously injected with a specific pattern of nodes required by CivitAI.
        It returns an index indicating where these nodes start, or 0 if no such
        injection is found.

        Args:
            nodes (dict): The dictionary containing existing nodes.

        Returns:
            int: The base index where the CivitAI-injected nodes start, or 0 if not found.
        """
        for id, node in nodes.items():

            # get the integer value of 'id' which should always be greater than 5
            if isinstance(id, str) and id.isdigit():
                id = int(id)
            if not isinstance(id, int):
                continue
            if id <= 5:
                continue

            # check only CheckpointLoaderSimple nodes
            if not isinstance(node,dict) or node.get('class_type', '') != 'CheckpointLoaderSimple':
                continue

            # verify that it is a CheckpointLoaderSimple node that was injected
            ckpt_name = node.get('inputs',{}).get('ckpt_name','')
            if ckpt_name != "z-image_turbo_.safetensors":
                continue

            # to be sure we have the right injected node,
            # the next one should be a FluxGuidance with a guidance value between 8.1 and 8.2
            next_node = nodes.get( str(id+1), {} )
            if not isinstance(next_node,dict) or next_node.get("class_type", "") != "FluxGuidance":
                continue
            guidance = next_node.get("inputs", {}).get("guidance", None)
            if not isinstance(guidance, (float,int)) or guidance <= 8.1 or guidance >= 8.2:
                continue

            base_index = (id - 5)
            first_node = nodes.get( str(base_index+1), None )
            if isinstance(first_node,dict) and first_node.get("class_type", "") == "CLIPTextEncode":
                return base_index

        return 0


    @classmethod
    def inject_civitai_nodes(cls,
                             nodes : dict[ str, dict ],
                             /,*,
                             positive     : str,
                             negative     : str,
                             seed         : int,
                             steps        : int,
                             cfg          : float,
                             sampler_name : str = "euler",
                             scheduler    : str = "simple",
                             width        : int = 1024,
                             height       : int = 1024,
                             ) -> dict:
        """
        Injects generation parameters into a node format that Civitai can read.

        This method takes an existing dictionary with nodes and injects additional
        nodes required by Civitai. The modified dictionary, now compatible with
        Civitai's expected structure, is returned.

        Args:
            nodes         (dict): Original dictionary containing existing nodes.
            positive       (str): Positive prompt text for generation.
            negative       (str): Negative prompt text for generation.
            seed           (int): Random seed value for reproducibility.
            steps          (int): Number of steps in the sampling process.
            cfg          (float): CFG scale, controlling how much the negative prompt affects the output.
            sampler_name   (str): Name of the sampler to be used in generation.
            scheduler (optional): Scheduler name. Defaults to "simple".
            width     (optional): Image width in pixels. Defaults to 1024.
            height    (optional): Image height in pixels. Defaults to 1024.

        Returns:
            Updated node dictionary with Civitai nodes included.
        """

        # check if `nodes` already has Civitai nodes injected
        base_index   = cls.find_civitai_nodes(nodes)
        not_injected = (base_index==0)

        # if there are no Civitai nodes injected,
        # get the maximum index of any node,
        # that will be the base for inject CivitAI nodes
        if not_injected:
            base_index = 0
            for index in nodes.keys():
                if isinstance(index, str):
                    index = int(index)
                if isinstance(index, int) and index > base_index:
                    base_index = index
            base_index += 100

            # reenumerate the CivitAI nodes from `base_index`
            # this way they don't collide with the nodes in the actual workflow
            civitai_nodes = cls.CIVITAI_NODES
            for i in range(1, 9):
                civitai_nodes = civitai_nodes.replace(f'"${i}"', f'"{base_index+i}"')
            civitai_nodes = json.loads(civitai_nodes)

            # inject CivitAI nodes into `nodes`
            # these nodes are still "templates", they need to be configured with values
            nodes = {**nodes, **civitai_nodes}

        # modify the CivitAI nodes "1", "2" and "4" assigning them the parameters
        # prompt-positve, prompt-negative, seed, steps, etc...
        positive_node = nodes[ str(base_index+1) ]
        positive_node["inputs"]["text"] = positive

        negative_node = nodes[ str(base_index+2) ]
        negative_node["inputs"]["text"] = negative

        latent_image_node = nodes[ str(base_index+3) ]
        latent_image_node["inputs"]["width" ] = int(width)
        latent_image_node["inputs"]["height"] = int(height)

        ksampler_node = nodes[ str(base_index+4) ]
        ksampler_node["inputs"]["seed"]         = int(seed)
        ksampler_node["inputs"]["steps"]        = int(steps)
        ksampler_node["inputs"]["cfg"]          = cfg
        ksampler_node["inputs"]["sampler_name"] = sampler_name
        ksampler_node["inputs"]["scheduler"]    = scheduler

        return nodes


    @classmethod
    def find_initial_sampler(cls, nodes: dict) -> tuple[dict | None, int, int, float, str]:
        """
        Find the sampler node that seems to generate the initial image

        This function iterates through all nodes, searching for those with any
        class type related to sampling, and it checks if these are connected to
        any empty latent image generator.

        Args:
            nodes (dict): Dictionary containing all nodes in the graph.

        Returns:
            A tuple containing the following elements:
                - The first element is a dict representing the found initial sampler node,
                  or None if no such node was found.
                - The second element is an integer representing the seed value for sampling.
                - The third element is an integer representing the number of steps in the sampling process.
                - The fourth element is a float representing the CFG scale.
                - The fifth element is a string representing the name of the sampler used.
            If no suitable node is found, the function returns None for the first element
            and default values (0, 0, 0.0, "") for the remaining elements.
        """
        for node in nodes.values():
            class_type = node.get("class_type")
            if not class_type:
                continue

            if class_type == "KSampler":
                latent_image = cls.get_input_node(node,"latent_image", nodes=nodes)
                if cls.is_empty_latent(latent_image):
                    seed         = int  ( cls.get_input_value(node, "seed"        , default=0      ))
                    steps        = int  ( cls.get_input_value(node, "steps"       , default=8      ))
                    cfg          = float( cls.get_input_value(node, "cfg"         , default=3.5    ))
                    sampler_name = str  ( cls.get_input_value(node, "sampler_name", default="euler"))
                    return (node, seed, steps, cfg, sampler_name)

            if class_type.startswith("ZSamplerTurbo"):
                latent_input = cls.get_input_node(node,"latent_input", nodes=nodes)
                if cls.is_empty_latent(latent_input):
                    seed         = int( cls.get_input_value(node, "seed" , default=0) )
                    steps        = int( cls.get_input_value(node, "steps", default=8) )
                    cfg          = 1.0
                    sampler_name = "euler"
                    return (node, seed, steps, cfg, sampler_name)

        return None, 0, 0, 0.0, ""


    @classmethod
    def get_prompt_text(cls, node: dict, type: str, nodes: dict, depth: int = 0) -> str:
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

        class_type = node.get("class_type", "")
        if class_type == "ControlNetApply":
            conditioning = cls.get_input_node(node,"conditioning", nodes=nodes)
            return cls.get_prompt_text(conditioning, type, nodes=nodes, depth=depth+1)

        if class_type == "FluxGuidance":
            conditioning = cls.get_input_node(node,"conditioning", nodes=nodes)
            return cls.get_prompt_text(conditioning, type, nodes=nodes, depth=depth+1)

        TEXT_NAMES = ("text", "text_g", f"text_{type}", "populated_text")
        for name in TEXT_NAMES:

            text = str( cls.get_input_value(node, name , default="!") )
            if text != "!": return text

            text_node = cls.get_input_node(node,"text", nodes=nodes)
            if text_node:
                return cls.get_prompt_text(text_node, type, nodes=nodes, depth=depth+1)

        return ""


    @classmethod
    def get_positive_negative(cls, sampler_node: dict, nodes: dict) -> tuple[str,str]:
        """
        Retrieves positive and negative prompt texts from the given sampler node.
        Args:
            sampler_node (dict): The sampler node with connections to positive and negative prompts.
            nodes              : A dictionary containing all nodes in the workflow.

        Returns:
            tuple[str, str]: A pair of strings with the positive and negative prompt texts.
        """
        positive_node = cls.get_input_node(sampler_node,"positive",nodes=nodes)
        positive      = cls.get_prompt_text(positive_node, type="positive", nodes=nodes)
        negative_node = cls.get_input_node(sampler_node,"negative",nodes=nodes)
        negative      = cls.get_prompt_text(negative_node, type="positive", nodes=nodes)
        return positive, negative


    @staticmethod
    def get_input_node(node: dict, connection_name:str, *, nodes:dict) -> dict:
        """
        Retrieves the connected node for a given input connection.
        Args:
            node (dict)    : The current node in consideration.
            connection_name: Name of the connection to look up.
            nodes          : Dictionary containing all nodes in the workflow.
        Returns:
            A dictionary representing the connected node, or an empty dict if no such connection exists.
        """
        wire = node.get("inputs", {}).get(connection_name, {})
        node_id = str(wire[0]) if isinstance(wire,list) and len(wire)>0 else ""
        return nodes.get(node_id, {})


    @staticmethod
    def get_input_value(node: dict, value_name: str, default: str|float|int = 0) -> str | float | int:
        """
        Retrieves the value of a given parameter for a node.
        Args:
            node (dict): The current node in consideration.
            value_name : Name of the input value to look up.
            default    : Default value to return if `value_name` is not found in the node.
        Returns:
            The value or the provided default value if `value_name` is not found.
        """
        value = node.get("inputs", {}).get(value_name, default)
        if not isinstance(value, (str,float,int)):
            return default
        return value


    @staticmethod
    def is_empty_latent(node: dict) -> bool:
        """
        Determines whether a given node represents an empty latent image generator.
        """
        class_type = node.get("class_type", "") if isinstance(node,dict) else ""
        if class_type in ["EmptyLatentImage", "EmptySD3LatentImage"]:
            return True
        if class_type.startswith("EmptyZImageLatentImage"):
            return True
        return False

