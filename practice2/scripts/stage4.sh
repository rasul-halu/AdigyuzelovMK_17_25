#!/bin/sh
# stage4
cd "$(dirname "$0")/.." || exit 1
echo "=== load order: diamond ==="
python3 src/main.py configs/test_simple.xml --load-order
echo
echo "=== load order: cycle ==="
python3 src/main.py configs/test_cycle.xml --load-order
echo
echo "=== load order: complex graph ==="
python3 src/main.py configs/test_complex.xml --load-order
echo
echo "=== load order: chalk ==="
python3 src/main.py configs/chalk.xml --load-order
echo
