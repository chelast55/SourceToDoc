import subprocess
import shutil
from pathlib import Path

def run_meson(path_to_repo : Path, additional_args : list[str] = []):
    build_folder : Path = path_to_repo / "build"
    if build_folder.exists() and build_folder.is_dir():
        shutil.rmtree(build_folder)
    subprocess.run(["meson", "setup", "-Db_coverage=true", "build"] + additional_args, cwd=path_to_repo)
    subprocess.run(["ninja", "-C", "build", "test"], cwd=path_to_repo)
    subprocess.run(["ninja", "-C", "build", "coverage-html"], cwd=path_to_repo)

if __name__ == '__main__':
    path : Path = Path.home() / "SOURCE" / "libavtp"
    run_meson(path)

#     subprocess.run([""])
