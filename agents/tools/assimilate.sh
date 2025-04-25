#!/bin/bash
echo "▶️ Initiating command protocol... All paths now lead to assimilation."
# Parse input commands and assign agents
AGENT=$1
shift
echo "[Seven] Delegating mission to $AGENT..."
./../$AGENT/run.sh "$@"
