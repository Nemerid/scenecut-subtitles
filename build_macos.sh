#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  build_macos.sh — Construit Scene Cut Subtitles.app + archive de distribution
#  Usage : ./build_macos.sh
#  Résultat : dist/Scene_Cut_Subtitles_macOS.zip
# ─────────────────────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")"

APP_NAME="Scene Cut Subtitles"
DIST_DIR="dist"
ARCHIVE="${DIST_DIR}/Scene_Cut_Subtitles_macOS.zip"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Build — ${APP_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Vérifier Python
echo "[1/4] Vérification Python…"
python3 --version

# 2. Installer les dépendances de build
echo "[2/4] Installation des dépendances…"
pip3 install --quiet --upgrade pyinstaller websockets aiohttp

# 3. Construire le .app
echo "[3/4] PyInstaller…"
pyinstaller scenecut_subtitles.spec --clean --noconfirm

# 4. Créer l'archive zip de distribution
echo "[4/4] Création de l'archive…"
cd "${DIST_DIR}"
rm -f "../${ARCHIVE}"
zip -r --quiet "Scene_Cut_Subtitles_macOS.zip" "${APP_NAME}.app"
cd ..

echo ""
echo "  ✓ Build terminé !"
echo "  Fichier : ${ARCHIVE}"
echo ""
echo "  Pour distribuer : copier ce .zip aux utilisateurs."
echo "  Ils extraient et glissent l'app dans /Applications."
echo ""
