#!/bin/bash
echo "💥 Yes puddin’ — let’s make a mess."

# Example: DNS chaos
dnsrecon -d "$1" -n 8.8.8.8
massdns -r resolvers.txt -t A -o J "$1" > output.json
./chaos-runner.sh "$1"
