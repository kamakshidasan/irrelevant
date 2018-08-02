# irrelevant

To be able to run code from this repository, install TTK using [these](https://topology-tool-kit.github.io/installation.html) guidlelines. This code has been tested with TTK 0.95 on Ubuntu 16.04/MacOS High Sierra. 

TTK provides the ability to visualize and analyse scalar fields.
However, analysing time-varying data by repeating the same tasks over and over again, can be tedious with TTK.

This repository provides code to automate tasks in TTK:

- Display scalar field
- Divide the domain
- Compute persistence diagram
- Simplify scalar field using persistence diagram
- Display critical points
- Compute Merge Trees
- Compute bottleneck/wasserstein distances

To run the code:

- Place your data within the folder titled 'input'
- For details on other folder you may want to create, look into helper.py and compute.py
- Then execute, `python run.py`
- To run TTK parallelly, execute `python test.py <number of files> <number of cores>`
