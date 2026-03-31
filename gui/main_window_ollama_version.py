from llm.ollama_client import ask_ollama
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from geometry.rao import RaoBell
from geometry.converging import converging_parabola
from geometry.throat import throat_fillet
from mesh.msh_generator import generate_axi_mesh
from llm.ollama_client import ask_ollama
import meshio


# -----------------------------
# PLOT CANVAS (DARK THEME)
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
# RANGE SLIDER (MIN-MAX SYSTEM)
# -----------------------------
class RangeSliderWidget(QWidget):

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

        try:
            min_val = float(self.min_box.text())
            max_val = float(self.max_box.text())

            if min_val >= max_val:
                self.min_box.setStyleSheet("background:#550000;")
                return
            else:
                self.min_box.setStyleSheet("")

            self.slider.setMinimum(int(min_val / self.scale))
            self.slider.setMaximum(int(max_val / self.scale))

            mid = (min_val + max_val) / 2

            self.slider.setValue(int(mid / self.scale))

        except:
            pass

    def get_value(self):

        return self.slider.value() * self.scale


# -----------------------------
# MAIN WINDOW
# -----------------------------
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

    # -----------------------------
    # MENU BAR
    # -----------------------------
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

        menu.addMenu("Documentation")
        menu.addMenu("Help")

        llm_menu = menu.addMenu("LLM")
        llm_menu.addAction("Toggle Chat", self.toggle_llm)

    # -----------------------------
    # MAIN LAYOUT
    # -----------------------------
    def create_layout(self):

        central = QWidget()

        self.main_layout = QHBoxLayout()

        self.main_layout.addWidget(self.create_inputs(), 1)
        self.main_layout.addWidget(self.create_plots(), 3)

        central.setLayout(self.main_layout)

        self.setCentralWidget(central)

    # -----------------------------
    # INPUT PANEL
    # -----------------------------
    def create_inputs(self):

        panel = QVBoxLayout()

        panel.addWidget(QLabel("Engine Inputs"))

        # RANGE SLIDERS
        self.thrust = RangeSliderWidget("Thrust (N)", 100, 5000)
        self.pressure = RangeSliderWidget("Chamber Pressure (bar)", 5, 100)
        self.mr = RangeSliderWidget("Mixture Ratio", 1, 5)

        panel.addWidget(self.thrust)
        panel.addWidget(self.pressure)
        panel.addWidget(self.mr)

        # OPTIONAL INPUTS
        panel.addWidget(QLabel("Chamber Temperature (K) [Optional]"))
        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("Auto")
        panel.addWidget(self.temp_input)

        panel.addWidget(QLabel("Contraction Ratio [Optional]"))
        self.contraction_input = QLineEdit()
        self.contraction_input.setPlaceholderText("Auto")
        panel.addWidget(self.contraction_input)

        panel.addWidget(QLabel("Ambient Pressure (bar) [Optional]"))
        self.ambient_input = QLineEdit()
        self.ambient_input.setPlaceholderText("Auto")
        panel.addWidget(self.ambient_input)

        # BUTTONS
        self.run_button = QPushButton("Run Simulation")
        self.mesh_button = QPushButton("Generate Mesh")

        self.run_button.clicked.connect(self.run_simulation)
        self.mesh_button.clicked.connect(self.generate_mesh)

        panel.addWidget(self.run_button)
        panel.addWidget(self.mesh_button)

        # DESCRIPTION
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

    # -----------------------------
    # PLOTS
    # -----------------------------
    def create_plots(self):

        layout = QHBoxLayout()

        self.geometry_plot = PlotCanvas("Nozzle Geometry")
        self.mesh_plot = PlotCanvas("CFD Mesh")

        layout.addWidget(self.geometry_plot)
        layout.addWidget(self.mesh_plot)

        container = QWidget()
        container.setLayout(layout)

        return container

    # -----------------------------
    # LLM PANEL (RIGHT SIDE)
    # -----------------------------
    def create_llm_panel(self):

        self.llm_panel = QDockWidget("LLM Assistant", self)

        container = QWidget()
        layout = QVBoxLayout()
	
	self.chat_display=QTextEdit()
	self.chat_display.setReadOnly(True)

        self.chat_input = QTextEdit()
	self.chat_input.setPlaceholderText("Ask anything about rocket engines, CFD, or ML...")

        self.send_button = QPushButton("Send")
   	self.send_button.clicked.connect(self.send_llm_message)

    	layout.addWidget(self.chat_display)
    	layout.addWidget(self.chat_input)
    	layout.addWidget(self.send_button)

    	container.setLayout(layout)

    	self.llm_panel.setWidget(container)

    	self.addDockWidget(Qt.RightDockWidgetArea, self.llm_panel)

    	self.llm_panel.hide()

  

    def toggle_llm(self):

        self.llm_panel.setVisible(not self.llm_panel.isVisible())
    def send_llm_message(self):

    	prompt = self.chat_input.toPlainText().strip()

   	if not prompt:
        	return

    	self.chat_display.append("You: " + prompt)

    	self.chat_input.clear()

    	self.chat_display.append("Bot: Thinking...")

    	QApplication.processEvents()

    	try:
        	response = ask_ollama(prompt)
        	self.chat_display.append(response)

    	except Exception as e:
        	self.chat_display.append("Error: " + str(e))

    # -----------------------------
    # STATUS BAR
    # -----------------------------
    def create_status(self):

        self.status = QLabel("Geometry dimensions (SI Units)")

        self.statusBar().addWidget(self.status)

    # -----------------------------
    # SIMULATION
    # -----------------------------
    def run_simulation(self):

        thrust = self.thrust.get_value()

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
            f"rt={rt:.4f} m | re={re:.4f} m | rc={rc:.4f} m | L={L:.4f} m"
        )

    # -----------------------------
    # MESH
    # -----------------------------
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

    # -----------------------------
    def toggle_fullscreen(self):

        self.showNormal() if self.isFullScreen() else self.showFullScreen()
