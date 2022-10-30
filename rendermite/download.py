from rendermite.exceptions import InvalidVersionError
from io import BytesIO
import urllib.request
import zipfile
import logging
import json
import os

LOGGER = logging.getLogger(__name__)

VERSION_MANIFEST_URL = r"https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

def download_assets(version:str, output:str):
    """Downloads the Minecraft assets for the specified version into the specified output directory"""
    # LOCATE VERSION PACKAGE
    with urllib.request.urlopen(VERSION_MANIFEST_URL) as response:
        version_manifest = json.load(response)

    if version.startswith("latest"): # Get latest versions
        if version == "latest.release":
            version = version_manifest["latest"]["release"]
        elif version == "latest.snapshot":
            version = version_manifest["latest"]["snapshot"]
        else: version = version_manifest["latest"]["release"]

    package_info = next((p for p in version_manifest["versions"] if p["id"] == version), None)
    if package_info is None: raise InvalidVersionError() # Ensure version exists
    LOGGER.info("Fetching Package for %s %s", package_info["type"], package_info["id"])

    # GET VERSION PACKAGE
    with urllib.request.urlopen(package_info["url"]) as response:
        version_package = json.load(response)
    
    # DOWNLOAD ASSETS
    LOGGER.info("Downloading assets...")
    assets_url = version_package["downloads"]["client"]["url"]
    with urllib.request.urlopen(assets_url) as response:
        buffer = BytesIO(response.read())
    
    # EXTRACT ASSETS
    LOGGER.info("Extracting assets...")
    zip = zipfile.ZipFile(buffer)
    for zip_path in zip.namelist():
        if not zip_path.startswith("assets/"): continue
        output_path = os.path.join(output, zip_path[7:])
        directory, _ = os.path.split(output_path)
        os.makedirs(directory, exist_ok=True)
        with open(output_path, "wb") as file: file.write(zip.read(zip_path))
    
