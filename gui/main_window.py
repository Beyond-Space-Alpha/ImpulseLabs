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
        self.resize(1500, 850)

        self.contour = None

        self.create_menu()

        self.create_layout()

        self.create_llm_panel()

        self.create_status()

    # ------------------------------------------------
    # MENU
    # ------------------------------------------------

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
        llm_menu.addAction("Toggle Chat", self.toggle_llm)

    # ------------------------------------------------
    # MAIN LAYOUT
    # ------------------------------------------------

    def create_layout(self):

        central = QWidget()

        self.main_layout = QHBoxLayout()

        self.main_layout.addWidget(self.create_inputs(), 1)

        self.main_layout.addWidget(self.create_plots(), 3)

        central.setLayout(self.main_layout)

        self.setCentralWidget(central)

    # ------------------------------------------------
    # INPUT PANEL
    # ------------------------------------------------

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

        # OPTIONAL INPUTS

        panel.addWidget(QLabel("Chamber Temperature (K)  [Optional]"))
        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("Auto if empty")
        panel.addWidget(self.temp_input)

        panel.addWidget(QLabel("Contraction Ratio  [Optional]"))
        self.contraction_input = QLineEdit()
        self.contraction_input.setPlaceholderText("Auto if empty")
        panel.addWidget(self.contraction_input)

        panel.addWidget(QLabel("Ambient Pressure (bar)  [Optional]"))
        self.ambient_input = QLineEdit()
        self.ambient_input.setPlaceholderText("Auto if empty")
        panel.addWidget(self.ambient_input)

        # BUTTONS

        self.run_button = QPushButton("Run Simulation")
        self.mesh_button = QPushButton("Generate Mesh")

        panel.addWidget(self.run_button)
        panel.addWidget(self.mesh_button)

        self.run_button.clicked.connect(self.run_simulation)
        self.mesh_button.clicked.connect(self.generate_mesh)

        # DESCRIPTION

        desc = QTextEdit()
        desc.setReadOnly(True)

        desc.setText(
            "Thrust (N)\nDesired engine thrust.\n\n"
            "Chamber Pressure (bar)\nPressure inside combustion chamber.\n\n"
            "Mixture Ratio\nOxidizer/Fuel mass ratio.\n\n"
            "Optional Inputs\nIf left blank, ImpulseLabs assumes standard values."
        )

        panel.addWidget(QLabel("Parameter Description"))
        panel.addWidget(desc)

        widget = QWidget()
        widget.setLayout(panel)

        return widget

    # ------------------------------------------------
    # SLIDER
    # ------------------------------------------------

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

        return {"widget": widget, "slider": slider, "textbox": textbox}

    # ------------------------------------------------
    # PLOTS
    # ------------------------------------------------

    def create_plots(self):

        layout = QHBoxLayout()

        self.geometry_plot = PlotCanvas("Nozzle Geometry")
        self.mesh_plot = PlotCanvas("CFD Mesh")

        layout.addWidget(self.geometry_plot)
        layout.addWidget(self.mesh_plot)

        container = QWidget()
        container.setLayout(layout)

        return container

    # ------------------------------------------------
    # LLM PANEL
    # ------------------------------------------------

    def create_llm_panel(self):

        self.llm_panel = QDockWidget("Impulse Labs Assistant", self)

        self.llm_panel.setAllowedAreas(Qt.RightDockWidgetArea)

        chat = QTextEdit()

        chat.setPlaceholderText("Ask questions about propulsion, equations, or geometry...")

        self.llm_panel.setWidget(chat)

        self.addDockWidget(Qt.RightDockWidgetArea, self.llm_panel)

        self.llm_panel.hide()

    def toggle_llm(self):

        if self.llm_panel.isVisible():
            self.llm_panel.hide()
        else:
            self.llm_panel.show()

    # ------------------------------------------------
    # STATUS BAR
    # ------------------------------------------------

    def create_status(self):

        self.status = QLabel("Geometry dimensions will appear here (SI units).")

        self.statusBar().addWidget(self.status)

    # ------------------------------------------------
    # SIMULATION
    # ------------------------------------------------

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

    # ------------------------------------------------
    # MESH
    # ------------------------------------------------

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

    # ------------------------------------------------

    def toggle_fullscreen(self):

        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()