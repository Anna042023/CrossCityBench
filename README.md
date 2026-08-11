# 🏙️ CrossCityBench: A Comprehensive Benchmark for Cross-City Spatio-Temporal Data Management

<img src="https://img.shields.io/badge/Paper-ICDE-blue" alt="Paper">  <img src="https://img.shields.io/badge/Dataset-Public-green" alt="Dataset">

## 🏆 Contribution

<div align="center">
  <img src="images/CrossCityBench.png" alt="The CrossCityBench architecture" width="90%">
  <br>
  <strong>The CrossCityBench Architecture</strong>
</div>
<br>

This paper proposes CrossCityBench, a data‑centric evaluation‑diagnosis‑decision framework for cross‑city spatio‑temporal data management, with its core work structured around a three‑tier logic of **“Evaluation – Diagnosis – Decision”**.

- **Evaluation**: A unified evaluation system is constructed, systematically categorizing data utilization strategies into single‑source data modeling, cross‑source data transfer paradigms (alignment‑based, meta‑learning‑based, pre‑training‑based, and knowledge‑distillation‑based), and privacy‑preserving data federation frameworks.
  
- **Diagnosis**: Based on multi‑dimensional in‑depth diagnostics, model behaviors are analyzed in terms of computational efficiency, robustness to missing data and distribution shifts, interpretability via a spatio‑temporal pattern bank (STPB), and collaboration costs in federated learning scenarios, revealing their characteristics under data scarcity and real‑world data imperfections.
  
- **Decision**: Experimental findings are synthesized into a pathway matrix, providing well‑founded guidance for method selection and deployment trade‑offs in practical spatio‑temporal data management scenarios.
  
All analyses are supported by a complete set of supplementary materials (including experimental details, extended datasets, evaluation metrics, baseline methods, case studies, etc.), ensuring the reproducibility of the research and the comprehensiveness of the conclusions. Through systematic evaluation, diagnosis, and decision support, this framework promotes the practical adoption and paradigm evolution of cross‑city spatio‑temporal data management solutions.

## 💾 Datasets

### Core Datasets

<p align="center"><b>Table 1: The overview of core datasets</b></p>

<div align="center">

|  Datasets  |     Tasks      | #Nodes |   Interval   | Time Span (min) |
|:---------:|:-------------:|:--------:|:-------------:|:--------:|
| PeMS03    | Traffic Flow  | 358      | 5 min| 131,040    |
| PeMS08    | Traffic Flow  | 170      | 5 min| 89,280    |
| PeMS-BAY  | Traffic Speed | 325      | 5 min| 217,440    |
| METR-LA   | Traffic Speed | 207      | 5 min| 175,680    |

</div>

