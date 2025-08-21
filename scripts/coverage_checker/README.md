# coverage_checker.py

Script to support check of the function coverage by Component Integration Tests. Will be depreciated once requirements are available as that's our metric for CIT.

``` text
usage: coverage_checker.py [-h] [-v {PUB,PUB_CRATE,PUB_SELF,PUB_SUPER}] [-t {CRATE,MOD,STRUCT,ENUM,TYPE,TRAIT,FN,CONST_FN,ASYNC_FN,ALL_FN}] [-r REFERENCE] [-o OUTPUT] input

Filter and compare Rust crate structure

positional arguments:
  input                 'cargo modules structure --package <package>' output file

options:
  -h, --help            show this help message and exit
  -v {PUB,PUB_CRATE,PUB_SELF,PUB_SUPER}, --visibility {PUB,PUB_CRATE,PUB_SELF,PUB_SUPER}
                        Visibility to filter (default: PUB)
  -t {CRATE,MOD,STRUCT,ENUM,TYPE,TRAIT,FN,CONST_FN,ASYNC_FN,ALL_FN}, --item-type {CRATE,MOD,STRUCT,ENUM,TYPE,TRAIT,FN,CONST_FN,ASYNC_FN,ALL_FN}
                        Item type to focus on (default: ALL_FN)
  -r REFERENCE, --reference REFERENCE
                        Reference result created by this script to copy comments from
  -o OUTPUT, --output OUTPUT
                        File to write output to (default: stdout)
```

## Prerequisities

* [cargo-module](https://crates.io/crates/cargo-modules)
  * Install by `cargo install cargo-modules`

## Example usage

`tabs 4` - required to display correctly tabs  
`cd <inc_orchestrator_repo>`  
`cargo modules structure --package orchestration | sed 's/\x1b\[[0-9;]*m//g' > input_report.txt` - sed is required to remove colored output  
`python3 coverage_checker.py -r <older_orchestration_report> input_report.txt`  

Next, it should be checked manually in generated output if some uncovered/newly added functions in crate are now covered by tests with latest revision.
