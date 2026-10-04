# ComfyUI VRAM Unloader Filter for Open-WebUI
"""
ComfyUI VRAM Unloader
Automatically unloads models and frees VRAM in ComfyUI before running LLM inference.

This filter intercepts incoming chat completion requests before they are sent
to the LLM backend (e.g., llama.cpp/Ollama) and sends HTTP POST requests to
ComfyUI's `/free` or `/prompt` API endpoints based on configured valves.

Host and port settings are configurable via environment variables (`COMFYUI_HOST`, `COMFYUI_PORT`)
or directly through the Open-WebUI Functions settings panel.

Installation Instructions in Open-WebUI:
1. Go to Admin Panel > Functions.
2. Click the '+' (Create Function) button.
3. Set the function type to 'Filter'.
4. Paste this code into the editor and click Save.
5. Enable the filter globally or toggle it on within specific model settings.
6. (Optional) Pass COMFYUI_HOST and COMFYUI_PORT as environment variables in your
   Docker container startup command or docker-compose.yml file.
"""

import os
import sys
import logging
import requests
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


# Global constants read from environment variables with sensible fallback defaults.
DEFAULT_HOST = os.getenv("COMFYUI_HOST", "127.0.0.1")
DEFAULT_PORT = os.getenv("COMFYUI_PORT", "8188")


class Filter:
    """
    Open-WebUI Filter that frees up VRAM in ComfyUI before LLM inference.

    Sends HTTP POST requests to ComfyUI's API endpoints to unload diffusion
    models and flush memory/caches independently as configured.
    """

    class Valves(BaseModel):
        """
        Configurable knobs (valves) for the filter, exposed through
        the Open-WebUI Functions settings panel.
        """
        comfyui_host: str = Field(
            default=DEFAULT_HOST,
            description="Host or IP address of the ComfyUI server.",
        )
        comfyui_port: str = Field(
            default=DEFAULT_PORT,
            description="Port on which ComfyUI listens.",
        )
        send_empty_workflow: bool = Field(
            default=True,
            description="Send an empty workflow prompt to trigger a smart offload to system RAM while clearing VRAM.",
        )
        unload_models: bool = Field(
            default=False,
            description="Unload models loaded in VRAM.",
        )
        free_memory: bool = Field(
            default=False,
            description="Run torch.cuda.empty_cache() to free the CUDA memory cache.",
        )
        free_execution_cache: bool = Field(
            default=False,
            description="Free execution cache (outputs/intermediates held in RAM/VRAM).",
        )


    def __init__(self):
        """
        Initialize the filter with its default valves configuration.
        """
        self.valves = self.Valves()


    def inlet(self, body: dict, user: dict | None = None) -> dict:
        """
        Intercept the incoming request right before it is sent to the LLM backend.

        Args:
            body : The request body (chat completion payload) being sent to the backend.
            user : Optional user metadata dictionary.

        Returns:
            The original `body` dictionary, unchanged.
        """
        logger.info(">>> Launching ComfyUI VRAM unloader <<<")

        # Normalize the host URL
        host = self.valves.comfyui_host.strip()
        port = self.valves.comfyui_port.strip()
        if not host.startswith("http://") and not host.startswith("https://"):
            host = f"http://{host}"

        comfy_base_url = f"{host}:{port}"

        try:
            # Send empty workflow independently
            if self.valves.send_empty_workflow:
                url_prompt     = f"{comfy_base_url}/prompt"
                prompt_payload = {"prompt": {}}

                res_prompt = requests.post(url_prompt, json=prompt_payload, timeout=8)
                if res_prompt.status_code == 200:
                    logger.info(f"[ComfyUI Unloader] Empty workflow sent successfully to {url_prompt}.")
                else:
                    logger.info(f"[ComfyUI Unloader] Error {res_prompt.status_code} sending empty workflow to {url_prompt}")

            # Memory and Model cleaning flags via /free endpoint
            # (checks if at least one of the three options is activated)
            if (
                self.valves.unload_models
                or self.valves.free_memory
                or self.valves.free_execution_cache
            ):
                url_free = f"{comfy_base_url}/free"
                free_payload = {
                    "unload_models": self.valves.unload_models,
                    "free_memory": self.valves.free_memory,
                    "free_execution_cache": self.valves.free_execution_cache,
                }

                res_free = requests.post(url_free, json=free_payload, timeout=8)
                if res_free.status_code == 200:
                    logger.info(f"[ComfyUI Unloader] Free payload sent successfully to {url_free}: {free_payload}")
                else:
                    logger.info(f"[ComfyUI Unloader] Error {res_free.status_code} calling {url_free}")

        # comfyui might be down: catch timeouts and refused connections gracefully
        except Exception as e:
            logger.info(f"[ComfyUI Unloader] Could not connect to ComfyUI: {e}")

        # return the body unchanged so the request continues to the backend
        return body
