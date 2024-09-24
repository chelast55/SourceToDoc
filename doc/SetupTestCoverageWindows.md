The penultimate one (CMocka) is more complicated, as it has to be built from source.  
A Guide how to set it up can be found here: https://sam.hooke.me/note/2022/04/setting-up-cmocka/  
What is not mentioned in the guide, is that mingw32 (and mingw32-make) have to be installed: https://sourceforge.net/projects/mingw/ (make sure to manually enable mingw32-make)  
Additionally, an implementation of `strtok_r()` has to be added in `cmocka.c` (a public domain implementation of this function by Charlie Gordon can be found [here](http://groups.google.com/group/comp.lang.c/msg/2ab1ecbb86646684)).

The big problem arises at the final dependency: `lcov`.  
A windows build of lcov can be downloaded from [here](https://github.com/Farigh/lcov-for-windows).
Look for the newest release there and installation instructions are provided in the README file.
This generates various Perl scripts (without file extension), which should technically be runnable, as the mingw-step should also have installed Perl.  
For projects using Make or CMake, providing the path of these generated scripts should make running with test coverage evaluation and report generation possible. 

However, even after successful installation and even after ensuring the scripts are callable from the console from anywhere by just their name (
- adding the path to the scripts to the PATH environment variable
- adding a `.py`-extension and configuring windows
- adding `.py` to PATHEXT to make them executable
- following something like here to tell Windows how to execute Perl scripts using Perl automatically  

) ninja will likely still not find `lcov` and `genhtml` and thus **generating a report will fail**.

Until figuring out some way to "properly" install lcov on Windows at a "system level" (similar to using apt on Ubuntu), a passable workaround is installing `gcovr` via pip later (`pip install gcovr`), after installing all other python requirements.
Note, that this will generate a HTML report, but due to gcovrs hashed filenames, interlinking more than the Index pages is not possible.
