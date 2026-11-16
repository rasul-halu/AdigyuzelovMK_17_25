#!/bin/sh
# stage5
cd "$(dirname "$0")/.." || exit 1
echo "=== test: diamond ==="
python3 src/main.py configs/test_simple.xml
echo
echo "=== test: cycle ==="
python3 src/main.py configs/test_cycle.xml
echo
echo "=== test: complex ==="
python3 src/main.py configs/test_complex.xml
echo
echo "=== express ==="
python3 src/main.py configs/express.xml
echo
echo "=== chalk ==="
python3 src/main.py configs/chalk.xml
echo
echo "=== axios ==="
python3 src/main.py configs/axios.xml
echo
