from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import numpy as np
import markdown

from core.inputs import EngineInputs
from core.engine_solver import run_engine_pipeline


# -------------------------
# Markdown + LaTeX Viewer
# -------------------------
class MarkdownViewer(QWebEngineView):
    def set_markdown(self, md_text):
        html_body = markdown.markdown(md_text)

        html = f"""
        <html>
        <head>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <style>
        body {{
            background-color: #111;
            color: white;
            font-family: Arial;
            padding: 15px;
        }}
        </style>
        </head>
        <body>
        {html_body}
        </body>
        </html>
        """

        self.setHtml(html)


# -------------------------
# Plot Canvas
# -------------------------
class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self):
        fig = Figure(facecolor="#111")
        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor("#111")
        self.ax.tick_params(colors="white")
        super().__init__(fig)


# -------------------------
# Range Input
# -------------------------
class RangeInput(QWidget):
    def __init__(self, label, mn, mx):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        title = QLabel(label)
        layout.addWidget(title)

        row = QHBoxLayout()

        self.min = QLineEdit(str(mn))
        self.slider = QSlider(Qt.Horizontal)
        self.max = QLineEdit(str(mx))
        self.val = QDoubleSpinBox()

        row.addWidget(self.min)
        row.addWidget(self.slider)
        row.addWidget(self.max)

        layout.addLayout(row)
        layout.addWidget(self.val)

        self.setLayout(layout)

        self.update_all()

        self.min.editingFinished.connect(self.update_all)
        self.max.editingFinished.connect(self.update_all)
        self.slider.valueChanged.connect(
            lambda: self.val.setValue(float(self.slider.value()))
        )
        self.val.valueChanged.connect(
            lambda: self.slider.setValue(int(self.val.value()))
        )

    def update_all(self):
        try:
            mn = float(self.min.text())
            mx = float(self.max.text())
        except ValueError:
            return

        if mn >= mx:
            return

        self.slider.setMinimum(int(mn))
        self.slider.setMaximum(int(mx))

        self.val.setMinimum(mn)
        self.val.setMaximum(mx)
        self.val.setDecimals(3)

        current = self.val.value()
        if current < mn or current > mx or current == 0:
            current = (mn + mx) / 2

        self.slider.setValue(int(current))
        self.val.setValue(current)

    def get(self):
        return self.val.value()


