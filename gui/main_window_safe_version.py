import meshio
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSlider, QPushButton,
    QTextEdit, QDockWidget
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from geometry.rao import RaoBell
from geometry.converging import converging_parabola
from geometry.throat import throat_fillet
from mesh.msh_generator import generate_axi_mesh


# -----------------------------
# PLOT CANVAS (DARK THEME)
# -----------------------------
class PlotCanvas(FigureCanvasQTAgg):
    """Matplotlib canvas configured for a dark UI theme."""

    def __init__(self, title):
        fig = Figure(facecolor="#121212")
        self.ax = fig.add_subplot(111)

        self.ax.set_facecolor("#121212")
        self.ax.set_title(title, color="white")
        self.ax.tick_params(colors="white")

        # Set spine colors to white for visibility
        for spine in self.ax.spines.values():
            spine.set_color("white")

        super().__init__(fig)


# -----------------------------
# RANGE SLIDER (MIN-MAX SYSTEM)
# -----------------------------
class RangeSliderWidget(QWidget):
    """A custom widget combining a QSlider with min/max QLineEdit boxes."""

    def __init__(self, label, min_default, max_default, scale=1):
        super().__init__()

        self.scale = scale

        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))

        row = QHBoxLayout()

        self.min_box = QLineEdit(str(min_default))
        self.min_box.setFixedWidth(60)

        self.slider = QSlider(Qt.Horizontal)

        self.max_box = QLineEdit(str(max_default))
        self.max_box.setFixedWidth(60)

        row.addWidget(self.min_box)
        row.addWidget(self.slider)
        row.addWidget(self.max_box)

        layout.addLayout(row)
        self.setLayout(layout)

        self.update_slider()

        self.min_box.editingFinished.connect(self.update_slider)
        self.max_box.editingFinished.connect(self.update_slider)

    def update_slider(self):
        """Syncs the slider range with the values in the line edits."""
        try:
            min_val = float(self.min_box.text())
            max_val = float(self.max_box.text())

            if min_val >= max_val:
                self.min_box.setStyleSheet("background:#550000;")
                return

            self.min_box.setStyleSheet("")
            self.slider.setMinimum(int(min_val / self.scale))
            self.slider.setMaximum(int(max_val / self.scale))

            mid = (min_val + max_val) / 2
            self.slider.setValue(int(mid / self.scale))

        except ValueError:
            pass

    def get_value(self):
        """Returns the current scaled value of the slider."""
        return self.slider.value() * self.scale


