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
# genhtml coverage.info --output-directory out
GENHTML: list[str] = ["genhtml", "coverage.info", "--output-directory", "coveragereport"]
#endregion

def run_cmake(out_folder: Path, 
              cmakelist_location: Path, 
              cmake_configure_args: list[str] = [".."], 
              cmake_build_args: list[str] = ["."], 
              ctest_args: list[str] = [],
              ctest_substitute: list[str] = [],
              build_folder_name: Path = Path("build"), 
              keep_build_folder: bool = False) -> None:
    """
    
    """
    build_folder: Path = cmakelist_location / build_folder_name
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
    if ctest_substitute is not None:
        subprocess.run(ctest_substitute, cwd=build_folder)
    else:
        subprocess.run(CTEST + ctest_args, cwd=build_folder)

    # creating coverage report
    subprocess.run(LCOV, cwd=build_folder)
    subprocess.run(GENHTML, cwd=build_folder)

    copytree(report_folder, out_folder, dirs_exist_ok=True)
    if not keep_build_folder:
        rmtree(build_folder)