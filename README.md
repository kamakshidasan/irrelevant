# irrelevant

To be able to run code from this repository, install TTK using [these](https://topology-tool-kit.github.io/installation.html) guidlelines. This code has been tested with TTK 0.96 on Ubuntu 16.04/MacOS High Sierra. 

This repository provides code to perform the following tasks.

- Display scalar field
- Divide the domain
- Compute persistence diagram
- Simplify scalar field using persistence diagram
- Display critical points
- Compute Merge Trees
- Compute bottleneck/wasserstein distances
- Vertex Segmentation based on Merge/Contour Trees
- Face Segmentation based on Merge Trees

To run the code:

- Place your data within a folder titled 'input'
- For details on other folders you may want to create, look into `helper.py` and `compute.py`
- Then execute, `python run.py`
- To run TTK parallelly, execute `python test.py <number of files> <number of cores>`