Core datasets (PeMS03, PeMS08, PeMS-BAY, and METR-LA) are available at [Google Drive](https://drive.google.com/file/d/1oPLRyEN32peSLWLVNVcropHt5iBNUQxo).

### Extended Datasets

<p align="center"><b>Table 2: The overview of extended datasets</b></p>

<div align="center">

| Datasets | #Nodes | Interval | Time Span (min) | Datasets | #Nodes | Interval | Time Span (min) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| BJMetro | 276 | 10min | 47,520 | BJTT | 1260 | 5min | 11,160 |
| CHIBike | 270 | 30min | 132,480 | Didi-Chengdu | 524 | 10min | 17,280 |
| Didi-Shenzhen | 627 | 10min | 17,280 | Dublin2021 | 33 | 5min | 105,120 |
| England | 248 | 15min | 260,640 | HKData | 617 | 5min | 89,280 |
| HZMetro | 80 | 15min | 36,000 | Los-Loop | 207 | 5min | 44,640 |
| NE-BJ | 500 | 5min | 44,640 | NYCBike | 250 | 30min | 131,040 |
| NYCTaxi | 266 | 30min | 131,040 | PeMS04 | 307 | 5min | 16,992 |
| PeMS07 | 228 | 5min | 12,672 | PeMSD7(L) | 1026 | 5min | 87,840 |
| PeMSD7(M) | 228 | 5min | 87,840 | PeMS-Rainy | 308 | 5min | 105,120 |
| Seattle-Loop | 323 | 5min | 525,600 | SHMetro | 288 | 15min | 132,480 |
| SZ-Taxi | 156 | 5min | 44,640 | T-Drive | 1024 | 60min | 216,000 |
| WHBT | 251 | 5min | 50,400 | XMBRT | 44 | 5min | 37,440 |

</div>

## 📚 Taxonomy of Data Utilization Paradigms and the Benchmark Method Suite

To guide the benchmark design and clarify the methodological landscape, we categorize existing data utilization strategies into a structured taxonomy and construct a comprehensive method suite for evaluation. The taxonomy, summarizing the paradigms, their principles, and characteristics, is presented in Table 3.

<p align="center"><b>Table 3: Taxonomy of data utilization paradigms and the benchmark method suite</b></p>

<div align="center">

<table align="center">
  <thead>
    <tr>
      <th align="center">Categories</th>
      <th align="center">Sub-Categories</th>
      <th align="center">Guiding Principles</th>
      <th align="center">Representative Methods</th>
      <th align="center">Key Strengths</th>
      <th align="center">Primary Challenges</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center" rowspan="1"><strong>Single‑Source Data Modeling</strong></td>
      <td align="center">—</td>
      <td align="center">Learn city-specific dynamics without transfer</td>
      <td align="center">GBRT, VAR, AGCRN, AllDeepSet, DCRNN, DyHSL, GRU, GWNet, STGCN, STG‑NCDE</td>
      <td align="center">No cross-city bias</td>
      <td align="center">Analytical reliability degrades under data scarcity</td>
    </tr>
    <tr>
      <td align="center" rowspan="4"><strong>Cross‑Source Data Utilization</strong></td>
      <td align="center"><em>Alignment‑based transfer</em></td>
      <td align="center">Explicitly align source‑target distributions</td>
      <td align="center">DASTNet, D2MHyper, DAGN, ST‑DAAN</td>
      <td align="center">Mitigates moderate distribution shifts</td>
      <td align="center">Sensitive to large heterogeneity; alignment cost</td>
    </tr>
    <tr>
      <td align="center"><em>Meta‑learning‑based transfer</em></td>
      <td align="center">Learn‑to‑adapt rapidly with few examples</td>
      <td align="center">MAML, ST‑GFSL</td>
      <td align="center">Fast adaptation to new cities</td>
      <td align="center">Requires diverse meta‑tasks; unstable optimization</td>
    </tr>
    <tr>
      <td align="center"><em>Pre‑training‑based transfer</em></td>
      <td align="center">Learn transferable representations from multi‑city data</td>
      <td align="center">CrossST, MTPB, STGCN‑FT</td>
      <td align="center">Strong generalization; scalable</td>
      <td align="center">Needs large pre‑training corpus; catastrophic forgetting</td>
    </tr>
    <tr>
      <td align="center"><em>Knowledge‑distillation‑based transfer</em></td>
      <td align="center">Compress teacher knowledge into a lightweight student</td>
      <td align="center">FGITrans</td>
      <td align="center">Efficient deployment</td>
      <td align="center">Teacher‑student capability gap; distillation loss</td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><strong>Privacy‑Preserving Data Federation</strong></td>
      <td align="center">—</td>
      <td align="center">Collaborate without sharing raw data</td>
      <td align="center">FedCTPM, pFedCTP, FedGTP</td>
      <td align="center">Addresses scarcity and privacy jointly</td>
      <td align="center">Communication overhead; client heterogeneity</td>
    </tr>
  </tbody>
</table>

</div>

## 🔍 STPB Specification and Interpretability Validation

To ensure the reproducibility and validity of the interpretability analysis, the construction and validation of the spatio‑temporal pattern bank (STPB) proceeds in three clearly defined steps.

**Prototype Construction:** Extract pattern segments from PeMS03 and PeMS‑BAY datasets. Perform K‑means clustering on normalized pattern embeddings.

**Prototype Selection:** Determine the number of clusters using the elbow method. Retain only prototypes that appear in more than 70\% of cities, ensuring generality.

**Interpretability Validation:** Conduct a user study with 5 domain experts. Each expert rates interpretability (scale 1‑5) based on model outputs. Compute the correlation between STPB similarity and human ratings.


<p align="center"><b>Table 4: Formal specification of STPB prototypes</b></p>

<div align="center">

| Item                     | Setting                                                                 |
|:------------------------:|:-----------------------------------------------------------------------:|
| Prototype source data    | Pattern segments extracted from PeMS03 + PeMS‑BAY                   |
| Candidate pattern pool   | Trend, periodicity, peak‑shift, burstiness, local fluctuation segments |
| Prototype construction   | K‑means clustering on normalized pattern embeddings                |
| Number of clusters \(K\) | 8                                                                   |
| K selection criterion    | Elbow method on within‑cluster SSE                                 |
| Prototype retention rule | Retain prototypes appearing in >70% of cities                       |
| Final prototype bank size| 8 prototypes                                                        |
| Similarity metric        | Average cosine similarity between model representation and prototype vectors |

</div>

<p align="center"><b>Table 5: STPB vs. human interpretability</b></p>

<div align="center">

| Model      | STPB Similarity | Expert Rating (1‑5) | Rank by STPB | Rank by Experts |
|:----------:|:--------------:|:-------------------:|:------------:|:---------------:|
| D2MHyper   | 0.0743          | 4.4 ± 0.3           | 1            | 1               |
| CrossST    | 0.0227          | 3.8 ± 0.5           | 2            | 2               |
| FGITrans   | -0.0226         | 3.1 ± 0.4           | 3            | 3               |
| ST‑GFSL    | -0.0368         | 2.6 ± 0.4           | 4            | 4               |
| DyHSL      | -0.0473         | 2.5 ± 0.5           | 5            | 5               |

</div>

<p align="center"><b>Table 6: Statistical validity of STPB</b></p>

<div align="center">

| Metric                       | Value   |
|:---------------------------:|:-------:|
| Pearson $r$                | 0.79|
| p-value                      | 0.008|
| Spearman $\rho$            | 1.00|
| p-value                      | <0.001|
| Intraclass Correlation Coefficient (ICC)  | 0.81|

</div>

**Results Analysis**

(1) **STPB is clearly defined.** As shown in Table 4, the prototype bank is constructed via K‑means ($K=8$, elbow method) on patterns from PeMS03 + PeMS‑BAY, with a $>70\%$ cross‑city filtering rule. This makes STPB fully specified and reproducible.

(2) **STPB correlates well with human interpretability.** From Tables 5‑6, STPB similarity is strongly aligned with expert ratings (Pearson $r = 0.79$, $p < 0.01$), and the model rankings are fully consistent (Spearman $\rho = 1.00$, $p < 0.001$). This validates STPB as a reliable interpretability proxy for data management diagnostics.

(3) **STPB captures meaningful differences across methods.** Methods such as D2MHyper and CrossST achieve higher STPB scores and human ratings, while others are lower, showing that STPB can effectively distinguish interpretability across different data utilization strategies.

## 🎯 The Technical Pathway Decision Matrix for Cross‑City Spatio‑Temporal Data Management

Based on quantitative insights from our multi‑dimensional diagnostic evaluation, the following evidence‑based decision matrix maps practical data management constraints (e.g., data scarcity, distribution shifts, privacy needs) to suitable data utilization paradigms. Each recommendation is directly linked to the diagnostic analyses that quantify its trade‑offs, providing a traceable, data‑driven selection tool. Empirical thresholds are derived from systematic experiments; leave‑one‑city‑out validation on 6 unseen pairs shows the recommended paradigm achieves top‑2 accuracy in 83% of cases.

<p align="center"><b>Table 7: The technical pathway decision matrix for cross‑city spatio‑temporal data management</b></p>

<div align="center">

<table align="center">
  <thead>
    <tr>
      <th align="center">Constraints</th>
      <th align="center">Primary Goals</th>
      <th align="center">Paradigms</th>
      <th align="center">Example Models</th>
      <th align="center">Key Limitations</th>
      <th align="center">Quantitative References</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="left">Large distribution shift ($\Delta\mathcal{M}_\text{shift} > 25\%$)</td>
      <td align="left">Optimal accuracy</td>
      <td align="left">Alignment</td>
      <td align="left">D2MHyper</td>
      <td align="left">Needs source data; Unstable training</td>
      <td align="left">High $\Delta\mathcal{M}_\text{shift}$</td>
    </tr>
    <tr>
      <td align="left">Extreme data scarcity (target training days &lt; 3)</td>
      <td align="left">Fast adaptation</td>
      <td align="left">Meta‑learning</td>
      <td align="left">ST‑GFSL</td>
      <td align="left">High meta‑training cost; Task‑sensitive</td>
      <td align="left">High latency; Robustness</td>
    </tr>
    <tr>
      <td align="left">Multi‑source data available</td>
      <td align="left">Zero‑shot robustness</td>
      <td align="left">Pre‑training</td>
      <td align="left">CrossST</td>
      <td align="left">High pre‑training resource cost</td>
      <td align="left">High memory use; Robustness</td>
    </tr>
    <tr>
      <td align="left">Deployment efficiency critical (latency &lt; 0.5s)</td>
      <td align="left">Efficient inference</td>
      <td align="left">Distillation</td>
      <td align="left">FGITrans</td>
      <td align="left">Teacher‑dependent</td>
      <td align="left">Low latency, small size</td>
    </tr>
    <tr>
      <td align="left">Privacy constraints (no data sharing)</td>
      <td align="left">Privacy‑preserving performance</td>
      <td align="left">Federated learning</td>
      <td align="left">FedCTPM</td>
      <td align="left">Communication cost; Utility gap</td>
      <td align="left">Communication overhead and 𝒢_util</td>
    </tr>
    <tr>
      <td align="left">Ample resources (high compute budget)</td>
      <td align="left">Competitive zero‑shot accuracy</td>
      <td align="left">Foundation model (zero‑shot/fine‑tune)</td>
      <td align="left">UniST, UrbanGPT, ST‑LLM+</td>
      <td align="left">5–10× higher latency; 10–20× larger GPU memory</td>
      <td align="left">MAE 16.71–17.89 vs. CrossST 16.25 (PeMS03→08)</td>
    </tr>
  </tbody>
</table>

</div>

## 📎 Code and Data

The code and datasets used in this benchmark are publicly available at [https://github.com/Anna042023/CrossCityBench](https://github.com/Anna042023/CrossCityBench). All experiments are fully reproducible with the provided scripts and configuration files.

# 🆕 CrossCityBench Revision Notes — ICDE 2027

These notes accompany the revised manuscript *CrossCityBench: A Comprehensive Benchmark for Cross‑City Spatio‑Temporal Data Management* (ICDE 2027).  
We expand upon the rebuttal clarifications with precise evidence extracted from the original manuscript, highlighting the logical connections between each component and the overall data‑management contribution.  
Code, data, and documentation: https://github.com/Anna042023/CrossCityBench.

---

## 1. Core Contribution and ICDE Positioning (R1‑W2, R5‑W2, R5‑D1, R5‑Relevance, R2‑D4)

CrossCityBench is not a database engine or a query‑processing system. Its novelty does not lie in a new forecasting algorithm. Instead, it introduces a unified benchmark‑level evaluation capability for comparing cross‑city spatio‑temporal data‑utilization paradigms under identical, operationally realistic conditions. The contribution is structured in three layers.

**Layer 1: Unified evaluation protocol.** Prior studies evaluate different paradigms on heterogeneous datasets, with inconsistent prediction horizons, target‑data budgets, and normalization procedures. CrossCityBench standardises these elements: all 23 methods listed in Table III use the same 12‑step input, 12‑step output configuration, a fixed 3‑day target training window, Z‑score normalization computed from the training split only, and identical random seeds. This eliminates the confounding effect of differing experimental setups and makes cross‑paradigm comparison fair for the first time.

**Layer 2: Multi‑dimensional diagnosis beyond accuracy.** Existing benchmarks typically report only point‑forecast accuracy (MAE, RMSE, MAPE). CrossCityBench adds five complementary diagnostic dimensions. Computational efficiency is captured through training time, inference latency, GPU memory footprint, and model size. Robustness is measured via degradation under controlled missing‑data ratios (10%–50%) and under heterogeneous versus homogeneous city‑pair shifts. Interpretability is quantified through the Spatio‑Temporal Pattern Bank (STPB), a learned reference space of recurring traffic patterns that measures how well a model’s internal representations align with these canonical patterns. Federated collaboration cost is expressed as communication overhead (MB) and utility gap (ΔMAE relative to centralized training). The resulting profile reveals deployment‑relevant characteristics that a pure accuracy table cannot show.

**Layer 3: Traceable decision matrix.** The empirical evidence from all diagnostic dimensions is distilled into a constraint‑to‑paradigm matrix (Table XI in the manuscript). Every cell will be linked to the specific figures and tables that justify it, so the matrix is not a qualitative summary but a verifiable, evidence‑grounded decision aid. This transforms the benchmark from a leaderboard that says “method X is better” into a data‑management diagnostic that answers “which data‑utilization strategy should be used when the target city has only a few days of data, distribution shifts are large, or privacy rules forbid data sharing.”

Taken together, these three layers define the data‑management contribution of CrossCityBench: it provides the evaluation and decision layer for cross‑city data utilization, without claiming to be a storage engine or a query processor. We will sharpen this positioning in the final manuscript and adjust the phrasing in Section V.D to reflect this scope precisely.

---

## 2. What Is Genuinely Learned from the Benchmark (R1‑W1, R1‑D4, R5‑W5)

The revised manuscript will include a new Diagnostic Discussion section that draws out benchmark‑level findings that are not visible from accuracy alone. Four findings, supported by the existing experimental data, collectively demonstrate why accuracy is insufficient for selecting a cross‑city data‑utilization paradigm.

### Finding 1: Cross‑city transfer is not uniformly beneficial.
Under extreme data scarcity (3 days of target training data), only two transfer paradigms consistently outperform the strongest single‑source baselines on both traffic flow and speed tasks. Table 1 synthesises the relevant numbers from the original Tables IV and V (whose captions will be corrected from 7 days to 3 days).

| Task | Best single‑source MAE | D2MHyper MAE | CrossST MAE | Other transfer methods |
|------|------------------------|--------------|-------------|------------------------|
| Flow (PeMS03→PeMS08) | 18.62 (STG‑NCDE) | 17.54 | 14.67 | 18.36–24.89 |
| Speed (PeMS‑BAY→METR‑LA) | 3.82 (DyHSL) | 2.74 | 3.21 | 3.33–4.91 |

These results show that meta‑learning, knowledge distillation, and several alignment baselines do not beat the best model trained only on the scarce target data. Therefore, the usefulness of external data is conditional on the utilization paradigm. This finding directly challenges the commonly held assumption that more external data necessarily improves target performance.

### Finding 2: Robustness and accuracy are decoupled.
Table 2 summarizes the distribution‑shift degradation (ΔMshift) reported in Fig. 5(b) of the manuscript. A lower value indicates better resilience to cross‑city heterogeneity.

| Paradigm | Method | ΔMshift |
|----------|--------|---------|
| Pre‑training | CrossST | 0.28% |
| Distillation | FGITrans | 0.55% |
| Meta‑learning | ST‑GFSL | 16.75% |
| Alignment | D2MHyper | 32.52% |
| Single‑source | DyHSL | –5.24% |

Pre‑training achieves near‑zero degradation, while the most accurate alignment method (D2MHyper) experiences the largest shift sensitivity. Distillation remains stable despite not being the top‑accuracy option. These divergences mean that a practitioner cannot assume that the best‑accuracy method will also be the most robust under changing city conditions; rather, robustness and accuracy must be evaluated and traded off explicitly.

### Finding 3: Federated methods reveal a clear utility–communication trade‑off.
The three federated strategies evaluated in Table VI and Fig. 7 of the manuscript form a distinct frontier, summarised in Table 3.

| Method | Utility gap (ΔMAE) | Communication cost (MB) |
|--------|--------------------|--------------------------|
| FedCTPM | 0.8965 | 1.0880 |
| pFedCTP | 0.3035 | 0.2221 |
| FedGTP | 0.1327 | 0.1106 |

FedGTP simultaneously achieves the smallest utility gap and the lowest communication overhead, while FedCTPM incurs both the highest gap and the highest cost. This finding corrects the original decision matrix, which erroneously recommended FedCTPM as the primary privacy‑preserving option, and shows that under the current evidence FedGTP is the preferred low‑communication, low‑utility‑gap choice.

### Finding 4: The preferred paradigm depends on the data regime, not on accuracy alone.
Because the best paradigm changes with the amount of target data, the magnitude of distribution shift, and the available computational budget, no single method can be declared universally optimal. This observation is not a weakness of the benchmark; it is precisely the insight that motivates the constraint‑aware decision matrix. The revised paper will explicitly trace how each row of Table XI follows from the measured accuracy, robustness, efficiency, and communication profiles.

To further strengthen the analysis, we will add a compact stratified examination relating paradigm performance to three interpretable data characteristics: spatial scale (number of nodes), temporal volatility (variance of the target variable), and peak‑hour concentration (ratio of traffic in the top 3 hours). This exploratory analysis will help practitioners anticipate which paradigm is likely to work well on a previously unseen city pair by inspecting simple summary statistics.

### Mechanistic discussion.
The current experimental results are consistent with the following mechanisms: alignment methods explicitly reduce distribution mismatch, which explains their higher shift sensitivity when the mismatch is large; pre‑training learns more transferable representations, consistent with the near‑zero degradation of CrossST; meta‑learning depends heavily on the diversity of source tasks, which accounts for its strong performance in the multi‑source setting but weaker results in few‑shot transfer. We will explicitly examine these mechanisms through additional diagnostic experiments in the revised manuscript, and we will present the discussion with appropriate caution, noting that these interpretations are based on the observed evidence rather than on formal causal identification.

Finally, we will conduct sensitivity analyses on the target training budget (1, 3, 5, and 7 days), the prediction horizon (15, 30, 60, and 120 minutes), and the shared hyper‑parameters (learning rate and batch size) to assess whether paradigm rankings remain stable under these perturbations. These checks will provide quantitative confidence bounds for the practical recommendations derived from the benchmark.

---

## 3. Experimental Rigor and Reproducibility (R2‑W3, R5‑D7, R2‑D3, R5‑D5, R5‑D6, R2‑Code)

### Statistical variability.
The original manuscript reports results from single runs with a fixed random seed. We agree that this is insufficient for drawing reliable conclusions, especially when differences are small (e.g., the 0.09 MAE gap between CrossST and FGITrans). In the revised version, all core experiments will be repeated with three independent random seeds, and we will report mean ± standard deviation in Tables IV–VII. The focus will be on ranking stability rather than on the significance of any single pairwise difference. We will explicitly avoid making claims based on small absolute gaps unless they are consistently observed across repetitions.

### Hyper‑parameter fairness.
All methods currently share one configuration (learning rate 0.001, batch size 16, hidden dimension 64). This design intentionally avoids per‑method tuning advantages, but we acknowledge that it may not maximize each method’s individual performance. To clarify this trade‑off, we will add a sensitivity analysis that varies the learning rate in {0.0005, 0.001, 0.002} and batch size in {8, 16, 32}, and we will report whether the paradigm rankings remain stable. The originally published optimal settings for each method will be reported separately as a supplementary reference, without mixing them into the primary controlled comparison. This two‑tier protocol preserves both fairness and external validity.

### Methodological details.
The following elements, which were absent or underspecified in the original submission, will be added to Section IV‑A and to the relevant definitions.
- **Data split.** A precise chronological 70/10/20 (training/validation/test) split will be described. The 3‑day target training window corresponds to the first three days of the training portion, not a random sample.
- **Validation usage.** Validation sets are used for early stopping in all centralized methods; the stopping criterion will be stated explicitly.
- **Compatibility matrix.** A new table will indicate which paradigm–dataset combinations are valid. For example, federated methods require multiple clients and are therefore evaluated only in the multi‑source setting, while single‑source methods cannot handle cross‑city transfers involving structural mismatches.
- **Source‑data usage.** For each paradigm, we will describe exactly how source data are utilized during training versus inference, distinguishing between scenarios that require ongoing source‑data access (alignment) and those that only need the source data during a pre‑training phase.

### Code and reproducibility.
The original code release was incomplete: seven method implementations (GBRT, VAR, AllDeepSet, GRU, D2MHyper, DAGN, STGCN‑FT) and the STPB construction/evaluation code were missing. We will release all seven implementations, a unified benchmark runner, a requirements.txt environment specification, and a step‑by‑step README. The exact code commit will be documented in the revised manuscript to guarantee full reproducibility.

---

## 4. Cross‑City Validity and Generalization (R5‑D2, R5‑D3, R5‑W3, R5‑W4)

The four core datasets (PeMS03, PeMS08, PeMS‑BAY, METR‑LA) are all drawn from California highway sensor networks and share a uniform 5‑minute resolution. This choice was intentional: it ensures that the primary comparisons are directly reproducible and comparable with the majority of published studies in the field. In the revision, we will explicitly label these datasets as “California highway benchmarks” and discuss their limitations in terms of geographical and modality diversity.

To strengthen the cross‑city claim, we will add genuinely inter‑regional transfer pairs from the extended dataset collection (Table II in the manuscript). The new pairs will be selected such that the prediction target and temporal semantics are matched. A concrete example is PeMS‑BAY to Seattle‑Loop, where both datasets record traffic speed at 5‑minute intervals from fixed loop detectors, but the cities differ in geography, climate, and network topology. Other compatible inter‑regional traffic datasets will be included, always avoiding pairs that mix incompatible prediction targets (e.g., traffic flow with taxi demand).

With this addition, the experimental design becomes a two‑tier validity framework. The original core pairs serve as a controlled reproducibility benchmark, where distribution shifts are studied within a single sensor infrastructure; the new pairs serve as an external validity benchmark, testing whether the paradigm recommendations generalize to different urban environments and sensor deployments. Intra‑infrastructure shifts are already substantial: for instance, PeMS03 and PeMS08 differ in node count (358 vs. 170) and traffic density, and the benchmark already captures these variations. The additional inter‑regional transfers will complement these tests by introducing genuine geographic heterogeneity.

We will also add “Data Category” and “Geographic Region” columns to Table II, making the diversity of the extended collection immediately visible.

---

## 5. Factual Corrections and Decision‑Matrix Revisions (R2‑W1, R2‑W2, R2‑W4, R2‑W5, R2‑D1, R2‑D2, R2‑D3)

### Citation errors.
We sincerely apologize for the incorrect references. All citations will be corrected so that each baseline method points to the paper that introduced it. Unrelated text‑to‑SQL and vector‑DB citations that appeared in the introduction will be removed.

### Training data amount.
The core experimental setting uses 3 days of target training data, not 7 days. The captions of Tables IV and V incorrectly state 7 days; they will be corrected to 3 days. The text describing the scarcity regime will be unified accordingly.

### Claim about transfer versus single‑source.
The original claim that “most transfer paradigms outperform single‑source” is not supported by the tables. As shown in Finding 1 (Table 1 above), only D2MHyper and CrossST consistently beat the best single‑source baseline on both tasks. We will replace the sweeping statement with the accurate, nuanced finding: under extreme scarcity, only alignment and pre‑training deliver consistent accuracy improvements over strong no‑transfer models; other paradigms offer complementary benefits such as efficiency or privacy, but they do not always improve accuracy.

### Shenzhen transfer correction.
For the M,P,C to Shenzhen transfer in Table VII, the original text stated that DASTNet consistently outperforms DCRNN. In fact, DASTNet yields slightly worse MAE at every horizon (2.05 vs. 2.01 at 10 min, for example), and ST‑GFSL is the best method overall. We will correct this error and explain that the alignment gain of DASTNet depends on the similarity of the source–target pair; on this particular pair, meta‑learning benefits more from the diverse source cities.

### Decision‑matrix corrections.
The original decision matrix (Table XI in the manuscript) contained two incorrect recommendations, which we will fix as follows.

**Privacy‑preserving recommendation.** FedCTPM was recommended despite having the worst utility gap (0.8965) and the highest communication cost (1.0880 MB) among the three federated methods (see Table 3 above). In the revised matrix, FedGTP, which achieves the smallest utility gap (0.1327) and the lowest communication cost (0.1106 MB), will be identified as the preferred low‑communication, low‑utility‑gap option under the current decision criteria. FedCTPM will be retained only as a baseline.

**Latency‑critical recommendation.** FGITrans was recommended for deployment scenarios with strict latency constraints, but Fig. 4 shows that it incurs a peak GPU memory footprint of 14.32 GB, making it unsuitable for memory‑constrained environments. In the revised matrix, lightweight single‑source models with empirically low memory requirements (e.g., STGCN, subject to its measured resource profile) will be recommended for stringent resource budgets. Distillation will be repositioned as a latency‑oriented strategy whose memory cost can remain substantial. The matrix will also explicitly state that the distillation paradigm is currently represented by a single method (FGITrans); we therefore scope our conclusions to FGITrans and identify broader distillation coverage as an avenue for future benchmark extensions.

### Additional corrections.
The missing isolated local training results will be added to Fig. 7, providing the lower bound for the federated analysis. The apparent contradiction in ST‑GFSL’s ranking (worst in the few‑shot setting of Tables IV–V, best in the multi‑source setting of Table VII) will be discussed in terms of meta‑learning’s dependence on diverse source tasks, thereby turning a potential inconsistency into an informative benchmark observation.

For a consolidated view of all factual corrections described above, Table 4 provides a concise cross‑reference between each original issue and its corresponding revision.

**Table 4. Summary of factual corrections in the revised manuscript.**

| Issue | Original text | Corrected text | Reference |
|-------|---------------|----------------|-----------|
| Training data amount | Table IV/V captions state 7‑day training data | 3‑day target training data | Section IV‑A, Tables IV, V |
| Transfer vs. single‑source claim | “Most transfer paradigms outperform single‑source” | Only alignment (D2MHyper) and pre‑training (CrossST) consistently beat the best no‑transfer baseline | Section IV‑B1 |
| Shenzhen DASTNet vs. DCRNN | “DASTNet consistently outperforms DCRNN” | DASTNet slightly worse; ST‑GFSL best overall | Table VII |
| FedCTPM recommendation | FedCTPM recommended for privacy‑preserving scenarios | FedGTP (utility gap 0.1327, comm. 0.1106 MB) is preferred; FedCTPM retained as baseline | Table XI |
| FGITrans latency recommendation | FGITrans recommended for latency‑critical deployment | Lightweight single‑source models (e.g., STGCN) for strict memory budgets; distillation repositioned as latency‑oriented, memory‑heavy | Fig. 4, Table XI |
| Isolated local training | Missing from Fig. 7 | Isolated local training results added as lower bound | Fig. 7 |
| ST‑GFSL ranking contradiction | Not discussed | Explained via meta‑learning’s dependence on task diversity | Tables IV, V, VII |
| Citation errors | Incorrect references for STGCN, DCRNN, MAML, etc. | All corrected to the original papers | Bibliography |
| Unrelated text‑to‑SQL/vector‑DB citations | Present in introduction | Removed | Introduction |

### Traceability of the decision matrix.
To address the concern that the decision matrix is a qualitative summary, we will make every entry in Table XI explicitly traceable to the specific figures, tables, and metric values that support it. This transforms the matrix from a heuristic guide into a verifiable, evidence‑grounded decision aid. Table 5 maps each row of the revised decision matrix to its supporting quantitative evidence and, where applicable, the correction applied.

**Table 5. Traceability mapping for the revised decision matrix (Table XI).**

| Constraint | Recommended paradigm | Key quantitative evidence | Supporting reference | Correction applied |
|------------|----------------------|--------------------------|----------------------|-------------------|
| Large distribution shift (ΔMshift > 25%) | Alignment (e.g., D2MHyper) | ΔMshift = 32.52% (highest sensitivity) | Fig. 5(b) | Removed claim of universal accuracy; alignment recommended *under shift* but sensitivity flagged |
| Extreme data scarcity (< 3 days) | Meta‑learning (e.g., ST‑GFSL) | Adaptation speed, few‑shot performance | Tables IV, V, VII; Fig. 4 latency | Qualified with task‑sensitivity note |
| Multi‑source data available | Pre‑training (e.g., CrossST) | ΔMshift = 0.28%, robustness under missing data 0.34–1.44% | Fig. 5, Section IV‑D2 | — |
| Deployment efficiency critical (latency < 0.5 s) | Distillation (e.g., FGITrans) | Latency < 0.8 s, but memory 14.32 GB | Fig. 4 | Corrected recommendation: FGITrans removed from strict‑memory use; lightweight single‑source alternatives added |
| Privacy constraints (no data sharing) | Federated learning (FedGTP) | Utility gap = 0.1327, comm. = 0.1106 MB | Table VI, Fig. 7 | FedCTPM replaced by FedGTP as primary recommendation |
| Ample resources (high compute) | Foundation model (zero‑shot) | MAE 16.71–17.89 vs. CrossST 16.25 | Table XI row, PeMS03→08 | — |

This traceability table will be included as supplementary material and referenced in the revised Section V.D, ensuring that readers can verify every recommendation against the underlying benchmark data.

---

## 6. STPB and Interpretability (R1‑D3, R5‑W2, R2‑D5)

### Specification.
The STPB is fully specified in Tables VIII–X of the manuscript. Table VIII defines the construction procedure: pattern segments are extracted from PeMS03 and PeMS‑BAY, K‑means clustering (K=8, chosen by the elbow method on within‑cluster SSE) is applied to normalized pattern embeddings, and prototypes that appear in more than 70% of cities are retained. The final bank contains 8 prototypes representing trend, periodicity, peak‑shift, burstiness, and local fluctuation patterns. The STPB similarity score is the average cosine similarity between a model’s representation vector and the prototype vectors.

### Validation.
A user study with five domain experts was conducted. Each expert rated the interpretability of five model outputs on a 1–5 scale. Table IX reports the resulting STPB scores and expert ratings: D2MHyper (0.0743, 4.4), CrossST (0.0227, 3.8), FGITrans (–0.0226, 3.1), ST‑GFSL (–0.0368, 2.6), DyHSL (–0.0473, 2.5). The rank correlation is perfect (Spearman ρ=1.0) and the Pearson correlation is 0.79 (p<0.01), as summarised in Table X.

### Positioning in the revision.
In the revised manuscript, we will introduce the STPB earlier (Section III‑G) and clarify its role: it is a benchmark‑level diagnostic proxy that measures the alignment of model representations with recurring spatio‑temporal patterns. It is not a claim of universal interpretability. The current ranking agreement is based on only five model‑level observations, which is encouraging but preliminary. We will transparently report the user‑study protocol, including the participant and task counts, the rating scale, and the aggregation procedure, without overstating the statistical generalizability. This cautious presentation turns a potential weakness into a credible, scoped diagnostic contribution.

### Additional presentation fixes.
We will correct the typographical errors “mean absolute srror” and “School of Chumin,” improve the resolution of all figures, and reduce forward references so that each section is self‑contained and easier to follow.

---

## 7. Summary of Revisions

Collectively, the revision reframes CrossCityBench as a reproducible, evidence‑grounded framework for diagnosing and selecting cross‑city data‑utilization strategies under realistic operational constraints. It is no longer a collection of forecasting comparisons. The data‑utilization decision layer makes explicit what prior fragmented evaluations could not: a traceable pipeline from a unified evaluation protocol, through multi‑dimensional diagnosis, to constraint‑aware, evidence‑backed paradigm recommendations. The specific changes include:

- A refined ICDE data‑management positioning that distinguishes the evaluation and decision layer from storage or query execution.
- A new Diagnostic Discussion presenting benchmark‑level findings not visible from accuracy alone, together with mechanistic analysis and dataset‑characteristic stratification.
- Statistical re‑runs with multiple seeds, hyper‑parameter sensitivity analysis, and the addition of isolated local training results.
- Expanded cross‑city experiments on inter‑regional transfer pairs with matched task semantics, establishing a two‑tier validity framework.
- Full correction of citation errors, factual claims, and decision‑matrix entries, making every recommendation traceable to the underlying quantitative evidence, as detailed in Tables 4 and 5.
- Completion of all missing code, including the seven baseline implementations and the STPB module, together with a unified benchmark runner and environment specification.

These revisions directly address the reviewers’ concerns on novelty, analytical depth, experimental rigor, cross‑city validity, reproducibility, and ICDE relevance. We hope that the revised manuscript will be found suitable for publication.
