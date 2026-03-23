# ui/main_window.py

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import numpy as np
import cadquery as cq
import meshio

from geometry.rao import RaoBell
from geometry.converging import converging_parabola
from geometry.throat import throat_fillet


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

        layout.addWidget(QLabel(label))

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
        self.slider.valueChanged.connect(lambda: self.val.setValue(self.slider.value()))
        self.val.valueChanged.connect(lambda: self.slider.setValue(int(self.val.value())))

    def update_all(self):
        mn, mx = float(self.min.text()), float(self.max.text())
        if mn >= mx: return
        self.slider.setMinimum(int(mn))
        self.slider.setMaximum(int(mx))
        mid = (mn+mx)/2
        self.slider.setValue(int(mid))
        self.val.setValue(mid)

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

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.sim_tab(), "Simulation")
        self.tabs.addTab(self.export_tab(), "Export")

    # -------------------------
    # TAB 1
    # -------------------------
    def sim_tab(self):

        layout = QHBoxLayout()

        layout.addWidget(self.input_col(),1)
        layout.addWidget(self.learning_col(),1)
        layout.addWidget(self.plot_col(),3)
        layout.addWidget(self.llm_col(),1)

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

        self.thrust = RangeInput("Thrust",100,5000)
        self.pc = RangeInput("Chamber Pressure",5,100)
        self.mr = RangeInput("Mixture Ratio",1,5)

        layout.addWidget(self.thrust)
        layout.addWidget(self.pc)
        layout.addWidget(self.mr)

        self.prop = QComboBox()
        self.prop.addItems(["LOX/RP1","LOX/LH2","N2O/CH4"])
        layout.addWidget(self.prop)

        # optional
        for name in ["Ox Temp","Fuel Temp","Contraction Ratio","Ambient Pressure"]:
            box = QLineEdit()
            box.setPlaceholderText(name+" (optional)")
            layout.addWidget(box)

        # description
        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setText("Defines propulsion conditions and geometry.")
        layout.addWidget(desc)

        btn = QPushButton("Explain (LLM)")
        layout.addWidget(btn)

        return QWidget(layout=layout)

    # -------------------------
    # LEARNING COLUMN
    # -------------------------
    def learning_col(self):

        layout = QVBoxLayout()

        self.learn_toggle = QCheckBox("Learning Mode")
        layout.addWidget(self.learn_toggle)

        self.learn_text = QTextEdit()
        self.learn_text.setMarkdown(
            "## Isentropic Flow\n"
            "$T/T_0 = 1/(1+(γ-1)/2M^2)$"
        )

        layout.addWidget(self.learn_text)

        reload = QPushButton("Reload")
        layout.addWidget(reload)

        return QWidget(layout=layout)

    # -------------------------
    # PLOT COLUMN (FIXED)
    # -------------------------
    def plot_col(self):

        layout = QVBoxLayout()

        self.plot = PlotCanvas()
        layout.addWidget(self.plot)

        # toggle
        row = QHBoxLayout()

        self.mode = QComboBox()
        self.mode.addItems(["Mach","Temperature","Pressure"])
        self.mode.currentIndexChanged.connect(self.run_sim)

        row.addWidget(QLabel("Field"))
        row.addWidget(self.mode)

        layout.addLayout(row)

        self.info = QLabel("Nozzle Data")
        layout.addWidget(self.info)

        run = QPushButton("Run Simulation")
        run.clicked.connect(self.run_sim)
        layout.addWidget(run)

        return QWidget(layout=layout)

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

        return QWidget(layout=layout)

    # -------------------------
    # API POPUP
    # -------------------------
    def api_popup(self):

        dlg = QDialog(self)
        dlg.setWindowTitle("API Config")

        l = QVBoxLayout()

        l.addWidget(QLineEdit("API Key"))
        l.addWidget(QLineEdit("Secret"))
        l.addWidget(QComboBox())

        dlg.setLayout(l)
        dlg.exec()

    # -------------------------
    # SIMULATION CORE (FIXED)
    # -------------------------
    def run_sim(self):

        thrust = self.thrust.get()

        rt = 0.01 + thrust/20000
        re = rt*3
        rc = rt*2

        conv = converging_parabola(rc,rt,0,0.03)
        throat = throat_fillet(rt,0.01,conv[-1][0])
        rao = RaoBell()

        L = rao.length(rt,re)
        bell = rao.contour(rt,re,L,throat[-1][0])

        contour = conv + throat + bell

        x = np.array([p[0] for p in contour])
        y = np.array([p[1] for p in contour])

        # flow
        A = np.pi*y**2
        At = min(A)

        M = np.sqrt(A/At)
        T = 1/(1+0.2*M**2)
        P = T**3.5

        if self.mode.currentText()=="Mach":
            Z, cmap = M, "viridis"
        elif self.mode.currentText()=="Temperature":
            Z, cmap = T, "inferno"
        else:
            Z, cmap = P, "cividis"

        X,Yg = np.meshgrid(x,np.linspace(-max(y),max(y),200))
        Zg = np.tile(Z,(200,1))

        # mask outside nozzle
        mask = np.abs(Yg) <= np.interp(X[0],x,y)
        Zg[~mask] = np.nan

        self.plot.ax.clear()

        self.plot.ax.plot(x,y,color="white")
        self.plot.ax.plot(x,-y,color="white")

        im = self.plot.ax.imshow(
            Zg,
            extent=[x.min(),x.max(),-max(y),max(y)],
            cmap=cmap,
            origin="lower",
            aspect="auto"
        )

        self.plot.figure.colorbar(im,ax=self.plot.ax)

        self.plot.ax.set_xlabel("Axial Length")
        self.plot.ax.set_ylabel("Radius")

        self.plot.draw()

        self.info.setText(
            f"rt={rt:.4f} m | re={re:.4f} m | L={L:.4f} m | Me={M[-1]:.2f}"
        )

    # -------------------------
    # TAB 2 EXPORT
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

        return QWidget(layout=layout)