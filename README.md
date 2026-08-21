# 🚀 BALI SPACE EXPERIENCE

A ready-to-build Windows fullscreen audio-reactive visual system for BALI.

## Download
After the Windows workflow completes, open **Releases → BALI SPACE EXPERIENCE — Windows Latest** and download:

- `BALI_SPACE_EXPERIENCE_Setup.exe` — installer (recommended)
- `BALI_SPACE_EXPERIENCE.exe` — portable version

## What it does
- 16:9 fullscreen club / LED-screen visual
- captures Windows system audio using WASAPI loopback
- analyzes bass / mids / highs in real time
- estimates beats and BPM
- BALI bear astronaut floats and pulses with the music
- procedural stars accelerate with track energy
- asteroid field reacts to tempo and energy
- Earth rotates faster with the track
- high-energy moments enter a warp-speed visual state
- golden beat flashes and glow accents
- automatic demo motion if system-audio capture is unavailable

## BALI astronaut design
The application generates its mascot asset during the Windows build so the repository stays lightweight. The character keeps the defining visual language:

- bear-shaped helmet with two integrated round ears
- white spacesuit
- gold helmet / visor / trim
- red chest panel with `BALI NIGHTCLUB`

## Controls
- `Esc` or `Q` — exit
- `H` or `F1` — show/hide status overlay

## Windows build
Every push to `main` automatically runs GitHub Actions, packages the app with PyInstaller, builds an Inno Setup installer and publishes both files to the rolling `windows-latest` GitHub Release.

## Local build
```powershell
pip install -r requirements.txt
python generate_asset.py
pip install pyinstaller
pyinstaller --clean BaliSpaceExperience.spec
```

Windows 10/11 x64 is supported. For large 4K club displays, a dedicated GPU is recommended.