# -----------------------------
# MAIN WINDOW
# -----------------------------
class ImpulseLabsWindow(QMainWindow):
    """Main application window for the nozzle design and mesh tool."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Impulse Labs")
        self.resize(1500, 850)

        self.contour = None

        self.create_menu()
        self.create_layout()
        self.create_llm_panel()
        self.create_status()

    def create_menu(self):
        """Initializes the top menu bar."""
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        file_menu.addAction("New")
        file_menu.addAction("Open Contour")
        file_menu.addAction("Open Mesh")
        file_menu.addAction("Export")
        file_menu.addAction("Download")

        view_menu = menu.addMenu("View")
        view_menu.addAction("Fullscreen", self.toggle_fullscreen)

        menu.addMenu("Documentation")
        menu.addMenu("Help")

        llm_menu = menu.addMenu("LLM")
        llm_menu.addAction("Toggle Chat", self.toggle_llm)

    def create_layout(self):
        """Sets up the main QHBoxLayout splitting inputs and plots."""
        central = QWidget()
        self.main_layout = QHBoxLayout()

        self.main_layout.addWidget(self.create_inputs(), 1)
        self.main_layout.addWidget(self.create_plots(), 3)

        central.setLayout(self.main_layout)
        self.setCentralWidget(central)

    def create_inputs(self):
        """Constructs the left-hand input panel."""
        panel = QVBoxLayout()
        panel.addWidget(QLabel("<b>Engine Inputs</b>"))

        # Range Sliders
        self.thrust = RangeSliderWidget("Thrust (N)", 100, 5000)
        self.pressure = RangeSliderWidget("Chamber Pressure (bar)", 5, 100)
        self.mr = RangeSliderWidget("Mixture Ratio", 1, 5)

        panel.addWidget(self.thrust)
        panel.addWidget(self.pressure)
        panel.addWidget(self.mr)

        # Optional Inputs
        panel.addWidget(QLabel("Chamber Temperature (K) [Optional]"))
        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("Auto")
        panel.addWidget(self.temp_input)

        panel.addWidget(QLabel("Contraction Ratio [Optional]"))
        self.contraction_input = QLineEdit()
        self.contraction_input.setPlaceholderText("Auto")
        panel.addWidget(self.contraction_input)

        # Buttons
        self.run_button = QPushButton("Run Simulation")
        self.mesh_button = QPushButton("Generate Mesh")

        self.run_button.clicked.connect(self.run_simulation)
        self.mesh_button.clicked.connect(self.generate_mesh)

        panel.addWidget(self.run_button)
        panel.addWidget(self.mesh_button)

        # Description
        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setText(
            "Thrust: Desired force output (N)\n"
            "Chamber Pressure: Pressure inside chamber (bar)\n"
            "Mixture Ratio: Oxidizer/Fuel ratio\n\n"
            "Optional inputs will be assumed if not provided."
        )

        panel.addWidget(QLabel("Description"))
        panel.addWidget(desc)

        widget = QWidget()
        widget.setLayout(panel)
        return widget

    def create_plots(self):
        """Constructs the plotting area with two dark-themed canvases."""
        layout = QHBoxLayout()

        self.geometry_plot = PlotCanvas("Nozzle Geometry")
        self.mesh_plot = PlotCanvas("CFD Mesh")

        layout.addWidget(self.geometry_plot)
        layout.addWidget(self.mesh_plot)

        container = QWidget()
        container.setLayout(layout)
        return container

    def create_llm_panel(self):
        """Sets up the collapsible right-side chat panel."""
        self.llm_panel = QDockWidget("LLM Assistant", self)
        chat = QTextEdit()
        chat.setPlaceholderText("Ask anything...")

        self.llm_panel.setWidget(chat)
        self.addDockWidget(Qt.RightDockWidgetArea, self.llm_panel)
        self.llm_panel.hide()

    def toggle_llm(self):
        """Shows or hides the LLM dock widget."""
        self.llm_panel.setVisible(not self.llm_panel.isVisible())

    def create_status(self):
        """Initializes the status bar."""
        self.status = QLabel("Geometry dimensions (SI Units)")
        self.statusBar().addWidget(self.status)

    def run_simulation(self):
        """Generates geometry and updates the nozzle plot."""
        thrust = self.thrust.get_value()

        # Simple scaling for demonstration
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

        # Assemble full contour while removing overlapping points
        self.contour = chamber + conv[1:] + throat[1:] + bell[1:]

        x = [p[0] for p in self.contour]
        y = [p[1] for p in self.contour]

        self.geometry_plot.ax.clear()
        self.geometry_plot.ax.plot(x, y, color="cyan")
        self.geometry_plot.ax.plot(x, [-v for v in y], color="cyan")
        self.geometry_plot.ax.set_aspect("equal")
        self.geometry_plot.draw()

        self.status.setText(
            f"rt={rt:.4f} m | re={re:.4f} m | rc={rc:.4f} m | L={L:.4f} m"
        )

    def generate_mesh(self):
        """Triggers mesh generation and updates the tri-mesh plot."""
        if self.contour is None:
            return

        generate_axi_mesh(self.contour)

        try:
            mesh = meshio.read("engine_axi.msh")
            points = mesh.points[:, :2]
            cells = None

            for c in mesh.cells:
                if c.type.startswith("triangle"):
                    cells = c.data[:, :3]

            if cells is None:
                return

            self.mesh_plot.ax.clear()
            self.mesh_plot.ax.triplot(
                points[:, 0], points[:, 1], cells,
                linewidth=0.5, color="red"
            )
            self.mesh_plot.ax.set_aspect("equal")
            self.mesh_plot.draw()
        except Exception as e:
            self.status.setText(f"Mesh loading error: {e}")

    def toggle_fullscreen(self):
        """Toggles window fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()