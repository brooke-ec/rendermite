from typing import Dict, List, Tuple
from rendermite.exceptions import OrphanModelError
import json
import os

def split_path(namespace:str, path:str) -> Tuple[str, str]:
    """Splits a minecraft formatted path into its namespace and path"""
    split = path.split(":")
    if len(split) > 1: namespace = split[0]
    return namespace, split[-1]

def normalise_path(namespace:str, path:str) -> str:
    """Formats a minecraft path to always include its namespace"""
    namespace, path = split_path(namespace, path)
    return f"{namespace}:{path}"


class MinecraftModel:
    """Represents a loaded Minecraft model"""
    
    @classmethod
    def from_file(cls, path:str, base_path,
    overrides_location = os.path.join(os.path.split(__file__)[0], "overrides")):
        """Loads a Minecraft model from the specified model file"""
        subject = cls()
        subject.model = normalise_path("minecraft", path)
        subject._base_path = base_path
        subject._overrides_path = overrides_location
        subject._load_model("minecraft", path)
        subject._consolidate_textures()
        return subject

    def __init__(self) -> None:
        # Setup variables
        self.model = None
        self._base_path = None
        self._overrides_path = None
        self.elements:List[ModelElement] = []
        self.textures:Dict[str, str] = {}
        self.displays:Dict[str, ModelDisplay] = {}
        self.texture_size = [16, 16]
        self.gui_light = "side"
        self.builtin = None

    def get_texture_path(self, namespace:str, path:str) -> str:
        """Gets the path the the specified texture"""
        if path.startswith("#"): return path
        namespace, path = split_path(namespace, path)
        return self.get_path(namespace, "textures", path, "png")

    def get_path(self, *segments):
        """Gets the path to the joined segments, taking overrides into account."""
        base = os.path.join(*segments[:-1])+f".{segments[-1]}"
        override = os.path.join(self._overrides_path, base)
        if os.path.exists(override): return override
        else: return os.path.abspath(os.path.join(self._base_path, base))

    def _consolidate_textures(self):
        """Consolidates all texture variables to their final values"""
        for ele in self.elements:
            for direction, face in list(ele.faces.items()):
                if face.texture.startswith("#"):
                    texture = self._consolidate_texture(face.texture[1:])
                    if texture is None: ele.faces.pop(direction)
                    else: face.texture = texture
    
    def _consolidate_texture(self, id:str) -> str:
        """Recursively consolidates a texture variable to its final value"""
        texture = self.textures.get(id)
        if texture is not None and texture.startswith("#"):
            texture = self._consolidate_texture(texture[1:])
            self.textures[id] = texture
        return texture

    def _load_model(self, namespace, path):
        """Recursively loads a model file consolidating inherited properties"""
        namespace, path = split_path(namespace, path)

        # Handle Builtins
        if path.startswith("builtin/"):
            self.builtin = path
            return

        # Load data
        location = self.get_path(namespace, "models", path, "json")
        if not os.path.exists(location): raise OrphanModelError(f"Model file {namespace}:{path} does not exist")
        data:dict = json.load(open(location, "r", encoding="UTF-8"))

        # Enact on attributes
        if "parent" in data: self._load_model(namespace, data["parent"])
        if "textures" in data: self.textures |= {k:self.get_texture_path(namespace, v) for k,v in data["textures"].items()}
        if "elements" in data: self.elements += [ModelElement(self, namespace, e) for e in data["elements"]]
        if "display" in data: self.displays |= {k:ModelDisplay(v) for k,v in data["display"].items()}
        if "gui_light" in data: self.gui_light = data["gui_light"]


class ModelDisplay:
    """Represents one of a Minecraft model's display options"""

    def __init__(self, data:dict) -> None:
        self.rotation:List[float] = data["rotation"] if "rotation" in data else [0, 0, 0]
        self.translation:List[float] = data["translation"] if "translation" in data else [0, 0, 0]
        self.scale:List[float] = data["scale"] if "scale" in data else [1, 1, 1]


class ModelElement:
    """Represents an Element belonging to a `MinecraftModel`"""

    def __init__(self, model:MinecraftModel, namespace:str, data:dict) -> None:
        self.model:MinecraftModel = model
        self.comment:str = data["__comment"] if "__comment" in data else None
        self.name:str = data["name"] if "name" in data else None
        self.start:List[int] = data["from"]
        self.end:List[int] = data["to"]
        self.faces:Dict[str,ElementFace] = {k:ElementFace(k, namespace, v, self) for k,v in data["faces"].items()}
        self.rotation = ElementRotation(data["rotation"]) if "rotation" in data else None

    def __str__(self) -> str:
        if self.name is not None:
            display = self.name
        elif self.comment is not None:
            display = self.comment
        else: display = "Element"
        return f"<{display}>"

    def __repr__(self) -> str:
        return self.__str__()


class ElementFace:
    """Represents a face belonging to one of a `MinecraftModel`'s `ModelElement`s"""

    AUTO_UV = {
        "DOWN": [0, 2, 3, 5],
        "UP": [0, 2, 3, 5],
        "NORTH": [0, 1, 3, 4],
        "SOUTH": [0, 1, 3, 4],
        "WEST": [5, 1, 2, 4],
        "EAST": [5, 1, 2, 4]
    }
    
    def __init__(self, direction:str, namespace:str, data:dict, element:ModelElement) -> None:
        self.element:ModelElement = element
        self.direction = direction.upper()
        self.uv = data["uv"] if "uv" in data else self.calculate_uv()
        self.texture = element.model.get_texture_path(namespace, data["texture"])
        self.rotation:int = data["rotation"] if "rotation" in data else 0
        self.cullface:str | None = data["cullface"] if "cullface" in data else None

    def calculate_uv(self) -> List[float]:
        shape = self.element.start + self.element.end
        data = self.AUTO_UV.get(self.direction)
        return [shape[data[0]], shape[data[1]], shape[data[2]], shape[data[3]]]
        

class ElementRotation:
    """Represents the rotation of a `ModelElement`"""

    def __init__(self, data:dict) -> None:
        self.angle:float = data["angle"]
        self.axis:str = data["axis"]
        self.origin:List[int] = data["origin"]
