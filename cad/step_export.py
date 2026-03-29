import cadquery as cq


def export_step(shape, filename):
    """
    Exports a CadQuery shape to a STEP file.
    
    Args:
        shape: The CadQuery object (e.g., a solid or workplane).
        filename (str): The destination path for the STEP file.
    """
    # Ensure the file has the correct extension for CAD software compatibility
    if not filename.lower().endswith((".step", ".stp")):
        filename += ".step"
        
    cq.exporters.export(shape, filename)