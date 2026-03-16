# def build_full_contour(chamber_pts, conv_pts, bell_pts):

#     contour = []

#     contour.extend(chamber_pts)

#     if contour[-1] == conv_pts[0]:
#         conv_pts = conv_pts[1:]

#     contour.extend(conv_pts)

#     if contour[-1] == bell_pts[0]:
#         bell_pts = bell_pts[1:]

#     contour.extend(bell_pts)

#     return contour
from geometry.converging import converging_parabola
from geometry.rao import RaoBell

"""
def build_full_contour(chamber_pts, conv_pts, bell_pts):

    contour = []

    contour.extend(chamber_pts)

    if contour and contour[-1] == conv_pts[0]:
        conv_pts = conv_pts[1:]

    contour.extend(conv_pts)

    if contour and contour[-1] == bell_pts[0]:
        bell_pts = bell_pts[1:]

    contour.extend(bell_pts)

    return contour
    """


def build_full_contour(rt, re, rc, chamber_length, conv_length):

    chamber_pts = [
        (-chamber_length, rc),
        (0.0, rc)
    ]

    conv_pts = converging_parabola(
        rc=rc,
        rt=rt,
        x0=0.0,
        length=conv_length
    )

    rao = RaoBell()
    nozzle_length = rao.length(rt, re)

    bell_pts = rao.contour(
        rt=rt,
        re=re,
        L=nozzle_length,
        x0=conv_pts[-1][0]
    )

    contour = []
    contour.extend(chamber_pts)

    if contour and contour[-1] == conv_pts[0]:
        conv_pts = conv_pts[1:]
    contour.extend(conv_pts)

    if contour and contour[-1] == bell_pts[0]:
        bell_pts = bell_pts[1:]
    contour.extend(bell_pts)

    return {
        "chamber": chamber_pts,
        "converging": conv_pts,
        "bell": bell_pts,
        "contour": contour,
        "nozzle_length": nozzle_length
    }