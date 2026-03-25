import cadquery as cq


def export_step(shape, filename):
    """
    Exports a CadQuery shape to a STEP file.
    """
    cq.exporters.export(shape, filename)