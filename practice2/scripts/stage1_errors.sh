#!/bin/sh
# stage1_errors
cd "$(dirname "$0")/.." || exit 1
echo "=== config.xml (correct) ==="
python3 src/main.py config.xml
echo
echo "=== missing config file ==="
python3 src/main.py configs/errors/no_such_file.xml
echo
echo "=== bad_ascii_tree ==="
python3 src/main.py configs/errors/bad_ascii_tree.xml
echo
echo "=== bad_npm_name ==="
python3 src/main.py configs/errors/bad_npm_name.xml
echo
echo "=== bad_output_ext ==="
python3 src/main.py configs/errors/bad_output_ext.xml
echo
echo "=== bad_test_mode ==="
python3 src/main.py configs/errors/bad_test_mode.xml
echo
echo "=== bad_test_name ==="
python3 src/main.py configs/errors/bad_test_name.xml
echo
echo "=== bad_url ==="
python3 src/main.py configs/errors/bad_url.xml
echo
echo "=== bad_version ==="
python3 src/main.py configs/errors/bad_version.xml
echo
echo "=== broken_xml ==="
python3 src/main.py configs/errors/broken_xml.xml
echo
echo "=== depth_not_int ==="
python3 src/main.py configs/errors/depth_not_int.xml
echo
echo "=== depth_zero ==="
python3 src/main.py configs/errors/depth_zero.xml
echo
echo "=== duplicate_param ==="
python3 src/main.py configs/errors/duplicate_param.xml
echo
echo "=== empty_package ==="
python3 src/main.py configs/errors/empty_package.xml
echo
echo "=== missing_output_dir ==="
python3 src/main.py configs/errors/missing_output_dir.xml
echo
echo "=== missing_param ==="
python3 src/main.py configs/errors/missing_param.xml
echo
echo "=== missing_repo_file ==="
python3 src/main.py configs/errors/missing_repo_file.xml
echo
echo "=== unknown_param ==="
python3 src/main.py configs/errors/unknown_param.xml
echo
echo "=== wrong_root ==="
python3 src/main.py configs/errors/wrong_root.xml
echo
