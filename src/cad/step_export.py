import cadquery as cq


def export_step(shape, filename):
    """
    Export a CadQuery shape to STEP.
    """
    if not filename.lower().endswith((".step", ".stp")):
        filename += ".step"

    cq.exporters.export(shape, filename)
    return filename


def export_stl(shape, filename):
    """
    Export a CadQuery shape to STL for GUI previewing.
    """
    if not filename.lower().endswith(".stl"):
        filename += ".stl"

    cq.exporters.export(shape, filename)
    return filename