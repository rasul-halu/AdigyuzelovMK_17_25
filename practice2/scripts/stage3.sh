#!/bin/sh
# stage3
cd "$(dirname "$0")/.." || exit 1
echo "=== diamond without cycles ==="
python3 src/main.py configs/test_simple.xml
echo
echo "=== package without dependencies ==="
python3 src/main.py configs/test_leaf.xml
echo
echo "=== cycle A-B-C-A ==="
python3 src/main.py configs/test_cycle.xml
echo
echo "=== two cycles B-D and E-E ==="
python3 src/main.py configs/test_complex.xml
echo
echo "=== max_depth=2 on chain A-F ==="
python3 src/main.py configs/test_deep2.xml
echo
echo "=== real package express, depth 3 ==="
python3 src/main.py configs/express.xml
echo
