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

<table style="width:100%; border-collapse: collapse;">
  <thead>
    <tr>
      <th rowspan="2" style="border:1px solid #ddd; padding:8px;">Methods (Paradigms)</th>
      <th colspan="12" style="border:1px solid #ddd; padding:8px; text-align:center;">PeMS08 (Target Domain)</th>
    </tr>
    <tr>
      <th colspan="3" style="border:1px solid #ddd; padding:8px; text-align:center;">15 min</th>
      <th colspan="3" style="border:1px solid #ddd; padding:8px; text-align:center;">30 min</th>
      <th colspan="3" style="border:1px solid #ddd; padding:8px; text-align:center;">60 min</th>
      <th colspan="3" style="border:1px solid #ddd; padding:8px; text-align:center;">Average</th>
    </tr>
    <tr>
      <th style="border:1px solid #ddd; padding:8px;">&nbsp;</th>
      <th style="border:1px solid #ddd; padding:8px;">MAE</th><th style="border:1px solid #ddd; padding:8px;">RMSE</th><th style="border:1px solid #ddd; padding:8px;">MAPE (%)</th>
      <th style="border:1px solid #ddd; padding:8px;">MAE</th><th style="border:1px solid #ddd; padding:8px;">RMSE</th><th style="border:1px solid #ddd; padding:8px;">MAPE (%)</th>
      <th style="border:1px solid #ddd; padding:8px;">MAE</th><th style="border:1px solid #ddd; padding:8px;">RMSE</th><th style="border:1px solid #ddd; padding:8px;">MAPE (%)</th>
      <th style="border:1px solid #ddd; padding:8px;">MAE</th><th style="border:1px solid #ddd; padding:8px;">RMSE</th><th style="border:1px solid #ddd; padding:8px;">MAPE (%)</th>
    </tr>
  </thead>
  <tbody>
    <tr><td colspan="13" style="border:1px solid #ddd; padding:8px;"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">GBRT</td><td style="border:1px solid #ddd; padding:8px;">27.11</td><td style="border:1px solid #ddd; padding:8px;">44.28</td><td style="border:1px solid #ddd; padding:8px;">16.41</td><td style="border:1px solid #ddd; padding:8px;">29.35</td><td style="border:1px solid #ddd; padding:8px;">46.93</td><td style="border:1px solid #ddd; padding:8px;">17.79</td><td style="border:1px solid #ddd; padding:8px;">34.12</td><td style="border:1px solid #ddd; padding:8px;">52.76</td><td style="border:1px solid #ddd; padding:8px;">21.05</td><td style="border:1px solid #ddd; padding:8px;">29.68</td><td style="border:1px solid #ddd; padding:8px;">47.37</td><td style="border:1px solid #ddd; padding:8px;">18.09</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">VAR</td><td style="border:1px solid #ddd; padding:8px;">30.04</td><td style="border:1px solid #ddd; padding:8px;">44.90</td><td style="border:1px solid #ddd; padding:8px;">18.38</td><td style="border:1px solid #ddd; padding:8px;">32.37</td><td style="border:1px solid #ddd; padding:8px;">48.58</td><td style="border:1px solid #ddd; padding:8px;">19.85</td><td style="border:1px solid #ddd; padding:8px;">37.83</td><td style="border:1px solid #ddd; padding:8px;">56.31</td><td style="border:1px solid #ddd; padding:8px;">23.81</td><td style="border:1px solid #ddd; padding:8px;">32.86</td><td style="border:1px solid #ddd; padding:8px;">49.16</td><td style="border:1px solid #ddd; padding:8px;">20.33</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">AGCRN</td><td style="border:1px solid #ddd; padding:8px;">26.48</td><td style="border:1px solid #ddd; padding:8px;">46.25</td><td style="border:1px solid #ddd; padding:8px;">13.59</td><td style="border:1px solid #ddd; padding:8px;">26.65</td><td style="border:1px solid #ddd; padding:8px;">46.92</td><td style="border:1px solid #ddd; padding:8px;">13.61</td><td style="border:1px solid #ddd; padding:8px;">32.49</td><td style="border:1px solid #ddd; padding:8px;">52.35</td><td style="border:1px solid #ddd; padding:8px;">17.22</td><td style="border:1px solid #ddd; padding:8px;">28.03</td><td style="border:1px solid #ddd; padding:8px;">48.09</td><td style="border:1px solid #ddd; padding:8px;">14.50</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">AllDeepSet</td><td style="border:1px solid #ddd; padding:8px;">19.90</td><td style="border:1px solid #ddd; padding:8px;">29.33</td><td style="border:1px solid #ddd; padding:8px;">13.66</td><td style="border:1px solid #ddd; padding:8px;">25.37</td><td style="border:1px solid #ddd; padding:8px;">34.25</td><td style="border:1px solid #ddd; padding:8px;">37.15</td><td style="border:1px solid #ddd; padding:8px;">36.84</td><td style="border:1px solid #ddd; padding:8px;">52.75</td><td style="border:1px solid #ddd; padding:8px;">25.88</td><td style="border:1px solid #ddd; padding:8px;">26.72</td><td style="border:1px solid #ddd; padding:8px;">38.65</td><td style="border:1px solid #ddd; padding:8px;">19.82</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">DCRNN</td><td style="border:1px solid #ddd; padding:8px;">17.06</td><td style="border:1px solid #ddd; padding:8px;">26.46</td><td style="border:1px solid #ddd; padding:8px;">12.71</td><td style="border:1px solid #ddd; padding:8px;">20.11</td><td style="border:1px solid #ddd; padding:8px;">31.26</td><td style="border:1px solid #ddd; padding:8px;">14.29</td><td style="border:1px solid #ddd; padding:8px;">26.61</td><td style="border:1px solid #ddd; padding:8px;">40.51</td><td style="border:1px solid #ddd; padding:8px;">19.51</td><td style="border:1px solid #ddd; padding:8px;">20.53</td><td style="border:1px solid #ddd; padding:8px;">31.66</td><td style="border:1px solid #ddd; padding:8px;">14.82</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">DyHSL</td><td style="border:1px solid #ddd; padding:8px;">16.87</td><td style="border:1px solid #ddd; padding:8px;">25.46</td><td style="border:1px solid #ddd; padding:8px;">12.70</td><td style="border:1px solid #ddd; padding:8px;">18.95</td><td style="border:1px solid #ddd; padding:8px;">29.44</td><td style="border:1px solid #ddd; padding:8px;">14.09</td><td style="border:1px solid #ddd; padding:8px;">23.45</td><td style="border:1px solid #ddd; padding:8px;">35.98</td><td style="border:1px solid #ddd; padding:8px;">17.05</td><td style="border:1px solid #ddd; padding:8px;">19.16</td><td style="border:1px solid #ddd; padding:8px;">29.64</td><td style="border:1px solid #ddd; padding:8px;">14.71</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">GRU</td><td style="border:1px solid #ddd; padding:8px;">23.79</td><td style="border:1px solid #ddd; padding:8px;">33.02</td><td style="border:1px solid #ddd; padding:8px;">24.61</td><td style="border:1px solid #ddd; padding:8px;">33.34</td><td style="border:1px solid #ddd; padding:8px;">42.95</td><td style="border:1px solid #ddd; padding:8px;">38.50</td><td style="border:1px solid #ddd; padding:8px;">37.22</td><td style="border:1px solid #ddd; padding:8px;">51.33</td><td style="border:1px solid #ddd; padding:8px;">45.44</td><td style="border:1px solid #ddd; padding:8px;">30.02</td><td style="border:1px solid #ddd; padding:8px;">40.80</td><td style="border:1px solid #ddd; padding:8px;">34.02</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">GWNet</td><td style="border:1px solid #ddd; padding:8px;">21.03</td><td style="border:1px solid #ddd; padding:8px;">29.92</td><td style="border:1px solid #ddd; padding:8px;">20.19</td><td style="border:1px solid #ddd; padding:8px;">25.51</td><td style="border:1px solid #ddd; padding:8px;">36.89</td><td style="border:1px solid #ddd; padding:8px;">22.65</td><td style="border:1px solid #ddd; padding:8px;">36.30</td><td style="border:1px solid #ddd; padding:8px;">51.17</td><td style="border:1px solid #ddd; padding:8px;">29.62</td><td style="border:1px solid #ddd; padding:8px;">26.56</td><td style="border:1px solid #ddd; padding:8px;">38.07</td><td style="border:1px solid #ddd; padding:8px;">23.83</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">STGCN</td><td style="border:1px solid #ddd; padding:8px;">18.85</td><td style="border:1px solid #ddd; padding:8px;">29.14</td><td style="border:1px solid #ddd; padding:8px;">12.87</td><td style="border:1px solid #ddd; padding:8px;">23.65</td><td style="border:1px solid #ddd; padding:8px;">36.55</td><td style="border:1px solid #ddd; padding:8px;">15.60</td><td style="border:1px solid #ddd; padding:8px;">33.31</td><td style="border:1px solid #ddd; padding:8px;">51.41</td><td style="border:1px solid #ddd; padding:8px;">20.49</td><td style="border:1px solid #ddd; padding:8px;">24.61</td><td style="border:1px solid #ddd; padding:8px;">38.00</td><td style="border:1px solid #ddd; padding:8px;">15.95</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">STG-NCDE</td><td style="border:1px solid #ddd; padding:8px;">16.94</td><td style="border:1px solid #ddd; padding:8px;">25.59</td><td style="border:1px solid #ddd; padding:8px;">13.34</td><td style="border:1px solid #ddd; padding:8px;">18.02</td><td style="border:1px solid #ddd; padding:8px;">28.71</td><td style="border:1px solid #ddd; padding:8px;">14.32</td><td style="border:1px solid #ddd; padding:8px;">22.31</td><td style="border:1px solid #ddd; padding:8px;">35.11</td><td style="border:1px solid #ddd; padding:8px;">17.02</td><td style="border:1px solid #ddd; padding:8px;">18.62</td><td style="border:1px solid #ddd; padding:8px;">29.41</td><td style="border:1px solid #ddd; padding:8px;">14.72</td></tr>

    <tr><td colspan="13" style="border:1px solid #ddd; padding:8px;"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">DASTNet</td><td style="border:1px solid #ddd; padding:8px;">17.79</td><td style="border:1px solid #ddd; padding:8px;">26.65</td><td style="border:1px solid #ddd; padding:8px;">13.03</td><td style="border:1px solid #ddd; padding:8px;">20.64</td><td style="border:1px solid #ddd; padding:8px;">31.09</td><td style="border:1px solid #ddd; padding:8px;">14.56</td><td style="border:1px solid #ddd; padding:8px;">27.14</td><td style="border:1px solid #ddd; padding:8px;">40.02</td><td style="border:1px solid #ddd; padding:8px;">18.80</td><td style="border:1px solid #ddd; padding:8px;">21.15</td><td style="border:1px solid #ddd; padding:8px;">31.98</td><td style="border:1px solid #ddd; padding:8px;">15.47</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">D2MHyper</td><td style="border:1px solid #ddd; padding:8px;">15.34</td><td style="border:1px solid #ddd; padding:8px;"><ins>23.49</ins></td><td style="border:1px solid #ddd; padding:8px;"><ins>12.01</ins></td><td style="border:1px solid #ddd; padding:8px;">17.00</td><td style="border:1px solid #ddd; padding:8px;"><ins>26.29</ins></td><td style="border:1px solid #ddd; padding:8px;"><ins>12.75</ins></td><td style="border:1px solid #ddd; padding:8px;">21.69</td><td style="border:1px solid #ddd; padding:8px;">33.37</td><td style="border:1px solid #ddd; padding:8px;"><ins>16.79</ins></td><td style="border:1px solid #ddd; padding:8px;">17.54</td><td style="border:1px solid #ddd; padding:8px;"><ins>26.98</ins></td><td style="border:1px solid #ddd; padding:8px;"><ins>13.48</ins></td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">DAGN</td><td style="border:1px solid #ddd; padding:8px;">16.83</td><td style="border:1px solid #ddd; padding:8px;">24.53</td><td style="border:1px solid #ddd; padding:8px;">12.57</td><td style="border:1px solid #ddd; padding:8px;">17.73</td><td style="border:1px solid #ddd; padding:8px;">26.86</td><td style="border:1px solid #ddd; padding:8px;">14.03</td><td style="border:1px solid #ddd; padding:8px;">21.78</td><td style="border:1px solid #ddd; padding:8px;">33.88</td><td style="border:1px solid #ddd; padding:8px;">17.20</td><td style="border:1px solid #ddd; padding:8px;">18.36</td><td style="border:1px solid #ddd; padding:8px;">27.95</td><td style="border:1px solid #ddd; padding:8px;">14.56</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">ST-DAAN</td><td style="border:1px solid #ddd; padding:8px;">18.33</td><td style="border:1px solid #ddd; padding:8px;">27.37</td><td style="border:1px solid #ddd; padding:8px;">12.27</td><td style="border:1px solid #ddd; padding:8px;">21.98</td><td style="border:1px solid #ddd; padding:8px;">32.99</td><td style="border:1px solid #ddd; padding:8px;">15.19</td><td style="border:1px solid #ddd; padding:8px;">29.33</td><td style="border:1px solid #ddd; padding:8px;">43.47</td><td style="border:1px solid #ddd; padding:8px;">19.78</td><td style="border:1px solid #ddd; padding:8px;">22.44</td><td style="border:1px solid #ddd; padding:8px;">33.63</td><td style="border:1px solid #ddd; padding:8px;">15.23</td></tr>

    <tr><td colspan="13" style="border:1px solid #ddd; padding:8px;"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">MAML</td><td style="border:1px solid #ddd; padding:8px;">20.20</td><td style="border:1px solid #ddd; padding:8px;">28.61</td><td style="border:1px solid #ddd; padding:8px;">19.33</td><td style="border:1px solid #ddd; padding:8px;">24.30</td><td style="border:1px solid #ddd; padding:8px;">33.70</td><td style="border:1px solid #ddd; padding:8px;">25.05</td><td style="border:1px solid #ddd; padding:8px;">32.65</td><td style="border:1px solid #ddd; padding:8px;">44.25</td><td style="border:1px solid #ddd; padding:8px;">36.49</td><td style="border:1px solid #ddd; padding:8px;">24.89</td><td style="border:1px solid #ddd; padding:8px;">34.40</td><td style="border:1px solid #ddd; padding:8px;">26.11</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">ST-GFSL</td><td style="border:1px solid #ddd; padding:8px;">19.71</td><td style="border:1px solid #ddd; padding:8px;">28.35</td><td style="border:1px solid #ddd; padding:8px;">16.00</td><td style="border:1px solid #ddd; padding:8px;">23.41</td><td style="border:1px solid #ddd; padding:8px;">33.18</td><td style="border:1px solid #ddd; padding:8px;">19.53</td><td style="border:1px solid #ddd; padding:8px;">30.28</td><td style="border:1px solid #ddd; padding:8px;">42.48</td><td style="border:1px solid #ddd; padding:8px;">27.52</td><td style="border:1px solid #ddd; padding:8px;">23.75</td><td style="border:1px solid #ddd; padding:8px;">33.64</td><td style="border:1px solid #ddd; padding:8px;">20.25</td></tr>

    <tr><td colspan="13" style="border:1px solid #ddd; padding:8px;"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">CrossST</td><td style="border:1px solid #ddd; padding:8px;"><strong>13.68</strong></td><td style="border:1px solid #ddd; padding:8px;"><strong>21.79</strong></td><td style="border:1px solid #ddd; padding:8px;"><strong>8.81</strong></td><td style="border:1px solid #ddd; padding:8px;"><strong>14.65</strong></td><td style="border:1px solid #ddd; padding:8px;"><strong>23.60</strong></td><td style="border:1px solid #ddd; padding:8px;"><strong>9.63</strong></td><td style="border:1px solid #ddd; padding:8px;"><ins>16.25</ins></td><td style="border:1px solid #ddd; padding:8px;"><strong>26.00</strong></td><td style="border:1px solid #ddd; padding:8px;"><strong>10.60</strong></td><td style="border:1px solid #ddd; padding:8px;"><strong>14.67</strong></td><td style="border:1px solid #ddd; padding:8px;"><strong>23.49</strong></td><td style="border:1px solid #ddd; padding:8px;"><strong>9.59</strong></td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">MTPB</td><td style="border:1px solid #ddd; padding:8px;">21.92</td><td style="border:1px solid #ddd; padding:8px;">31.69</td><td style="border:1px solid #ddd; padding:8px;">15.17</td><td style="border:1px solid #ddd; padding:8px;">24.21</td><td style="border:1px solid #ddd; padding:8px;">34.71</td><td style="border:1px solid #ddd; padding:8px;">15.50</td><td style="border:1px solid #ddd; padding:8px;">27.53</td><td style="border:1px solid #ddd; padding:8px;">39.75</td><td style="border:1px solid #ddd; padding:8px;">18.30</td><td style="border:1px solid #ddd; padding:8px;">24.47</td><td style="border:1px solid #ddd; padding:8px;">35.39</td><td style="border:1px solid #ddd; padding:8px;">16.14</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">STGCN-FT</td><td style="border:1px solid #ddd; padding:8px;">18.11</td><td style="border:1px solid #ddd; padding:8px;">27.17</td><td style="border:1px solid #ddd; padding:8px;">13.99</td><td style="border:1px solid #ddd; padding:8px;">20.94</td><td style="border:1px solid #ddd; padding:8px;">31.39</td><td style="border:1px solid #ddd; padding:8px;">16.83</td><td style="border:1px solid #ddd; padding:8px;">26.63</td><td style="border:1px solid #ddd; padding:8px;">39.17</td><td style="border:1px solid #ddd; padding:8px;">20.09</td><td style="border:1px solid #ddd; padding:8px;">21.92</td><td style="border:1px solid #ddd; padding:8px;">32.72</td><td style="border:1px solid #ddd; padding:8px;">16.77</td></tr>

    <tr><td colspan="13" style="border:1px solid #ddd; padding:8px;"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">FGITrans</td><td style="border:1px solid #ddd; padding:8px;"><ins>14.63</ins></td><td style="border:1px solid #ddd; padding:8px;">28.29</td><td style="border:1px solid #ddd; padding:8px;">18.91</td><td style="border:1px solid #ddd; padding:8px;"><ins>14.73</ins></td><td style="border:1px solid #ddd; padding:8px;">28.58</td><td style="border:1px solid #ddd; padding:8px;">18.98</td><td style="border:1px solid #ddd; padding:8px;"><strong>14.93</strong></td><td style="border:1px solid #ddd; padding:8px;"><ins>29.14</ins></td><td style="border:1px solid #ddd; padding:8px;">19.10</td><td style="border:1px solid #ddd; padding:8px;"><ins>14.76</ins></td><td style="border:1px solid #ddd; padding:8px;">28.67</td><td style="border:1px solid #ddd; padding:8px;">19.00</td></tr>

    <tr><td colspan="13" style="border:1px solid #ddd; padding:8px;"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">ST-LLM+</td><td style="border:1px solid #ddd; padding:8px;">15.80</td><td style="border:1px solid #ddd; padding:8px;">24.80</td><td style="border:1px solid #ddd; padding:8px;">12.60</td><td style="border:1px solid #ddd; padding:8px;">17.20</td><td style="border:1px solid #ddd; padding:8px;">27.20</td><td style="border:1px solid #ddd; padding:8px;">13.80</td><td style="border:1px solid #ddd; padding:8px;">20.60</td><td style="border:1px solid #ddd; padding:8px;">31.80</td><td style="border:1px solid #ddd; padding:8px;">16.80</td><td style="border:1px solid #ddd; padding:8px;">17.87</td><td style="border:1px solid #ddd; padding:8px;">27.93</td><td style="border:1px solid #ddd; padding:8px;">14.40</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">UrbanGPT</td><td style="border:1px solid #ddd; padding:8px;">17.50</td><td style="border:1px solid #ddd; padding:8px;">27.00</td><td style="border:1px solid #ddd; padding:8px;">13.80</td><td style="border:1px solid #ddd; padding:8px;">19.80</td><td style="border:1px solid #ddd; padding:8px;">30.50</td><td style="border:1px solid #ddd; padding:8px;">15.20</td><td style="border:1px solid #ddd; padding:8px;">24.50</td><td style="border:1px solid #ddd; padding:8px;">37.80</td><td style="border:1px solid #ddd; padding:8px;">18.90</td><td style="border:1px solid #ddd; padding:8px;">20.60</td><td style="border:1px solid #ddd; padding:8px;">31.77</td><td style="border:1px solid #ddd; padding:8px;">15.97</td></tr>
    <tr><td style="border:1px solid #ddd; padding:8px;">UniST</td><td style="border:1px solid #ddd; padding:8px;">18.20</td><td style="border:1px solid #ddd; padding:8px;">28.00</td><td style="border:1px solid #ddd; padding:8px;">14.20</td><td style="border:1px solid #ddd; padding:8px;">20.70</td><td style="border:1px solid #ddd; padding:8px;">31.80</td><td style="border:1px solid #ddd; padding:8px;">15.80</td><td style="border:1px solid #ddd; padding:8px;">25.60</td><td style="border:1px solid #ddd; padding:8px;">39.20</td><td style="border:1px solid #ddd; padding:8px;">19.60</td><td style="border:1px solid #ddd; padding:8px;">21.50</td><td style="border:1px solid #ddd; padding:8px;">33.00</td><td style="border:1px solid #ddd; padding:8px;">16.53</td></tr>
  </tbody>
</table>

### PeMS-BAY → METR-LA



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
