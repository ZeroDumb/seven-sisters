#!/bin/bash
echo "☠️ Slide. Just... slide."

# Tampering and weird headers
curl -s -H "X-Break-The-System: true" "$1"
# Or plug into Burp via repeater proxy
