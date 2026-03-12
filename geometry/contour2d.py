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