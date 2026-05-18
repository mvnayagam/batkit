# ***batkit* - *Bat*tery data processing *kit***

**`batkit`** is a lightweight Python toolkit for electrochemical and battery-data analysis with emphasis on:

- simplicity
- reproducibility
- notebook-based workflows
- publication-quality visualization
- modular scientific software design

The package combines efficient data-processing utilities with reusable plotting tools to streamline analysis of EC-Lab and BT-lab experimental datasets.

---

# `mprtools` Class

The `mprtools` class provides utilities for reading, processing, filtering, and exporting electrochemical data stored in EC-Lab `.mpr` files. It acts as the primary data-access layer of `batkit`, converting raw experimental measurements into structured pandas DataFrames suitable for scientific analysis and visualization.

The class is designed for notebook-friendly workflows and supports efficient handling of galvanostatic cycling, impedance spectroscopy, and time-dependent electrochemical datasets.

## Main Features

- Read EC-Lab `.mpr` files using `yadg`
- Automatic conversion to pandas DataFrame
- Automatic cycle-number generation from half-cycle data
- Extraction of selected columns as NumPy arrays
- Cycle-range filtering utilities
- Export selected data columns to text/CSV formats
- Cached dataset loading for improved performance

## Typical Usage

```python
from lib.mprtools import mprtools

pad = os.getcwd()
ds  = mprtool(path=os.path.join(pad), filename="test.mpr")
df  = ds.load()

df.export_csv(
    columns=["freq", "|Z|", "Phase(Z)"],
    start_cycle=0,
    end_cycle=10
)
```
By default, the exported data will be written to `filename_{columns}.dat`. Example, `test_freq_Z_Phasez.dat`.

---

# `plotdata` Class

The `plotdata` class contains high-level scientific plotting utilities for electrochemical and battery-analysis workflows. The class provides standardized visualization tools for cycling performance, impedance spectroscopy, voltage/current profiles, and time-dependent electrochemical behavior.

The plotting API is designed to generate publication-quality matplotlib figures while maintaining flexibility for interactive notebook analysis.

The class internally uses shared styling utilities through the `PlotStyle` base class to ensure consistent figure formatting across all plots.

## Main Features

- Charge/discharge capacity vs cycle plots
- Bode impedance visualization
- Voltage/current vs time plots
- Voltage/current vs cycle-number plots
- Time-cycle synchronized electrochemical plots
- Dual-axis and secondary-axis plotting utilities
- Automatic tick/grid styling
- Publication-oriented figure formatting
- Figure/axes return support for further customization

## Typical Usage

```python
from lib.plotdata import plotdata

plotdata.plot_Qchargedischarge(df)

plotdata.plot_bode_impedance(
    df,
    startcyclerange=0,
    endcyclerange=20
)

fig, ax = plotdata.timevsEandI(df)
```
By default, saving figure is not activated. To save the plots

```python
fig.savefig("select-filename.{png or pdf}", dpi=600)
```

The usage of `batkit` is explained in jupyter notebook, available in ``./example/ex01-testmpr``.

-----

To install `batkit`, use `pyproject.toml`

# Contributors:
  - [Muthu Vallinayagam](https://github.com/mvnayagam)
  - [Oliver Schmidt]()
  - 

# Acknowledgements
This small project is developed under the funding programm:
  - [Alpobat](https://blogs.hrz.tu-freiberg.de/alpobat/)