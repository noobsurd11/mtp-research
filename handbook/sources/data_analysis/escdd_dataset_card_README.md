---
license: mit
---

<div align="center">
  
  <h1 style="font-size: 2.8em; margin-bottom: 0.3em;">
    E-SCDD Dataset
  </h1>
  
  <a href="https://github.com/sntubix/pv-ddpm.git" target="_blank">
    <img alt="GitHub Repo" 
       src="https://img.shields.io/badge/GitHub-e--scdd-000000?logo=github&logoColor=white" />
  </a>
  <a href="https://arxiv.org/abs/2511.09604" target="_blank">
    <img alt="arXiv"
         src="https://img.shields.io/badge/arXiv-2511.09604-b31b1b?logo=arxiv&logoColor=white" />
  </a>
  
</div>

## Overview

**E-SCDD** is an extended electroluminescence (EL) imagery dataset for photovoltaic (PV) module analysis.  
It expands the existing [BenchmarkELimages](https://github.com/TheMakiran/BenchmarkELimages) dataset by adding additional EL samples,
refined pixel-level annotations, and standardized splits to support research on:

- defect detection  
- anomaly segmentation  
- robustness evaluation  
- generative modeling  
- PV modules' health monitoring and maintenance  

## Dataset Structure

- Images: EL imagery of PV modules, including multiple defect types such as cracks and inactive regions.

- Annotations: pixel-level segmentation masks provided in indexed PNG format.

- Splits: train, validation, and test folders following the original schema

## Citation
This dataset extends and builds upon the [BenchmarkELimages](https://github.com/TheMakiran/BenchmarkELimages) dataset, 
originally released under the MIT License.

Please cite both works when using this dataset.
```
@misc{hanifi2025bridgingdatagapspatially,
      title={Bridging the Data Gap: Spatially Conditioned Diffusion Model for Anomaly Generation in Photovoltaic Electroluminescence Images}, 
      author={Shiva Hanifi and Sasan Jafarnejad and Marc Köntges and Andrej Wentnagel and Andreas Kokkas and Raphael Frank},
      year={2025},
      eprint={2511.09604},
      archivePrefix={arXiv},
      primaryClass={eess.IV},
      url={https://arxiv.org/abs/2511.09604}, 
}

@article{pratt2023benchmark,
      title={A benchmark dataset for defect detection and classification in electroluminescence images of PV modules using semantic segmentation},
      author={Pratt, Lawrence and Mattheus, Jana and Klein, Richard},
      journal={Systems and Soft Computing},
      pages={200048},
      year={2023},
      publisher={Elsevier} }
```