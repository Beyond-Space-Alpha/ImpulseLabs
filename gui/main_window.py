from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import meshio

from geometry.rao import RaoBell
from geometry.converging import converging_parabola
from geometry.throat import throat_fillet
from mesh.msh_generator import generate_axi_mesh


class PlotCanvas(FigureCanvasQTAgg):

    def __init__(self):

        self.figure = Figure()

        self.ax = self.figure.add_subplot(111)

        super().__init__(self.figure)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("ImpulseLabs Rocket Tool")

        self.contour = None

        layout = QVBoxLayout()

        # INPUTS

        self.thrust = QDoubleSpinBox()
        self.thrust.setValue(500)

        self.pressure = QDoubleSpinBox()
        self.pressure.setValue(30)

        self.mr = QDoubleSpinBox()
        self.mr.setValue(2.5)

        self.oxidizer = QComboBox()
        self.oxidizer.addItems(["LOX","N2O","GOX"])

        self.fuel = QComboBox()
        self.fuel.addItems(["RP1","LH2","CH4"])

        layout.addWidget(QLabel("Thrust"))
        layout.addWidget(self.thrust)

        layout.addWidget(QLabel("Chamber Pressure"))
        layout.addWidget(self.pressure)

        layout.addWidget(QLabel("Mixture Ratio"))
        layout.addWidget(self.mr)

        layout.addWidget(QLabel("Oxidizer"))
        layout.addWidget(self.oxidizer)

        layout.addWidget(QLabel("Fuel"))
        layout.addWidget(self.fuel)

        # BUTTONS

        self.run_button = QPushButton("Run Simulation")
        self.mesh_button = QPushButton("Generate Mesh")

        layout.addWidget(self.run_button)
        layout.addWidget(self.mesh_button)

        self.run_button.clicked.connect(self.run_simulation)
        self.mesh_button.clicked.connect(self.generate_mesh)

        # GEOMETRY PLOT

        layout.addWidget(QLabel("Nozzle Geometry"))

        self.geometry_plot = PlotCanvas()

        layout.addWidget(self.geometry_plot)

        # MESH PLOT

        layout.addWidget(QLabel("Mesh"))

        self.mesh_plot = PlotCanvas()

        layout.addWidget(self.mesh_plot)

        widget = QWidget()

        widget.setLayout(layout)

        self.setCentralWidget(widget)


    def run_simulation(self):

        self.geometry_plot.ax.clear()

        rt = 0.02
        re = 0.06
        rc = 0.04

        chamber_length = 0.05

        chamber = [
            (-chamber_length, rc),
            (0, rc)
        ]

        conv = converging_parabola(
            rc,
            rt,
            x0=0,
            length=0.03
        )

        throat = throat_fillet(
            rt,
            radius=0.01,
            x0=conv[-1][0]
        )

        rao = RaoBell()

        L = rao.length(rt, re)

        bell = rao.contour(
            rt,
            re,
            L,
            x0=throat[-1][0]
        )

        self.contour = chamber + conv[1:] + throat[1:] + bell[1:]

        x = [p[0] for p in self.contour]
        y = [p[1] for p in self.contour]

        self.geometry_plot.ax.plot(x,y)
        self.geometry_plot.ax.plot(x,[-v for v in y])

        self.geometry_plot.ax.set_aspect("equal")

        self.geometry_plot.ax.set_title("Rocket Nozzle Contour")

        self.geometry_plot.draw()


    def generate_mesh(self):

        if self.contour is None:

            QMessageBox.warning(
                self,
                "Error",
                "Run simulation first."
            )

            return

        generate_axi_mesh(self.contour)

        mesh = meshio.read("engine_axi.msh")

        self.mesh_plot.ax.clear()

        points = mesh.points[:, :2]

        cells = None

        for cell in mesh.cells:

            if cell.type.startswith("triangle"):

                cells = cell.data[:, :3]

                break

        if cells is None:

            QMessageBox.warning(
                self,
                "Mesh Error",
                "No triangular elements found."
            )

            return

        self.mesh_plot.ax.triplot(
            points[:,0],
            points[:,1],
            cells,
            linewidth=0.5
        )

        self.mesh_plot.ax.set_aspect("equal")

        self.mesh_plot.ax.set_title("Axisymmetric Mesh")

        self.mesh_plot.draw()