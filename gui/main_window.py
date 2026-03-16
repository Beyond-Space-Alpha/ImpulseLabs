from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from geometry.rao import RaoBell
from geometry.converging import converging_parabola
from geometry.throat import throat_fillet
from mesh.msh_generator import generate_axi_mesh

import meshio


class PlotCanvas(FigureCanvasQTAgg):

    def __init__(self, title):

        fig = Figure(facecolor="#121212")

        self.ax = fig.add_subplot(111)

        self.ax.set_facecolor("#121212")

        self.ax.set_title(title, color="white")

        self.ax.tick_params(colors="white")

        super().__init__(fig)


class ImpulseLabsWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Impulse Labs")

        self.resize(1400, 800)

        self.contour = None

        self.create_menu()

        self.create_layout()

    # ----------------------------------------------------
    # MENU BAR
    # ----------------------------------------------------

    def create_menu(self):

        menu = self.menuBar()

        file_menu = menu.addMenu("File")

        file_menu.addAction("New")
        file_menu.addAction("Open Contour")
        file_menu.addAction("Open Mesh")
        file_menu.addAction("Export")
        file_menu.addAction("Download")

        view_menu = menu.addMenu("View")
        view_menu.addAction("Fullscreen", self.toggle_fullscreen)

        docs_menu = menu.addMenu("Documentation")
        docs_menu.addAction("Open Docs")

        help_menu = menu.addMenu("Help")
        help_menu.addAction("User Guide")

        llm_menu = menu.addMenu("LLM")
        llm_menu.addAction("Open Chat", self.toggle_llm)

    # ----------------------------------------------------
    # MAIN LAYOUT
    # ----------------------------------------------------

    def create_layout(self):

        central = QWidget()

        layout = QHBoxLayout()

        layout.addWidget(self.create_inputs(), 1)

        layout.addWidget(self.create_plots(), 3)

        central.setLayout(layout)

        self.setCentralWidget(central)

        self.create_status()

    # ----------------------------------------------------
    # INPUT PANEL
    # ----------------------------------------------------

    def create_inputs(self):

        panel = QVBoxLayout()

        title = QLabel("Engine Inputs")

        title.setStyleSheet("font-size:18px")

        panel.addWidget(title)

        self.thrust = self.slider("Thrust (N)", 100, 5000, 500)

        self.pressure = self.slider("Chamber Pressure (bar)", 5, 100, 30)

        self.mr = self.slider("Mixture Ratio", 10, 50, 25, scale=0.1)

        panel.addWidget(self.thrust["widget"])
        panel.addWidget(self.pressure["widget"])
        panel.addWidget(self.mr["widget"])

        self.run_button = QPushButton("Run Simulation")

        self.mesh_button = QPushButton("Generate Mesh")

        self.run_button.clicked.connect(self.run_simulation)

        self.mesh_button.clicked.connect(self.generate_mesh)

        panel.addWidget(self.run_button)
        panel.addWidget(self.mesh_button)

        desc = QTextEdit()

        desc.setReadOnly(True)

        desc.setText(
            "Thrust (N)\n"
            "Desired engine thrust.\n\n"
            "Chamber Pressure (bar)\n"
            "Combustion chamber pressure.\n\n"
            "Mixture Ratio\n"
            "Oxidizer/Fuel mass ratio."
        )

        panel.addWidget(QLabel("Parameter Description"))
        panel.addWidget(desc)

        widget = QWidget()
        widget.setLayout(panel)

        return widget

    # ----------------------------------------------------
    # SLIDER + TEXT INPUT
    # ----------------------------------------------------

    def slider(self, label, minv, maxv, value, scale=1):

        layout = QVBoxLayout()

        layout.addWidget(QLabel(label))

        row = QHBoxLayout()

        slider = QSlider(Qt.Horizontal)

        slider.setRange(minv, maxv)

        slider.setValue(value)

        textbox = QLineEdit(str(value * scale))

        slider.valueChanged.connect(
            lambda v: textbox.setText(str(v * scale))
        )

        textbox.editingFinished.connect(
            lambda: slider.setValue(int(float(textbox.text()) / scale))
        )

        row.addWidget(slider)
        row.addWidget(textbox)

        layout.addLayout(row)

        widget = QWidget()
        widget.setLayout(layout)

        return {"widget": widget, "slider": slider, "textbox": textbox, "scale": scale}

    # ----------------------------------------------------
    # PLOTS
    # ----------------------------------------------------

    def create_plots(self):

        layout = QHBoxLayout()

        self.geometry_plot = PlotCanvas("Nozzle Geometry")

        self.mesh_plot = PlotCanvas("Mesh")

        layout.addWidget(self.geometry_plot)
        layout.addWidget(self.mesh_plot)

        container = QWidget()
        container.setLayout(layout)

        return container

    # ----------------------------------------------------
    # STATUS BAR
    # ----------------------------------------------------

    def create_status(self):

        self.status = QLabel("Geometry dimensions will appear here (SI units).")

        self.statusBar().addWidget(self.status)

    # ----------------------------------------------------
    # SIMULATION
    # ----------------------------------------------------

    def run_simulation(self):

        thrust = self.thrust["slider"].value()

        rt = 0.01 + thrust / 20000

        re = rt * 3

        rc = rt * 2

        chamber_length = 0.05

        chamber = [(-chamber_length, rc), (0, rc)]

        conv = converging_parabola(rc, rt, 0, 0.03)

        throat = throat_fillet(rt, 0.01, conv[-1][0])

        rao = RaoBell()

        L = rao.length(rt, re)

        bell = rao.contour(rt, re, L, throat[-1][0])

        self.contour = chamber + conv[1:] + throat[1:] + bell[1:]

        x = [p[0] for p in self.contour]

        y = [p[1] for p in self.contour]

        self.geometry_plot.ax.clear()

        self.geometry_plot.ax.plot(x, y)
        self.geometry_plot.ax.plot(x, [-v for v in y])

        self.geometry_plot.ax.set_aspect("equal")

        self.geometry_plot.draw()

        self.status.setText(
            f"Throat Radius: {rt:.4f} m | Exit Radius: {re:.4f} m | Chamber Radius: {rc:.4f} m | Nozzle Length: {L:.4f} m"
        )

    # ----------------------------------------------------
    # MESH
    # ----------------------------------------------------

    def generate_mesh(self):

        if self.contour is None:
            return

        generate_axi_mesh(self.contour)

        mesh = meshio.read("engine_axi.msh")

        points = mesh.points[:, :2]

        cells = None

        for c in mesh.cells:

            if c.type.startswith("triangle"):
                cells = c.data[:, :3]

        if cells is None:
            return

        self.mesh_plot.ax.clear()

        self.mesh_plot.ax.triplot(points[:, 0], points[:, 1], cells, linewidth=0.5)

        self.mesh_plot.ax.set_aspect("equal")

        self.mesh_plot.draw()

    # ----------------------------------------------------
    # TOOLS
    # ----------------------------------------------------

    def toggle_llm(self):

        dlg = QDialog(self)

        dlg.setWindowTitle("Impulse Labs LLM Assistant")

        layout = QVBoxLayout()

        layout.addWidget(QTextEdit())

        dlg.setLayout(layout)

        dlg.resize(400, 500)

        dlg.show()

    def toggle_fullscreen(self):

        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()