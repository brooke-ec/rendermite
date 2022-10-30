from rendermite.loader import MinecraftModel, ElementFace, ModelDisplay
from trimesh.visual.texture import TextureVisuals
from trimesh.visual.material import PBRMaterial
from rendermite.matricies import *
from typing import Dict, List
from PIL import Image
import trimesh.util
import numpy as np
import pyrender
import trimesh
import os

FACE_DATA = {
    "DOWN": {"rotation":0,"normal":[0, -1, 0],"vertices":[[-.5, -.5, -.5],[0.5, -.5, -.5],[0.5, -.5, 0.5],[-.5, -.5, 0.5]]},
    "UP": {"rotation":-1,"normal":[0, 1,0],"vertices":[[-.5, 0.5, -.5],[-.5, 0.5, 0.5],[0.5, 0.5, 0.5],[0.5, 0.5, -.5]]},
    "NORTH": {"rotation":1,"normal":[0, 0, -1],"vertices":[[-.5, -.5, -.5],[-.5, 0.5, -.5],[0.5, 0.5, -.5],[0.5, -.5, -.5]]},
    "SOUTH": {"rotation":0,"normal":[0, 0, 1],"vertices":[[-.5, -.5, 0.5],[0.5, -.5, 0.5],[0.5, 0.5, 0.5],[-.5, 0.5, 0.5]]},
    "WEST": {"rotation":1,"normal":[-1, 0, 0],"vertices":[[-.5, -.5, 0.5],[-.5, 0.5, 0.5],[-.5, 0.5, -.5],[-.5, -.5, -.5]]},
    "EAST": {"rotation":1,"normal":[1, 0, 0],"vertices":[[0.5, -.5, -.5],[0.5, 0.5, -.5],[0.5, 0.5, 0.5],[0.5, -.5, 0.5]]}
}

def load_texture(path:str) -> Image.Image:
    """Loads the texture at the specified path"""
    # Get specified texture or default if it does not exist
    if not os.path.exists(path):
        image = Image.new("RGBA", (2,2), (0,0,0))
        image.putpixel((0,0),(248,0,248))
        image.putpixel((1,1),(248,0,248))
    else: image = Image.open(path).convert('RGBA')

    # Crop image if it is animated
    if os.path.exists(path+".mcmeta"):
        width = image.width
        image = image.crop((0, 0, width, width))
    return image

def rotate_list(list:list, amount:int):
    """Rotates the list by the specified number of items"""
    a = int(amount) % len(list)
    return list[a:]+list[:a]

def _generate_face(direction:str, texture:Image.Image, uv:List[float], rotation:int) -> trimesh.Trimesh:
    # Get correct data from FACE_DATA
    data = FACE_DATA.get(direction.upper())
    rotate = data.get("rotation") + rotation/90
    vertices = data.get("vertices")
    normal = data.get("normal")

    # Calculate UV coordinates
    uv = np.divide(uv, 16)
    uv = [uv[0], 1-uv[3], uv[2], 1-uv[1]]
    uv = [uv[:2],[uv[2],uv[1]],uv[2:],[uv[0], uv[3]]]

    # Generate Material and Trimesh
    material = PBRMaterial(baseColorTexture=texture, alphaMode="MASK", alphaCutoff=0)
    visual = TextureVisuals(material=material, uv=rotate_list(uv, rotate))
    return trimesh.Trimesh(vertices, [[0, 1, 2 ,3]], [normal, normal], visual=visual, process=True, validate=True)

def _generate_box(faces:Dict[str, ElementFace], transform:List[List[float]]=np.eye(4)) -> List[trimesh.Trimesh]:
    meshes = []
    # Generate the necessary faces for the box
    for direction, face in faces.items():
        mesh = _generate_face(direction, load_texture(face.texture), face.uv, face.rotation)
        mesh.apply_transform(transform)
        meshes.append(mesh)
    return meshes

def pyrender_converter(model:MinecraftModel) -> pyrender.Mesh:
    """Converts a given `MinecraftModel` into a `pyrender.Mesh`"""

    trimeshes = []
    # Generate model elements
    for element in model.elements:
        size = np.subtract(element.end, element.start)
        location = element.start

        # Get Rotation
        pivot = [0, 0, 0]
        rotation = element.rotation
        x_rot, y_rot, z_rot = 0, 0, 0
        if rotation is not None:
            x_rot = rotation.angle if rotation.axis == "x" else 0
            y_rot = rotation.angle if rotation.axis == "y" else 0
            z_rot = rotation.angle if rotation.axis == "z" else 0
            pivot = rotation.origin

        # Compute Transformation Matrix
        transform = multiply_matricies(
            trans_mat(.5, .5, .5),
            scale_mat(*size),
            trans_mat(*location),
            
            trans_mat(*np.array(pivot) * -1),
            rotx_mat(x_rot),
            roty_mat(y_rot),
            rotz_mat(z_rot),
            trans_mat(*pivot)
        )

        trimeshes += _generate_box(element.faces, transform)
    
    mesh = pyrender.Mesh.from_trimesh(trimeshes, smooth=False)

    # Set Texture Filtering
    primitive:pyrender.Primitive
    for primitive in mesh.primitives:
        sampler = primitive.material.baseColorTexture.sampler
        sampler.magFilter = pyrender.constants.GLTF.NEAREST
        sampler.minFilter = pyrender.constants.GLTF.NEAREST

    return mesh


def get_display_matrix(display:ModelDisplay) -> List[List[float]]:
    """Computes the transformation matrix for the given `ModelDisplay`"""
    return multiply_matricies(
        trans_mat(-8, -8, -8),
        scale_mat(*display.scale),

        rotz_mat(display.rotation[2]),
        roty_mat(display.rotation[1]),
        rotx_mat(display.rotation[0]),

        trans_mat(*display.translation)
    )