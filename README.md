# 🏙️ CrossCityBench: A Comprehensive Benchmark for Cross-City Traffic Prediction

## 🏆 Contribution

<div align="center">
  <img src="images/crosscitybench.jpg" alt="The CrossCityBench architecture" width="90%">
  <br>
  <small>The CrossCityBench architecture</small>
</div>
<br>

This paper proposes CrossCityBench, a benchmark framework for cross-city traffic prediction, with its core work structured around a three-tier logic of "**Evaluation–Diagnosis–Decision**".

- **Evaluation**: A unified evaluation system is constructed, systematically categorizing methods into single-domain models, cross-city transfer models (including alignment-based, meta-learning-based, pre-training-based, and knowledge distillation-based strategies), and privacy-preserving collaborative models.
  
- **Diagnosis**: Based on multi-dimensional in-depth diagnostics, model behaviors are analyzed in terms of efficiency, robustness, interpretability, and collaboration costs in federated learning scenarios, revealing their characteristics under challenges such as data scarcity and distribution shifts.
  
- **Decision**: Experimental findings are synthesized into a pathway matrix, providing well-founded guidance for method selection and deployment trade-offs in practical scenarios.
  
All analyses are supported by a complete set of supplementary materials (including experimental details, extended datasets, evaluation metrics, baseline methods, case studies, etc.), ensuring the reproducibility of the research and the comprehensiveness of the conclusions. Through systematic evaluation, diagnosis, and decision support, this framework promotes the practical adoption and paradigm evolution of cross-city prediction models.

## 💾 Core Datasets
<div align="center">

|  Datasets  |     Tasks      | #Nodes |   Interval   | Time Span (min) |
|:---------:|:-------------:|:--------:|:-------------:|:--------:|
| PeMS03    | Traffic Flow  | 358      | 5 min| 131,040    |
| PeMS08    | Traffic Flow  | 170      | 5 min| 89,280    |
| PeMS-BAY  | Traffic Speed | 325      | 5 min| 217,440    |
| METR-LA   | Traffic Speed | 207      | 5 min| 175,680    |

</div>

