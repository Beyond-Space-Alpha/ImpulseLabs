from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction

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
# Range Input (ONLY ADDITION: hover hook)
# -------------------------
class RangeInput(QWidget):
    def __init__(self, label, mn, mx, tooltip="", parent_window=None):
        super().__init__()

        self.desc = tooltip
        self.parent_window = parent_window

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        title = QLabel(label)
        title.setToolTip(tooltip)
        title.setMouseTracking(True)

        layout.addWidget(title)

        row = QHBoxLayout()

        self.min = QLineEdit(str(mn))
        self.slider = QSlider(Qt.Horizontal)
        self.max = QLineEdit(str(mx))
        self.val = QDoubleSpinBox()
        self.setToolTip(tooltip)

        for w in [self.min, self.slider, self.max, self.val]:
            w.setToolTip(tooltip)

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
    

    # 🔥 NEW: hover updates description panel
    def enterEvent(self, event):
        if self.parent_window and hasattr(self.parent_window, "desc_box"):
            self.parent_window.desc_box.setText(self.desc)
        super().enterEvent(event)

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
        self.llm_visible = True

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.sim_tab(), "Simulation")
        self.tabs.addTab(self.export_tab(), "Export")

        self.create_menu()

    # -------------------------
    # MENU BAR
    # -------------------------
    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.reset_inputs)

        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_inputs)

        sim_tab_action = QAction("Simulation Tab", self)
        sim_tab_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))

        export_tab_action = QAction("Export Tab", self)
        export_tab_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))

        file_menu.addAction(new_action)
        file_menu.addAction(reset_action)
        file_menu.addSeparator()
        file_menu.addAction(sim_tab_action)
        file_menu.addAction(export_tab_action)

        view_menu = menubar.addMenu("View")

        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)

        view_menu.addAction(fullscreen_action)

        llm_menu = menubar.addMenu("LLM")

        agent_action = QAction("Set Agent", self)
        agent_action.triggered.connect(self.api_popup)

        toggle_chat = QAction("Toggle Chat Panel", self)
        toggle_chat.triggered.connect(self.toggle_llm_panel)

        llm_menu.addAction(agent_action)
        llm_menu.addAction(toggle_chat)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def update_plot(self, contour, solution):
        x = np.array([p[0] for p in contour], dtype=float)
        y = np.array([p[1] for p in contour], dtype=float)

        # Basic area ratio reconstruction
        A = np.pi * y**2
        At = np.pi * float(solution["rt"]) ** 2
        eps = np.where(A > 0, A / At, 1.0)

        throat_idx = int(np.argmin(np.abs(y - float(solution["rt"]))))

        gamma = float(solution["gamma"])

        M = np.ones_like(eps)
        for i, e in enumerate(eps):
            M[i] = self._approx_mach(e, gamma=gamma, supersonic=(i >= throat_idx))

        T = 1.0 / (1.0 + 0.5 * (gamma - 1.0) * M**2)
        P = T ** (gamma / (gamma - 1.0))

        if self.mode.currentText() == "Mach":
            Z, label, cmap = M, "Mach", "viridis"
        elif self.mode.currentText() == "Temperature":
            Z, label, cmap = T, "T/Tc", "inferno"
        else:
            Z, label, cmap = P, "P/Pc", "cividis"

        y_max = float(np.max(y))
        yg = np.linspace(-y_max, y_max, 300)
        X, Yg = np.meshgrid(x, yg)
        Zg = np.tile(Z, (len(yg), 1))

        wall = np.interp(X[0], x, y)
        wall2d = np.tile(wall, (len(yg), 1))
        mask = np.abs(Yg) <= wall2d
        Zg = np.where(mask, Zg, np.nan)

        # ---- Clean redraw ----
        self.plot.figure.clear()
        ax = self.plot.figure.add_subplot(111)
        self.plot.ax = ax

        ax.set_facecolor("#111")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        for spine in ax.spines.values():
            spine.set_color("white")

        # Filled field inside nozzle
        im = ax.pcolormesh(X, Yg, Zg, shading="auto", cmap=cmap)

        # Nozzle wall
        ax.plot(x, y, color="white", linewidth=2.0)
        ax.plot(x, -y, color="white", linewidth=2.0)

        # Centerline
        ax.plot(x, np.zeros_like(x), color="gray", linestyle="--", linewidth=0.8, alpha=0.7)

        ax.set_xlabel("Axial Length (m)")
        ax.set_ylabel("Radius (m)")
        ax.set_title("Nozzle Contour", color="white")

        # THIS is the important part that fixes distortion
        ax.set_aspect("equal", adjustable="box")

        cbar = self.plot.figure.colorbar(im, ax=ax)
        cbar.set_label(label, color="white")
        cbar.ax.tick_params(colors="white")
        cbar.outline.set_edgecolor("white")

        self.plot.figure.tight_layout()
        self.plot.draw()
    
    @staticmethod
    def _approx_mach(area_ratio, gamma, supersonic):
        if area_ratio <= 1.0:
            return 1.0

        M = 2.0 if supersonic else 0.2

        for _ in range(100):
            t = 1.0 + 0.5 * (gamma - 1.0) * M**2
            exp = (gamma + 1.0) / (2.0 * (gamma - 1.0))
            f = ((2.0 / (gamma + 1.0)) * t) ** exp / M - area_ratio

            # Numerical derivative
            dM = 1e-6
            Mp = M + dM
            tp = 1.0 + 0.5 * (gamma - 1.0) * Mp**2
            fp = ((2.0 / (gamma + 1.0)) * tp) ** exp / Mp - area_ratio
            df = (fp - f) / dM

            if abs(df) < 1e-12:
                break

            M_new = M - f / df

            if supersonic:
                M = max(M_new, 1.0001)
            else:
                M = min(max(M_new, 1e-6), 0.9999)

        return M
    
    def update_info(self, solution):
        self.info.setText(
            f"Isp={solution['Isp']:.1f} s | "
            f"rt={solution['rt']:.4f} m | "
            f"re={solution['re']:.4f} m | "
            f"Me={solution['Me']:.2f} | "
            f"mdot={solution['mdot']:.4f} kg/s | "
            f"Tc={solution['Tc']:.0f} K"
        )

    def toggle_llm_panel(self):
        self.llm_visible = not self.llm_visible
        self.llm_widget.setVisible(self.llm_visible)

    def reset_inputs(self):
        self.thrust.val.setValue(1000)
        self.pc.val.setValue(50)
        self.mr.val.setValue(2.5)

        self.ox_temp.clear()
        self.fuel_temp.clear()
        self.contraction_ratio_input.clear()
        self.ambient_pressure_input.clear()

    # -------------------------
    # TAB 1
    # -------------------------
    def sim_tab(self):
        layout = QHBoxLayout()

        layout.addWidget(self.input_col(), 1)
        layout.addWidget(self.learning_col(), 1)
        layout.addWidget(self.plot_col(), 3)

        self.llm_widget = self.llm_col()
        layout.addWidget(self.llm_widget, 1)

        w = QWidget()
        w.setLayout(layout)
        return w

    def learning_col(self):
        layout = QVBoxLayout()

        self.learn_toggle = QCheckBox("Learning Mode")
        layout.addWidget(self.learn_toggle)

        self.learn_view = MarkdownViewer()
        self.learn_view.set_markdown("Learning...")
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
"""
# ImpulseLabs Propulsion Design – Fully Solved Flow

## Input Parameters
- Chamber Pressure (Pc) = 30 bar = 3 × 10^6 Pa  
- Mixture Ratio (O/F) = 2.5  
- Thrust (F) = 1000 N  
- Propellants = LOX + RP-1  
- Contraction Ratio (CR) = 3  

---

## 1. Thermochemical Properties

- Chamber Temperature → Tc ≈ 3500 K  
- Specific Heat Ratio → γ ≈ 1.22  
- Gas Constant → R ≈ 355 J/kg·K  
- Characteristic Velocity → c* ≈ 1650 m/s  

---

## 2. Isentropic Relations

### Pressure
$$
\\frac{P}{P_c} = \\left(1 + \\frac{\\gamma - 1}{2} M^2 \\right)^{-\\frac{\\gamma}{\\gamma - 1}}
$$

### Temperature
$$
\\frac{T}{T_c} = \\left(1 + \\frac{\\gamma - 1}{2} M^2 \\right)^{-1}
$$

---

## 3. Exit Conditions (Assume Me ≈ 3)

### Exit Pressure
$$
P_e ≈ 0.1 \\times P_c = 3 \\text{ bar}
$$

### Exit Temperature
$$
T_e = 3500 \\times (1 + 0.11 \\times 9)^{-1} ≈ 1750 \\text{ K}
$$

---

## 4. Exit Velocity

$$
V_e = \\sqrt{ \\frac{2 \\gamma}{\\gamma - 1} \\cdot R \\cdot T_c \\cdot \\left(1 - \\left(\\frac{P_e}{P_c}\\right)^{\\frac{\\gamma - 1}{\\gamma}} \\right)}
$$

$$
V_e ≈ 2600 \\text{ m/s}
$$

---

## 5. Specific Impulse

$$
I_{sp} = \\frac{V_e}{g_0}
$$

$$
I_{sp} ≈ \\frac{2600}{9.81} ≈ 265 \\text{ s}
$$

---

## 6. Thrust Coefficient

$$
C_f ≈ 1.5
$$

---

## 7. Mass Flow Rate

$$
\\dot{m} = \\frac{F}{C_f \\cdot c^*}
$$

$$
\\dot{m} = \\frac{1000}{1.5 \\times 1650} ≈ 0.404 \\text{ kg/s}
$$

---

## 8. Throat Area

$$
A_t = \\frac{\\dot{m} \\cdot c^*}{P_c}
$$

$$
A_t = \\frac{0.404 \\times 1650}{3 \\times 10^6} ≈ 2.22 \\times 10^{-4} \\text{ m}^2
$$

### Throat Radius
$$
R_t = \\sqrt{\\frac{A_t}{\\pi}} ≈ 8.4 \\text{ mm}
$$

---

## 9. Expansion Ratio

$$
\\epsilon ≈ 6
$$

---

## 10. Exit Area

$$
A_e = \\epsilon \\cdot A_t
$$

$$
A_e ≈ 1.33 \\times 10^{-3} \\text{ m}^2
$$

### Exit Radius
$$
R_e = \\sqrt{\\frac{A_e}{\\pi}} ≈ 20.6 \\text{ mm}
$$

---

## 11. Chamber Geometry

### Chamber Area
$$
A_c = CR \\cdot A_t
$$

$$
A_c ≈ 6.66 \\times 10^{-4} \\text{ m}^2
$$

### Chamber Radius
$$
R_c = \\sqrt{\\frac{A_c}{\\pi}} ≈ 14.6 \\text{ mm}
$$

---

### Characteristic Length (Assume L* ≈ 1 m)

$$
L_c = \\frac{L^* \\cdot A_t}{A_c}
$$

$$
L_c ≈ 0.33 \\text{ m}
$$

---

## 12. Rao Nozzle Geometry

- Entrant Radius = 1.5 Rt ≈ 12.6 mm  
- Throat Radius = 0.382 Rt ≈ 3.2 mm  
- Initial Angle = 15°  
- Exit Angle = 30°  

---

## 13. Final Results

| Parameter | Value |
|----------|------|
| Exit Velocity | 2600 m/s |
| Specific Impulse | 265 s |
| Mass Flow Rate | 0.404 kg/s |
| Throat Radius | 8.4 mm |
| Exit Radius | 20.6 mm |
| Chamber Length | 0.33 m |
| Expansion Ratio | 6 |

---

## Flow Summary

Inputs → Combustion → Expansion → Velocity → Thrust → Geometry → Nozzle

---

## TLDR

- 30 bar LOX/RP1 gives ~2600 m/s exhaust  
- ~0.4 kg/s flow needed for 1000 N thrust  
- Compact engine: ~8 mm throat, ~20 mm exit  
- Solid baseline design for small rocket engine  

"""
)  
        
    def rerender_last_result(self):
        if self._last_result is None:
            return

        self.update_plot(
            self._last_result["contour"],
            self._last_result["solution"],
        )
        
        
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
            self.info.setText(f"Error: {str(exc)}")
            QMessageBox.critical(self, "Simulation Error", str(exc))

        finally:
            self.run_btn.setEnabled(True)
            
    def llm_col(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("LLM"))

        self.chat = QTextEdit()
        layout.addWidget(self.chat)

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
    # INPUT COLUMN (ONLY MODIFIED: desc_box + parent wiring)
    # -------------------------
    def input_col(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Inputs"))

        self.thrust = RangeInput(
            "Thrust",
            100,
            5000,
            "Engine thrust (Newtons). Determines total force output.",
            parent_window=self
        )
        self.pc = RangeInput(
            "Chamber Pressure",
            5,
            100,
            "Pressure inside combustion chamber (bar). Affects efficiency and expansion.",
            parent_window=self
        )
        self.mr = RangeInput(
            "Mixture Ratio",
            1,
            5,
            "Oxidizer to fuel ratio. Controls combustion characteristics.",
            parent_window=self
        )

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

        # 🔥 modified
        self.desc_box = QTextEdit()
        self.desc_box.setReadOnly(True)
        self.desc_box.setText("Defines propulsion conditions and geometry.")
        layout.addWidget(self.desc_box)

        layout.addWidget(QPushButton("Explain (LLM)"))

        w = QWidget()
        w.setLayout(layout)
        return w
    
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
        
    def _read_optional_float(self, widget, default):
        text = widget.text().strip()
        if not text:
            return default
        try:
            return float(text)
        except ValueError:
            return default

    # -------------------------
    # REMAINING CODE = EXACT SAME
    # (unchanged from your original)