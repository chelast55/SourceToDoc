import subprocess
from shutil import rmtree, copytree
from pathlib import Path

#region commands
# TODO describe commands
MESON_SETUP: list[str] = ["meson", "setup", "-Db_coverage=true"]
NINJA_TEST: list[str] = ["ninja", "test"]
NINJA_COVERAGE: list[str] = ["ninja", "coverage-html"]
#endregion

def run_meson(project_path: Path, build_folder_name: Path = Path("build"), meson_setup_args: list[str] = []):
    build_folder: Path = project_path / build_folder_name
    report_folder: Path = build_folder / "meson-logs" / "coveragereport"
    out_folder: Path = Path("out") / "testcoveragereport"

    if build_folder.exists() and build_folder.is_dir():
        print(f"Deleting {build_folder}")
        rmtree(build_folder)

    subprocess.run(MESON_SETUP + [str(build_folder_name)] + meson_setup_args, cwd=project_path)
    subprocess.run(NINJA_TEST, cwd=build_folder)
    subprocess.run(NINJA_COVERAGE, cwd=build_folder)

    copytree(report_folder, out_folder, dirs_exist_ok=True)
    # TODO: deleting build folder?

if __name__ == '__main__':
    # pathtest = str(Path(".").absolute())
    path: Path = Path.home() / "SOURCE" / "libavtp"
    run_meson(path)

