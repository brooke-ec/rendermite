from rendermite.exceptions import OrphanModelError, MissingDisplayError, UnsupportedBuiltinError
from rendermite.download import download_assets
from rendermite.generator import generate_item
from urllib.error import HTTPError
from multiprocessing import Pool
from itertools import repeat
import logging
import shutil
import os

LOGGER = logging.getLogger("rendermite")

def process_model(model:str, base:str, output:str):
    try: im = generate_item(f"minecraft:item/{model}", base)
    except (OrphanModelError, MissingDisplayError, UnsupportedBuiltinError) as ex:
        LOGGER.warning("Error generating %s: %s", model, ex)
        return
    im.save(open(os.path.join(output, f"{model}.png"), "wb"), "png")
    print(f"Generated {model}")

def run_generator(version:str, temp_dir:str, output:str, max_children:int):
    try:
        download_assets(version, temp_dir)
        items_location = os.path.join(temp_dir, "minecraft", "models", "item")
        models = [os.path.splitext(x)[0] for x in os.listdir(items_location)]
        LOGGER.info(f"Found {len(models)} items to generate")
        os.makedirs(output, exist_ok=True)
        if max_children < 2:
            for model in models: process_model(model, temp_dir, output)
        else:
            with Pool(max_children) as p:
                p.starmap(process_model, zip(models, repeat(temp_dir), repeat(output)))
    except HTTPError as ex:
        LOGGER.error(f"Could not download assets: {ex}")
    shutil.rmtree(temp_dir)
    LOGGER.info("DONE!")