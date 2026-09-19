# Attribution and changes

This project is a remix of two Thingiverse designs. Both are licensed under Creative Commons
Attribution-ShareAlike, and this remix is released under **CC BY-SA 4.0** (see `LICENSE`).
The original authors do not endorse this remix.

## Raspberry Pi A+ Case

- **Title:** Raspberry Pi A+ Case
- **Author:** adafruit
- **Source:** https://www.thingiverse.com/thing:546427
- **License:** Creative Commons - Attribution - Share Alike (as listed on Thingiverse; the page does not show a version number)
- **Files used:** `piaplus-case.stl`, `piaplus-top.stl` (unmodified copies are in `originals/`)

**Changes made here:**
- `stl/pi-case.stl`: the USB opening in the short wall is widened from 17.5 x 10.1 mm to 22 x 11.8 mm so a USB WiFi dongle with an external antenna fits.
- `stl/lid.stl`: two 3.4 mm screw holes added so the hinge mount can be bolted to the lid.

## Raspberry Pi Camera Stand

- **Title:** Raspberry Pi Camera Stand
- **Author:** atleberg
- **Source:** https://www.thingiverse.com/thing:274111
- **License:** Creative Commons - Attribution - Share Alike (as listed on Thingiverse; the page does not show a version number)
- **Files used:** `camera_front_box_v003.stl`, `camera_back_cover_v002.stl`, `camera_stand_v001.stl` (unmodified copies are in `originals/`)

**Changes made here:**
- `stl/camera-box.stl` and `stl/camera-cover.stl` are unmodified copies of the original box and cover.
- The stand's round base is not used. Its hinge idea is reimplemented as a new `stl/hinge-mount.stl` that bolts to the Pi case lid, with the pin hole position measured from the original box mesh.

## New in this remix

- `stl/hinge-mount.stl`: mounting plate with two hinge ears and nut pockets.
- `build_case.py`: the Blender script that generates and checks every part in `stl/`.

Built with the help of Claude (Anthropic).
