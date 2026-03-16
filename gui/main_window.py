from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import meshio

from geometry.rao import RaoBell
from geometry.converging import converging_parabola
from geometry.throat import throat_fillet
from mesh.msh_generator import generate_axi_mesh


class PlotCanvas(FigureCanvasQTAgg):

    def __init__(self, title=""):

        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)

        self.ax.set_title(title)

        super().__init__(self.figure)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("ImpulseLabs")

        self.contour = None

        main_layout = QVBoxLayout()

        # TOP AREA (inputs + plots)
        top_layout = QHBoxLayout()

        # -------------------------
        # INPUT PANEL
        # -------------------------

        input_layout = QVBoxLayout()

        title = QLabel("Engine Inputs")
        title.setStyleSheet("font-size:16px;font-weight:bold")

        input_layout.addWidget(title)

        # thrust slider

        self.thrust_slider = QSlider()
        self.thrust_slider.setOrientation(1)
        self.thrust_slider.setRange(10, 10000)
        self.thrust_slider.setValue(500)

        self.thrust_value = QLabel("500 N")

        input_layout.addWidget(QLabel("Thrust"))
        input_layout.addWidget(self.thrust_slider)
        input_layout.addWidget(self.thrust_value)

        # pressure slider

        self.pressure_slider = QSlider()
        self.pressure_slider.setOrientation(1)
        self.pressure_slider.setRange(5, 150)
        self.pressure_slider.setValue(30)

        self.pressure_value = QLabel("30 bar")

        input_layout.addWidget(QLabel("Chamber Pressure"))
        input_layout.addWidget(self.pressure_slider)
        input_layout.addWidget(self.pressure_value)

        # mixture ratio

        self.mr_slider = QSlider()
        self.mr_slider.setOrientation(1)
        self.mr_slider.setRange(10, 50)
        self.mr_slider.setValue(25)

        self.mr_value = QLabel("2.5")

        input_layout.addWidget(QLabel("Mixture Ratio"))
        input_layout.addWidget(self.mr_slider)
        input_layout.addWidget(self.mr_value)

        # propellant

        self.oxidizer = QComboBox()
        self.oxidizer.addItems(["LOX", "N2O", "GOX"])

        self.fuel = QComboBox()
        self.fuel.addItems(["RP1", "LH2", "CH4"])

        input_layout.addWidget(QLabel("Oxidizer"))
        input_layout.addWidget(self.oxidizer)

        input_layout.addWidget(QLabel("Fuel"))
        input_layout.addWidget(self.fuel)

        # buttons

        self.run_button = QPushButton("Run Simulation")
        self.mesh_button = QPushButton("Generate Mesh")

        input_layout.addWidget(self.run_button)
        input_layout.addWidget(self.mesh_button)

        # description box

        self.description = QTextEdit()
        self.description.setReadOnly(True)

        self.description.setText(
            "Thrust: Desired engine thrust (N)\n"
            "Chamber Pressure: Pressure inside combustion chamber (bar)\n"
            "Mixture Ratio: Oxidizer/Fuel mass ratio\n"
            "Propellant: Fuel and oxidizer combination"
        )

        input_layout.addWidget(QLabel("Parameter Description"))
        input_layout.addWidget(self.description)

        # -------------------------
        # PLOTS
        # -------------------------

        graph_layout = QHBoxLayout()

        self.geometry_plot = PlotCanvas("Nozzle Geometry")
        self.mesh_plot = PlotCanvas("Mesh")

        graph_layout.addWidget(self.geometry_plot)
        graph_layout.addWidget(self.mesh_plot)

        top_layout.addLayout(input_layout, 1)
        top_layout.addLayout(graph_layout, 3)

        main_layout.addLayout(top_layout)

        # -------------------------
        # DIMENSION OUTPUT
        # -------------------------

        self.dimensions = QLabel("Geometry dimensions will appear here")

        self.dimensions.setStyleSheet("font-size:12px")

        main_layout.addWidget(self.dimensions)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)

        # connections

        self.run_button.clicked.connect(self.run_simulation)
        self.mesh_button.clicked.connect(self.generate_mesh)

        self.thrust_slider.valueChanged.connect(
            lambda v: self.thrust_value.setText(f"{v} N")
        )

        self.pressure_slider.valueChanged.connect(
            lambda v: self.pressure_value.setText(f"{v} bar")
        )

        self.mr_slider.valueChanged.connect(
            lambda v: self.mr_value.setText(f"{v/10}")
        )

    # -------------------------
    # RUN SIMULATION
    # -------------------------

    def run_simulation(self):

        thrust = self.thrust_slider.value()
        pressure = self.pressure_slider.value()
        mr = self.mr_slider.value() / 10

        # example scaling for geometry
        rt = 0.01 + thrust / 20000
        re = rt * 3
        rc = rt * 2

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

        self.geometry_plot.ax.clear()

        self.geometry_plot.ax.plot(x, y)
        self.geometry_plot.ax.plot(x, [-v for v in y])

        self.geometry_plot.ax.set_aspect("equal")

        self.geometry_plot.draw()

        # display dimensions

        self.dimensions.setText(
            f"Throat Radius: {rt:.4f} m   |   Exit Radius: {re:.4f} m   |   "
            f"Chamber Radius: {rc:.4f} m   |   Nozzle Length: {L:.4f} m"
        )

    # -------------------------
    # MESH GENERATION
    # -------------------------

    def generate_mesh(self):

        if self.contour is None:

            QMessageBox.warning(self, "Error", "Run simulation first")
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
            return

        self.mesh_plot.ax.triplot(
            points[:, 0],
            points[:, 1],
            cells,
            linewidth=0.5
        )

        self.mesh_plot.ax.set_aspect("equal")

        self.mesh_plot.draw()