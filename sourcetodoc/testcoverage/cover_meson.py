import subprocess
from shutil import rmtree, copytree
from pathlib import Path

#region commands
# TODO describe commands
MESON_SETUP: list[str] = ["meson", "setup", "-Db_coverage=true"]
NINJA_TEST: list[str] = ["ninja", "test", "-C"]
NINJA_COVERAGE: list[str] = ["ninja", "coverage-html", "-C"]
#endregion

def run_meson(path_to_repo: Path, relative_build_path: Path = Path("build"), additional_args: list[str] = []):
    build_folder: Path = path_to_repo / relative_build_path
    if build_folder.exists() and build_folder.is_dir():
        print(f"Deleting {build_folder}")
        rmtree(build_folder)
    subprocess.run(MESON_SETUP + [str(relative_build_path)] + additional_args, cwd=path_to_repo)
    subprocess.run(NINJA_TEST + [str(relative_build_path)], cwd=path_to_repo)
    subprocess.run(NINJA_COVERAGE + [str(relative_build_path)], cwd=path_to_repo)


# if __name__ == '__main__':
#     path : Path = Path.home() / "SOURCE" / "libavtp"
#     run_meson(path)

#     subprocess.run([""])
