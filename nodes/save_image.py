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
import json
import numpy as np
import folder_paths
from PIL                 import Image
from PIL.PngImagePlugin  import PngInfo
from comfy_api.latest    import io
from typing              import Any
from .core.system        import logger
from .core.helpers       import expand_date_and_vars, normalize_images
from .core.node_helpers  import get_input_int, get_input_float, get_input_string, \
                                get_input_node, get_class_type, find_prompt


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
        images         = normalize_images(images)
        image_width    = images[0].shape[1]
        image_height   = images[0].shape[0]
        extra_pnginfo  = cls.hidden.extra_pnginfo

        prompt_nodes   = cls.hidden.prompt
        workflow_nodes = extra_pnginfo.get("workflow") if extra_pnginfo else None

        # expand `filename_prefix` variables entered by the user and get the full path
        filename_prefix = expand_date_and_vars( f"{filename_prefix}{cls.xEXTRA_PREFIX}", vars = {} )
        full_output_folder, name, counter, subfolder, filename_prefix \
            = folder_paths.get_save_image_path(filename_prefix,
                                               output_dir,
                                               image_width,
                                               image_height)


        # attempt to inject CivitAI compatible metadata
        if civitai_compatible_metadata:
            params = {}

            # try to find generation parameters from the initial sampler node,
            # initial sampler is defined as any sampler that is connected to an empty latent generator
            initial_sampler_node, sampler_params = cls.find_initial_sampler(nodes=prompt_nodes)
            params.update( sampler_params )

            # attempt to identify generation parameters from nodes tagged by the user with ">>C"
            contrib_count, user_params = cls.find_user_params(title_tag=">>C", nodes=prompt_nodes)
            params.update( user_params )

            # if important parameters are found, inject all into the image's metadata,
            # this is done by creating new nodes that contain these parameters but are recognizable by CivitAI
            found_params = ("positive" in params) or ("seed" in params)
            if found_params:
                prompt_nodes = cls.inject_civitai_nodes(prompt_nodes,
                                                        positive     = params.get("positive"    , ""      ),
                                                        negative     = params.get("negative"    , ""      ),
                                                        seed         = params.get("seed"        , 0       ),
                                                        steps        = params.get("steps"       , 50      ),
                                                        cfg          = params.get("cfg"         , 1.0     ),
                                                        sampler_name = params.get("sampler_name", "euler" ),
                                                        scheduler    = params.get("scheduler"   , "simple"),
                                                        width        = params.get("width"       , 1024    ),
                                                        height       = params.get("height"      , 1024    ),
                                                        )
            # log the outcome of this metadata injection process to provide feedback
            if not found_params:
                logger.warning(f'"Save Image" was unable to locate generation parameters for injection as CivitAI metadata. Injection skipped.')
            elif contrib_count==0:
                logger.info(f'"Save Image" extracted parameters from a {get_class_type(initial_sampler_node)} node to inject CivitAI metadata.')
            else:
                logger.info(f'"Save Image" utilized parameters from {contrib_count} user-tagged nodes to inject CivitAI metadata.')



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
                             negative     : str   = "",
                             seed         : int   = 1,
                             steps        : int   = 8,
                             cfg          : float = 1.0,
                             sampler_name : str   = "euler",
                             scheduler    : str   = "simple",
                             width        : int   = 1024,
                             height       : int   = 1024,
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
            for node_id in nodes.keys():
                index = cls.max_index_from_node_identifier(node_id)
                base_index = max(base_index, index)
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
        positive_node["inputs"]["text"] = str(positive) if positive is not None else ""

        negative_node = nodes[ str(base_index+2) ]
        negative_node["inputs"]["text"] = str(negative) if negative is not None else ""

        latent_image_node = nodes[ str(base_index+3) ]
        latent_image_node["inputs"]["width" ] = int(width ) if isinstance(width ,(int,float)) else 1024
        latent_image_node["inputs"]["height"] = int(height) if isinstance(height,(int,float)) else 1024

        ksampler_node = nodes[ str(base_index+4) ]
        ksampler_node["inputs"]["seed"]         = int(seed        ) if isinstance(seed ,(int,float)) else 1
        ksampler_node["inputs"]["steps"]        = int(steps       ) if isinstance(steps,(int,float)) else 25
        ksampler_node["inputs"]["cfg"]          = float(cfg       ) if isinstance(cfg  ,(int,float)) else 1.0
        ksampler_node["inputs"]["sampler_name"] = str(sampler_name) if sampler_name is not None else "euler"
        ksampler_node["inputs"]["scheduler"]    = str(scheduler   ) if scheduler    is not None else "simple"

        return nodes


    @classmethod
    def find_initial_sampler(cls, nodes: dict) -> tuple[dict, dict]:
        """
        Find the sampler node that seems to generate the initial image

        This function iterates through all nodes, searching for those with any
        class type related to sampling, and then checks if it is connected to
        a latent image creator. This indicates it might be the initial image
        generator.

        Args:
            nodes: Dictionary containing all nodes (prompt structure)

        Returns:
            A tuple containing the following elements:
                - The first element is a dict representing the found initial sampler node,
                  or empty dict if no suitable sampler is found.
                - The second element is a dict containing the parameters of the found sampler,
                  or empty dict if no parameters were found.
        """
        initial_sampler_node = {}
        params = {}

        # iterates through all nodes and analyzes those related to sampling
        for node in nodes.values():
            class_type: str = node.get("class_type","") if isinstance(node, dict) else ""
            if not class_type:
                continue

            if class_type == "KSampler":
                latent_node = get_input_node(node,"latent_image", nodes=nodes)
                if cls.is_empty_latent_node(latent_node):
                    initial_sampler_node = node
                    params["positive"]     = find_prompt(node, type="positive", nodes=nodes)
                    params["negative"]     = find_prompt(node, type="negative", nodes=nodes)
                    params["seed"]         = get_input_int   (node, "seed"        , default=-1  )
                    params["steps"]        = get_input_int   (node, "steps"       , default=-1  )
                    params["cfg"]          = get_input_float (node, "cfg"         , default=-1.0)
                    params["sampler_name"] = get_input_string(node, "sampler_name", default=""  )
                    params["scheduler"]    = get_input_string(node, "scheduler"   , default=""  )
                    break

            if class_type.startswith("ZSamplerTurbo "):
                latent_node = get_input_node(node,"latent_input", nodes=nodes)
                if cls.is_empty_latent_node(latent_node):
                    initial_sampler_node = node
                    params["positive"]     = find_prompt(node, type="positive", nodes=nodes)
                    params["seed"]         = get_input_int(node, "seed" , default=-1)
                    params["steps"]        = get_input_int(node, "steps", default=-1)
                    params["cfg"]          = 1.0      # this node always uses cfg = 1.0
                    params["sampler_name"] = "euler"  # internally, this node always uses "euler"
                    # no scheduler, this node uses a fixed custom scheduler
                    break

        # remove any parameter that is out of range or empty
        if not params.get("positive"    ): params.pop("positive"    , None)
        if not params.get("negative"    ): params.pop("negative"    , None)
        if not params.get("sampler_name"): params.pop("sampler_name", None)
        if not params.get("scheduler"   ): params.pop("scheduler"   , None)
        if params.get("seed" ,-1) < 0    : params.pop("seed"        , None)
        if params.get("steps",-1) < 1    : params.pop("steps"       , None)
        if params.get("cfg"  ,-1) < 0    : params.pop("cfg"         , None)
        return initial_sampler_node, params


    @classmethod
    def find_user_params(cls, title_tag: str, nodes: dict) -> tuple[int, dict[str, Any]]:
        all_params = {}
        contrib_count = 0

        for node in nodes.values():
            if not isinstance(node,dict):
                continue

            # verify that all components of a node are present
            meta = node.get("_meta")

            # verify that the node has a valid "title" and it is tagged
            title  = meta.get("title") if isinstance(meta,dict) else None
            if not isinstance(title,str)  or  (not title_tag in title):
                continue

            params = {}

            prompt = get_input_string(node, "text", default="")
            if prompt:
                if "negative" in title.lower():  params["negative"] = prompt
                else:                            params["positive"] = prompt

            seed = get_input_int(node, "seed", default=-1)
            if seed>=0: params["seed"] = int(seed)

            steps = get_input_int(node, "steps", default=-1)
            if steps>0: params["steps"] = int(steps)

            cfg = get_input_float(node, "cfg", default=-1.0)
            if cfg>=0: params["cfg"] = float(cfg)

            sampler_name = get_input_string(node, "sampler_name", default="")
            if sampler_name: params["sampler_name"] = sampler_name

            scheduler = get_input_string(node, "scheduler", default="")
            if scheduler: params["scheduler"] = scheduler

            width = get_input_int(node, "width", default=-1)
            if width>0: params["width"] = int(width)

            height = get_input_int(node, "height", default=-1)
            if height>0: params["height"] = int(height)

            if params:
                contrib_count += 1

            all_params.update(params)

        return contrib_count, all_params


    @staticmethod
    def is_empty_latent_node(node: dict) -> bool:
        """
        Determines whether a given node represents an empty latent image generator.
        """
        class_type = node.get("class_type", "") if isinstance(node,dict) else ""
        if class_type in ["EmptyLatentImage", "EmptySD3LatentImage"]:
            return True
        if class_type.startswith("EmptyZImageLatentImage"):
            return True
        return False


    @staticmethod
    def max_index_from_node_identifier(identifier: Any) -> int:
        """
        Converts a node identifier to integer, taking into account sub-graphs format ("sub-graph:node").

        Args:
            identifier: The node identifier to convert to integer.

        Returns:
            The maximum index extracted from the identifier.
            If the identifier cannot be processed, returns 0.
        """
        if isinstance(identifier, (int,float)):
            return int(identifier)
        if isinstance(identifier,str):
            max_index = 0
            # splitting the identifier by ':' to process sub-graph elements
            # (sub-graph and internal elements seem to form a single identifier delimited by ':')
            for index in identifier.split(":"):
                if not index.isdigit():
                    continue
                max_index = max(int(index), max_index)
            return max_index
        return 0
