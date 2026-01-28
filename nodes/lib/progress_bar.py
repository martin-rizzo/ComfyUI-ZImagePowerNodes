"""
File    : core/progress_bar.py
Purpose : Custom progress bar designed to allow progress hierarchies.
Author  : Martin Rizzo | <martinrizzo@gmail.com>
Date    : Jan 16, 2026
Repo    : https://github.com/martin-rizzo/ComfyUI-ZImagePowerNodes
License : MIT
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
                          ComfyUI-ZImagePowerNodes
         ComfyUI nodes designed specifically for the "Z-Image" model.
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
import torch
import latent_preview
from typing      import Any
from comfy.utils import ProgressBar as ComfyProgressBar


#============================== PROGRESS BAR ===============================#
class ProgressBar:
    """
    A progress bar class designed to allow nesting of progress bars.

    This enables breaking down longer tasks into smaller, more granular
    sub-tasks, allowing for more detailed progress tracking.

    Args:
        steps    (int): The total number of steps for the current task.
        parent (tuple): A tuple containing:
            - The parent `ProgressBar` instance.
            - The minimum progress value at the parent's bar where the current task begins.
            - The maximum progress value at the parent's bar where the current task ends.
    """
    def __init__(self,
                 steps : int,
                 parent: tuple[Any, int, int],
                 ):
        self.parent    = parent[0]
        self.range_min = int(parent[1])
        self.range_max = int(parent[2])
        self.current   = 0
        self.total     = steps


    @classmethod
    def from_comfyui(cls, steps: int) -> "ProgressBar":
        """
        Creates a ProgressBar instance for integration with a ComfyUI environment.
        Args:
            steps (int): The total number of steps.
        """
        comfy_progress_bar = ComfyProgressBar(steps)
        return cls(steps, parent=(comfy_progress_bar, int(0), steps))


    def update_absolute(self,
                        value  : int,
                        total  : int   | None = None,
                        preview: tuple | None = None):
        """
        Updates the progress bar to a specific absolute value.
        Args:
            value        (int): The current step value.
            total   (optional): The total number of steps.
                                Defaults to None (use the `steps` value from initialization)
            preview (optional): Internal data used for comfyui's latent preview.
        """
        # calculate the current progress level [0.0 -> 1.0]
        self.total     = total or self.total
        self.current   = min(value, self.total)
        progress_level = float(self.current) / self.total if self.total > 0 else 1.0

        # apply the progress level to the parent bar
        if self.parent:
            parent_value = self.range_min + (progress_level * (self.range_max - self.range_min))
            self.parent.update_absolute(parent_value, None, preview)


    def update(self, value):
        """
        Updates the progress bar by a given value.
        Args:
            value (int): The amount to increment the progress bar by.
        """
        self.update_absolute(self.current + value)



#===================== PROGRESS BAR WITH LIVE PREVIEW ======================#
class ProgressPreview:

    def __init__(self,
                 steps : int,
                 parent: tuple[Any, int, int],
                 ):
        self.parent    = parent[0]
        self.range_min = int(parent[1])
        self.range_max = int(parent[2])
        self.total     = steps


    @classmethod
    def from_comfyui(cls, model: object, steps: int):
        callback = latent_preview.prepare_callback(model, steps)
        return cls(steps, parent=(callback, 0, steps))


    def __call__(self,
                 step       : int,
                 x0         : torch.Tensor,
                 x          : torch.Tensor,
                 total_steps: int | None = None
                 ) -> None:

        # calculate the current progress level [0.0 -> 1.0]
        self.total     = total_steps or self.total
        self.current   = min(step, self.total)
        progress_level = float(self.current) / self.total if self.total > 0 else 1.0

        # apply the progress level to the parent bar
        if self.parent:
            parent_value = self.range_min + (progress_level * (self.range_max - self.range_min))
            self.parent( int(parent_value), x0, x, None )

