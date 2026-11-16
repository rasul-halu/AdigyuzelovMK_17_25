#!/bin/sh
# Сравнение с настоящим npm: npm ls --all и порядок выполнения скриптов.
# Использование: scripts/compare_npm.sh <пакет> <версия>   (нужен Node.js)
cd "$(dirname "$0")/.." || exit 1
PKG=${1:-chalk}
VER=${2:-4.1.2}
OUT=$(pwd)/output
TMP=$(mktemp -d)
(cd "$TMP" && npm init -y >/dev/null && npm install "$PKG@$VER" --ignore-scripts --no-audit --no-fund >/dev/null \
  && npm ls --all > "$OUT/npm_ls_$PKG.txt" \
  && find node_modules -name package.json -maxdepth 3 -not -path '*/node_modules/*/node_modules/*/*' > "$OUT/npm_installed_$PKG.txt")
echo "npm ls --all: output/npm_ls_$PKG.txt"
cat "$OUT/npm_ls_$PKG.txt"
rm -rf "$TMP"
