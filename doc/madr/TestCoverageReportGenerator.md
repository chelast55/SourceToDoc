<!-- based on this template: https://github.com/adr/madr/blob/develop/template/adr-template-minimal.md -->

# Testcoverage Report Generator

## Context and Problem Statement

We want to integrate testcoverage report generation into our toolchain. Therefore we had to choose a tool, that's accessible (i.e. free) and widely used, so our toolchain works on the majority of projects.

## Considered Options

* Gcovr
* LCOV

## Decision Outcome

We decided to go with lcov, as this was the easiest to integrate. Its html structure is optimal for inserting the links to doxygens output. Since it was the recommended tool by our tutor we also have the most experience with it. 

### Consequences

* Integration was easy and error detection swift.
* Windows support is less optimal (gcovr could potentially be better supported on windows).

## Pros and Cons of the Options

### Gcovr

* (+) Looks more modern and similar to doxygen awesome.
* (-) Linkig to doxygen is harder because the produced html isn't as simple and predetermined. 
* Availability not fully tested. We decided to go with LCOV before testing on windows.

### LCOV

* (+) Simple html makes linking to doxygen easy and robust.
* (-) Availability slightly less optimal, as the package available with pip ships with a genhtml executable that ninja doesn't recognize.
 
## More Information

We also considered usage of a css skin of lcov to make it look more modern, but its license was to constricting. 
Another attempt at making lcov look similar to doxygen was to edit its css ourselves at runtime. But our limited front end developing experience prevented useable results.