from core.inputs import EngineInputs
from core.performance import compute_performance

from geometry.rao import RaoMethod
from geometry.contour import generate_contour

from cad.nozzle3d import create_nozzle
from cad.step_export import export_step

from mesh.msh_generator import generate_mesh

from utils.plot import plot_contour


def main():

    inputs=EngineInputs(

        chamber_pressure=3e6,
        chamber_temperature=3400,
        gamma=1.22,
        gas_constant=355,
        exit_pressure=101325,
        thrust=500
    )


    perf=compute_performance(inputs)

    rt=perf["rt"]
    re=perf["re"]

    rao=RaoMethod("simple")

    length=rao.compute_length(rt,re)

    contour=generate_contour(rt,re,length)

    plot_contour(contour)

    nozzle=create_nozzle(contour)

    export_step(nozzle,"nozzle.step")

    generate_mesh("nozzle.step","nozzle.msh")

    print("Pipeline complete")


if __name__=="__main__":

    main()