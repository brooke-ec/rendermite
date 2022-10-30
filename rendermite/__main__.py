import argparse
import logging

logging.basicConfig(level="DEBUG", format="%(name)s [%(levelname)s] %(message)s")
logging.getLogger("trimesh").setLevel("WARN")
logging.getLogger("OpenGL.GL.shaders").setLevel("WARN")
logging.getLogger("OpenGL.arrays.arraydatatype").setLevel("WARN")
logging.getLogger("OpenGL.acceleratesupport").setLevel("WARN")
logging.getLogger("PIL.PngImagePlugin").setLevel("WARN")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="rendermite", description="Rendermite - A tool to generate the inventory icons for every Minecraft item.")
    parser.add_argument("-v", "--version", metavar="version", type=str, help="The version of Minecraft to generate from.", default="latest", required=True)
    parser.add_argument("-o", "--output", metavar="path", type=str, help="The output location to save the images.", default=r"./output/", required=False)
    parser.add_argument("-t", "--tempdir", metavar="path", type=str, help="The location minecraft assets should be temporarily downloaded to.", default=r"./tmp/", required=False)
    parser.add_argument("-p", "--processes", metavar="", type=int, help="The number of child processes used for generating textures", default=0, required=False)
    args = parser.parse_args()

    from rendermite.cli import run_generator
    run_generator(args.version, args.tempdir, args.output, args.processes)