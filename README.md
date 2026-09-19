# Raspberry Pi A+ camera case (camera stands on the Pi)

A remix of two Thingiverse designs, both **Creative Commons Attribution-ShareAlike**, so this remix
is released under the same license with credit to:

- **Raspberry Pi A+ Case** by adafruit, thing:546427 (case base and lid)
- **Raspberry Pi Camera Stand** by atleberg, thing:274111 (camera box, back cover, hinge idea)

The Pi case is the stable base. A small hinge mount bolts to the lid and holds the camera box
standing up; it tilts on an M3 pin so the lens can be aimed at the 3D printer for timelapses.

## License

Released under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**, the same
license family as both originals. See [`LICENSE`](LICENSE) for the full text and
[`ATTRIBUTION.md`](ATTRIBUTION.md) for who made what and what was changed. You may share and adapt it,
including commercially, as long as you credit the original authors, say what you changed, and release
your version under the same license.

## Print list (`stl/`, all in print orientation, no supports)

| File | What | Notes |
|---|---|---|
| `pi-case.stl` | Case base | adafruit, with the USB opening widened to 22 x 11.8 mm for a WiFi dongle |
| `lid.stl` | Case lid | adafruit lid plus two 3.4 mm holes for the hinge mount |
| `hinge-mount.stl` | **New**: plate with two hinge ears | plate down, nut pockets underneath |
| `camera-box.stl` | Camera box | atleberg, unmodified |
| `camera-cover.stl` | Camera back cover | atleberg, unmodified |

0.2 mm layers, 3 walls, 20% infill. PLA or PETG. Adafruit suggests a 0.25 mm lid tolerance already built in.

## Hardware

- 1x **M3 x 25** screw and 1x M3 nut: the hinge pin (tighten the nut to hold the tilt angle).
- 2x **M3 x 5** screws and 2x M3 nuts: fasten the hinge mount to the lid.
- **#4-40** screws for the Pi (per adafruit), and whatever holds the camera board (see below).

## Assembly

1. Drop the two M3 nuts into the hex pockets on the underside of the hinge mount.
2. Set the mount on the outside of the lid over the two holes. From inside the lid, screw the two M3 x 5 screws up into the nuts.
3. Put the Pi in the case, thread the camera ribbon up through the lid slot, and snap the lid on.
4. Set the camera box's tab between the two ears and pass the M3 x 25 pin through. Tighten the nut just enough to hold the angle.

## Geometry

- The lid prints outer face down and goes on flipped; the hinge mount sits on its outer face.
- The pin hole in the camera box's tab is at y = -46.0, z = 3.5 in the box's frame (3.1 mm, measured from the mesh).
- Ear radius is 5.2 mm on purpose: the box's shoulders start 5.76 mm from the pin, so a bigger arch collides.
- `build_case.py` checks the swing: with the default hinge the box clears the case and lid from 90 degrees
  forward (pointing over the lid) through vertical to 110 degrees back (lens looking down).

## Confirmed from a photo of the real Pi A+

The CAMERA connector sits between the HDMI port and the audio jack, so the lid slot beside the hinge mount is the
camera cable slot. The DISPLAY (DSI) connector is at the other end, and the USB port is on the short edge.

## Assumptions still to verify

- **Camera board:** unknown. atleberg's box does not fit a v1.3 camera board; when the board is found, check the two
  posts and the lens hole, and adjust `camera-box.stl`.
- **USB WiFi dongle:** the widened opening is sized for a Cable Matters dongle with a ~15.5 mm body and an RP-SMA
  antenna plugged straight into the Pi's single USB port. Not test-fitted; the dongle's thickness is unknown.
- **Lid plate thickness** is taken as 1.5 mm from adafruit's listing.
- Print the camera box and cover alone first as a fit test.

## Rebuild

    /Applications/Blender.app/Contents/MacOS/Blender --background --python build_case.py

Edit the values at the top of `build_case.py` (hinge position, mount size, ear radius, screw sizes) and re-run;
it rewrites `stl/`, prints a mesh check and renders `preview/case-*.png`.
