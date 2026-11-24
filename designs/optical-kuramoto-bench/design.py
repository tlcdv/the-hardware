"""OKB-BENCH: optical Kuramoto bench, a printed base for a small optical loop.

One rigid base holds the four blocks of the desktop loop on
/photonic-substrate/:

  Block 1  laser cradle (-X). One 16.4 mm bore with an M3 lock screw and
           printed split sleeves for 7, 11 and 12 mm laser modules.
  Block 2  seat for the 25.4 mm 50:50 beamsplitter cube (centre) and two
           mirror pads (+X and +Y) for a Michelson interferometer. Each pad
           takes a Thorlabs KM100 or the printed kinematic mount in this
           design (same optic height, same screw slot).
  Block 3  seat for the Thorlabs DET10A2 detector (-Y), a tray for a fast
           comparator module, and the Tang Nano 9K bay (the same bay and lid
           as designs/tang-nano-9k-case).
  Block 4  the oscilloscope is not on the bench. The detector BNC and the
           comparator SMA cables go to it.

Printed parts:
  base     the plate with all seats, feet and the FPGA bay
  shroud   a light cover over the optical path (open bottom, sits on a lip)
  lid      the FPGA bay lid with the Boltzmann vents (from tang-nano-9k-case)
  sleeve-7mm, sleeve-11mm, sleeve-12mm
  mirror-bracket, mirror-plate   printed kinematic mount, print two of each

Variants (NOTICE):
  store     part number and licence only. For print services.
  branded   compass mark on the shroud and the lid, source URL under the
            base. Personal prints only, never sold.

All dimensions in millimetres. Coordinates: see components.py.
"""

import importlib.util
import os
import sys

import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))

import components as c  # noqa: E402
from common import style  # noqa: E402


