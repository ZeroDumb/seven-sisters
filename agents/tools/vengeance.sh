#!/bin/bash
echo "🔪 Kill command confirmed."

# Final clean-up and optional archive
rm -rf ./tmp/*
tar -czvf final_payload.tgz ./loot
echo "[The Bride] Strike complete."
