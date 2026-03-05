# Scene Cut Subtitles

Pont entre [Scene Cut](https://scenecut.jondi-film.com) et VLC media player.
Permet de contrôler VLC (navigation, sous-titres) depuis l'interface Scene Cut.

## Téléchargement

Aller dans [**Releases**](../../releases/latest) et télécharger :

- **macOS** → `Scene_Cut_Subtitles_macOS.zip`
- **Windows** → `Scene_Cut_Subtitles_Windows.zip`

## Installation et utilisation

Voir [README_installation.md](README_installation.md) pour le guide complet.

## Développeurs — Build local

```bash
pip install pyinstaller websockets aiohttp
# macOS
./build_macos.sh
# Windows
build_windows.bat
```
