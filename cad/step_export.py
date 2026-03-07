import cadquery as cq


def export_step(shape,filename):

    cq.exporters.export(shape,filename)