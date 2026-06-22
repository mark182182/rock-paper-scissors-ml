#!/bin/bash

if ! [ -d .venv ]; then
    
    uv sync
    
fi

. .venv/bin/activate


while getopts ":pt" option; do
    case $option in
        p)
            echo "Running main plays"
            python boilerplate-rock-paper-scissors/main.py
        exit;;
        t)
            echo "Testing plays"
            python boilerplate-rock-paper-scissors/test_module.py
        exit;;
        *)
            echo "Unhandled option. Exiting."
        exit;;
    esac
done

