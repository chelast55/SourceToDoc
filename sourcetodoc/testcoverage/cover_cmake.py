import subprocess
from shutil import rmtree, copytree 
from pathlib import Path

#region commands
# cmake configure
CMAKE_CONFIGURE: list[str] = ["cmake"]
# cmake --build
CMAKE_BUILD: list[str] = ["cmake", "--build"]

# ctest
CTEST: list[str] = ["ctest", "-VV"]

# lcov --capture --directory . --output-file coverage.info
LCOV: list[str] = ["lcov", "-c", "-d", ".", "-o", "coverage.info"]
# genhtml coverage.info --output-directory coveragereport
GENHTML: list[str] = ["genhtml", "coverage.info", "-o", "coveragereport"]
#endregion


def run_cmake(out_folder: Path, 
              project_root: Path, 
              cmake_configure_args: list[str] = [".."], 
              cmake_build_args: list[str] = ["."], 
              ctest_args: list[str] = [],
              ctest_substitute: list[str] = [],
              build_folder_name: Path = Path("build"), 
              keep_build_folder: bool = False) -> None:
    """
    Produce a test coverage report using the Cmake build system.

    Parameters
    ----------
    out_folder: Path
        The location to copy the testcoverage report into. To then link it to the Documentation.
    project_root: Path
        Path to the project root dir. In which the build folder will be created.
    cmake_configure_args: list[str]
        Arguments passed to the 'cmake' command. '..' by default. Executed in the build folder.
    cmake_build_args: list[str]
        Arguments passed to the 'cmake --build' command. '.' by default. Executed in the build folder.
    ctest_args: list[str]
        Arguments passed to the 'ctest' command. Executed in the build folder.
    ctest_substitute: list[str]
        Command to use instead of 'ctest' to execute tests. Executed in the build folder.
    build_folder_name: Path
        Name the build folder will have. Can be nested (sub / build).
    keep_build_folder: bool
        Wether to keep the freshly built build folder, or not.
    """
    build_folder: Path = project_root / build_folder_name
    report_folder: Path = build_folder / "coveragereport"

    # Deleting existing build folder
    if build_folder.exists() and build_folder.is_dir():
        print(f"Deleting {build_folder}")
        rmtree(build_folder)

    # Creating empty build folder, used in subsequent steps
    build_folder.mkdir()

    # Build steps execution
    subprocess.run(CMAKE_CONFIGURE + cmake_configure_args, cwd=build_folder)
    subprocess.run(CMAKE_BUILD + cmake_build_args, cwd=build_folder)

    # Run tests
    if ctest_substitute:
        subprocess.run(ctest_substitute, cwd=build_folder)
    else:
        subprocess.run(CTEST + ctest_args, cwd=build_folder)

    # creating coverage report
    subprocess.run(LCOV, cwd=build_folder)
    subprocess.run(GENHTML, cwd=build_folder)

    if report_folder.exists() and report_folder.is_dir():  # if build failed or is impossible, there is nothing to copy
        copytree(report_folder, out_folder, dirs_exist_ok=True)
    if not keep_build_folder:
        rmtree(build_folder)