def _load_case():
    path = os.path.join(HERE, "..", "tang-nano-9k-case", "case.py")
    spec = importlib.util.spec_from_file_location("okb_tn9k_case", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


case = _load_case()
b = case.b                      # Tang Nano 9K board geometry

DESIGN_ID = "OKB-BENCH"
VERSION = "0.1.0"
SOURCE_URL = "github.com/tlcdv/the-hardware"

# Print fit. 0.2 mm per side suits PETG on FDM and nylon on MJF.
FIT = 0.2
WALL = style.WALL
PLATE = 5.0                     # base plate thickness
Z_PLATE_BOTTOM = -PLATE
FOOT = 18.0                     # feet height under the plate (room for
FOOT_SIZE = 18.0                # jumper wires on the FPGA header pins)
M3_INSERT_D = 4.0               # hole for an M3 heat-set insert
M3_INSERT_DEPTH = 5.0
M3_CLEAR = 3.4
M4_CLEAR = 4.5

# Optical zone: the shroud covers it.
OPT_X = (-68.0, 92.0)           # shroud inner faces
OPT_Y = (-64.0, 92.0)
SHROUD_TOP_Z = 64.0             # outer top of the shroud
SHROUD_INNER_Z = SHROUD_TOP_Z - WALL
LIP_WIDTH = case.LIP_WIDTH
LIP_HEIGHT = case.LIP_HEIGHT
LIP_GAP = case.LIP_GAP

# FPGA bay: the tang-nano-9k-case base turned by -90 degrees, so the HDMI
# end faces -Y and the USB-C end is at the +Y edge of the base.
BAY_X = 112.0
BAY_Y_MAX = 97.0
BAY_Y = BAY_Y_MAX - case.OUTER_L / 2
BAY_Z = -case.Z_BOTTOM + Z_PLATE_BOTTOM      # PCB bottom in bench z (0.0)

BASE_X = (OPT_X[0] - WALL - 3.0, BAY_X + case.OUTER_W / 2)
BASE_Y = (OPT_Y[0] - WALL - 3.0, BAY_Y_MAX)

# Block 1: laser cradle.
CRADLE_X = (-64.0, -40.0)
CRADLE_W = 26.0
SLEEVE_OD = 16.0
BORE_D = SLEEVE_OD + 2 * FIT
SLEEVE_L = 22.0
SLEEVE_SLIT = 1.5
CRADLE_TOP = c.Z_BEAM + BORE_D / 2 + 7.0
SLEEVES = {"sleeve-7mm": 7.0, "sleeve-11mm": 11.0, "sleeve-12mm": 12.0}

# Block 2: cube seat.
SEAT_POCKET = c.CUBE + 2 * FIT
SEAT_OUTER = SEAT_POCKET + 2 * 3.6
SEAT_FLOOR = c.Z_BEAM - c.CUBE / 2       # cube bottom face
SEAT_TOP = SEAT_FLOOR + 3.0

# Mirror pads: an M4 slot along the arm under each mount.
PAD_SLOT = (c.ARM + 8.0, c.ARM + 24.0)

# Printed kinematic mount (in +X orientation, mirror surface at x = ARM).
MP_FRONT = c.ARM + 2.0          # mirror stands 2 mm proud of the plate
MP_T = 8.0
MP_SIZE = 48.0
MP_POCKET_D = c.MIRROR_D + 2 * FIT
MP_POCKET_DEPTH = 4.0
MP_APERTURE = 22.0
MB_GAP = 2.0
MB_BACK_X = MP_FRONT + MP_T + MB_GAP
MB_BACK_T = 6.0
MB_FOOT_X = (MB_BACK_X, c.ARM + 30.0)
MB_FOOT_T = 5.0
MP_Z0 = c.Z_BEAM - MP_SIZE / 2
ADJUST = [(-17.0, -17.0), (17.0, -17.0), (-17.0, 17.0)]   # pivot, H, V
PULL = [(17.0, 17.0), (0.0, -20.0)]

# Block 3: detector seat and comparator tray.
DET_RIM = 1.6
DET_RIM_H = 2.5
COMP_X = (98.0, 126.0)
COMP_Y = (-64.0, 16.0)
COMP_HOLES_X = (102.0, 122.0)


def _rbox(x0, x1, y0, y1, z0, z1, r):
    part = c.box(x0, x1, y0, y1, z0, z1)
    return part.edges("|Z").fillet(r) if r > 0 else part


def _bay_place(shape):
    return (shape.rotate((0, 0, 0), (0, 0, 1), -90)
            .translate((BAY_X, BAY_Y, BAY_Z)))


def _bay_base():
    """The tang-nano-9k-case base, without its engraving, in bench place."""
    engrave = case._engrave_bottom
    case._engrave_bottom = lambda part, lines, size: part
    try:
        bay = case.build_base("store")
    finally:
        case._engrave_bottom = engrave
    return _bay_place(bay)


def _bay_footprint(z0, z1, grow=0.0):
    block = case._rounded_block(case.OUTER_L + 2 * grow,
                                case.OUTER_W + 2 * grow, z0, z1,
                                style.EDGE_RADIUS + grow)
    return block.rotate((0, 0, 0), (0, 0, 1), -90).translate((BAY_X, BAY_Y, 0))


def _header_slots():
    xs = b.header_x_positions()
    slot_len = xs[-1] - xs[0] + 3.4
    cut = None
    for y in (-b.HEADER_ROW_Y, b.HEADER_ROW_Y):
        s = (cq.Workplane("XY").workplane(offset=case.Z_BOTTOM - 1)
             .center((xs[0] + xs[-1]) / 2, y).slot2D(slot_len, 3.4)
             .extrude(case.FLOOR + 2))
        cut = s if cut is None else cut.union(s)
    return _bay_place(cut)


def _engrave_bottom(part, lines, size, centre):
    plane = cq.Plane(origin=(centre[0], centre[1], Z_PLATE_BOTTOM),
                     xDir=(1, 0, 0), normal=(0, 0, -1))
    wp = cq.Workplane(plane)
    step = size * 1.6
    y0 = step * (len(lines) - 1) / 2
    for i, line in enumerate(lines):
        text = wp.center(0, y0 - i * step).text(
            line, size, -style.ENGRAVE_DEPTH, combine=False,
            halign="center", valign="center")
        part = part.cut(text)
    return part


def _cradle():
    x0, x1 = CRADLE_X
    block = _rbox(x0, x1, -CRADLE_W / 2, CRADLE_W / 2, 0.0, CRADLE_TOP, 3.0)
    block = block.faces(">Z").edges().chamfer(style.EDGE_CHAMFER)
    block = block.cut(c.cylinder_x(BORE_D, x0 - 1, x1 + 1))
    xm = (x0 + x1) / 2
    insert = (cq.Workplane("XY").workplane(offset=CRADLE_TOP - M3_INSERT_DEPTH)
              .center(xm, 0).circle(M3_INSERT_D / 2).extrude(M3_INSERT_DEPTH + 1))
    screw = (cq.Workplane("XY").workplane(offset=c.Z_BEAM)
             .center(xm, 0).circle(M3_CLEAR / 2).extrude(CRADLE_TOP))
    return block.cut(insert).cut(screw)


def _cube_seat():
    h = SEAT_OUTER / 2
    seat = _rbox(-h, h, -h, h, 0.0, SEAT_TOP, 2.0)
    p = SEAT_POCKET / 2
    pocket = c.box(-p, p, -p, p, SEAT_FLOOR, SEAT_TOP + 1)
    corners = (cq.Workplane("XY").workplane(offset=SEAT_FLOOR - 0.6)
               .pushPoints([(sx * p, sy * p) for sx in (-1, 1) for sy in (-1, 1)])
               .circle(1.5).extrude(SEAT_TOP))
    return seat.cut(pocket).cut(corners)


def _det_rim():
    x0 = -c.DET_APERTURE_FROM_LEFT - FIT - DET_RIM
    x1 = x0 + c.DET_W + 2 * (FIT + DET_RIM)
    y1 = c.DET_FRONT_Y + FIT + DET_RIM
    y0 = c.DET_FRONT_Y - c.DET_D - FIT - DET_RIM
    rim = _rbox(x0, x1, y0, y1, 0.0, DET_RIM_H, 2.0)
    inner = c.box(x0 + DET_RIM, x1 - DET_RIM, y0 + DET_RIM, y1 - DET_RIM,
                  c.DET_PAD, DET_RIM_H + 1)
    # Open the front so the SM1 boss and the light are never blocked.
    front = c.box(-16.0, 16.0, y1 - DET_RIM - 0.5, y1 + 1, c.DET_PAD,
                  DET_RIM_H + 1)
    return rim.cut(inner).cut(front)


def _slot_cut(x0, x1, y, rotate):
    s = (cq.Workplane("XY").workplane(offset=Z_PLATE_BOTTOM - 1)
         .center((x0 + x1) / 2, y).slot2D(x1 - x0, M4_CLEAR)
         .extrude(PLATE + 2))
    return s.rotate((0, 0, 0), (0, 0, 1), rotate)


def _axis_marks():
    """Shallow lines on the plate top along both arms and to the detector."""
    w, d = 0.8, 0.4
    marks = c.box(c.ARM - 4, c.ARM + 26, -w / 2, w / 2, -d, 0.1)
    marks = marks.union(c.box(-w / 2, w / 2, c.ARM - 4, c.ARM + 26, -d, 0.1))
    return marks


def _feet():
    s = FOOT_SIZE
    x0, x1 = BASE_X
    y0, y1 = BASE_Y
    spots = [(x0, y0), (x0, y1 - s), (20.0, y0), (20.0, y1 - s),
             (x1 - s, y0), (x1 - s, BAY_Y - case.OUTER_L / 2 - s - 2.0)]
    feet = None
    for fx, fy in spots:
        f = _rbox(fx, fx + s, fy, fy + s, Z_PLATE_BOTTOM - FOOT,
                  Z_PLATE_BOTTOM + 0.01, 3.0)
        feet = f if feet is None else feet.union(f)
    return feet


def build_base(variant="store"):
    x0, x1 = BASE_X
    y0, y1 = BASE_Y
    plate = _rbox(x0, x1, y0, y1, Z_PLATE_BOTTOM, 0.0, style.EDGE_RADIUS)
    plate = plate.cut(_bay_footprint(Z_PLATE_BOTTOM - 1, 20.0))
    plate = plate.union(_bay_base())
    # Fill the chamfer groove where the bay bottom meets the plate.
    plate = plate.union(_bay_footprint(Z_PLATE_BOTTOM, Z_PLATE_BOTTOM + 1.0))
    plate = plate.cut(_header_slots())

    # Lip for the shroud.
    ox0, ox1 = OPT_X
    oy0, oy1 = OPT_Y
    r_in = style.EDGE_RADIUS - WALL
    lip = _rbox(ox0 - LIP_WIDTH, ox1 + LIP_WIDTH, oy0 - LIP_WIDTH,
                oy1 + LIP_WIDTH, 0.0, LIP_HEIGHT, r_in + LIP_WIDTH)
    lip = lip.cut(_rbox(ox0, ox1, oy0, oy1, -1, LIP_HEIGHT + 1, r_in))
    plate = plate.union(lip)

    plate = plate.union(_cradle()).union(_cube_seat()).union(_det_rim())

    # Mount slots under M1 (+X) and M2 (+Y), and the detector screw hole.
    plate = plate.cut(_slot_cut(PAD_SLOT[0], PAD_SLOT[1], 0.0, 0))
    plate = plate.cut(_slot_cut(PAD_SLOT[0], PAD_SLOT[1], 0.0, 90))
    tap_y = c.DET_FRONT_Y - c.DET_TAP_FROM_FRONT
    plate = plate.cut(cq.Workplane("XY").workplane(offset=Z_PLATE_BOTTOM - 1)
                      .center(0, tap_y).circle(M4_CLEAR / 2).extrude(PLATE + 2))
    plate = plate.cut(_axis_marks())

    # Comparator tray: a grid of M3 insert holes and two cable-tie slots.
    holes = [(hx, hy) for hx in COMP_HOLES_X
             for hy in range(int(COMP_Y[0]) + 4, int(COMP_Y[1]), 10)]
    plate = plate.cut(cq.Workplane("XY").workplane(offset=-M3_INSERT_DEPTH + 1)
                      .pushPoints(holes).circle(M3_INSERT_D / 2).extrude(5))
    ties = [((COMP_X[0] + COMP_X[1]) / 2, y) for y in (-40.0, -10.0)]
    plate = plate.cut(cq.Workplane("XY").workplane(offset=Z_PLATE_BOTTOM - 1)
                      .pushPoints(ties).slot2D(5.0, 2.4).extrude(PLATE + 2))

    # Room for an HDMI plug in front of the bay.
    hy = BAY_Y - case.OUTER_L / 2
    plate = plate.cut(c.box(BAY_X - 11, BAY_X + 11, hy - 22, hy + 0.5,
                            -2.5, 1.0))

    lines = [f"{DESIGN_ID} v{VERSION}", "CERN-OHL-S-2.0"]
    if variant == "branded":
        lines.append(SOURCE_URL)
    plate = _engrave_bottom(plate, lines, 4.0, (5.0, 15.0))
    return plate.union(_feet())


def build_shroud(variant="store"):
    ox0, ox1 = OPT_X
    oy0, oy1 = OPT_Y
    r = style.EDGE_RADIUS
    shell = _rbox(ox0 - WALL, ox1 + WALL, oy0 - WALL, oy1 + WALL, 0.0,
                  SHROUD_TOP_Z, r)
    shell = shell.faces(">Z").edges().chamfer(style.EDGE_CHAMFER)
    shell = shell.cut(_rbox(ox0, ox1, oy0, oy1, -1, SHROUD_INNER_Z,
                            r - WALL))
    g = LIP_WIDTH + LIP_GAP
    shell = shell.cut(_rbox(ox0 - g, ox1 + g, oy0 - g, oy1 + g, -1,
                            LIP_HEIGHT + LIP_GAP, r - WALL + g))
    # Opening for the detector BNC and battery cap.
    ym = c.DET_FRONT_Y - c.DET_D / 2
    shell = shell.cut(_rbox(-20.0, 20.0, ym - 9.0, ym + 9.0,
                            SHROUD_INNER_Z - 1, SHROUD_TOP_Z + 1, 4.0))
    # Notch for the laser wires at the -X wall.
    shell = shell.cut(_rbox(ox0 - WALL - 1, ox0 + 1, -5.0, 5.0, -1, 9.0, 0))
    if variant == "branded":
        mark = style.compass_mark(diameter=18.0)
        shell = shell.cut(mark.translate((60.0, 60.0,
                                          SHROUD_TOP_Z - style.ENGRAVE_DEPTH)))
    return shell


def build_lid(variant="store"):
    return _bay_place(case.build_lid(variant))


def build_sleeve(bore):
    tube = c.cylinder_x(SLEEVE_OD, CRADLE_X[0] - 1.0,
                        CRADLE_X[0] - 1.0 + SLEEVE_L)
    tube = tube.cut(c.cylinder_x(bore + 2 * FIT, CRADLE_X[0] - 2,
                                 CRADLE_X[1] + 2))
    slit = c.box(CRADLE_X[0] - 2, CRADLE_X[1] + 2, -SLEEVE_SLIT / 2,
                 SLEEVE_SLIT / 2, c.Z_BEAM, c.Z_BEAM + SLEEVE_OD)
    return tube.cut(slit)


def build_mirror_plate():
    x0, x1 = MP_FRONT, MP_FRONT + MP_T
    h = MP_SIZE / 2
    plate = _rbox(x0, x1, -h, h, MP_Z0, MP_Z0 + MP_SIZE, 0)
    plate = plate.edges("|X").fillet(3.0)
    plate = plate.cut(c.cylinder_x(MP_POCKET_D, x0 - 1, x0 + MP_POCKET_DEPTH))
    plate = plate.cut(c.cylinder_x(MP_APERTURE, x0, x1 + 1))
    for y, z in PULL:
        plate = plate.cut(c.cylinder_x(M3_CLEAR, x0 - 1, x1 + 1, y=y,
                                       z=c.Z_BEAM + z))
    # Small cups where the three adjuster tips touch.
    for y, z in ADJUST:
        plate = plate.cut(c.cylinder_x(2.4, x1 - 0.8, x1 + 1, y=y,
                                       z=c.Z_BEAM + z))
    return plate


def build_mirror_bracket():
    h = MP_SIZE / 2 + 1.0
    back = _rbox(MB_BACK_X, MB_BACK_X + MB_BACK_T, -h, h, 0.0,
                 MP_Z0 + MP_SIZE + 1.0, 0)
    back = back.edges("|X").fillet(3.0)
    foot = c.box(MB_FOOT_X[0], MB_FOOT_X[1], -h, h, 0.0, MB_FOOT_T)
    bracket = back.union(foot)
    # Ribs between foot and back plate.
    for y in (-h, h - 3.0):
        rib = (cq.Workplane("XZ").workplane(offset=-(y + 3.0))
               .polyline([(MB_BACK_X + MB_BACK_T, MB_FOOT_T),
                          (MB_FOOT_X[1], MB_FOOT_T),
                          (MB_BACK_X + MB_BACK_T, 30.0)]).close().extrude(3.0))
        bracket = bracket.union(rib)
    xb0, xb1 = MB_BACK_X, MB_BACK_X + MB_BACK_T
    for y, z in ADJUST + PULL:
        bracket = bracket.cut(c.cylinder_x(M3_INSERT_D, xb0 - 1, xb1 + 1,
                                           y=y, z=c.Z_BEAM + z))
    bracket = bracket.cut(c.cylinder_x(MP_APERTURE - 4, xb0 - 1, xb1 + 1))
    # M4 slot in the foot, on the same line as the base slot.
    slot = (cq.Workplane("XY").workplane(offset=-1)
            .center((PAD_SLOT[0] + PAD_SLOT[1]) / 2 + 4.0, 0)
            .slot2D(MB_FOOT_X[1] - MB_FOOT_X[0] - 8.0, M4_CLEAR)
            .extrude(MB_FOOT_T + 2))
    return bracket.cut(slot)


def build_board_proxy():
    return _bay_place(case.build_board_proxy())


def build_all():
    parts = {}
    for variant in ("store", "branded"):
        parts[f"base-{variant}"] = build_base(variant)
        parts[f"shroud-{variant}"] = build_shroud(variant)
        parts[f"lid-{variant}"] = build_lid(variant)
    for name, bore in SLEEVES.items():
        parts[name] = build_sleeve(bore)
    parts["mirror-bracket"] = build_mirror_bracket()
    parts["mirror-plate"] = build_mirror_plate()
    return parts


def _turn(shape, angle):
    return shape.rotate((0, 0, 0), (0, 0, 1), angle) if angle else shape


def components(km100=True):
    """Bought parts (and printed mounts when km100 is False), by name."""
    comps = {"board": build_board_proxy().val(),
             "laser": c.laser().val(),
             "cube": c.cube().val(),
             "detector": c.detector().val()}
    for label, angle in (("M1", 0), ("M2", 90)):
        comps[f"{label} mirror"] = c.mirror(angle).val()
        if km100:
            comps[f"{label} KM100"] = c.km100(angle).val()
        else:
            comps[f"{label} bracket"] = _turn(build_mirror_bracket(), angle).val()
            comps[f"{label} plate"] = _turn(build_mirror_plate(), angle).val()
    return comps


def fit_checks(shapes, overlap, report):
    limit = 0.01
    beam = c.beam(d=3.0).val()
    for variant in ("store", "branded"):
        base = shapes[f"base-{variant}"]
        shroud = shapes[f"shroud-{variant}"]
        lid = shapes[f"lid-{variant}"]
        pairs = {"base/shroud": (base, shroud), "base/lid": (base, lid),
                 "shroud/lid": (shroud, lid), "base/beam": (base, beam),
                 "shroud/beam": (shroud, beam)}
        for label, (x, y) in pairs.items():
            v = overlap(x, y)
            report(f"{variant} {label} overlap", v <= limit, f"{v:.3f} mm3")
        for km in (True, False):
            for name, comp in components(km).items():
                if not km and name in ("board", "laser", "cube", "detector"):
                    continue
                for part_name, part in (("base", base), ("shroud", shroud),
                                        ("lid", lid)):
                    v = overlap(part, comp)
                    report(f"{variant} {part_name}/{name}", v <= limit,
                           f"{v:.3f} mm3")
    # Sleeves: inside the cradle bore, around the laser.
    base = shapes["base-store"]
    laser = c.laser().val()
    for name in SLEEVES:
        sleeve = shapes[name]
        report(f"{name}/base overlap", overlap(sleeve, base) <= limit,
               f"{overlap(sleeve, base):.3f} mm3")
    v = overlap(shapes["sleeve-7mm"], laser)
    report("sleeve-7mm/laser overlap", v <= limit, f"{v:.3f} mm3")
    # Printed mount: bracket, plate, mirror and beam do not collide.
    br, pl = shapes["mirror-bracket"], shapes["mirror-plate"]
    m = c.mirror(0).val()
    for label, (x, y) in {"bracket/plate": (br, pl), "plate/mirror": (pl, m),
                          "bracket/mirror": (br, m),
                          "plate/beam": (pl, beam),
                          "bracket/beam": (br, beam)}.items():
        v = overlap(x, y)
        report(f"printed mount {label}", v <= limit, f"{v:.3f} mm3")
    # The mirror sits in the pocket: its front is at the arm length.
    mb = m.BoundingBox()
    report("mirror surface at arm length", abs(mb.xmin - c.ARM) < 1e-6,
           f"x = {mb.xmin:.2f} mm")
    print(f"  optical axis z_beam = {c.Z_BEAM:.1f} mm above the plate top")
    print(f"  arms: {c.ARM:.1f} mm each, cube centre to mirror surface")


# Render views (render.py).
def render_views():
    base = build_base("branded")
    shroud = build_shroud("branded")
    lid = build_lid("branded")
    km = [c.km100(0), c.km100(90)]
    mirrors = [c.mirror(0), c.mirror(90)]
    parts_dark = [(c.laser(), "board"), (c.detector(), "board"),
                  (build_board_proxy(), "board"),
                  (c.comparator(112.0, -24.0, 1.0), "board")]
    glass = [(c.cube(), "glass")] + [(m, "glass") for m in mirrors]
    sleeve = build_sleeve(7.0)
    beam = c.beam(d=1.4)
    hero = [(260, -330, 300), (25, 15, 18), (0, 0, 1)]
    top = [(20, 15, 520), (20, 15, 0), (0, 1, 0)]
    low = [(-380, -430, 330), (20, 15, 60), (0, 0, 1)]
    printed = ([(build_mirror_bracket(), "device"),
                (build_mirror_plate(), "glass")] + [(mirrors[0], "glass")])
    printed_view = [(-60, -150, 90), (65, 0, 25), (0, 0, 1)]
    open_items = ([(base, "device"), (sleeve, "glass"), (lid, "glass"),
                   (beam, "trace")] + parts_dark + glass
                  + [(k, "board") for k in km])
    closed = [(base, "device"), (shroud, "glass"), (lid, "glass")]
    exploded = ([(base, "device"), (sleeve, "glass"),
                 (lid.translate((0, 0, 40)), "glass"),
                 (shroud.translate((0, 0, 95)), "glass"),
                 (beam, "trace")] + parts_dark + glass
                + [(k, "board") for k in km])
    store = [(build_base("store"), "device"), (build_shroud("store"), "glass"),
             (build_lid("store"), "glass")]
    return [("bench-open-branded.png", open_items, hero, 1.25),
            ("bench-top-beam.png", open_items, top, 1.3),
            ("bench-closed-branded.png", closed, hero, 1.25),
            ("bench-closed-store.png", store, hero, 1.25),
            ("bench-exploded-branded.png", exploded, low, 1.0),
            ("printed-mirror-mount.png", printed, printed_view, 1.2)]
