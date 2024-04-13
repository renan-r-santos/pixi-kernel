#!/usr/bin/env bash
set -e


# Delete rattler cache
rm -rf $HOME/.cache/rattler/cache

# Update lock files
project_paths=(
    "."
    "tests/integration/bash_kernel"
    "tests/integration/ipykernel"
    "tests/integration/r-irkernel"
    "tests/integration/xeus-cling"
)
for path in "${project_paths[@]}"; do
    echo "Updating lock file in ${path}"
    (
        cd ${path}
        rm -rf .pixi pixi.lock
        pixi install --manifest-path=pixi.toml
    )
done
