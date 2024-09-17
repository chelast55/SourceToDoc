import subprocess
from shutil import rmtree, copytree
from pathlib import Path

#region commands
# Sets up build folder, has potential for custom commands by the user.
MESON_SETUP: list[str] = ["meson", "setup", "-Db_coverage=true"]
# Execute tests, gcov tracks covered lines.
NINJA_TEST: list[str] = ["ninja", "test"]
# Produce coverage report, file will be in a subfolder of the build directory.
NINJA_COVERAGE: list[str] = ["ninja", "coverage-html"]
#endregion

def run_meson(out_folder: Path, meson_build_location: Path, build_folder_name: Path = Path("build"), keep_build_folder: bool = False, meson_setup_args: list[str] = []):
    """
    Produce a test coverage report using the Meson + Ninja build system.

    Parameters
    ----------
    meson_build_location: Path
        Path to the root directory of the project. Where a "meson.build" file should be located.
    build_folder_name: Path
        Name the build folder will have. Can be nested (sub / build).
    meson_setup_args: list[str]
        Arguments passed to the Meson Setup step. --backend is not allowed!
    """
    build_folder: Path = meson_build_location / build_folder_name
    report_folder: Path = build_folder / "meson-logs" / "coveragereport"

    if build_folder.exists() and build_folder.is_dir():
        print(f"Deleting {build_folder}")
        rmtree(build_folder)

    subprocess.run(MESON_SETUP + [str(build_folder_name)] + meson_setup_args, cwd=meson_build_location)
    subprocess.run(NINJA_TEST, cwd=build_folder)
    subprocess.run(NINJA_COVERAGE, cwd=build_folder)

    if report_folder.exists() and report_folder.is_dir():  # if build failed or is impossible, there is nothing to copy
        copytree(report_folder, out_folder, dirs_exist_ok=True)
    if not keep_build_folder:
        rmtree(build_folder)

# if __name__ == '__main__':
#     # pathtest = str(Path(".").absolute())
#     path: Path = Path.home() / "SOURCE" / "libavtp"
#     run_meson(path)
