# 🏙️ CrossCityBench: A Comprehensive Benchmark for Cross-City Traffic Prediction

## 🏆 Contribution

<div align="center">
  <img src="https://github.com/user-attachments/assets/0088f9b2-df3e-45d4-aef9-4318343845a9" width="100%">
  <br>
  <small> The CrossCityBench architecture</small>
</div>
<br>

This paper proposes CrossCityBench, a benchmark framework for cross-city traffic prediction, with its core work structured around a three-tier logic of "**Evaluation–Diagnosis–Decision**".

- **Evaluation**: A unified evaluation system is constructed, systematically categorizing methods into single-domain models, cross-city transfer models (including alignment-based, meta-learning-based, pre-training-based, and knowledge distillation-based strategies), and privacy-preserving collaborative models.
  
- **Diagnosis**: Based on multi-dimensional in-depth diagnostics, model behaviors are analyzed in terms of efficiency, robustness, interpretability, and collaboration costs in federated learning scenarios, revealing their characteristics under challenges such as data scarcity and distribution shifts.
  
- **Decision**: Experimental findings are synthesized into a pathway matrix, providing well-founded guidance for method selection and deployment trade-offs in practical scenarios.
  
All analyses are supported by a complete set of supplementary materials (including experimental details, extended datasets, evaluation metrics, baseline methods, case studies, etc.), ensuring the reproducibility of the research and the comprehensiveness of the conclusions. Through systematic evaluation, diagnosis, and decision support, this framework promotes the practical adoption and paradigm evolution of cross-city prediction models.

## 📊 Core Datasets
<div align="center">

|  Dataset  |     Task      | #Sensors |   Time Range   | Interval |
|:---------:|:-------------:|:--------:|:-------------:|:--------:|
| PeMS03    | Traffic Flow  | 358      | 09/2018-11/2018| 5 min    |
| PeMS08    | Traffic Flow  | 170      | 07/2016-08/2016| 5 min    |
| METR-LA   | Traffic Speed | 207      | 03/2012-06/2012| 5 min    |
| PeMS-BAY  | Traffic Speed | 325      | 01/2017-05/2017| 5 min    |

</div>

All datasets (PeMS03, PeMS08, PeMS-BAY, and METR-LA) are available at [Google Drive](https://drive.google.com/file/d/1oPLRyEN32peSLWLVNVcropHt5iBNUQxo).

## 🏷️ Taxonomy of Learning Paradigms and Benchmark Model Zoo

<table>
  <thead>
    <tr>
      <th>Categories</th>
      <th>Sub-categories</th>
      <th>Guiding Principles</th>
      <th>Representative Methods</th>
      <th>Key Strengths</th>
      <th>Primary Challenges</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="1"><strong>Single-Domain Models</strong></td>
      <td></td>
      <td>Learn city-specific dynamics without transfer</td>
      <td>GBRT, VAR, AGCRN, AllDeepSet, DCRNN, DyHSL, GRU, GWNet, STGCN, STG-NCDE</td>
      <td>No cross-city bias</td>
      <td>Performance degrades under data scarcity</td>
    </tr>
    <tr>
      <td rowspan="4"><strong>Cross-City Transfer Models</strong></td>
      <td><em>Alignment-based transfer</em></td>
      <td>Explicitly align source-target distributions</td>
      <td>DASTNet, D2MHyper, DAGN, ST-DAAN</td>
      <td>Mitigates moderate distribution shifts</td>
      <td>Sensitive to large heterogeneity; alignment cost</td>
    </tr>
    <tr>
      <td><em>Meta-learning-based transfer</em></td>
      <td>Learn-to-adapt rapidly with few examples</td>
      <td>MAML, ST-GFSL</td>
      <td>Fast adaptation to new cities</td>
      <td>Requires diverse meta-tasks; unstable optimization</td>
    </tr>
    <tr>
      <td><em>Pre-training-based transfer</em></td>
      <td>Learn transferable representations from multi-city data</td>
      <td>CrossST, MTPB, STGCN-FT</td>
      <td>Strong generalization; scalable</td>
      <td>Needs large pre-training corpus; catastrophic forgetting</td>
    </tr>
    <tr>
      <td><em>Knowledge-distillation-based transfer</em></td>
      <td>Compress teacher knowledge into a lightweight student</td>
      <td>FGITrans</td>
      <td>Efficient deployment</td>
      <td>Teacher-student capability gap; distillation loss</td>
    </tr>
    <tr>
      <td rowspan="1"><strong>Privacy-Preserving Collaborative Models</strong></td>
      <td></td>
      <td>Collaborate without sharing raw data</td>
      <td>FedCTPM, pFedCTP, FedGTP</td>
      <td>Addresses scarcity and privacy jointly</td>
      <td>Communication overhead; client heterogeneity</td>
    </tr>
  </tbody>
</table>
