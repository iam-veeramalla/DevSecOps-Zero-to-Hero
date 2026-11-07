#!/bin/bash

if git diff --cached | grep -i "secret"; then
    echo "secret detected "
    exit 1
fi

echo "commit"
