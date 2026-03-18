import pandas as pd
import cadquery as cq
import pyvista as pv
import os
import tempfile
from pathlib import Path
from datetime import datetime

class RocketNozzleSystem:
    def __init__(self, csv_file="optimal_nozzle_data.csv"):
        self.csv_file = csv_file
        self.current_nozzle = None

    def build_nozzle(self, design_index=0):
        """Builds the parametric CAD model."""
        df = pd.read_csv(self.csv_file)
        row = df.iloc[design_index]
        
        Ri, Rt, Re = row['r_inlet'], row['r_throat'], row['r_exit']
        Lc, Ld = row['len_conv'], row['len_div']
        
        p1, p2, p3 = (Ri, 0), (Rt, Lc), (Re, Lc + Ld)
        p_mid = ((Rt + Re) / 1.8, Lc + (Ld / 2))

        profile = (
            cq.Workplane("XY")
            .lineTo(p1[0], p1[1])
            .lineTo(p2[0], p2[1])
            .threePointArc(p_mid, p3)
            .lineTo(0, Lc + Ld)
            .lineTo(0, 0)
            .close()
        )
        
        nozzle_solid = profile.revolve(360, (0, 0, 0), (0, 1, 0))
        self.current_nozzle = nozzle_solid.faces(">Y or <Y").shell(-2.0)
        return self.current_nozzle

    def export_callback(self, state):
        """Finds the Windows Downloads folder and exports the STEP file."""
        if state and self.current_nozzle:
            # 1. Automatically find the user's Downloads folder
            downloads_path = str(Path.home() / "Downloads")
            
            # 2. Create a unique filename with a timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nozzle_design_{timestamp}.step"
            full_path = os.path.join(downloads_path, filename)

            # 3. Export
            cq.exporters.export(self.current_nozzle, full_path)
            
            print("\n" + "="*40)
            print(f"📥 DOWNLOAD COMPLETE!")
            print(f"📄 File: {filename}")
            print(f"📁 Folder: {downloads_path}")
            print("="*40)

    def run_interface(self):
        """Launches the UI with the Download button."""
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            tmp_path = tmp.name
        cq.exporters.export(self.current_nozzle, tmp_path)
        mesh = pv.read(tmp_path)
        os.remove(tmp_path) 

        plotter = pv.Plotter(title="Rocket Nozzle CAD System")
        plotter.set_background("#2c3e50")

        plotter.add_mesh(mesh, color="silver", show_edges=True, edge_color="#1a1a1a", smooth_shading=True, specular=0.6)

        # Lame Ahh Square
        plotter.add_checkbox_button_widget(
            self.export_callback,
            value=False,
            color_on="green",
            color_off="white",
            position=(15, 15),
            size=40
        )

        plotter.add_text("CLICK WHITE SQUARE TO DOWNLOAD (.STEP)", position="lower_left", font_size=9, color="white")
        plotter.add_axes()
        plotter.show()

if __name__ == "__main__":
    # CSV existence lol
    if not os.path.exists("optimal_nozzle_data.csv"):
        pd.DataFrame({
            'design_id': [1], 'r_inlet': [50.0], 'r_throat': [15.0], 
            'r_exit': [80.0], 'len_conv': [40.0], 'len_div': [120.0]
        }).to_csv("optimal_nozzle_data.csv", index=False)

    app = RocketNozzleSystem()
    app.build_nozzle(design_index=0)
    app.run_interface()