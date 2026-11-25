"""Simple models of the bought parts on the optical Kuramoto bench.

These solids are for fit checks and renders only. They are not drawings of
the real parts. Each value says where it comes from.

Bench coordinates (all in millimetres):
  origin   centre of the beamsplitter cube, on the top face of the base plate
           in z (z = 0 is the plate top)
  +X       from the laser (-X) through the cube to mirror M1 (+X)
  +Y       from the detector (-Y) through the cube to mirror M2 (+Y)
  z_beam   height of the optical axis above the plate top
"""

import cadquery as cq

# Optical axis height. The KM100 optic centre is 25.4 mm above its base
# (Thorlabs drawing 6628-E0W, rev C). The DET10A2 active area is 25.0 mm
# above its base (Thorlabs drawing TTN133878-E0W, rev A), so the detector
# stands on a 0.4 mm pad.
Z_BEAM = 25.4

# Beamsplitter cube, Thorlabs BS013 (catalog: 25.4 mm cube).
CUBE = 25.4

# Michelson arms: distance from the cube centre to each mirror surface.
ARM = 50.0

# Laser modules (hardware_catalog.yml): Quarton VLM-650-03 is 7 x 21 mm,
# Thorlabs CPS635R has an 11 mm housing. A 12 mm sleeve fits 12 mm modules.
LASER_D = 7.0
LASER_L = 21.0
LASER_FRONT_X = -41.0           # front face of the laser module

# DET10A2 (Thorlabs drawing TTN133878-E0W).
DET_W = 49.8                    # along X
DET_H = 59.3                    # body height, without BNC and battery cap
DET_D = 20.3                    # body depth along Y, without the SM1 boss
DET_TOTAL_H = 70.9              # with the BNC connector
DET_BOSS_D = 25.9               # SM1 external thread, about 1.035 in
DET_BOSS_L = 2.2
DET_APERTURE_FROM_LEFT = 25.0   # active area, from the left side, front view
DET_PAD = Z_BEAM - 25.0         # 0.4 mm pad under the detector
DET_FRONT_Y = -40.0             # front face of the body (boss in front of it)
DET_TAP_FROM_FRONT = 12.8       # bottom 8-32 / M4 tap, from the front face
# BNC and battery cap positions on the top face are estimated from the
# drawing views (+-2 mm). They are not dimensioned.
DET_BNC = (-9.0, 10.0)          # x offset from the aperture, diameter
DET_CAP = (9.0, 13.0)

# KM100 kinematic mirror mount (Thorlabs drawing 6628-E0W, rev C).
KM_FACE = 49.9                  # width and height of the front face
KM_DEPTH = 21.1                 # plate stack, nominal
KM_KNOB_DEPTH = 38.4            # with the adjuster knobs
KM_OPTIC_FROM_SIDE = 25.4

# Ø1 inch mirror (BB1-E02 or PF10-03-P01): 25.4 mm diameter, 6 mm thick.
MIRROR_D = 25.4
MIRROR_T = 6.0

# Tang Nano 9K: see designs/tang-nano-9k-case/board.py.

# Comparator module. The TLV3501 SMA modules on sale have no published
# drawing. This is a generic block for renders only, not for fit checks.
COMP_SIZE = (22.0, 40.0, 1.6)   # x, y, PCB thickness
COMP_SMA_D = 6.4


def cylinder_x(d, x0, x1, y=0.0, z=Z_BEAM):
    return (cq.Workplane("YZ").workplane(offset=x0).center(y, z)
            .circle(d / 2).extrude(x1 - x0))


def cylinder_y(d, y0, y1, x=0.0, z=Z_BEAM):
    # Workplane XZ has its normal along -Y, so extrude toward -Y from y1.
    return (cq.Workplane("XZ").workplane(offset=-y1).center(x, z)
            .circle(d / 2).extrude(y1 - y0))


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def laser():
    return cylinder_x(LASER_D, LASER_FRONT_X - LASER_L, LASER_FRONT_X)


def cube():
    h = CUBE / 2
    return box(-h, h, -h, h, Z_BEAM - h, Z_BEAM + h)


def detector():
    x0 = -DET_APERTURE_FROM_LEFT
    y1 = DET_FRONT_Y
    y0 = y1 - DET_D
    z0 = DET_PAD
    body = box(x0, x0 + DET_W, y0, y1, z0, z0 + DET_H)
    body = body.edges("|Y").fillet(3.0)
    boss = cylinder_y(DET_BOSS_D, y1, y1 + DET_BOSS_L)
    ym = (y0 + y1) / 2
    top = z0 + DET_H
    for (dx, d), h in ((DET_BNC, DET_TOTAL_H - DET_H), (DET_CAP, 7.0)):
        body = body.union(cq.Workplane("XY").workplane(offset=top)
                          .center(dx, ym).circle(d / 2).extrude(h))
    return body.union(boss)


def km100(rotate=0):
    """KM100 for the mirror on +X (rotate=0) or +Y (rotate=90).

    The mirror surface sits at x = ARM, flush with the front face.
    """
    x0 = ARM
    y0 = -KM_OPTIC_FROM_SIDE
    body = box(x0, x0 + KM_DEPTH, y0, y0 + KM_FACE, 0.0, KM_FACE)
    body = body.cut(cylinder_x(25.4, x0 - 1, x0 + 7.0))
    for y, z in ((KM_FACE / 2 - 7.4, KM_FACE - 7.4), (KM_FACE / 2 - 7.4, 7.4)):
        body = body.union(cylinder_x(9.0, x0 + KM_DEPTH, x0 + KM_KNOB_DEPTH,
                                     y=y, z=z))
    return body.rotate((0, 0, 0), (0, 0, 1), rotate)


def mirror(rotate=0):
    m = cylinder_x(MIRROR_D, ARM, ARM + MIRROR_T)
    return m.rotate((0, 0, 0), (0, 0, 1), rotate)


def beam(d=1.2):
    """The light path, for renders and clearance checks.

    Laser to cube, cube to M1 and back, cube to M2 and back, cube to the
    detector. The two returned beams meet again in the cube.
    """
    h = CUBE / 2
    path = cylinder_x(d, LASER_FRONT_X, -h)
    path = path.union(cylinder_x(d, h, ARM))
    path = path.union(cylinder_y(d, h, ARM))
    path = path.union(cylinder_y(d, DET_FRONT_Y + DET_BOSS_L, -h))
    return path


def comparator(x, y, z):
    sx, sy, t = COMP_SIZE
    pcb = box(x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z, z + t)
    for dy in (-sy / 2, sy / 2 - 9.0):
        pcb = pcb.union(cylinder_y(COMP_SMA_D, y + dy, y + dy + 9.0, x=x,
                                   z=z + t + COMP_SMA_D / 2))
    return pcb