All datasets (PeMS03, PeMS08, PeMS-BAY, and METR-LA) are available at [Google Drive](https://drive.google.com/file/d/1oPLRyEN32peSLWLVNVcropHt5iBNUQxo).

## 📊 Overall Performance Comparison

### PeMS03 → PeMS08

<table>
<thead>
<tr>
<th rowspan="2">Methods (Paradigms)</th>
<th colspan="3">15 min</th>
<th colspan="3">30 min</th>
<th colspan="3">60 min</th>
<th colspan="3">Average</th>
</tr>
<tr>
<th>MAE</th><th>RMSE</th><th>MAPE (%)</th>
<th>MAE</th><th>RMSE</th><th>MAPE (%)</th>
<th>MAE</th><th>RMSE</th><th>MAPE (%)</th>
<th>MAE</th><th>RMSE</th><th>MAPE (%)</th>
</tr>
</thead>
<tbody>

<tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr>
<tr><td>GBRT</td><td>27.11</td><td>44.28</td><td>16.41</td><td>29.35</td><td>46.93</td><td>17.79</td><td>34.12</td><td>52.76</td><td>21.05</td><td>29.68</td><td>47.37</td><td>18.09</td></tr>
<tr><td>VAR</td><td>30.04</td><td>44.90</td><td>18.38</td><td>32.37</td><td>48.58</td><td>19.85</td><td>37.83</td><td>56.31</td><td>23.81</td><td>32.86</td><td>49.16</td><td>20.33</td></tr>
<tr><td>AGCRN</td><td>26.48</td><td>46.25</td><td>13.59</td><td>26.65</td><td>46.92</td><td>13.61</td><td>32.49</td><td>52.35</td><td>17.22</td><td>28.03</td><td>48.09</td><td>14.50</td></tr>
<tr><td>AllDeepSet</td><td>19.90</td><td>29.33</td><td>13.66</td><td>25.37</td><td>34.25</td><td>37.15</td><td>36.84</td><td>52.75</td><td>25.88</td><td>26.72</td><td>38.65</td><td>19.82</td></tr>
<tr><td>DCRNN</td><td>17.06</td><td>26.46</td><td>12.71</td><td>20.11</td><td>31.26</td><td>14.29</td><td>26.61</td><td>40.51</td><td>19.51</td><td>20.53</td><td>31.66</td><td>14.82</td></tr>
<tr><td>DyHSL</td><td>16.87</td><td>25.46</td><td>12.70</td><td>18.95</td><td>29.44</td><td>14.09</td><td>23.45</td><td>35.98</td><td>17.05</td><td>19.16</td><td>29.64</td><td>14.71</td></tr>
<tr><td>GRU</td><td>23.79</td><td>33.02</td><td>24.61</td><td>33.34</td><td>42.95</td><td>38.50</td><td>37.22</td><td>51.33</td><td>45.44</td><td>30.02</td><td>40.80</td><td>34.02</td></tr>
<tr><td>GWNet</td><td>21.03</td><td>29.92</td><td>20.19</td><td>25.51</td><td>36.89</td><td>22.65</td><td>36.30</td><td>51.17</td><td>29.62</td><td>26.56</td><td>38.07</td><td>23.83</td></tr>
<tr><td>STGCN</td><td>18.85</td><td>29.14</td><td>12.87</td><td>23.65</td><td>36.55</td><td>15.60</td><td>33.31</td><td>51.41</td><td>20.49</td><td>24.61</td><td>38.00</td><td>15.95</td></tr>
<tr><td>STG-NCDE</td><td>16.94</td><td>25.59</td><td>13.34</td><td>18.02</td><td>28.71</td><td>14.32</td><td>22.31</td><td>35.11</td><td>17.02</td><td>18.62</td><td>29.41</td><td>14.72</td></tr>

<tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr>
<tr><td>DASTNet</td><td>17.79</td><td>26.65</td><td>13.03</td><td>20.64</td><td>31.09</td><td>14.56</td><td>27.14</td><td>40.02</td><td>18.80</td><td>21.15</td><td>31.98</td><td>15.47</td></tr>
<tr>
<td>D2MHyper</td>
<td>15.34</td>
<td><ins>23.49</ins></td>
<td><ins>12.01</ins></td>
<td>17.00</td>
<td><ins>26.29</ins></td>
<td><ins>12.75</ins></td>
<td>21.69</td>
<td>33.37</td>
<td><ins>16.79</ins></td>
<td>17.54</td>
<td><ins>26.98</ins></td>
<td><ins>13.48</ins></td>
</tr>
<tr><td>DAGN</td><td>16.83</td><td>24.53</td><td>12.57</td><td>17.73</td><td>26.86</td><td>14.03</td><td>21.78</td><td>33.88</td><td>17.20</td><td>18.36</td><td>27.95</td><td>14.56</td></tr>
<tr><td>ST-DAAN</td><td>18.33</td><td>27.37</td><td>12.27</td><td>21.98</td><td>32.99</td><td>15.19</td><td>29.33</td><td>43.47</td><td>19.78</td><td>22.44</td><td>33.63</td><td>15.23</td></tr>

<tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
<tr><td>MAML</td><td>20.20</td><td>28.61</td><td>19.33</td><td>24.30</td><td>33.70</td><td>25.05</td><td>32.65</td><td>44.25</td><td>36.49</td><td>24.89</td><td>34.40</td><td>26.11</td></tr>
<tr><td>ST-GFSL</td><td>19.71</td><td>28.35</td><td>16.00</td><td>23.41</td><td>33.18</td><td>19.53</td><td>30.28</td><td>42.48</td><td>27.52</td><td>23.75</td><td>33.64</td><td>20.25</td></tr>

<tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
<tr>
<td>CrossST</td>
<td><strong>13.68</strong></td><td><strong>21.79</strong></td><td><strong>8.81</strong></td>
<td><strong>14.65</strong></td><td><strong>23.60</strong></td><td><strong>9.63</strong></td>
<td><ins>16.25</ins></td><td><strong>26.00</strong></td><td><strong>10.60</strong></td>
<td><strong>14.67</strong></td><td><strong>23.49</strong></td><td><strong>9.59</strong></td>
</tr>

<tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
<tr>
<td>FGITrans</td>
<td><ins>14.63</ins></td><td>28.29</td><td>18.91</td>
<td><ins>14.73</ins></td><td>28.58</td><td>18.98</td>
<td><strong>14.93</strong></td><td><ins>29.14</ins></td><td>19.10</td>
<td><ins>14.76</ins></td><td>28.67</td><td>19.00</td>
</tr>

</tbody>
</table>
### PeMS-BAY → METR-LA

<table>
<thead>
<tr>
<th rowspan="2">Methods (Paradigms)</th>
<th colspan="3">15 min</th>
<th colspan="3">30 min</th>
<th colspan="3">60 min</th>
<th colspan="3">Average</th>
</tr>
<tr>
<th>MAE</th><th>RMSE</th><th>MAPE (%)</th>
<th>MAE</th><th>RMSE</th><th>MAPE (%)</th>
<th>MAE</th><th>RMSE</th><th>MAPE (%)</th>
<th>MAE</th><th>RMSE</th><th>MAPE (%)</th>
</tr>
</thead>
<tbody>

<tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr>
<tr><td>GBRT</td><td>8.73</td><td>16.05</td><td>16.57</td><td>9.81</td><td>18.53</td><td>18.59</td><td>11.28</td><td>20.77</td><td>20.93</td><td>9.73</td><td>18.16</td><td>18.38</td></tr>
<tr><td>VAR</td><td>8.38</td><td>15.32</td><td>15.14</td><td>9.48</td><td>16.93</td><td>17.04</td><td>11.04</td><td>19.28</td><td>20.28</td><td>9.45</td><td>16.84</td><td>17.12</td></tr>
<tr><td>AGCRN</td><td>5.47</td><td>10.86</td><td>9.56</td><td>6.43</td><td>12.94</td><td>11.91</td><td>8.03</td><td>15.56</td><td>15.51</td><td>6.45</td><td>13.05</td><td>12.02</td></tr>
<tr><td>AllDeepSet</td><td>3.39</td><td>6.58</td><td>9.14</td><td>4.10</td><td>8.03</td><td>11.21</td><td>5.14</td><td>10.31</td><td>14.87</td><td>4.09</td><td>8.02</td><td>11.33</td></tr>
<tr><td>DCRNN</td><td>3.44</td><td>6.89</td><td>8.94</td><td>4.07</td><td>8.25</td><td>11.67</td><td>5.21</td><td>9.94</td><td>15.54</td><td>4.08</td><td>8.15</td><td>11.72</td></tr>
<tr><td>DyHSL</td><td>3.23</td><td>6.31</td><td>8.32</td><td>3.77</td><td>7.88</td><td>10.74</td><td>4.75</td><td>9.62</td><td>14.03</td><td>3.82</td><td>7.83</td><td>10.76</td></tr>
<tr><td>GRU</td><td>3.59</td><td>7.11</td><td>9.37</td><td>4.28</td><td>8.75</td><td>12.27</td><td>5.69</td><td>10.46</td><td>16.69</td><td>4.36</td><td>8.58</td><td>12.41</td></tr>
<tr><td>GWNet</td><td>3.27</td><td>6.37</td><td>9.88</td><td>4.04</td><td>7.80</td><td>12.28</td><td>5.09</td><td>9.84</td><td>16.68</td><td>4.01</td><td>7.72</td><td>12.45</td></tr>
<tr><td>STGCN</td><td>3.40</td><td>6.51</td><td>9.22</td><td>3.99</td><td>8.15</td><td>11.57</td><td>5.14</td><td>10.18</td><td>14.96</td><td>4.04</td><td>8.12</td><td>11.67</td></tr>
<tr><td>STG-NCDE</td><td>3.71</td><td>6.87</td><td>7.47</td><td>4.90</td><td>10.25</td><td>10.47</td><td>6.89</td><td>14.06</td><td>14.90</td><td>4.76</td><td>10.10</td><td>10.20</td></tr>

<tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr>
<tr><td>DASTNet</td><td>3.72</td><td>7.50</td><td>9.30</td><td>4.57</td><td>9.52</td><td>12.07</td><td>6.01</td><td>11.58</td><td>16.25</td><td>4.59</td><td>9.07</td><td>12.07</td></tr>

<tr>
<td>D2MHyper</td>
<td><strong>2.31</strong></td><td><strong>4.36</strong></td><td><strong>6.09</strong></td>
<td><strong>2.66</strong></td><td><strong>5.00</strong></td><td><strong>6.99</strong></td>
<td><strong>3.55</strong></td><td><strong>7.17</strong></td><td><strong>10.45</strong></td>
<td><strong>2.74</strong></td><td><strong>5.28</strong></td><td><strong>7.47</strong></td>
</tr>

<tr>
<td>DAGN</td>
<td>3.04</td><td>5.57</td><td><u>7.24</u></td>
<td>3.29</td><td><u>6.32</u></td><td><u>8.49</u></td>
<td>3.93</td><td><u>7.41</u></td><td><u>10.78</u></td>
<td>3.33</td><td><u>6.35</u></td><td><u>8.63</u></td>
</tr>

<tr><td>ST-DAAN</td><td>3.16</td><td>5.98</td><td>8.02</td><td>3.74</td><td>7.56</td><td>10.68</td><td>4.95</td><td>9.47</td><td>15.24</td><td>3.81</td><td>7.53</td><td>10.89</td></tr>

<tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
<tr><td>MAML</td><td>4.04</td><td>7.60</td><td>11.82</td><td>4.87</td><td>9.24</td><td>14.88</td><td>6.28</td><td>10.87</td><td>19.15</td><td>4.90</td><td>9.07</td><td>14.90</td></tr>
<tr><td>ST-GFSL</td><td>4.02</td><td>7.52</td><td>11.57</td><td>4.85</td><td>9.36</td><td>14.36</td><td>6.42</td><td>11.43</td><td>18.53</td><td>4.91</td><td>9.25</td><td>14.47</td></tr>

<tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
<tr>
<td>CrossST</td>
<td><u>2.85</u></td><td><u>5.55</u></td><td>7.58</td>
<td><u>3.26</u></td><td>6.58</td><td>9.21</td>
<td><u>3.72</u></td><td>7.58</td><td>10.93</td>
<td><u>3.21</u></td><td>6.40</td><td>9.02</td>
</tr>

<tr><td>MTPB</td><td>3.14</td><td>5.68</td><td>7.59</td><td>3.70</td><td>7.10</td><td>10.00</td><td>4.68</td><td>8.57</td><td>13.17</td><td>3.75</td><td>7.00</td><td>10.08</td></tr>
<tr><td>STGCN-FT</td><td>3.41</td><td>6.60</td><td>8.93</td><td>3.90</td><td>7.78</td><td>11.31</td><td>4.89</td><td>9.53</td><td>15.02</td><td>3.94</td><td>7.82</td><td>11.50</td></tr>

<tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
<tr><td>FGITrans</td><td>3.27</td><td>6.39</td><td>12.07</td><td>3.88</td><td>7.36</td><td>13.54</td><td>4.75</td><td>8.55</td><td>15.04</td><td>3.97</td><td>7.43</td><td>13.55</td></tr>

<tr><td colspan="13"><strong>Foundation Models / LLM-Based Transfer (Paradigm 6)</strong></td></tr>
<tr><td>ST-LLM+</td><td>3.05</td><td>5.90</td><td>7.55</td><td>3.50</td><td>6.95</td><td>9.35</td><td>4.15</td><td>8.15</td><td>11.90</td><td>3.57</td><td>7.00</td><td>9.60</td></tr>
<tr><td>UrbanGPT</td><td>3.22</td><td>6.20</td><td>8.05</td><td>3.75</td><td>7.30</td><td>9.90</td><td>4.55</td><td>8.80</td><td>12.90</td><td>3.84</td><td>7.43</td><td>10.28</td></tr>
<tr><td>UniST</td><td>3.30</td><td>6.35</td><td>8.30</td><td>3.85</td><td>7.50</td><td>10.20</td><td>4.65</td><td>9.00</td><td>13.30</td><td>3.93</td><td>7.62</td><td>10.60</td></tr>

</tbody>
</table>

## 🏷️ Taxonomy of Learning Paradigms and Benchmark Model Zoo

<table align="center">
  <thead>
    <tr>
      <th align="center">Categories</th>
      <th align="center">Sub-categories</th>
      <th align="center">Guiding Principles</th>
      <th align="center">Representative Methods</th>
      <th align="center">Key Strengths</th>
      <th align="center">Primary Challenges</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center" rowspan="1"><strong>Single-Domain Models</strong></td>
      <td align="center"></td>
      <td align="center">Learn city-specific dynamics without transfer</td>
      <td align="center">GBRT, VAR, AGCRN, AllDeepSet, DCRNN, DyHSL, GRU, GWNet, STGCN, STG-NCDE</td>
      <td align="center">No cross-city bias</td>
      <td align="center">Performance degrades under data scarcity</td>
    </tr>
    <tr>
      <td align="center" rowspan="4"><strong>Cross-City Transfer Models</strong></td>
      <td align="center"><em>Alignment-based transfer</em></td>
      <td align="center">Explicitly align source-target distributions</td>
      <td align="center">DASTNet, D2MHyper, DAGN, ST-DAAN</td>
      <td align="center">Mitigates moderate distribution shifts</td>
      <td align="center">Sensitive to large heterogeneity; alignment cost</td>
    </tr>
    <tr>
      <td align="center"><em>Meta-learning-based transfer</em></td>
      <td align="center">Learn-to-adapt rapidly with few examples</td>
      <td align="center">MAML, ST-GFSL</td>
      <td align="center">Fast adaptation to new cities</td>
      <td align="center">Requires diverse meta-tasks; unstable optimization</td>
    </tr>
    <tr>
      <td align="center"><em>Pre-training-based transfer</em></td>
      <td align="center">Learn transferable representations from multi-city data</td>
      <td align="center">CrossST, MTPB, STGCN-FT</td>
      <td align="center">Strong generalization; scalable</td>
      <td align="center">Needs large pre-training corpus; catastrophic forgetting</td>
    </tr>
    <tr>
      <td align="center"><em>Knowledge-distillation-based transfer</em></td>
      <td align="center">Compress teacher knowledge into a lightweight student</td>
      <td align="center">FGITrans</td>
      <td align="center">Efficient deployment</td>
      <td align="center">Teacher-student capability gap; distillation loss</td>
    </tr>
    <tr>
      <td align="center" rowspan="1"><strong>Privacy-Preserving Collaborative Models</strong></td>
      <td align="center"></td>
      <td align="center">Collaborate without sharing raw data</td>
      <td align="center">FedCTPM, pFedCTP, FedGTP</td>
      <td align="center">Addresses scarcity and privacy jointly</td>
      <td align="center">Communication overhead; client heterogeneity</td>
    </tr>
  </tbody>
</table>

## 🧩 The technical pathway decision matrix for cross-city traffic prediction

<table align="center" border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; margin: 20px 0;">
  <thead>
    <tr>
      <th align="center"><strong>Constraints</strong></th>
      <th align="center"><strong>Primary Goals</strong></th>
      <th align="center"><strong>Paradigms</strong></th>
      <th align="center"><strong>Example Models</strong></th>
      <th align="center"><strong>Key Limitations</strong></th>
      <th align="center"><strong>Quantitative References</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center">Large distribution shift</td>
      <td align="center">Optimal accuracy</td>
      <td align="center">Alignment</td>
      <td align="center">D2MHyper</td>
      <td align="center">Needs source data; Unstable training</td>
      <td align="center">High <img src="https://latex.codecogs.com/svg.latex?\Delta\mathcal{M}_\text{shift}" alt="ΔM_shift"></td>
    </tr>
    <tr>
      <td align="center">Extreme data scarcity</td>
      <td align="center">Fast adaptation</td>
      <td align="center">Meta-learning</td>
      <td align="center">ST-GFSL</td>
      <td align="center">High meta-training cost; Task-sensitive</td>
      <td align="center">High latency; Robustness</td>
    </tr>
    <tr>
      <td align="center">Multi-source data available</td>
      <td align="center">Zero-shot robustness</td>
      <td align="center">Pre-training</td>
      <td align="center">CrossST</td>
      <td align="center">High pre-training resource cost</td>
      <td align="center">High memory use; Robustness</td>
    </tr>
    <tr>
      <td align="center">Deployment efficiency critical</td>
      <td align="center">Efficient inference</td>
      <td align="center">Distillation</td>
      <td align="center">FGITrans</td>
      <td align="center">Teacher-dependent</td>
      <td align="center">Low latency, small size</td>
    </tr>
    <tr>
      <td align="center">Privacy constraints</td>
      <td align="center">Privacy-preserving performance</td>
      <td align="center">Federated learning</td>
      <td align="center">FedCTPM</td>
      <td align="center">Communication cost; Utility gap</td>
      <td align="center">Communication overhead and <img src="https://latex.codecogs.com/svg.latex?\mathcal{G}_\text{util}" alt="G_util"></td>
    </tr>
    <tr>
      <td align="center">Ample resources</td>
      <td align="center">Generalization</td>
      <td align="center">Foundation model</td>
      <td align="center">Exploring</td>
      <td align="center">Very high cost</td>
      <td align="center">To be explored</td>
    </tr>
  </tbody>
</table>
