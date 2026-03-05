# Scene Cut Subtitles — Guide d'installation

**Scene Cut Subtitles** est un petit programme à installer sur votre ordinateur.
Il fait le lien entre Scene Cut (dans votre navigateur) et VLC media player.

---

## Prérequis

- VLC media player installé ([vlc.me](https://www.videolan.org/vlc/))
- Scene Cut ouvert dans votre navigateur

---

## Installation (une seule fois)

### macOS

1. Télécharger `Scene_Cut_Subtitles_macOS.zip`
2. Double-cliquer sur le `.zip` pour extraire
3. Glisser **Scene Cut Subtitles.app** dans votre dossier `/Applications`
4. Au premier lancement : clic droit sur l'app → **Ouvrir** → confirmer
   *(macOS demande une confirmation la première fois pour les apps tierces)*

### Windows

1. Télécharger `Scene_Cut_Subtitles_Windows.zip`
2. Extraire le `.zip` dans un dossier de votre choix (ex. `Bureau`)
3. Double-cliquer sur **Scene Cut Subtitles.exe**
   *(Windows Defender peut afficher un avertissement — cliquer "Informations complémentaires" puis "Exécuter quand même")*

---

## Configuration VLC (une seule fois)

Cette étape active l'interface de contrôle de VLC que Scene Cut utilise.

1. Ouvrir VLC
2. Aller dans **VLC → Préférences** (macOS) ou **Outils → Préférences** (Windows)
3. En bas à gauche, cliquer **Tout afficher**
4. Dans le panneau gauche : **Interface → Interfaces principales**
5. Cocher la case **Web**
6. Toujours dans le panneau gauche : **Interface → Lua → Lua HTTP**
7. Dans le champ **Mot de passe**, saisir : `scenecut`
8. Cliquer **Enregistrer**
9. **Fermer et relancer VLC**

---

## Utilisation au quotidien

1. Lancer **VLC** et ouvrir votre film
2. Lancer **Scene Cut Subtitles** (double-clic sur l'app)
3. Une petite fenêtre apparaît — attendre que le statut passe au vert
4. Dans Scene Cut, aller dans le module **Sous-titres**
5. Cliquer **Connecter VLC**

La fenêtre Scene Cut Subtitles affiche alors "Scene Cut connecté" en vert.
Vous pouvez maintenant naviguer dans la vidéo depuis Scene Cut et envoyer
les sous-titres vers VLC.

---

## En cas de problème

| Symptôme | Solution |
|---|---|
| "VLC non détecté" en rouge | Vérifier que VLC est lancé et que l'interface Web est activée (voir configuration) |
| La connexion ne se fait pas | Vérifier que le mot de passe VLC est bien `scenecut` |
| macOS bloque l'ouverture | Clic droit → Ouvrir → Confirmer |
| Windows bloque l'ouverture | Cliquer "Informations complémentaires" → "Exécuter quand même" |
