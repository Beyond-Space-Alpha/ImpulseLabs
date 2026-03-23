from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import numpy as np
import meshio
import cadquery as cq
import pyvista as pv
from pyvistaqt import QtInteractor
import tempfile
import os

from geometry.rao import RaoBell
from geometry.converging import converging_parabola
from geometry.throat import throat_fillet
from mesh.msh_generator import generate_axi_mesh


# -----------------------------
# PLOT CANVAS
# -----------------------------
class PlotCanvas(FigureCanvasQTAgg):

    def __init__(self, title):

        fig = Figure(facecolor="#121212")
        self.ax = fig.add_subplot(111)

        self.ax.set_facecolor("#121212")
        self.ax.set_title(title, color="white")
        self.ax.tick_params(colors="white")

        super().__init__(fig)


# -----------------------------
# RANGE SLIDER (MIN-MAX + VALUE)
# -----------------------------
class RangeSliderWidget(QWidget):

    def __init__(self, label, min_default, max_default):

        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))

        row = QHBoxLayout()

        self.min_box = QLineEdit(str(min_default))
        self.slider = QSlider(Qt.Horizontal)
        self.max_box = QLineEdit(str(max_default))

        self.value_box = QDoubleSpinBox()
        self.value_box.setDecimals(4)

        row.addWidget(self.min_box)
        row.addWidget(self.slider)
        row.addWidget(self.max_box)

        layout.addLayout(row)
        layout.addWidget(self.value_box)

        self.setLayout(layout)

        self.update_slider()

        self.min_box.editingFinished.connect(self.update_slider)
        self.max_box.editingFinished.connect(self.update_slider)
        self.slider.valueChanged.connect(self.sync_value)
        self.value_box.valueChanged.connect(self.sync_slider)

    def update_slider(self):

        try:
            min_v = float(self.min_box.text())
            max_v = float(self.max_box.text())

            if min_v >= max_v:
                return

            self.slider.setMinimum(int(min_v))
            self.slider.setMaximum(int(max_v))

            mid = (min_v + max_v) / 2

            self.slider.setValue(int(mid))
            self.value_box.setValue(mid)

        except:
            pass

    def sync_value(self):
        self.value_box.setValue(self.slider.value())

    def sync_slider(self):
        self.slider.setValue(int(self.value_box.value()))

    def get_value(self):
        return self.value_box.value()


