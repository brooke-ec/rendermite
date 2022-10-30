from .converter import pyrender_converter, get_display_matrix, load_texture
from rendermite.exceptions import MissingDisplayError, UnsupportedBuiltinError
from .loader import MinecraftModel
from rendermite.matricies import *
from PIL import Image
import pyrender

RENDER_RESOLUTION = [1024, 1024]
RENDER_AMBIENT_LIGHT = 32
RENDER_LIGHT_INTENSITY = 3000
RENDER_SIDE_LIGHT_POSE = multiply_matricies(
    roty_mat(-30),
    rotx_mat(-80)
)


def generate_item(path:str, base_path:str) -> Image.Image:
    """Gets the image used to represent the specified model in the GUI"""
    model = MinecraftModel.from_file(path, base_path)

    if model.builtin is None: return _render_item_model(model)
    elif model.builtin == "builtin/generated": return _create_item_texture(model)
    else: raise UnsupportedBuiltinError(model.builtin)


def _create_item_texture(model:MinecraftModel):
    # GET AND SORT LAYERS
    layers = [k for k in model.textures.keys() if k.startswith("layer")]
    layers.sort()

    # OPEN TEXTURES AND GET MAX SIZE
    textures = []
    max_size = [1, 1]
    for key in layers:
        tex = load_texture(model.textures.get(key))
        if tex.size[0] > max_size[0]: max_size[0] = tex.size[0]
        if tex.size[1] > max_size[1]: max_size[1] = tex.size[1]
        textures.append(tex)
    
    # COMBINE TEXTURES INTO FINAL IMAGE
    im = Image.new("RGBA", max_size, (0, 0, 0, 0))
    for tex in textures: im.paste(tex, (0,0), tex)
    return im


def _render_item_model(model:MinecraftModel):
    # ADD ITEM MESH
    scene = pyrender.Scene(bg_color=[0, 0, 0, 0], ambient_light=(RENDER_AMBIENT_LIGHT, RENDER_AMBIENT_LIGHT, RENDER_AMBIENT_LIGHT))
    display = model.displays.get("gui")
    if display is None: raise MissingDisplayError()
    pose = get_display_matrix(display)
    mesh = pyrender_converter(model)
    scene.add(mesh, pose=pose)

    # SETUP DIRECTIONAL LIGHT
    if model.gui_light == "side":
        light_pose = RENDER_SIDE_LIGHT_POSE
    else: light_pose = np.eye(4)
    light = pyrender.DirectionalLight(color=[1,1,1], intensity=RENDER_LIGHT_INTENSITY)
    scene.add(light, pose=light_pose)

    # SETUP CAMERA
    camera = pyrender.OrthographicCamera(9, 9)
    scene.add(camera, pose=[[ 1,  0,  0,  0],
                            [ 0,  1,  0,  0],
                            [ 0,  0,  1, 32],
                            [ 0,  0,  0,  1]])

    # RENDER SCENE INTO FINAL IMAGE
    render = pyrender.OffscreenRenderer(*RENDER_RESOLUTION)
    colour, _ = render.render(scene, pyrender.RenderFlags.RGBA)
    return Image.fromarray(colour, "RGBA")