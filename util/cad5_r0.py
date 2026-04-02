import os
import tempfile
from datetime import datetime
from pathlib import Path

import cadquery as cq
import pandas as pd
import pyvista as pv


class RocketNozzleSystem:
    """
    Parametric CAD system for generating and exporting rocket nozzle designs.
    """

    def __init__(self, csv_file="optimal_nozzle_data.csv"):
        self.csv_file = csv_file
        self.current_nozzle = None

    def build_nozzle(self, design_index=0):
        """
        Builds the parametric CAD model from CSV data using a revolve and shell.

        Args:
            design_index (int): The row index in the CSV to use for parameters.

        Returns:
            cq.Workplane: The generated 3D solid.
        """
        df = pd.read_csv(self.csv_file)
        row = df.iloc[design_index]

        # Standard propulsion radii and lengths
        ri, rt, re = row['r_inlet'], row['r_throat'], row['r_exit']
        lc, ld = row['len_conv'], row['len_div']

        # Profile control points
        p1 = (ri, 0)
        p2 = (rt, lc)
        p3 = (re, lc + ld)
        p_mid = ((rt + re) / 1.8, lc + (ld / 2))

        # Create the 2D profile
        profile = (
            cq.Workplane("XY")
            .lineTo(p1[0], p1[1])
            .lineTo(p2[0], p2[1])
            .threePointArc(p_mid, p3)
            .lineTo(0, lc + ld)
            .lineTo(0, 0)
            .close()
        )

        # Revolve 2D profile into 3D solid and shell it (2mm thickness)
        nozzle_solid = profile.revolve(360, (0, 0, 0), (0, 1, 0))
        self.current_nozzle = nozzle_solid.faces(">Y or <Y").shell(-2.0)

        return self.current_nozzle

    def export_callback(self, state):
        """
        Finds the user's Downloads folder and exports the current model as .STEP.
        """
        if state and self.current_nozzle:
            # 1. Automatically find the user's Downloads folder
            downloads_path = Path.home() / "Downloads"

            # 2. Create a unique filename with a timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nozzle_design_{timestamp}.step"
            full_path = str(downloads_path / filename)

            # 3. Export via CadQuery
            cq.exporters.export(self.current_nozzle, full_path)

            print("\n" + "=" * 40)
            print("📥 DOWNLOAD COMPLETE!")
            print(f"📄 File: {filename}")
            print(f"📁 Folder: {downloads_path}")
            print("=" * 40)

    def run_interface(self):
        """
        Launches the PyVista 3D interface with an export trigger.
        """
        # Create a temporary STL for PyVista to read
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            tmp_path = tmp.name

        cq.exporters.export(self.current_nozzle, tmp_path)
        mesh = pv.read(tmp_path)
        
        # Cleanup temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        plotter = pv.Plotter(title="Rocket Nozzle CAD System")
        plotter.set_background("#2c3e50")

        # Visual styling
        plotter.add_mesh(
            mesh, 
            color="silver", 
            show_edges=True, 
            edge_color="#1a1a1a", 
            smooth_shading=True, 
            specular=0.6
        )

        # Interaction widget (checkbox used as a button)
        plotter.add_checkbox_button_widget(
            self.export_callback,
            value=False,
            color_on="green",
            color_off="white",
            position=(15, 15),
            size=40
        )

        plotter.add_text(
            "CLICK WHITE SQUARE TO DOWNLOAD (.STEP)", 
            position="lower_left", 
            font_size=9, 
            color="white"
        )
        
        plotter.add_axes()
        plotter.show()


if __name__ == "__main__":
    # Ensure dummy data exists for testing
    CSV_PATH = "optimal_nozzle_data.csv"
    if not os.path.exists(CSV_PATH):
        pd.DataFrame({
            'design_id': [1], 
            'r_inlet': [50.0], 
            'r_throat': [15.0],
            'r_exit': [80.0], 
            'len_conv': [40.0], 
            'len_div': [120.0]
        }).to_csv(CSV_PATH, index=False)

    app = RocketNozzleSystem()
    app.build_nozzle(design_index=0)
    app.run_interface()