# -----------------------------
# MAIN WINDOW
# -----------------------------
class ImpulseLabsWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Impulse Labs")
        self.resize(1600, 900)

        self.contour = None
        self.current_nozzle = None

        self.create_menu()
        self.create_layout()
        self.create_llm_panel()
        self.create_status()

    # -----------------------------
    # MENU BAR
    # -----------------------------
    def create_menu(self):

        menu = self.menuBar()

        menu.addMenu("File")
        menu.addMenu("View")
        menu.addMenu("Documentation")
        menu.addMenu("Help")

        llm_menu = menu.addMenu("LLM")
        llm_menu.addAction("Toggle Chat", self.toggle_llm)

    # -----------------------------
    # LAYOUT
    # -----------------------------
    def create_layout(self):

        main = QHBoxLayout()

        main.addWidget(self.create_inputs(), 1)
        main.addWidget(self.create_plots(), 3)

        container = QWidget()
        container.setLayout(main)

        self.setCentralWidget(container)

    # -----------------------------
    # INPUT PANEL (RESTORED)
    # -----------------------------
    def create_inputs(self):

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Engine Inputs"))

        self.thrust = RangeSliderWidget("Thrust (N)", 100, 5000)
        self.pressure = RangeSliderWidget("Chamber Pressure", 5, 100)
        self.mr = RangeSliderWidget("Mixture Ratio", 1, 5)

        layout.addWidget(self.thrust)
        layout.addWidget(self.pressure)
        layout.addWidget(self.mr)

        # OPTIONAL INPUTS
        self.temp = QLineEdit()
        self.temp.setPlaceholderText("Chamber Temp (optional)")

        self.contraction = QLineEdit()
        self.contraction.setPlaceholderText("Contraction Ratio (optional)")

        self.ambient = QLineEdit()
        self.ambient.setPlaceholderText("Ambient Pressure (optional)")

        layout.addWidget(self.temp)
        layout.addWidget(self.contraction)
        layout.addWidget(self.ambient)

        # BUTTONS
        self.run_btn = QPushButton("Run Simulation")
        self.mesh_btn = QPushButton("Generate Mesh")
        self.export_btn = QPushButton("Export STEP")

        self.run_btn.clicked.connect(self.run_simulation)
        self.mesh_btn.clicked.connect(self.generate_mesh)
        self.export_btn.clicked.connect(self.export_step)

        layout.addWidget(self.run_btn)
        layout.addWidget(self.mesh_btn)
        layout.addWidget(self.export_btn)

        # EQUATIONS
        layout.addWidget(QLabel("Equations"))

        eq = QTextEdit()
        eq.setReadOnly(True)
        eq.setText(
            "1D Isentropic Flow:\n"
            "T/T0 = 1/(1 + (γ-1)/2 M²)\n"
            "P/P0 = (T/T0)^(γ/(γ-1))\n"
            "Area-Mach relation"
        )
        layout.addWidget(eq)

        # SI UNITS
        layout.addWidget(QLabel("SI Units"))

        self.si_box = QLabel("Geometry values will appear here")
        layout.addWidget(self.si_box)

        # DESCRIPTION
        layout.addWidget(QLabel("Description"))

        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setText(
            "Rocket nozzle design tool.\n"
            "Generates geometry, mesh, and flow visualization."
        )
        layout.addWidget(desc)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    # -----------------------------
    # 2x2 PLOT GRID
    # -----------------------------
    def create_plots(self):

        grid = QGridLayout()

        self.geometry_plot = PlotCanvas("Geometry")
        self.mesh_plot = PlotCanvas("Mesh")
        self.isentropic_plot = PlotCanvas("Isentropic Flow")
        self.pv_widget = QtInteractor(self)

        grid.addWidget(self.geometry_plot, 0, 0)
        grid.addWidget(self.mesh_plot, 0, 1)
        grid.addWidget(self.isentropic_plot, 1, 0)
        grid.addWidget(self.pv_widget, 1, 1)

        container = QWidget()
        container.setLayout(grid)

        return container

    # -----------------------------
    # STATUS
    # -----------------------------
    def create_status(self):

        self.status = QLabel("Ready")
        self.statusBar().addWidget(self.status)

    # -----------------------------
    # LLM PANEL
    # -----------------------------
    def create_llm_panel(self):

        self.llm = QDockWidget("LLM Assistant", self)

        chat = QTextEdit()
        chat.setPlaceholderText("Ask anything...")

        self.llm.setWidget(chat)

        self.addDockWidget(Qt.RightDockWidgetArea, self.llm)
        self.llm.hide()

    def toggle_llm(self):
        self.llm.setVisible(not self.llm.isVisible())

    # -----------------------------
    # SIMULATION
    # -----------------------------
    def run_simulation(self):

        thrust = self.thrust.get_value()

        rt = 0.01 + thrust / 20000
        re = rt * 3
        rc = rt * 2

        chamber = [(-0.05, rc), (0, rc)]

        conv = converging_parabola(rc, rt, 0, 0.03)
        throat = throat_fillet(rt, 0.01, conv[-1][0])

        rao = RaoBell()
        L = rao.length(rt, re)

        bell = rao.contour(rt, re, L, throat[-1][0])

        self.contour = chamber + conv[1:] + throat[1:] + bell[1:]

        # -------- Geometry --------
        x = np.array([p[0] for p in self.contour])
        y = np.array([p[1] for p in self.contour])

        self.geometry_plot.ax.clear()
        self.geometry_plot.ax.plot(x, y)
        self.geometry_plot.ax.plot(x, -y)
        self.geometry_plot.ax.set_aspect("equal")
        self.geometry_plot.draw()

        # -------- Isentropic Heatmap --------
        A = np.pi * y**2
        At = np.min(A)

        gamma = 1.22
        M = np.sqrt(A / At)

        T = 1 / (1 + (gamma - 1)/2 * M**2)

        X, Y = np.meshgrid(x, np.linspace(-max(y), max(y), 100))

        Z = np.tile(T, (100, 1))
        mask = np.abs(Y) <= np.interp(X[0], x, y)
        Z[~mask] = np.nan

        self.isentropic_plot.ax.clear()

        im = self.isentropic_plot.ax.imshow(
            Z,
            extent=[x.min(), x.max(), -max(y), max(y)],
            origin="lower",
            aspect="auto"
        )

        self.isentropic_plot.figure.colorbar(im, ax=self.isentropic_plot.ax)
        self.isentropic_plot.draw()

        # -------- 3D CAD --------
        pts = [(r, x) for x, r in self.contour]

        profile = cq.Workplane("XY").polyline(pts).close()
        solid = profile.revolve(360, (0,0,0), (0,1,0))

        self.current_nozzle = solid

        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            tmp_path = tmp.name

        cq.exporters.export(self.current_nozzle, tmp_path)
        mesh = pv.read(tmp_path)

        self.pv_widget.clear()

        # Set black background
        self.pv_widget.set_background("black")

        # Add mesh
        self.pv_widget.add_mesh(
            mesh,
            color="lightgray",
            show_edges=True,
            edge_color="black",
            smooth_shading=True,
            specular=0.5
        )

        self.pv_widget.reset_camera()

        os.remove(tmp_path)

        # -------- SI OUTPUT --------
        text = f"rt={rt:.4f} m | re={re:.4f} m | rc={rc:.4f} m | L={L:.4f} m"

        self.status.setText(text)
        self.si_box.setText(text)

    # -----------------------------
    # MESH
    # -----------------------------
    def generate_mesh(self):

        if self.contour is None:
            return

        generate_axi_mesh(self.contour)

        mesh = meshio.read("engine_axi.msh")

        pts = mesh.points[:, :2]

        cells = None
        for c in mesh.cells:
            if c.type.startswith("triangle"):
                cells = c.data[:, :3]

        if cells is None:
            return

        self.mesh_plot.ax.clear()
        self.mesh_plot.ax.triplot(pts[:,0], pts[:,1], cells)
        self.mesh_plot.ax.set_aspect("equal")
        self.mesh_plot.draw()

    # -----------------------------
    # EXPORT STEP
    # -----------------------------
    def export_step(self):

        if self.current_nozzle:

            path = os.path.join(os.path.expanduser("~"), "Downloads", "nozzle.step")
            cq.exporters.export(self.current_nozzle, path)

            self.status.setText(f"STEP exported → {path}")