# -------------------------
# MAIN WINDOW
# -------------------------
class ImpulseLabsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Impulse Labs")
        self.resize(1800, 900)

        self._last_result = None

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.sim_tab(), "Simulation")
        self.tabs.addTab(self.export_tab(), "Export")

    # -------------------------
    # TAB 1
    # -------------------------
    def sim_tab(self):
        layout = QHBoxLayout()

        layout.addWidget(self.input_col(), 1)
        layout.addWidget(self.learning_col(), 1)
        layout.addWidget(self.plot_col(), 3)
        layout.addWidget(self.llm_col(), 1)

        w = QWidget()
        w.setLayout(layout)
        return w

    # -------------------------
    # INPUT COLUMN
    # -------------------------
    def input_col(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Inputs"))

        self.thrust = RangeInput("Thrust", 100, 5000)
        self.pc = RangeInput("Chamber Pressure", 5, 100)
        self.mr = RangeInput("Mixture Ratio", 1, 5)

        layout.addWidget(self.thrust)
        layout.addWidget(self.pc)
        layout.addWidget(self.mr)

        self.prop = QComboBox()
        self.prop.addItems(["LOX/RP1", "LOX/LH2", "N2O/CH4"])
        layout.addWidget(self.prop)

        self.ox_temp = QLineEdit()
        self.ox_temp.setPlaceholderText("Ox Temp (optional)")
        layout.addWidget(self.ox_temp)

        self.fuel_temp = QLineEdit()
        self.fuel_temp.setPlaceholderText("Fuel Temp (optional)")
        layout.addWidget(self.fuel_temp)

        self.contraction_ratio_input = QLineEdit()
        self.contraction_ratio_input.setPlaceholderText("Contraction Ratio (optional)")
        layout.addWidget(self.contraction_ratio_input)

        self.ambient_pressure_input = QLineEdit()
        self.ambient_pressure_input.setPlaceholderText("Ambient Pressure (bar) (optional)")
        layout.addWidget(self.ambient_pressure_input)

        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setText("Defines propulsion conditions and geometry.")
        layout.addWidget(desc)

        layout.addWidget(QPushButton("Explain (LLM)"))

        w = QWidget()
        w.setLayout(layout)
        return w

    # -------------------------
    # LEARNING COLUMN
    # -------------------------
    def learning_col(self):
        layout = QVBoxLayout()

        self.learn_toggle = QCheckBox("Learning Mode")
        layout.addWidget(self.learn_toggle)

        self.learn_view = MarkdownViewer()
        self.learn_view.set_markdown(
            r"""
# Isentropic Flow

$$
T/T_0 = \frac{1}{1 + \frac{\gamma - 1}{2} M^2}
$$

$$
P/P_0 = (T/T_0)^{\frac{\gamma}{\gamma - 1}}
$$
"""
        )
        layout.addWidget(self.learn_view)

        reload_btn = QPushButton("Reload")
        reload_btn.clicked.connect(self.reload_learning)
        layout.addWidget(reload_btn)

        w = QWidget()
        w.setLayout(layout)
        return w

    def reload_learning(self):
        if not self.learn_toggle.isChecked():
            self.learn_view.set_markdown("Learning Mode Disabled")
            return

        self.learn_view.set_markdown(
            r"""
# Rao Nozzle Approximation

$$
y = ax^2 + bx + c
$$

$$
\frac{dy}{dx} = \tan(\theta_e)
$$
"""
        )

    # -------------------------
    # PLOT COLUMN
    # -------------------------
    def plot_col(self):
        layout = QVBoxLayout()

        self.plot = PlotCanvas()
        layout.addWidget(self.plot)

        row = QHBoxLayout()

        self.mode = QComboBox()
        self.mode.addItems(["Mach", "Temperature", "Pressure"])
        self.mode.currentIndexChanged.connect(self.rerender_last_result)

        row.addWidget(QLabel("Field"))
        row.addWidget(self.mode)

        layout.addLayout(row)

        self.info = QLabel("Nozzle Data")
        layout.addWidget(self.info)

        self.run_btn = QPushButton("Run Simulation")
        self.run_btn.clicked.connect(self.run_sim)
        layout.addWidget(self.run_btn)

        w = QWidget()
        w.setLayout(layout)
        return w

    # -------------------------
    # LLM COLUMN
    # -------------------------
    def llm_col(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("LLM"))

        chat = QTextEdit()
        layout.addWidget(chat)

        api_btn = QPushButton("Set API Key")
        api_btn.clicked.connect(self.api_popup)
        layout.addWidget(api_btn)

        w = QWidget()
        w.setLayout(layout)
        return w

    def api_popup(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("API Config")

        l = QVBoxLayout()

        api_key = QLineEdit()
        api_key.setPlaceholderText("API Key")
        l.addWidget(api_key)

        secret = QLineEdit()
        secret.setPlaceholderText("Secret")
        l.addWidget(secret)

        provider = QComboBox()
        l.addWidget(provider)

        dlg.setLayout(l)
        dlg.exec()

    # -------------------------
    # INPUT HELPERS
    # -------------------------
    def _read_optional_float(self, widget, default):
        text = widget.text().strip()
        if not text:
            return default
        try:
            return float(text)
        except ValueError:
            return default

    def _build_inputs(self):
        prop = self.prop.currentText()

        if prop == "LOX/RP1":
            oxidizer, fuel = "LOX", "RP1"
        elif prop == "LOX/LH2":
            oxidizer, fuel = "LOX", "LH2"
        elif prop == "N2O/CH4":
            oxidizer, fuel = "N2O", "CH4"
        else:
            oxidizer, fuel = "LOX", "RP1"

        return EngineInputs(
            thrust=float(self.thrust.get()),
            oxidizer=oxidizer,
            fuel=fuel,
            chamber_pressure_bar=float(self.pc.get()),
            mixture_ratio=float(self.mr.get()),
            ambient_pressure_bar=self._read_optional_float(
                self.ambient_pressure_input, 1.0
            ),
            contraction_ratio=self._read_optional_float(
                self.contraction_ratio_input, 3.0
            ),
        )

    # -------------------------
    # SIMULATION
    # -------------------------
    def run_sim(self):
        self.run_btn.setEnabled(False)
        self.info.setText("Running...")
        QApplication.processEvents()

        try:
            inputs = self._build_inputs()
            result = run_engine_pipeline(inputs)

            self._last_result = result
            self.update_plot(result["contour"], result["solution"])
            self.update_info(result["solution"])

        except Exception as exc:
            self.info.setText(f"Pipeline failed: {type(exc).__name__}: {exc}")
            print(f"\nPIPELINE FAILED -> {type(exc).__name__}: {exc}\n")
            raise

        finally:
            self.run_btn.setEnabled(True)

    def rerender_last_result(self):
        if self._last_result is None:
            return

        self.update_plot(
            self._last_result["contour"],
            self._last_result["solution"],
        )

    # -------------------------
    # PLOT HELPERS
    # -------------------------
    @staticmethod
    def _approx_mach(area_ratio, supersonic):
        gamma = 1.4
        M = 2.0 if supersonic else 0.5

        for _ in range(50):
            t = 1.0 + 0.5 * (gamma - 1.0) * M**2
            exp = (gamma + 1.0) / (2.0 * (gamma - 1.0))
            f = ((2.0 / (gamma + 1.0)) * t) ** exp / M - area_ratio
            df = ((2.0 / (gamma + 1.0)) * t) ** exp * (
                (gamma - 1.0) * M / t - 1.0 / M**2
            )

            if abs(df) < 1e-12:
                break

            M -= f / df
            M = max(M, 1e-6)

        return M

    def update_plot(self, contour, solution):
        x = np.array([p[0] for p in contour], dtype=float)
        y = np.array([p[1] for p in contour], dtype=float)

        A = np.pi * y**2
        At = np.pi * float(solution["rt"]) ** 2
        eps = np.where(A > 0, A / At, 1.0)

        throat_idx = int(np.argmin(A))

        M = np.ones_like(eps)
        for i, e in enumerate(eps):
            M[i] = self._approx_mach(e, supersonic=(i >= throat_idx))

        gamma = float(solution["gamma"])
        T = 1.0 / (1.0 + 0.5 * (gamma - 1.0) * M**2)
        P = T ** (gamma / (gamma - 1.0))

        if self.mode.currentText() == "Mach":
            Z, cmap = M, "viridis"
        elif self.mode.currentText() == "Temperature":
            Z, cmap = T, "inferno"
        else:
            Z, cmap = P, "cividis"

        y_max = float(np.max(y))
        X, Yg = np.meshgrid(x, np.linspace(-y_max, y_max, 200))
        Zg = np.tile(Z, (200, 1))

        wall = np.interp(X, x, y)
        mask = np.abs(Yg) <= wall
        Zg[~mask] = np.nan

        self.plot.ax.clear()
        self.plot.ax.set_facecolor("#111")
        self.plot.ax.tick_params(colors="white")
        self.plot.ax.xaxis.label.set_color("white")
        self.plot.ax.yaxis.label.set_color("white")

        while len(self.plot.figure.axes) > 1:
            extra_ax = self.plot.figure.axes[-1]
            self.plot.figure.delaxes(extra_ax)

        self.plot.ax.plot(x, y, color="white")
        self.plot.ax.plot(x, -y, color="white")

        im = self.plot.ax.imshow(
            Zg,
            extent=[x.min(), x.max(), -y_max, y_max],
            cmap=cmap,
            origin="lower",
            aspect="auto",
        )

        cbar = self.plot.figure.colorbar(im, ax=self.plot.ax)
        cbar.ax.tick_params(colors="white")
        cbar.outline.set_edgecolor("white")

        self.plot.ax.set_xlabel("Axial Length")
        self.plot.ax.set_ylabel("Radius")

        self.plot.draw()

    def update_info(self, solution):
        self.info.setText(
            f"Isp={solution['Isp']:.1f} s | "
            f"rt={solution['rt']:.4f} m | "
            f"re={solution['re']:.4f} m | "
            f"Me={solution['Me']:.2f} | "
            f"mdot={solution['mdot']:.4f} kg/s | "
            f"Tc={solution['Tc']:.0f} K"
        )

    # -------------------------
    # EXPORT TAB
    # -------------------------
    def export_tab(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Exports"))
        layout.addWidget(QLabel("STEP Preview"))
        layout.addWidget(QLabel("MSH Preview"))

        layout.addWidget(QPushButton("Download STEP"))
        layout.addWidget(QPushButton("Download MSH"))
        layout.addWidget(QPushButton("Export PDF"))
        layout.addWidget(QPushButton("Export DOCX"))

        w = QWidget()
        w.setLayout(layout)
        return w