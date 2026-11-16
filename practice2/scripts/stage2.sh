#!/bin/sh
# stage2
cd "$(dirname "$0")/.." || exit 1
echo "=== express 4.18.2 ==="
python3 src/main.py configs/express.xml
echo
echo "=== chalk 4.1.2 ==="
python3 src/main.py configs/chalk.xml
echo
echo "=== axios 1.6.0 ==="
python3 src/main.py configs/axios.xml
echo
