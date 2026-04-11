# 🏙️ CrossCityBench: A Comprehensive Benchmark for Cross-City Traffic Prediction

## 🏆 Contribution

<div align="center">
  <img src="images/crosscitybench.jpg" alt="The CrossCityBench architecture" width="90%">
  <br>
  <strong>The CrossCityBench architecture</strong>
</div>
<br>

This paper proposes CrossCityBench, a benchmark framework for cross-city traffic prediction, with its core work structured around a three-tier logic of "**Evaluation–Diagnosis–Decision**".

- **Evaluation**: A unified evaluation system is constructed, systematically categorizing methods into single-domain models, cross-city transfer models (including alignment-based, meta-learning-based, pre-training-based, and knowledge distillation-based strategies), and privacy-preserving collaborative models.
  
- **Diagnosis**: Based on multi-dimensional in-depth diagnostics, model behaviors are analyzed in terms of efficiency, robustness, interpretability, and collaboration costs in federated learning scenarios, revealing their characteristics under challenges such as data scarcity and distribution shifts.
  
- **Decision**: Experimental findings are synthesized into a pathway matrix, providing well-founded guidance for method selection and deployment trade-offs in practical scenarios.
  
All analyses are supported by a complete set of supplementary materials (including experimental details, extended datasets, evaluation metrics, baseline methods, case studies, etc.), ensuring the reproducibility of the research and the comprehensiveness of the conclusions. Through systematic evaluation, diagnosis, and decision support, this framework promotes the practical adoption and paradigm evolution of cross-city prediction models.

## 💾 Datasets

### Core Datasets
<div align="center">

|  Datasets  |     Tasks      | #Nodes |   Interval   | Time Span (min) |
|:---------:|:-------------:|:--------:|:-------------:|:--------:|
| PeMS03    | Traffic Flow  | 358      | 5 min| 131,040    |
| PeMS08    | Traffic Flow  | 170      | 5 min| 89,280    |
| PeMS-BAY  | Traffic Speed | 325      | 5 min| 217,440    |
| METR-LA   | Traffic Speed | 207      | 5 min| 175,680    |

</div>

Core datasets (PeMS03, PeMS08, PeMS-BAY, and METR-LA) are available at [Google Drive](https://drive.google.com/file/d/1oPLRyEN32peSLWLVNVcropHt5iBNUQxo).

### Constructed Datasets

<div align="center">

|  Datasets  |     Tasks      | #Nodes |   Interval   | Time Span (min) |
|:---------:|:-------------:|:--------:|:-------------:|:--------:|
| Taiyuan    | Traffic Flow  | 280      | 5 min| 30,240    |
| Datong    | Traffic Flow  | 125      | 5 min| 11,520    |
| Fuzhou  | Traffic Flow | 360      | 5 min| 40,320    |

</div>

The three datasets described above, namely the Taiyuan, Datong, and Fuzhou datasets, are independently constructed by the authors based on traffic data collected from the cities where the authors are currently located. The data acquisition and processing pipeline are designed and implemented by the authors, with support from local traffic management authorities and publicly available traffic sensing platforms.

The motivation for constructing these datasets is to enrich the diversity and availability of urban traffic data. Existing public datasets are limited in terms of geographical coverage and structural variability. In contrast, the constructed datasets include cities with distinct road network topologies and traffic patterns, which provide a more comprehensive benchmark for evaluating the robustness and generalization ability of traffic forecasting models under heterogeneous urban scenarios.

#### **Taiyuan**

**City Description**  

The Taiyuan dataset is collected from Taiyuan, the capital city of Shanxi Province, China. Taiyuan is characterized by a basin-like terrain surrounded by mountains, which constrains urban expansion and leads to a road network with a combination of radial and ring structures. The city exhibits significant traffic congestion, especially along major arterial roads during peak hours. Due to the geographical constraints and dense urban core, traffic flows in Taiyuan show strong spatial heterogeneity and temporal peak patterns.

**Data Sources and Coverage**

Collected in collaboration with the **Shanxi Transportation Holdings Group Co., Ltd.**, covering:
- Urban expressways  
- Ring roads  
- Major arterial roads

A total of **280 traffic sensors** are deployed within:
- Latitude: `37.7°–38.1° N`  
- Longitude: `112.45°–112.75° E`

**Data Collection Protocol**  

- Time period: **February 15, 2026 – March 7, 2026 (21 days)**  
- Sampling interval: **5 minutes**
- Time step: **T = 21 × 24 × 12 = 6048**

**Data Format**

- `Taiyuan_nodes.csv` # sensor_id, latitude, longitude
- `Taiyuan_dist.csv` # from, to, distance (sparse graph)
- `Taiyuan.npz` # traffic data

**Features**

Each sensor records:
- Traffic flow  

**Data Shape**

(6048, 280, 1)

#### **Datong**

**City Description**  

The Datong dataset is collected from Datong, a medium-sized city located in northern Shanxi Province, China. Unlike Taiyuan, Datong features a relatively flat terrain and a well-planned urban layout with a grid-like road network. The traffic demand is comparatively moderate, and congestion is less severe. As a result, the traffic flow patterns in Datong tend to be more regular and stable, making it suitable for analyzing structured urban traffic dynamics.

**Data Sources and Coverage**

Provided by the **Shanxi Transportation Holdings Group Co., Ltd.**, covering:
- Urban main roads  
- Secondary roads

A total of **125 traffic sensors** are deployed within:
- Latitude: `40.0°–40.2° N`  
- Longitude: `113.0°–113.3° E`

**Data Collection Protocol**

- Time period: **March 1, 2026 – March 8, 2026 (8 days)**  
- Sampling interval: **5 minutes**
- Time step: **T = 8 × 24 × 12 = 2304**

**Data Format**

- `Datong_nodes.csv` # sensor_id, latitude, longitude
- `Datong_dist.csv` # from, to, distance (sparse graph)
- `Datong.npz` # traffic data

**Features**

Each sensor records:
- Traffic flow

**Data Shape**

(2304, 125, 1)

#### **Fuzhou**

**City Description** 

The Fuzhou dataset is collected from Fuzhou, the capital city of Fujian Province in southeastern China. Fuzhou has a complex geographical environment consisting of rivers, hills, and coastal areas, which results in a heterogeneous and partially constrained road network. The urban traffic is influenced by both natural barriers and high population density, leading to diverse traffic patterns with frequent fluctuations and localized congestion.

**Data Sources and Coverage**

Constructed in collaboration with the **Fujian Provincial Communication Transportation Group Co.,Ltd.**, covering:
- Urban trunk roads  
- Bridges  
- Cross-river corridors  

A total of **360 traffic sensors** are deployed within:
- Latitude: `26.0°–26.2° N`  
- Longitude: `119.25°–119.35° E`

**Data Collection Protocol**

- Time period: **February 1, 2026 – February 28, 2026 (28 days)**  
- Sampling interval: **5 minutes**
- Time step: **T = 28 × 24 × 12 = 8064**

**Data Format**

- `Fuzhou_nodes.csv` # sensor_id, latitude, longitude
- `Fuzhou_dist.csv` # from, to, distance (sparse graph)
- `Fuzhou.npz` # traffic data

**Features**

Each sensor records:
- Traffic flow

**Data Shape**

(8064, 360, 1)

<div align="center">
  <img src="Urban Structure.png" alt="Urban Structures" width="80%">
  <br>
  <strong>Urban Structures</strong>
</div>
<br>

The above three constructed datasets can be found in:
[All Revisions/Newly Constructed Datasets](./All%20Revisions/Newly%20Constructed%20Datasets/)

## 📊 Overall Performance Comparison

 **Revisions:** The original two cross-city transfer experiments have been extended to **12** experiment groups, as detailed below.

### Performance Comparison on Cross-City Traffic Flow Prediction (PeMS03 → PeMS08) with 7-Day Training Data

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
<tr><td>MTPB</td><td>21.92</td><td>31.69</td><td>15.17</td><td>24.21</td><td>34.71</td><td>15.50</td><td>27.53</td><td>39.75</td><td>18.30</td><td>24.47</td><td>35.39</td><td>16.14</td></tr>
<tr><td>STGCN-FT</td><td>18.11</td><td>27.17</td><td>13.99</td><td>20.94</td><td>31.39</td><td>16.83</td><td>26.63</td><td>39.17</td><td>20.09</td><td>21.92</td><td>32.72</td><td>16.77</td></tr>


<tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
<tr>
<td>FGITrans</td>
<td><ins>14.63</ins></td><td>28.29</td><td>18.91</td>
<td><ins>14.73</ins></td><td>28.58</td><td>18.98</td>
<td><strong>14.93</strong></td><td><ins>29.14</ins></td><td>19.10</td>
<td><ins>14.76</ins></td><td>28.67</td><td>19.00</td>
</tr>

<tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr>
   <tr>
      <td>ST-LLM+</td>
      <td>15.80</td><td>24.80</td><td>12.60</td>
      <td>17.20</td><td>27.20</td><td>13.80</td>
      <td>20.60</td><td>31.80</td><td>16.80</td>
      <td>17.87</td><td>27.93</td><td>14.40</td>
   </tr>
   <tr>
      <td>UrbanGPT</td>
      <td>17.50</td><td>27.00</td><td>13.80</td>
      <td>19.80</td><td>30.50</td><td>15.20</td>
      <td>24.50</td><td>37.80</td><td>18.90</td>
      <td>20.60</td><td>31.77</td><td>15.97</td>
   </tr>
   <tr>
      <td>UniST</td>
      <td>18.20</td><td>28.00</td><td>14.20</td>
      <td>20.70</td><td>31.80</td><td>15.80</td>
      <td>25.60</td><td>39.20</td><td>19.60</td>
      <td>21.50</td><td>33.00</td><td>16.53</td>
   </tr>

</tbody>
</table> 

### Performance Comparison on Cross-City Traffic Flow Prediction (PeMS08 → PeMS03) with 7-Day Training Data

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
    <tr><td>GBRT</td><td>28.34</td><td>45.12</td><td>17.22</td><td>30.68</td><td>48.03</td><td>18.65</td><td>35.47</td><td>54.21</td><td>22.10</td><td>31.02</td><td>48.45</td><td>18.99</td></tr>
    <tr><td>VAR</td><td>31.22</td><td>46.05</td><td>19.15</td><td>33.65</td><td>49.77</td><td>20.68</td><td>39.10</td><td>57.90</td><td>24.56</td><td>34.13</td><td>50.57</td><td>21.13</td></tr>
    <tr><td>AGCRN</td><td>27.56</td><td>47.33</td><td>14.22</td><td>27.89</td><td>48.05</td><td>14.30</td><td>33.82</td><td>53.90</td><td>18.05</td><td>29.22</td><td>49.42</td><td>15.23</td></tr>
    <tr><td>AllDeepSet</td><td>20.88</td><td>30.45</td><td>14.32</td><td>26.45</td><td>35.60</td><td>38.20</td><td>38.12</td><td>54.30</td><td>26.50</td><td>27.78</td><td>39.78</td><td>20.67</td></tr>
    <tr><td>DCRNN</td><td>17.98</td><td>27.33</td><td>13.45</td><td>21.05</td><td>32.15</td><td>15.00</td><td>27.70</td><td>41.80</td><td>20.30</td><td>21.57</td><td>32.76</td><td>15.58</td></tr>
    <tr><td>DyHSL</td><td>17.75</td><td>26.34</td><td>13.40</td><td>19.88</td><td>30.35</td><td>14.80</td><td>24.56</td><td>37.25</td><td>17.85</td><td>20.13</td><td>30.65</td><td>15.38</td></tr>
    <tr><td>GRU</td><td>24.88</td><td>34.20</td><td>25.40</td><td>34.66</td><td>44.20</td><td>39.60</td><td>38.55</td><td>52.90</td><td>46.80</td><td>31.37</td><td>42.10</td><td>35.27</td></tr>
    <tr><td>GWNet</td><td>22.10</td><td>31.05</td><td>21.05</td><td>26.68</td><td>38.10</td><td>23.40</td><td>37.65</td><td>52.80</td><td>30.55</td><td>27.81</td><td>39.32</td><td>24.67</td></tr>
    <tr><td>STGCN</td><td>19.77</td><td>30.05</td><td>13.55</td><td>24.65</td><td>37.68</td><td>16.20</td><td>34.55</td><td>53.05</td><td>21.30</td><td>25.66</td><td>39.26</td><td>16.68</td></tr>
    <tr><td>STG-NCDE</td><td>17.85</td><td>26.50</td><td>14.00</td><td>18.95</td><td>29.65</td><td>15.05</td><td>23.20</td><td>36.30</td><td>17.80</td><td>19.67</td><td>30.48</td><td>15.42</td></tr>
    <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr>
    <tr><td>DASTNet</td><td>18.66</td><td>27.55</td><td>13.68</td><td>21.55</td><td>32.05</td><td>15.25</td><td>28.20</td><td>41.30</td><td>19.65</td><td>22.14</td><td>33.00</td><td>16.20</td></tr>
    <tr><td>D2MHyper</td><td>16.10</td><td><ins>24.20</ins></td><td><ins>12.60</ins></td><td>17.85</td><td><ins>27.05</ins></td><td><ins>13.35</ins></td><td>22.70</td><td>34.50</td><td><ins>17.55</ins></td><td>18.42</td><td><ins>27.90</ins></td><td><ins>14.12</ins></td></tr>
    <tr><td>DAGN</td><td>17.68</td><td>25.30</td><td>13.20</td><td>18.60</td><td>27.70</td><td>14.70</td><td>22.85</td><td>35.05</td><td>18.05</td><td>19.28</td><td>28.85</td><td>15.28</td></tr>
    <tr><td>ST-DAAN</td><td>19.25</td><td>28.20</td><td>12.90</td><td>23.05</td><td>34.05</td><td>15.90</td><td>30.55</td><td>44.80</td><td>20.65</td><td>23.55</td><td>34.68</td><td>15.98</td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
    <tr><td>MAML</td><td>21.15</td><td>29.50</td><td>20.30</td><td>25.40</td><td>34.70</td><td>26.20</td><td>34.00</td><td>45.60</td><td>38.10</td><td>26.05</td><td>35.60</td><td>27.40</td></tr>
    <tr><td>ST-GFSL</td><td>20.65</td><td>29.20</td><td>16.80</td><td>24.50</td><td>34.15</td><td>20.50</td><td>31.60</td><td>43.80</td><td>28.80</td><td>24.85</td><td>34.72</td><td>21.20</td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
    <tr><td>CrossST</td><td><strong>14.38</strong></td><td><strong>22.50</strong></td><td><strong>9.25</strong></td><td><strong>15.40</strong></td><td><strong>24.35</strong></td><td><strong>10.10</strong></td><td><ins>17.05</ins></td><td><strong>26.80</strong></td><td><strong>11.10</strong></td><td><strong>15.42</strong></td><td><strong>24.22</strong></td><td><strong>10.05</strong></td></tr>
    <tr><td>MTPB</td><td>23.00</td><td>32.70</td><td>15.90</td><td>25.35</td><td>35.80</td><td>16.25</td><td>28.85</td><td>41.00</td><td>19.20</td><td>25.65</td><td>36.50</td><td>16.93</td></tr>
    <tr><td>STGCN-FT</td><td>19.00</td><td>28.05</td><td>14.68</td><td>21.95</td><td>32.35</td><td>17.65</td><td>27.90</td><td>40.40</td><td>21.05</td><td>22.95</td><td>33.75</td><td>17.59</td></tr>
    <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
    <tr><td>FGITrans</td><td><ins>15.35</ins></td><td>29.20</td><td>19.85</td><td><ins>15.45</ins></td><td>29.50</td><td>19.90</td><td><strong>15.65</strong></td><td><ins>30.05</ins></td><td>20.05</td><td><ins>15.48</ins></td><td>29.58</td><td>19.93</td></tr>
    <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr>
    <tr><td>ST-LLM+</td><td>16.60</td><td>25.60</td><td>13.20</td><td>18.05</td><td>28.05</td><td>14.45</td><td>21.60</td><td>32.80</td><td>17.60</td><td>18.75</td><td>28.82</td><td>15.08</td></tr>
    <tr><td>UrbanGPT</td><td>18.35</td><td>27.85</td><td>14.45</td><td>20.75</td><td>31.45</td><td>15.90</td><td>25.70</td><td>38.95</td><td>19.80</td><td>21.60</td><td>32.75</td><td>16.72</td></tr>
    <tr><td>UniST</td><td>19.10</td><td>28.85</td><td>14.90</td><td>21.70</td><td>32.80</td><td>16.55</td><td>26.85</td><td>40.40</td><td>20.55</td><td>22.55</td><td>34.02</td><td>17.33</td></tr>
  </tbody>
</table>
            
### Performance Comparison on Cross-City Traffic Speed Prediction (PeMS-BAY → METR-LA) with 7-Day Training Data

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
<td>3.04</td><td>5.57</td><td><ins>7.24</ins></td>
<td>3.29</td><td><ins>6.32</ins></td><td><ins>8.49</ins></td>
<td>3.93</td><td><ins>7.41</ins></td><td><ins>10.78</ins></td>
<td>3.33</td><td><ins>6.35</ins></td><td><ins>8.63</ins></td>
</tr>

<tr><td>ST-DAAN</td><td>3.16</td><td>5.98</td><td>8.02</td><td>3.74</td><td>7.56</td><td>10.68</td><td>4.95</td><td>9.47</td><td>15.24</td><td>3.81</td><td>7.53</td><td>10.89</td></tr>

<tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
<tr><td>MAML</td><td>4.04</td><td>7.60</td><td>11.82</td><td>4.87</td><td>9.24</td><td>14.88</td><td>6.28</td><td>10.87</td><td>19.15</td><td>4.90</td><td>9.07</td><td>14.90</td></tr>
<tr><td>ST-GFSL</td><td>4.02</td><td>7.52</td><td>11.57</td><td>4.85</td><td>9.36</td><td>14.36</td><td>6.42</td><td>11.43</td><td>18.53</td><td>4.91</td><td>9.25</td><td>14.47</td></tr>

<tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
<tr>
<td>CrossST</td>
<td><ins>2.85</ins></td><td><ins>5.55</ins></td><td>7.58</td>
<td><ins>3.26</ins></td><td>6.58</td><td>9.21</td>
<td><ins>3.72</ins></td><td>7.58</td><td>10.93</td>
<td><ins>3.21</ins></td><td>6.40</td><td>9.02</td>
</tr>

<tr><td>MTPB</td><td>3.14</td><td>5.68</td><td>7.59</td><td>3.70</td><td>7.10</td><td>10.00</td><td>4.68</td><td>8.57</td><td>13.17</td><td>3.75</td><td>7.00</td><td>10.08</td></tr>
<tr><td>STGCN-FT</td><td>3.41</td><td>6.60</td><td>8.93</td><td>3.90</td><td>7.78</td><td>11.31</td><td>4.89</td><td>9.53</td><td>15.02</td><td>3.94</td><td>7.82</td><td>11.50</td></tr>

<tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
<tr><td>FGITrans</td><td>3.27</td><td>6.39</td><td>12.07</td><td>3.88</td><td>7.36</td><td>13.54</td><td>4.75</td><td>8.55</td><td>15.04</td><td>3.97</td><td>7.43</td><td>13.55</td></tr>

<tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr>
<tr><td>ST-LLM+</td><td>3.05</td><td>5.90</td><td>7.55</td><td>3.50</td><td>6.95</td><td>9.35</td><td>4.15</td><td>8.15</td><td>11.90</td><td>3.57</td><td>7.00</td><td>9.60</td></tr>
<tr><td>UrbanGPT</td><td>3.22</td><td>6.20</td><td>8.05</td><td>3.75</td><td>7.30</td><td>9.90</td><td>4.55</td><td>8.80</td><td>12.90</td><td>3.84</td><td>7.43</td><td>10.28</td></tr>
<tr><td>UniST</td><td>3.30</td><td>6.35</td><td>8.30</td><td>3.85</td><td>7.50</td><td>10.20</td><td>4.65</td><td>9.00</td><td>13.30</td><td>3.93</td><td>7.62</td><td>10.60</td></tr>

</tbody>
</table>

### Performance Comparison on Cross-City Traffic Speed Prediction (METR-LA → PeMS-BAY) with 7-Day Training Data

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
    <tr><td>GBRT</td><td>9.56</td><td>17.20</td><td>17.80</td><td>10.68</td><td>19.65</td><td>19.90</td><td>12.20</td><td>22.10</td><td>22.30</td><td>10.62</td><td>19.38</td><td>19.75</td></tr>
    <tr><td>VAR</td><td>9.12</td><td>16.45</td><td>16.25</td><td>10.30</td><td>18.10</td><td>18.20</td><td>12.05</td><td>20.55</td><td>21.60</td><td>10.27</td><td>18.02</td><td>18.35</td></tr>
    <tr><td>AGCRN</td><td>6.05</td><td>11.70</td><td>10.30</td><td>7.08</td><td>13.95</td><td>12.80</td><td>8.85</td><td>16.75</td><td>16.70</td><td>7.10</td><td>14.08</td><td>13.00</td></tr>
    <tr><td>AllDeepSet</td><td>3.78</td><td>7.20</td><td>10.05</td><td>4.55</td><td>8.85</td><td>12.30</td><td>5.68</td><td>11.35</td><td>16.30</td><td>4.52</td><td>8.82</td><td>12.40</td></tr>
    <tr><td>DCRNN</td><td>3.82</td><td>7.55</td><td>9.85</td><td>4.50</td><td>9.05</td><td>12.80</td><td>5.75</td><td>10.90</td><td>17.00</td><td>4.51</td><td>8.96</td><td>12.85</td></tr>
    <tr><td>DyHSL</td><td>3.60</td><td>6.95</td><td>9.15</td><td>4.18</td><td>8.65</td><td>11.80</td><td>5.25</td><td>10.55</td><td>15.35</td><td>4.22</td><td>8.62</td><td>11.78</td></tr>
    <tr><td>GRU</td><td>4.00</td><td>7.85</td><td>10.30</td><td>4.75</td><td>9.65</td><td>13.45</td><td>6.28</td><td>11.50</td><td>18.25</td><td>4.82</td><td>9.45</td><td>13.60</td></tr>
    <tr><td>GWNet</td><td>3.65</td><td>7.05</td><td>10.85</td><td>4.48</td><td>8.60</td><td>13.45</td><td>5.62</td><td>10.85</td><td>18.25</td><td>4.45</td><td>8.52</td><td>13.62</td></tr>
    <tr><td>STGCN</td><td>3.78</td><td>7.18</td><td>10.15</td><td>4.42</td><td>8.98</td><td>12.70</td><td>5.68</td><td>11.22</td><td>16.35</td><td>4.46</td><td>8.95</td><td>12.80</td></tr>
    <tr><td>STG-NCDE</td><td>4.10</td><td>7.55</td><td>8.20</td><td>5.40</td><td>11.25</td><td>11.45</td><td>7.58</td><td>15.45</td><td>16.30</td><td>5.24</td><td>11.10</td><td>11.18</td></tr>
    <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr>
    <tr><td>DASTNet</td><td>4.10</td><td>8.25</td><td>10.20</td><td>5.02</td><td>10.45</td><td>13.25</td><td>6.60</td><td>12.70</td><td>17.80</td><td>5.05</td><td>9.97</td><td>13.25</td></tr>
    <tr><td>D2MHyper</td><td><strong>2.55</strong></td><td><strong>4.80</strong></td><td><strong>6.70</strong></td><td><strong>2.93</strong></td><td><strong>5.50</strong></td><td><strong>7.70</strong></td><td><strong>3.90</strong></td><td><strong>7.88</strong></td><td><strong>11.50</strong></td><td><strong>3.02</strong></td><td><strong>5.81</strong></td><td><strong>8.22</strong></td></tr>
    <tr><td>DAGN</td><td><ins>3.13</ins></td><td><ins>6.10</ins></td><td><ins>7.95</ins></td><td><ins>3.58</ins></td><td>7.24</td><td><ins>9.35</ins></td><td>4.32</td><td><ins>8.15</ins></td><td><ins>11.85</ins></td><td>3.67</td><td><ins>6.99</ins></td><td><ins>9.50</ins></td></tr>
    <tr><td>ST-DAAN</td><td>3.48</td><td>6.58</td><td>8.82</td><td>4.12</td><td>8.32</td><td>11.75</td><td>5.45</td><td>10.42</td><td>16.75</td><td>4.20</td><td>8.28</td><td>11.98</td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
    <tr><td>MAML</td><td>4.45</td><td>8.35</td><td>13.00</td><td>5.35</td><td>10.15</td><td>16.35</td><td>6.90</td><td>11.95</td><td>21.05</td><td>5.40</td><td>9.97</td><td>16.38</td></tr>
    <tr><td>ST-GFSL</td><td>4.42</td><td>8.27</td><td>12.70</td><td>5.33</td><td>10.28</td><td>15.78</td><td>7.05</td><td>12.55</td><td>20.35</td><td>5.40</td><td>10.17</td><td>15.90</td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
    <tr><td>CrossST</td><td>3.35</td><td>6.12</td><td>8.33</td><td>3.62</td><td><ins>6.95</ins></td><td>10.12</td><td><ins>4.09</ins></td><td>8.34</td><td>12.02</td><td><ins>3.53</ins></td><td>7.04</td><td>9.92</td></tr>
    <tr><td>MTPB</td><td>3.45</td><td>6.25</td><td>8.35</td><td>4.07</td><td>7.81</td><td>11.00</td><td>5.15</td><td>9.43</td><td>14.48</td><td>4.13</td><td>7.70</td><td>11.09</td></tr>
    <tr><td>STGCN-FT</td><td>3.75</td><td>7.25</td><td>9.82</td><td>4.29</td><td>8.56</td><td>12.44</td><td>5.38</td><td>10.48</td><td>16.52</td><td>4.33</td><td>8.60</td><td>12.65</td></tr>
    <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
    <tr><td>FGITrans</td><td>3.60</td><td>7.03</td><td>13.28</td><td>4.27</td><td>8.10</td><td>14.90</td><td>5.22</td><td>9.40</td><td>16.55</td><td>4.37</td><td>8.18</td><td>14.91</td></tr>
    <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr>
    <tr><td>ST-LLM+</td><td>3.35</td><td>6.50</td><td>8.30</td><td>3.85</td><td>7.65</td><td>10.28</td><td>4.56</td><td>8.97</td><td>13.09</td><td>3.93</td><td>7.70</td><td>10.56</td></tr>
    <tr><td>UrbanGPT</td><td>3.55</td><td>6.82</td><td>8.85</td><td>4.12</td><td>8.03</td><td>10.89</td><td>5.00</td><td>9.68</td><td>14.19</td><td>4.22</td><td>8.18</td><td>11.31</td></tr>
    <tr><td>UniST</td><td>3.63</td><td>6.99</td><td>9.13</td><td>4.23</td><td>8.25</td><td>11.22</td><td>5.12</td><td>9.90</td><td>14.63</td><td>4.33</td><td>8.38</td><td>11.66</td></tr>
  </tbody>
</table>

### Performance Comparison on Cross-City Traffic Flow Prediction (Taiyuan → Fuzhou) with 7-Day Training Data

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
    <tr><td>GBRT</td><td>6.88</td><td>12.25</td><td>13.45</td><td>7.68</td><td>14.05</td><td>15.00</td><td>8.85</td><td>15.70</td><td>16.90</td><td>7.65</td><td>13.83</td><td>14.85</td></tr>
    <tr><td>VAR</td><td>6.55</td><td>11.70</td><td>12.20</td><td>7.40</td><td>12.90</td><td>13.70</td><td>8.65</td><td>14.60</td><td>16.35</td><td>7.40</td><td>13.02</td><td>13.92</td></tr>
    <tr><td>AGCRN</td><td>4.32</td><td>8.30</td><td>7.70</td><td>5.05</td><td>9.90</td><td>9.55</td><td>6.30</td><td>11.90</td><td>12.40</td><td>5.07</td><td>10.02</td><td>9.73</td></tr>
    <tr><td>AllDeepSet</td><td>2.68</td><td>5.05</td><td>7.55</td><td>3.22</td><td>6.20</td><td>9.20</td><td>4.02</td><td>7.95</td><td>12.20</td><td>3.20</td><td>6.17</td><td>9.27</td></tr>
    <tr><td>DCRNN</td><td>2.72</td><td>5.30</td><td>7.40</td><td>3.20</td><td>6.35</td><td>9.60</td><td>4.08</td><td>7.65</td><td>12.75</td><td>3.20</td><td>6.28</td><td>9.63</td></tr>
    <tr><td>DyHSL</td><td>2.55</td><td>4.88</td><td>6.85</td><td>2.95</td><td>6.05</td><td>8.85</td><td>3.72</td><td>7.40</td><td>11.50</td><td>2.99</td><td>6.05</td><td>8.83</td></tr>
    <tr><td>GRU</td><td>2.85</td><td>5.50</td><td>7.70</td><td>3.35</td><td>6.75</td><td>10.10</td><td>4.45</td><td>8.05</td><td>13.70</td><td>3.42</td><td>6.62</td><td>10.20</td></tr>
    <tr><td>GWNet</td><td>2.60</td><td>4.95</td><td>8.15</td><td>3.18</td><td>6.02</td><td>10.10</td><td>3.98</td><td>7.60</td><td>13.70</td><td>3.16</td><td>5.97</td><td>10.22</td></tr>
    <tr><td>STGCN</td><td>2.68</td><td>5.05</td><td>7.60</td><td>3.13</td><td>6.30</td><td>9.55</td><td>4.02</td><td>7.85</td><td>12.25</td><td>3.16</td><td>6.27</td><td>9.60</td></tr>
    <tr><td>STG-NCDE</td><td>2.92</td><td>5.30</td><td>6.15</td><td>3.82</td><td>7.88</td><td>8.60</td><td>5.35</td><td>10.80</td><td>12.20</td><td>3.71</td><td>7.77</td><td>8.40</td></tr>
    <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr>
    <tr><td>DASTNet</td><td>2.92</td><td>5.78</td><td>7.65</td><td>3.55</td><td>7.32</td><td>9.95</td><td>4.68</td><td>8.90</td><td>13.35</td><td>3.58</td><td>6.98</td><td>9.94</td></tr>
    <tr><td>D2MHyper</td><td><ins>2.24</ins></td><td><ins>4.28</ins></td><td>6.25</td><td><ins>2.56</ins></td><td>5.08</td><td>7.60</td><td><ins>2.93</ins></td><td>5.85</td><td>9.02</td><td><ins>2.53</ins></td><td>4.94</td><td>7.45</td></tr>
    <tr><td>DAGN</td><td>2.40</td><td>4.30</td><td><ins>5.98</ins></td><td>2.60</td><td><ins>4.88</ins></td><td><ins>7.02</ins></td><td>3.10</td><td><ins>5.72</ins></td><td><ins>8.90</ins></td><td>2.64</td><td><ins>4.91</ins></td><td><ins>7.15</ins></td></tr>
    <tr><td>ST-DAAN</td><td>2.48</td><td>4.62</td><td>6.62</td><td>2.94</td><td>5.84</td><td>8.82</td><td>3.88</td><td>7.30</td><td>12.55</td><td>3.00</td><td>5.80</td><td>8.98</td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
    <tr><td>MAML</td><td>3.18</td><td>5.85</td><td>9.75</td><td>3.82</td><td>7.10</td><td>12.25</td><td>4.92</td><td>8.36</td><td>15.80</td><td>3.86</td><td>6.98</td><td>12.28</td></tr>
    <tr><td>ST-GFSL</td><td>3.16</td><td>5.80</td><td>9.55</td><td>3.80</td><td>7.20</td><td>11.85</td><td>5.05</td><td>8.80</td><td>15.25</td><td>3.86</td><td>7.12</td><td>11.92</td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
    <tr><td>CrossST</td><td><strong>1.82</strong></td><td><strong>3.36</strong></td><td><strong>5.02</strong></td><td><strong>2.09</strong></td><td><strong>3.85</strong></td><td><strong>5.78</strong></td><td><strong>2.78</strong></td><td><strong>5.52</strong></td><td><strong>8.62</strong></td><td><strong>2.16</strong></td><td><strong>4.07</strong></td><td><strong>6.17</strong></td></tr>
    <tr><td>MTPB</td><td>2.47</td><td>4.38</td><td>6.27</td><td>2.91</td><td>5.48</td><td>8.25</td><td>3.68</td><td>6.62</td><td>10.85</td><td>2.95</td><td>5.40</td><td>8.32</td></tr>
    <tr><td>STGCN-FT</td><td>2.68</td><td>5.08</td><td>7.36</td><td>3.07</td><td>6.00</td><td>9.33</td><td>3.85</td><td>7.35</td><td>12.40</td><td>3.10</td><td>6.03</td><td>9.50</td></tr>
    <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
    <tr><td>FGITrans</td><td>2.58</td><td>4.93</td><td>9.96</td><td>3.05</td><td>5.68</td><td>11.18</td><td>3.74</td><td>6.60</td><td>12.42</td><td>3.12</td><td>5.73</td><td>11.19</td></tr>
    <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr>
    <tr><td>ST-LLM+</td><td>2.40</td><td>4.55</td><td>6.22</td><td>2.76</td><td>5.35</td><td>7.70</td><td>3.27</td><td>6.28</td><td>9.82</td><td>2.81</td><td>5.39</td><td>7.92</td></tr>
    <tr><td>UrbanGPT</td><td>2.54</td><td>4.78</td><td>6.65</td><td>2.95</td><td>5.62</td><td>8.18</td><td>3.58</td><td>6.78</td><td>10.65</td><td>3.02</td><td>5.73</td><td>8.48</td></tr>
    <tr><td>UniST</td><td>2.60</td><td>4.90</td><td>6.85</td><td>3.03</td><td>5.78</td><td>8.42</td><td>3.67</td><td>6.93</td><td>10.98</td><td>3.10</td><td>5.87</td><td>8.75</td></tr>
  </tbody>
</table>

### Performance Comparison on Cross-City Traffic Flow Prediction (Fuzhou → Taiyuan) with 7-Day Training Data

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
    <tr><td>GBRT</td><td>7.02</td><td>12.50</td><td>13.70</td><td>7.85</td><td>14.35</td><td>15.30</td><td>9.05</td><td>16.05</td><td>17.20</td><td>7.81</td><td>14.12</td><td>15.13</td></tr>
    <tr><td>VAR</td><td>6.68</td><td>11.95</td><td>12.45</td><td>7.55</td><td>13.18</td><td>13.98</td><td>8.85</td><td>14.92</td><td>16.68</td><td>7.55</td><td>13.30</td><td>14.20</td></tr>
    <tr><td>AGCRN</td><td>4.42</td><td>8.48</td><td>7.88</td><td>5.16</td><td>10.12</td><td>9.76</td><td>6.44</td><td>12.16</td><td>12.68</td><td>5.18</td><td>10.24</td><td>9.95</td></tr>
    <tr><td>AllDeepSet</td><td>2.74</td><td>5.16</td><td>7.72</td><td>3.29</td><td>6.34</td><td>9.40</td><td>4.11</td><td>8.13</td><td>12.47</td><td>3.27</td><td>6.31</td><td>9.48</td></tr>
    <tr><td>DCRNN</td><td>2.78</td><td>5.42</td><td>7.56</td><td>3.27</td><td>6.49</td><td>9.81</td><td>4.17</td><td>7.82</td><td>13.03</td><td>3.27</td><td>6.42</td><td>9.85</td></tr>
    <tr><td>DyHSL</td><td>2.60</td><td>4.99</td><td>7.00</td><td>3.01</td><td>6.18</td><td>9.05</td><td>3.80</td><td>7.56</td><td>11.76</td><td>3.06</td><td>6.18</td><td>9.04</td></tr>
    <tr><td>GRU</td><td>2.91</td><td>5.62</td><td>7.87</td><td>3.42</td><td>6.90</td><td>10.32</td><td>4.55</td><td>8.23</td><td>14.01</td><td>3.49</td><td>6.77</td><td>10.44</td></tr>
    <tr><td>GWNet</td><td>2.66</td><td>5.06</td><td>8.33</td><td>3.25</td><td>6.15</td><td>10.32</td><td>4.07</td><td>7.77</td><td>14.01</td><td>3.23</td><td>6.10</td><td>10.45</td></tr>
    <tr><td>STGCN</td><td>2.74</td><td>5.16</td><td>7.77</td><td>3.20</td><td>6.44</td><td>9.76</td><td>4.11</td><td>8.03</td><td>12.53</td><td>3.23</td><td>6.41</td><td>9.82</td></tr>
    <tr><td>STG-NCDE</td><td>2.98</td><td>5.42</td><td>6.29</td><td>3.90</td><td>8.05</td><td>8.79</td><td>5.47</td><td>11.04</td><td>12.48</td><td>3.79</td><td>7.94</td><td>8.60</td></tr>
    <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr>
    <tr><td>DASTNet</td><td>2.98</td><td>5.90</td><td>7.82</td><td>3.63</td><td>7.48</td><td>10.17</td><td>4.78</td><td>9.09</td><td>13.65</td><td>3.66</td><td>7.13</td><td>10.16</td></tr>
    <tr><td>D2MHyper</td><td>2.45</td><td>4.39</td><td><strong>5.13</strong></td><td><ins>2.62</ins></td><td><strong>3.93</strong></td><td><strong>5.91</strong></td><td><strong>2.84</strong></td><td><strong>5.64</strong></td><td><strong>8.81</strong></td><td><strong>2.21</strong></td><td><strong>4.16</strong></td><td><strong>6.30</strong></td></tr>
    <tr><td>DAGN</td><td><strong>1.86</strong></td><td><ins>4.37</ins></td><td><ins>6.11</ins></td><td>2.66</td><td><ins>4.98</ins></td><td><ins>7.18</ins></td><td>3.17</td><td><ins>5.84</ins></td><td><ins>9.10</ins></td><td>2.70</td><td><ins>5.02</ins></td><td><ins>7.31</ins></td></tr>
    <tr><td>ST-DAAN</td><td>2.53</td><td>4.72</td><td>6.77</td><td>3.00</td><td>5.97</td><td>9.02</td><td>3.97</td><td>7.46</td><td>12.83</td><td>3.07</td><td>5.93</td><td>9.19</td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
    <tr><td>MAML</td><td>3.25</td><td>5.98</td><td>9.97</td><td>3.90</td><td>7.25</td><td>12.52</td><td>5.03</td><td>8.54</td><td>16.15</td><td>3.94</td><td>7.13</td><td>12.56</td></tr>
    <tr><td>ST-GFSL</td><td>3.23</td><td>5.93</td><td>9.76</td><td>3.88</td><td>7.36</td><td>12.12</td><td>5.16</td><td>8.99</td><td>15.59</td><td>3.94</td><td>7.27</td><td>12.19</td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
    <tr><td>CrossST</td><td><ins>2.29</ins></td><td><strong>3.43</strong></td><td>6.39</td><td><strong>2.14</strong></td><td>5.19</td><td>7.77</td><td><ins>2.99</ins></td><td>5.98</td><td>9.22</td><td><ins>2.59</ins></td><td>5.05</td><td>7.62</td></tr>
    <tr><td>MTPB</td><td>2.52</td><td>4.48</td><td>6.41</td><td>2.97</td><td>5.60</td><td>8.44</td><td>3.76</td><td>6.77</td><td>11.10</td><td>3.02</td><td>5.52</td><td>8.51</td></tr>
    <tr><td>STGCN-FT</td><td>2.74</td><td>5.19</td><td>7.53</td><td>3.14</td><td>6.13</td><td>9.54</td><td>3.94</td><td>7.51</td><td>12.68</td><td>3.17</td><td>6.16</td><td>9.72</td></tr>
    <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
    <tr><td>FGITrans</td><td>2.64</td><td>5.04</td><td>10.18</td><td>3.12</td><td>5.80</td><td>11.43</td><td>3.82</td><td>6.75</td><td>12.70</td><td>3.19</td><td>5.86</td><td>11.44</td></tr>
    <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr>
    <tr><td>ST-LLM+</td><td>2.45</td><td>4.65</td><td>6.36</td><td>2.82</td><td>5.47</td><td>7.87</td><td>3.34</td><td>6.42</td><td>10.04</td><td>2.87</td><td>5.51</td><td>8.10</td></tr>
    <tr><td>UrbanGPT</td><td>2.59</td><td>4.88</td><td>6.80</td><td>3.01</td><td>5.75</td><td>8.36</td><td>3.66</td><td>6.93</td><td>10.89</td><td>3.09</td><td>5.86</td><td>8.68</td></tr>
    <tr><td>UniST</td><td>2.65</td><td>5.00</td><td>7.00</td><td>3.09</td><td>5.91</td><td>8.61</td><td>3.75</td><td>7.08</td><td>11.23</td><td>3.17</td><td>6.00</td><td>8.95</td></tr>
  </tbody>
</table>

### Performance Comparison on Cross-City Traffic Flow Prediction (NYCTaxi → CHIBike) with 7-Day Training Data

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
    <tr><td>GBRT</td><td>8.12</td><td>14.85</td><td>15.80</td><td>9.05</td><td>17.10</td><td>17.65</td><td>10.45</td><td>19.25</td><td>19.90</td><td>9.04</td><td>16.82</td><td>17.50</td></tr>
    <tr><td>VAR</td><td>7.75</td><td>14.20</td><td>14.45</td><td>8.75</td><td>15.68</td><td>16.15</td><td>10.20</td><td>17.85</td><td>19.25</td><td>8.73</td><td>15.84</td><td>16.42</td></tr>
    <tr><td>AGCRN</td><td>5.12</td><td>10.08</td><td>9.12</td><td>6.00</td><td>12.05</td><td>11.25</td><td>7.48</td><td>14.55</td><td>14.65</td><td>6.02</td><td>12.19</td><td>11.47</td></tr>
    <tr><td>AllDeepSet</td><td>3.18</td><td>6.14</td><td>8.95</td><td>3.82</td><td>7.55</td><td>10.85</td><td>4.78</td><td>9.70</td><td>14.40</td><td>3.80</td><td>7.51</td><td>10.95</td></tr>
    <tr><td>DCRNN</td><td>3.23</td><td>6.44</td><td>8.78</td><td>3.80</td><td>7.72</td><td>11.30</td><td>4.85</td><td>9.32</td><td>15.05</td><td>3.80</td><td>7.64</td><td>11.15</td></tr>
    <tr><td>DyHSL</td><td>3.03</td><td>5.93</td><td>8.12</td><td>3.50</td><td>7.35</td><td>10.45</td><td>4.42</td><td>9.00</td><td>13.58</td><td>3.56</td><td>7.36</td><td>10.42</td></tr>
    <tr><td>GRU</td><td>3.38</td><td>6.68</td><td>9.12</td><td>3.98</td><td>8.20</td><td>11.90</td><td>5.28</td><td>9.80</td><td>16.15</td><td>4.06</td><td>8.06</td><td>12.05</td></tr>
    <tr><td>GWNet</td><td>3.09</td><td>6.02</td><td>9.65</td><td>3.78</td><td>7.32</td><td>11.90</td><td>4.73</td><td>9.25</td><td>16.15</td><td>3.76</td><td>7.27</td><td>12.06</td></tr>
    <tr><td>STGCN</td><td>3.18</td><td>6.14</td><td>9.00</td><td>3.72</td><td>7.66</td><td>11.25</td><td>4.78</td><td>9.55</td><td>14.45</td><td>3.76</td><td>7.63</td><td>11.32</td></tr>
    <tr><td>STG-NCDE</td><td>3.46</td><td>6.44</td><td>7.28</td><td>4.54</td><td>9.58</td><td>10.15</td><td>6.36</td><td>13.15</td><td>14.40</td><td>4.41</td><td>9.45</td><td>9.92</td></tr>
    <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr>
    <tr><td>DASTNet</td><td>3.46</td><td>7.02</td><td>9.05</td><td>4.22</td><td>8.90</td><td>11.75</td><td>5.55</td><td>10.82</td><td>15.75</td><td>4.26</td><td>8.50</td><td>11.72</td></tr>
    <tr><td>D2MHyper</td><td>2.85</td><td><strong>4.08</strong></td><td><strong>5.95</strong></td><td>3.09</td><td><strong>4.68</strong></td><td><strong>6.85</strong></td><td><strong>3.30</strong></td><td><strong>6.71</strong></td><td><strong>10.20</strong></td><td><strong>2.56</strong></td><td><strong>4.95</strong></td><td><strong>7.30</strong></td></tr>
    <tr><td>DAGN</td><td>2.85</td><td>5.23</td><td><ins>7.08</ins></td><td><strong>2.48</strong></td><td><ins>5.93</ins></td><td><ins>8.32</ins></td><td>3.68</td><td><ins>6.95</ins></td><td><ins>10.55</ins></td><td>3.14</td><td><ins>5.98</ins></td><td><ins>8.47</ins></td></tr>
    <tr><td>ST-DAAN</td><td>2.94</td><td>5.62</td><td>7.85</td><td>3.48</td><td>7.10</td><td>10.42</td><td>4.60</td><td>8.88</td><td>14.85</td><td>3.56</td><td>7.06</td><td>10.63</td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
    <tr><td>MAML</td><td>3.77</td><td>7.11</td><td>11.55</td><td>4.53</td><td>8.63</td><td>14.48</td><td>5.84</td><td>10.16</td><td>18.65</td><td>4.58</td><td>8.50</td><td>14.52</td></tr>
    <tr><td>ST-GFSL</td><td>3.75</td><td>7.05</td><td>11.30</td><td>4.51</td><td>8.76</td><td>14.00</td><td>5.99</td><td>10.70</td><td>18.00</td><td>4.58</td><td>8.66</td><td>14.08</td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
    <tr><td>CrossST</td><td><ins>2.66</ins></td><td><ins>5.20</ins></td><td>7.40</td><td><ins>3.04</ins></td><td>6.18</td><td>9.00</td><td><ins>3.48</ins></td><td>7.12</td><td>10.68</td><td><ins>3.01</ins></td><td>6.01</td><td>8.83</td></tr>
    <tr><td>MTPB</td><td>2.93</td><td>5.33</td><td>7.43</td><td>3.46</td><td>6.66</td><td>9.78</td><td>4.37</td><td>8.05</td><td>12.85</td><td>3.51</td><td>6.57</td><td>9.85</td></tr>
    <tr><td>STGCN-FT</td><td>3.18</td><td>6.17</td><td>8.73</td><td>3.65</td><td>7.30</td><td>11.05</td><td>4.58</td><td>8.95</td><td>14.68</td><td>3.69</td><td>7.34</td><td>11.25</td></tr>
    <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
    <tr><td>FGITrans</td><td>3.06</td><td>5.99</td><td>11.80</td><td>3.62</td><td>6.90</td><td>13.25</td><td>4.44</td><td>8.02</td><td>14.72</td><td>3.71</td><td>6.97</td><td>13.25</td></tr>
    <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr>
    <tr><td>ST-LLM+</td><td><strong>2.16</strong></td><td>5.53</td><td>7.38</td><td>3.28</td><td>6.51</td><td>9.12</td><td>3.88</td><td>7.64</td><td>11.63</td><td>3.34</td><td>6.56</td><td>9.38</td></tr>
    <tr><td>UrbanGPT</td><td>3.02</td><td>5.81</td><td>7.90</td><td>3.50</td><td>6.84</td><td>9.70</td><td>4.25</td><td>8.25</td><td>12.60</td><td>3.59</td><td>6.97</td><td>10.05</td></tr>
    <tr><td>UniST</td><td>3.09</td><td>5.95</td><td>8.13</td><td>3.59</td><td>7.03</td><td>9.98</td><td>4.36</td><td>8.44</td><td>12.98</td><td>3.68</td><td>7.14</td><td>10.35</td></tr>
  </tbody>
</table>

### Performance Comparison on Cross-City Traffic Flow Prediction (CHIBike → NYCTaxi) with 7-Day Training Data

<table> <thead> <tr> <th rowspan="2">Methods (Paradigms)</th> <th colspan="3">15 min</th> <th colspan="3">30 min</th> <th colspan="3">60 min</th> <th colspan="3">Average</th> </tr> <tr> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> </tr> </thead> <tbody> <tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></strong></td></tr> <tr><td>GBRT</td><td>8.45</td><td>15.35</td><td>16.45</td><td>9.42</td><td>17.68</td><td>18.35</td><td>10.88</td><td>19.90</td><td>20.70</td><td>9.41</td><td>17.40</td><td>18.22</td></tr> <tr><td>VAR</td><td>8.05</td><td>14.68</td><td>15.05</td><td>9.10</td><td>16.22</td><td>16.80</td><td>10.62</td><td>18.45</td><td>20.02</td><td>9.09</td><td>16.38</td><td>17.08</td></tr> <tr><td>AGCRN</td><td>5.33</td><td>10.42</td><td>9.50</td><td>6.24</td><td>12.45</td><td>11.70</td><td>7.78</td><td>15.05</td><td>15.25</td><td>6.27</td><td>12.61</td><td>11.95</td></tr> <tr><td>AllDeepSet</td><td>3.31</td><td>6.35</td><td>9.32</td><td>3.98</td><td>7.80</td><td>11.30</td><td>4.97</td><td>10.02</td><td>14.98</td><td>3.96</td><td>7.77</td><td>11.40</td></tr> <tr><td>DCRNN</td><td>3.36</td><td>6.66</td><td>9.14</td><td>3.96</td><td>7.98</td><td>11.76</td><td>5.05</td><td>9.64</td><td>15.65</td><td>3.96</td><td>7.90</td><td>11.60</td></tr> <tr><td>DyHSL</td><td>3.15</td><td>6.13</td><td>8.46</td><td>3.65</td><td>7.60</td><td>10.88</td><td>4.60</td><td>9.30</td><td>14.13</td><td>3.71</td><td>7.62</td><td>10.85</td></tr> <tr><td>GRU</td><td>3.52</td><td>6.90</td><td>9.50</td><td>4.15</td><td>8.48</td><td>12.38</td><td>5.50</td><td>10.13</td><td>16.80</td><td>4.23</td><td>8.33</td><td>12.54</td></tr> <tr><td>GWNet</td><td>3.22</td><td>6.22</td><td>10.05</td><td>3.94</td><td>7.57</td><td>12.38</td><td>4.92</td><td>9.56</td><td>16.80</td><td>3.92</td><td>7.52</td><td>12.55</td></tr> <tr><td>STGCN</td><td>3.31</td><td>6.35</td><td>9.37</td><td>3.88</td><td>7.92</td><td>11.70</td><td>4.97</td><td>9.88</td><td>15.03</td><td>3.92</td><td>7.89</td><td>11.78</td></tr> <tr><td>STG-NCDE</td><td>3.60</td><td>6.66</td><td>7.58</td><td>4.72</td><td>9.90</td><td>10.56</td><td>6.62</td><td>13.59</td><td>14.98</td><td>4.59</td><td>9.78</td><td>10.33</td></tr> <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr> <tr><td>DASTNet</td><td>3.60</td><td>7.26</td><td>9.42</td><td>4.39</td><td>9.20</td><td>12.22</td><td>5.78</td><td>11.18</td><td>16.38</td><td>4.43</td><td>8.78</td><td>12.20</td></tr> <tr><td>D2MHyper</td><td><ins>2.77</ins></td><td><ins>5.38</ins></td><td>7.70</td><td><strong>2.58</strong></td><td><strong>4.84</strong></td><td><strong>7.13</strong></td><td><strong>3.43</strong></td><td><strong>6.94</strong></td><td><strong>10.62</strong></td><td><strong>2.67</strong></td><td><strong>5.12</strong></td><td><strong>7.60</strong></td></tr> <tr><td>DAGN</td><td>2.97</td><td>5.41</td><td><ins>7.37</ins></td><td>3.22</td><td><ins>6.14</ins></td><td><ins>8.66</ins></td><td><ins>3.62</ins></td><td>7.36</td><td>11.12</td><td>3.27</td><td><ins>6.19</ins></td><td><ins>8.82</ins></td></tr> <tr><td>ST-DAAN</td><td>3.06</td><td>5.81</td><td>8.17</td><td>3.62</td><td>7.34</td><td>10.85</td><td>4.79</td><td>9.18</td><td>15.45</td><td>3.71</td><td>7.30</td><td>11.06</td></tr> <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr> <tr><td>MAML</td><td>3.92</td><td>7.35</td><td>12.02</td><td>4.72</td><td>8.92</td><td>15.07</td><td>6.08</td><td>10.50</td><td>19.40</td><td>4.77</td><td>8.78</td><td>15.11</td></tr> <tr><td>ST-GFSL</td><td>3.90</td><td>7.29</td><td>11.77</td><td>4.70</td><td>9.05</td><td>14.57</td><td>6.23</td><td>11.06</td><td>18.73</td><td>4.77</td><td>8.95</td><td>14.65</td></tr> <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr> <tr><td>CrossST</td><td><strong>2.25</strong></td><td><strong>4.22</strong></td><td><strong>6.19</strong></td><td><ins>3.17</ins></td><td>6.39</td><td>9.37</td><td>3.83</td><td><ins>7.19</ins></td><td><ins>10.98</ins></td><td><ins>3.13</ins></td><td>6.22</td><td>9.19</td></tr> <tr><td>MTPB</td><td>3.05</td><td>5.51</td><td>7.73</td><td>3.60</td><td>6.89</td><td>10.18</td><td>4.55</td><td>8.33</td><td>13.38</td><td>3.66</td><td>6.80</td><td>10.25</td></tr> <tr><td>STGCN-FT</td><td>3.31</td><td>6.38</td><td>9.09</td><td>3.80</td><td>7.55</td><td>11.50</td><td>4.77</td><td>9.25</td><td>15.28</td><td>3.84</td><td>7.59</td><td>11.72</td></tr> <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr> <tr><td>FGITrans</td><td>3.19</td><td>6.20</td><td>12.28</td><td>3.77</td><td>7.14</td><td>13.79</td><td>4.62</td><td>8.30</td><td>15.32</td><td>3.86</td><td>7.21</td><td>13.79</td></tr> <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr> <tr><td>ST-LLM+</td><td>2.97</td><td>5.72</td><td>7.68</td><td>3.41</td><td>6.73</td><td>9.50</td><td>4.04</td><td>7.90</td><td>12.10</td><td>3.48</td><td>6.78</td><td>9.76</td></tr> <tr><td>UrbanGPT</td><td>3.14</td><td>6.01</td><td>8.22</td><td>3.64</td><td>7.07</td><td>10.10</td><td>4.43</td><td>8.53</td><td>13.12</td><td>3.74</td><td>7.21</td><td>10.46</td></tr> <tr><td>UniST</td><td>3.22</td><td>6.16</td><td>8.47</td><td>3.74</td><td>7.27</td><td>10.39</td><td>4.54</td><td>8.73</td><td>13.52</td><td>3.83</td><td>7.38</td><td>10.78</td></tr> </tbody> </table>

### Performance Comparison on Cross-City Traffic Flow Prediction (HZMetro → WHBT) with 7-Day Training Data

<table> <thead> <tr> <th rowspan="2">Methods (Paradigms)</th> <th colspan="3">15 min</th> <th colspan="3">30 min</th> <th colspan="3">60 min</th> <th colspan="3">Average</th> </tr> <tr> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> </tr> </thead> <tbody> <tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr> <tr><td>GBRT</td><td>9.25</td><td>17.20</td><td>18.30</td><td>10.32</td><td>19.78</td><td>20.45</td><td>11.92</td><td>22.25</td><td>23.05</td><td>10.30</td><td>19.45</td><td>20.30</td></tr> <tr><td>VAR</td><td>8.82</td><td>16.45</td><td>16.75</td><td>9.96</td><td>18.15</td><td>18.70</td><td>11.62</td><td>20.65</td><td>22.30</td><td>9.96</td><td>18.34</td><td>19.03</td></tr> <tr><td>AGCRN</td><td>5.82</td><td>11.65</td><td>10.55</td><td>6.82</td><td>13.95</td><td>13.00</td><td>8.50</td><td>16.85</td><td>16.95</td><td>6.85</td><td>14.12</td><td>13.28</td></tr> <tr><td>AllDeepSet</td><td>3.62</td><td>7.10</td><td>10.35</td><td>4.35</td><td>8.73</td><td>12.55</td><td>5.45</td><td>11.20</td><td>16.65</td><td>4.33</td><td>8.68</td><td>12.67</td></tr> <tr><td>DCRNN</td><td>3.68</td><td>7.45</td><td>10.15</td><td>4.33</td><td>8.93</td><td>13.05</td><td>5.52</td><td>10.78</td><td>17.40</td><td>4.33</td><td>8.83</td><td>13.00</td></tr> <tr><td>DyHSL</td><td>3.45</td><td>6.85</td><td>9.40</td><td>3.98</td><td>8.50</td><td>12.08</td><td>5.03</td><td>10.40</td><td>15.70</td><td>4.06</td><td>8.52</td><td>12.05</td></tr> <tr><td>GRU</td><td>3.85</td><td>7.72</td><td>10.55</td><td>4.53</td><td>9.48</td><td>13.75</td><td>6.02</td><td>11.33</td><td>18.68</td><td>4.63</td><td>9.33</td><td>13.95</td></tr> <tr><td>GWNet</td><td>3.52</td><td>6.95</td><td>11.15</td><td>4.30</td><td>8.45</td><td>13.75</td><td>5.38</td><td>10.68</td><td>18.68</td><td>4.29</td><td>8.40</td><td>13.95</td></tr> <tr><td>STGCN</td><td>3.62</td><td>7.10</td><td>10.40</td><td>4.23</td><td>8.85</td><td>13.00</td><td>5.45</td><td>11.05</td><td>16.70</td><td>4.29</td><td>8.82</td><td>13.08</td></tr> <tr><td>STG-NCDE</td><td>3.95</td><td>7.45</td><td>8.42</td><td>5.18</td><td>11.08</td><td>11.73</td><td>7.25</td><td>15.20</td><td>16.65</td><td>5.03</td><td>10.93</td><td>11.45</td></tr> <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr> <tr><td>DASTNet</td><td>3.95</td><td>8.12</td><td>10.45</td><td>4.82</td><td>10.30</td><td>13.58</td><td>6.35</td><td>12.50</td><td>18.20</td><td>4.87</td><td>9.82</td><td>13.55</td></tr> <tr><td>D2MHyper</td><td>3.25</td><td>6.05</td><td><ins>8.20</ins></td><td>3.52</td><td><ins>6.87</ins></td><td><ins>9.63</ins></td><td>4.20</td><td><ins>8.05</ins></td><td><ins>12.20</ins></td><td>3.58</td><td><ins>6.92</ins></td><td><ins>9.80</ins></td></tr> <tr><td>DAGN</td><td><ins>3.03</ins></td><td><ins>6.02</ins></td><td>8.55</td><td><ins>3.47</ins></td><td>7.15</td><td>10.40</td><td><ins>3.97</ins></td><td>8.23</td><td>12.35</td><td><ins>3.42</ins></td><td>6.95</td><td>10.20</td></tr> <tr><td>ST-DAAN</td><td>3.35</td><td>6.50</td><td>9.08</td><td>3.97</td><td>8.22</td><td>12.05</td><td>5.25</td><td>10.27</td><td>17.15</td><td>4.07</td><td>8.17</td><td>12.30</td></tr> <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr> <tr><td>MAML</td><td>4.30</td><td>8.22</td><td>13.35</td><td>5.17</td><td>9.98</td><td>16.75</td><td>6.67</td><td>11.75</td><td>21.58</td><td>5.23</td><td>9.82</td><td>16.80</td></tr> <tr><td>ST-GFSL</td><td>4.28</td><td>8.15</td><td>13.07</td><td>5.15</td><td>10.12</td><td>16.20</td><td>6.85</td><td>12.37</td><td>20.83</td><td>5.23</td><td>10.02</td><td>16.30</td></tr> <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr> <tr><td>CrossST</td><td><strong>2.46</strong></td><td><strong>4.72</strong></td><td><strong>6.88</strong></td><td><strong>2.83</strong></td><td><strong>5.42</strong></td><td><strong>7.92</strong></td><td><strong>3.77</strong></td><td><strong>7.76</strong></td><td><strong>11.80</strong></td><td><strong>2.93</strong></td><td><strong>5.73</strong></td><td><strong>8.45</strong></td></tr> <tr><td>MTPB</td><td>3.34</td><td>6.16</td><td>8.58</td><td>3.94</td><td>7.70</td><td>11.30</td><td>4.98</td><td>9.32</td><td>14.85</td><td>4.02</td><td>7.60</td><td>11.40</td></tr> <tr><td>STGCN-FT</td><td>3.62</td><td>7.14</td><td>10.08</td><td>4.16</td><td>8.45</td><td>12.77</td><td>5.22</td><td>10.35</td><td>16.98</td><td>4.21</td><td>8.50</td><td>13.00</td></tr> <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></strong></td></tr> <tr><td>FGITrans</td><td>3.48</td><td>6.93</td><td>13.65</td><td>4.12</td><td>7.98</td><td>15.32</td><td>5.06</td><td>9.28</td><td>17.03</td><td>4.22</td><td>8.06</td><td>15.33</td></tr> <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></strong></td></tr> <tr><td>ST-LLM+</td><td>3.25</span></td><td>6.40</span></td><td>8.52</span></td><td>3.74</span></td><td>7.53</span></td><td>10.55</span></td><td>4.43</span></td><td>8.83</span><td>13.45</span></td><td>3.82</span></td><td>7.58</span></td><td>10.85</span></td></tr> <tr><td>UrbanGPT</span></td><td>3.44</span></td><td>6.72</span></td><td>9.12</span></td><td>3.99</span></td><td>7.92</span></td><td>11.20</span></td><td>4.85</span></td><td>9.53</span></td><td>14.58</span></td><td>4.10</span></td><td>8.05</span></td><td>11.62</span></td></tr> <tr><td>UniST</span></td><td>3.52</span></td><td>6.88</span></td><td>9.38</span></td><td>4.10</span></td><td>8.13</span></td><td>11.53</span></td><td>4.98</span></td><td>9.75</span></td><td>15.03</span></td><td>4.20</span></td><td>8.25</span></td><td>11.98</span></td></tr> </tbody> </table>

### Performance Comparison on Cross-City Traffic Flow Prediction (WHBT → HZMetro) with 7-Day Training Data

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
    <tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></strong></td></tr>
    <tr><td>GBRT</td><td>9.45</td><td>17.55</td><td>18.68</td><td>10.55</td><td>20.20</td><td>20.88</td><td>12.18</td><td>22.72</td><td>23.55</td><td>10.52</td><td>19.87</td><td>20.73</td></tr>
    <tr><td>VAR</td><td>9.02</td><td>16.80</td><td>17.10</td><td>10.18</td><td>18.55</td><td>19.10</td><td>11.88</td><td>21.10</td><td>22.78</td><td>10.18</td><td>18.74</td><td>19.45</td></tr>
    <tr><td>AGCRN</td><td>5.95</td><td>11.90</td><td>10.78</td><td>6.98</td><td>14.25</td><td>13.28</td><td>8.70</td><td>17.22</td><td>17.32</td><td>7.00</td><td>14.43</td><td>13.56</td></tr>
    <tr><td>AllDeepSet</td><td>3.70</td><td>7.25</td><td>10.58</td><td>4.45</td><td>8.92</td><td>12.82</td><td>5.57</td><td>11.45</td><td>17.02</td><td>4.42</td><td>8.87</td><td>12.95</td></tr>
    <tr><td>DCRNN</td><td>3.76</td><td>7.60</td><td>10.38</td><td>4.43</td><td>9.12</td><td>13.33</td><td>5.65</td><td>11.02</td><td>17.78</td><td>4.42</td><td>9.03</td><td>13.28</td></tr>
    <tr><td>DyHSL</td><td>3.53</td><td>7.00</td><td>9.60</td><td>4.08</td><td>8.68</td><td>12.35</td><td>5.15</td><td>10.63</td><td>16.05</td><td>4.15</td><td>8.71</td><td>12.32</td></tr>
    <tr><td>GRU</td><td>3.94</td><td>7.88</td><td>10.78</td><td>4.63</td><td>9.68</td><td>14.05</td><td>6.15</td><td>11.58</td><td>19.10</td><td>4.73</td><td>9.53</td><td>14.26</td></tr>
    <tr><td>GWNet</td><td>3.60</td><td>7.10</td><td>11.40</td><td>4.40</td><td>8.63</td><td>14.05</td><td>5.50</td><td>10.92</td><td>19.10</td><td>4.38</td><td>8.58</td><td>14.26</td></tr>
    <tr><td>STGCN</td><td>3.70</td><td>7.25</td><td>10.63</td><td>4.33</td><td>9.05</td><td>13.28</td><td>5.57</td><td>11.30</td><td>17.07</td><td>4.38</td><td>9.02</td><td>13.36</td></tr>
    <tr><td>STG-NCDE</td><td>4.04</td><td>7.60</td><td>8.60</td><td>5.30</td><td>11.32</td><td>11.98</td><td>7.42</td><td>15.55</td><td>17.02</td><td>5.14</td><td>11.18</td><td>11.70</td></tr>
    <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></strong></span></span></td></tr>
    <tr><td>DASTNet</td><td>4.04</td><td>8.30</td><td>10.68</td><td>4.93</td><td>10.52</td><td>13.88</td><td>6.50</td><td>12.78</td><td>18.60</td><td>4.98</td><td>10.04</td><td>13.85</td></tr>
    <tr><td>D2MHyper</td><td><strong>2.52</strong></td><td><strong>4.82</strong></td><td><strong>7.03</strong></td><td><strong>2.90</strong></td><td><strong>5.54</strong></td><td><strong>8.10</strong></td><td><strong>3.86</strong></td><td><strong>7.93</strong></td><td><strong>12.06</strong></td><td><strong>3.00</strong></td><td><strong>5.86</strong></td><td><strong>8.64</strong></td></tr>
    <tr><td>DAGN</td><td><ins>3.10</ins></td><td><ins>6.15</ins></td><td>8.74</td><td><ins>3.55</ins></td><td>7.31</td><td>10.63</td><td><ins>4.06</ins></td><td>8.42</td><td>12.63</td><td><ins>3.50</ins></td><td>7.11</td><td>10.43</td></tr>
    <tr><td>ST-DAAN</td><td>3.43</td><td>6.64</td><td>9.28</td><td>4.06</td><td>8.40</td><td>12.32</td><td>5.37</td><td>10.50</td><td>17.53</td><td>4.16</td><td>8.35</td><td>12.58</td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></strong></span></span></td></tr>
    <tr><td>MAML</td><td>4.40</td><td>8.40</td><td>13.65</td><td>5.29</td><td>10.20</td><td>17.13</td><td>6.82</td><td>12.02</td><td>22.07</td><td>5.35</td><td>10.04</td><td>17.17</td></tr>
    <tr><td>ST-GFSL</td><td>4.38</td><td>8.33</td><td>13.36</td><td>5.27</td><td>10.35</td><td>16.57</td><td>7.00</td><td>12.65</td><td>21.30</td><td>5.35</td><td>10.25</td><td>16.67</td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></strong></span></span></td></tr>
    <tr><td>CrossST</td><td>3.32</td><td>6.18</td><td><ins>8.38</ins></td><td>3.60</td><td><ins>7.02</ins></td><td><ins>9.85</ins></td><td>4.30</td><td><ins>8.23</ins></td><td><ins>12.48</ins></td><td>3.66</td><td><ins>7.08</ins></td><td><ins>10.02</ins></td></tr>
    <tr><td>MTPB</td><td>3.42</td><td>6.30</td><td>8.77</td><td>4.03</td><td>7.87</td><td>11.55</td><td>5.09</td><td>9.53</td><td>15.18</td><td>4.11</td><td>7.77</td><td>11.66</td></tr>
    <tr><td>STGCN-FT</td><td>3.70</td><td>7.30</td><td>10.31</td><td>4.26</td><td>8.64</td><td>13.06</td><td>5.34</td><td>10.58</td><td>17.36</td><td>4.31</td><td>8.69</td><td>13.30</td></tr>
    <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></strong></span></span></td></tr>
    <tr><td>FGITrans</td><td>3.56</td><td>7.08</td><td>13.95</td><td>4.21</td><td>8.16</td><td>15.66</td><td>5.18</td><td>9.49</td><td>17.41</td><td>4.32</td><td>8.24</td><td>15.67</td></tr>
    <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></strong></span></span></td></tr>
    <tr><td>ST-LLM+</td><td>3.32</td><td>6.54</td><td>8.71</td><td>3.82</td><td>7.70</td><td>10.78</td><td>4.53</td><td>9.03</td><td>13.75</td><td>3.90</td><td>7.75</td><td>11.10</td></tr>
    <tr><td>UrbanGPT</td><td>3.52</td><td>6.87</td><td>9.32</td><td>4.08</td><td>8.10</td><td>11.45</td><td>4.96</td><td>9.75</td><td>14.90</td><td>4.19</td><td>8.23</td><td>11.88</td></tr>
    <tr><td>UniST</td><td>3.60</td><td>7.04</td><td>9.59</td><td>4.19</td><td>8.32</td><td>11.79</td><td>5.09</td><td>9.97</td><td>15.36</td><td>4.30</td><td>8.44</td><td>12.24</td></tr>
  </tbody>
</table>

### Performance Comparison on Cross-City Traffic Index Prediction (Didi-Chengdu → Didi-Shenzhen) with 7-Day Training Data

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
    <tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></strong></td></tr>
    <tr><td>GBRT</span></td><td>10.65</span></td><td>19.80</span></td><td>21.10</span></td><td>11.88</span></td><td>22.78</span></td><td>23.55</span></td><td>13.72</span></td><td>25.62</span></td><td>26.55</span></td><td>11.86</span></td><td>22.40</span></td><td>23.38</span></td></tr>
    <tr><td>VAR</span></td><td>10.15</span></td><td>18.95</span></td><td>19.30</span></td><td>11.47</span></td><td>20.92</span></td><td>21.55</span></td><td>13.38</span></td><td>23.78</span></td><td>25.68</span></td><td>11.72</span></td><td>21.12</span></td><td>21.93</span></td></tr>
    <tr><td>AGCRN</span></td><td>6.70</span></td><td>13.42</span></td><td>12.15</span></td><td>7.85</span></td><td>16.05</span></td><td>14.98</span></td><td>9.80</span></td><td>19.40</span></td><td>19.52</span></td><td>7.88</span></td><td>16.26</span></td><td>15.28</span></td></tr>
    <tr><td>AllDeepSet</span></td><td>4.17</span></td><td>8.18</span></td><td>11.92</span></td><td>5.01</span></td><td>10.05</span></td><td>14.45</span></td><td>6.27</span></td><td>12.90</span></td><td>19.18</span></td><td>4.99</span></td><td>10.00</span></td><td>14.60</span></td></tr>
    <tr><td>DCRNN</span></td><td>4.24</span></td><td>8.58</span></td><td>11.68</span></td><td>4.98</span></td><td>10.28</span></td><td>15.03</span></td><td>6.35</span></td><td>12.42</span></td><td>20.03</span></td><td>4.99</span></td><td>10.18</span></td><td>14.98</span></td></tr>
    <tr><td>DyHSL</span></td><td>3.97</span></td><td>7.89</span></td><td>10.82</span></td><td>4.58</span></td><td>9.78</span></td><td>13.92</span></td><td>5.80</span></td><td>11.98</span></td><td>18.08</span></td><td>4.68</span></td><td>9.82</span></td><td>13.88</span></td></tr>
    <tr><td>GRU</span></td><td>4.44</span></td><td>8.89</span></td><td>12.15</span></td><td>5.22</span></td><td>10.92</span></td><td>15.83</span></td><td>6.93</span></td><td>13.05</span></td><td>21.50</span></td><td>5.33</span></td><td>10.75</span></td><td>16.05</span></td></tr>
    <tr><td>GWNet</span></td><td>4.05</span></td><td>8.01</span></td><td>12.85</span></td><td>4.95</span></td><td>9.73</span></td><td>15.83</span></td><td>6.20</span></td><td>12.30</span></td><td>21.50</span></td><td>4.94</span></td><td>9.68</span></td><td>16.05</span></td></tr>
    <tr><td>STGCN</span></td><td>4.17</span></td><td>8.18</span></td><td>11.98</span></td><td>4.88</span></td><td>10.20</span><td>14.98</span></td><td>6.27</span></td><td>12.72</span></td><td>19.23</span></td><td>4.94</span></td><td>10.18</span></td><td>15.05</span></td></tr>
    <tr><td>STG-NCDE</span></td><td>4.55</span></td><td>8.58</span></td><td>9.70</span></td><td>5.96</span></td><td>12.75</span></td><td>13.52</span></td><td>8.35</span></td><td>17.50</span></td><td>19.18</span></td><td>5.79</span></td><td>12.58</span></td><td>13.18</span></td></tr>
    <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></strong></span></td></tr>
    <tr><td>DASTNet</span></td><td>4.55</span></td><td>9.35</span></td><td>12.05</span></td><td>5.55</span></td><td>11.85</span></td><td>15.65</span></td><td>7.30</span></td><td>14.40</span></td><td>20.98</span></td><td>5.60</span></td><td>11.32</span></td><td>15.62</span></td></tr>
    <tr><td>D2MHyper</span></td><td><strong>2.84</strong></span></td><td>6.97</span></td><td><strong>7.93</strong></span></td><td><strong>3.27</strong></span></td><td><ins>7.92</ins></span></td><td><ins>11.10</ins></span></td><td><strong>4.35</strong></span></td><td><strong>8.94</strong></span></td><td><strong>13.60</strong></span></td><td><strong>3.38</strong></span></td><td><strong>6.60</strong></span></td><td><strong>9.74</strong></span></td></tr>
    <tr><td>DAGN</span></td><td>3.74</span></td><td><strong>5.44</strong></span></td><td><ins>9.45</ins></span></td><td><ins>4.06</ins></span></td><td><strong>6.24</strong></span></td><td><strong>9.13</strong></span></td><td>4.84</span></td><td><ins>9.28</ins></span></td><td><ins>14.07</ins></span></td><td>4.12</span></td><td><ins>7.98</ins></span></td><td><ins>11.30</ins></span></td></tr>
    <tr><td>ST-DAAN</span></td><td>3.86</span></td><td>7.49</span></td><td>10.47</span></td><td>4.57</span></td><td>9.47</span></td><td>13.90</span></td><td>6.05</span></td><td>11.83</span></td><td>19.78</span></td><td>4.69</span></td><td>9.42</span></td><td>14.18</span></td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></strong></span></span></td></tr>
    <tr><td>MAML</span></td><td>4.95</span></td><td>9.47</span></td><td>15.38</span></td><td>5.95</span></td><td>11.50</span></td><td>19.30</span></td><td>7.68</span></td><td>13.53</span></td><td>24.85</span></td><td>6.03</span></td><td>11.32</span></td><td>19.35</span></td></tr>
    <tr><td>ST-GFSL</span></td><td>4.93</span></td><td>9.39</span></td><td>15.05</span></td><td>5.93</span></td><td>11.66</span></td><td>18.67</span></td><td>7.88</span></td><td>14.25</span></td><td>23.98</span></td><td>6.03</span></td><td>11.55</span></td><td>18.77</span></td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></strong></span></span></td></tr>
    <tr><td>CrossST</span></td><td><ins>3.49</ins></span></td><td><ins>6.93</ins></span></td><td>9.85</span></td><td>3.99</span></td><td>8.23</span></td><td>11.98</span></td><td><ins>4.57</ins></span></td><td>9.48</span></td><td>14.23</span></td><td><ins>3.94</ins></span></td><td>8.01</span></td><td>11.75</span></td></tr>
    <tr><td>MTPB</span></td><td>3.85</span></td><td>7.10</span></td><td>9.88</span></td><td>4.54</span></td><td>8.87</span></td><td>13.02</span></td><td>5.73</span></td><td>10.73</span></td><td>17.10</span></td><td>4.63</span></td><td>8.76</span></td><td>13.13</span></td></tr>
    <tr><td>STGCN-FT</span></td><td>4.17</span></td><td>8.22</span></td><td>11.62</span></td><td>4.79</span></td><td>9.73</span></td><td>14.72</span></td><td>6.02</span></td><td>11.92</span></td><td>19.55</span></td><td>4.85</span></td><td>9.80</span></td><td>14.98</span></td></tr>
    <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></strong></span></span></td></tr>
    <tr><td>FGITrans</span></td><td>4.01</span></td><td>7.98</span></td><td>15.72</span></td><td>4.75</span></td><td>9.19</span></td><td>17.65</span></td><td>5.83</span></td><td>10.68</span></td><td>19.62</span></td><td>4.86</span></td><td>9.28</span></td><td>17.66</span></td></tr>
    <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></strong></span></span></td></tr>
    <tr><td>ST-LLM+</span></td><td>3.74</span></td><td>7.37</span></td><td>9.82</span></td><td>4.30</span></td><td>8.67</span></td><td>12.15</span></td><td>5.10</span></td><td>10.18</span></td><td>15.50</span></td><td>4.39</span></td><td>8.73</span></td><td>12.50</span></td></tr>
    <tr><td>UrbanGPT</span></td><td>3.96</span></td><td>7.74</span></td><td>10.50</span></td><td>4.60</span></td><td>9.12</span></td><td>12.90</span></td><td>5.58</span></td><td>10.98</span></td><td>16.80</span></td><td>4.72</span></td><td>9.28</span></td><td>13.38</span></td></tr>
    <tr><td>UniST</span></td><td>4.05</span></td><td>7.93</span></td><td>10.80</span></td><td>4.72</span></td><td>9.37</span></td><td>13.28</span></td><td>5.73</span></td><td>11.23</span></td><td>17.32</span></td><td>4.84</span></td><td>9.51</span></td><td>13.80</span></td></tr>
  </tbody>
</table>

### Performance Comparison on Cross-City Traffic Index Prediction (Didi-Shenzhen → Didi-Chengdu) with 7-Day Training Data

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
    <tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></strong></td></tr>
    <tr><td>GBRT</span></td><td>10.88</span></td><td>20.22</span></td><td>21.55</span></td><td>12.15</span></td><td>23.28</span></td><td>24.05</span></td><td>14.02</span></td><td>26.18</span></td><td>27.12</span></td><td>12.12</span></td><td>22.88</span></td><td>23.88</span></td></tr>
    <tr><td>VAR</span></td><td>10.38</span></td><td>19.35</span></td><td>19.72</span></td><td>11.72</span></td><td>21.38</span></td><td>22.02</span></td><td>13.68</span></td><td>24.30</span></td><td>26.23</span></td><td>11.98</span></td><td>21.58</span></td><td>22.40</span></td></tr>
    <tr><td>AGCRN</span></td><td>6.85</span></td><td>13.70</span></td><td>12.42</span></td><td>8.03</span></td><td>16.40</span></td><td>15.30</span></td><td>10.02</span></td><td>19.83</span></td><td>19.94</span></td><td>8.06</span></td><td>16.62</span></td><td>15.62</span></td></tr>
    <tr><td>AllDeepSet</span></td><td>4.26</span></td><td>8.35</span></td><td>12.18</span></td><td>5.12</span></td><td>10.27</span></td><td>14.77</span></td><td>6.41</span></td><td>13.18</span></td><td>19.60</span></td><td>5.10</span></td><td>10.22</span></td><td>14.92</span></td></tr>
    <tr><td>DCRNN</span></td><td>4.33</span></td><td>8.76</span></td><td>11.94</span></td><td>5.09</span></td><td>10.51</span></td><td>15.36</span></td><td>6.49</span></td><td>12.69</span></td><td>20.47</span></td><td>5.10</span></td><td>10.40</span></td><td>15.30</span></td></tr>
    <tr><td>DyHSL</span></td><td>4.06</span></td><td>8.06</span></td><td>11.06</span></td><td>4.68</span></td><td>10.00</span></td><td>14.23</span></td><td>5.93</span></td><td>12.24</span></td><td>18.48</span></td><td>4.78</span></td><td>10.04</span></td><td>14.18</span></td></tr>
    <tr><td>GRU</span></td><td>4.53</span></td><td>9.08</span></td><td>12.42</span></td><td>5.33</span></td><td>11.16</span></td><td>16.18</span></td><td>7.08</span></td><td>13.34</span></td><td>21.97</span></td><td>5.45</span></td><td>10.99</span></td><td>16.40</span></td></tr>
    <tr><td>GWNet</span></td><td>4.14</span></td><td>8.18</span></td><td>13.13</span></td><td>5.06</span></td><td>9.94</span></td><td>16.18</span></td><td>6.34</span></td><td>12.57</span></td><td>21.97</span></td><td>5.05</span></td><td>9.89</span></td><td>16.40</span></td></tr>
    <tr><td>STGCN</span></td><td>4.26</span></td><td>8.35</span></td><td>12.24</span></td><td>4.98</span></td><td>10.42</span></td><td>15.30</span></td><td>6.41</span></td><td>13.00</span></td><td>19.65</span></td><td>5.05</span></td><td>10.40</span></td><td>15.37</span></td></tr>
    <tr><td>STG-NCDE</span></td><td>4.65</span></td><td>8.76</span></td><td>9.91</span></td><td>6.09</span></td><td>13.03</span></td><td>13.82</span></td><td>8.54</span></td><td>17.88</span></td><td>19.60</span></td><td>5.92</span></td><td>12.86</span></td><td>13.47</span></td></tr>
    <tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></strong></span></span></td></tr>
    <tr><td>DASTNet</span></td><td>4.65</span></td><td>9.55</span></td><td>12.32</span></td><td>5.67</span></td><td>12.11</span></td><td>15.99</span></td><td>7.46</span></td><td>14.72</span></td><td>21.44</span></td><td>5.73</span></td><td>11.57</span></td><td>15.96</span></td></tr>
    <tr><td>D2MHyper</span></td><td><strong>2.90</strong></span></td><td><strong>5.56</strong></span></td><td><strong>8.10</strong></span></td><td><strong>3.34</strong></span></td><td><strong>6.38</strong></span></td><td><strong>9.33</strong></span></td><td><strong>4.45</strong></span></td><td><strong>9.14</strong></span></td><td><strong>13.90</strong></span></td><td><strong>3.46</strong></span></td><td><strong>6.75</strong></span></td><td><strong>9.95</strong></span></td></tr>
    <tr><td>DAGN</span></td><td><ins>3.57</ins></span></td><td><ins>7.08</ins></span></td><td><ins>9.66</ins></span></td><td>4.15</span></td><td><ins>8.09</ins></span></td><td><ins>11.34</ins></span></td><td>4.95</span><td>9.69</span></td><td><ins>14.38</ins></span></td><td>4.21</span></td><td><ins>8.16</ins></span></td><td><ins>11.55</ins></span></td></tr>
    <tr><td>ST-DAAN</span></td><td>3.94</span></td><td>7.65</span></td><td>10.70</span></td><td>4.67</span></td><td>9.68</span></td><td>14.20</span></td><td>6.18</span></td><td>12.09</span></td><td>20.22</span></td><td>4.79</span></td><td>9.63</span></td><td>14.49</span></td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></strong></span></span></span></td></tr>
    <tr><td>MAML</span></td><td>5.06</span></td><td>9.67</span></td><td>15.72</span></td><td>6.08</span></td><td>11.75</span></td><td>19.73</span></td><td>7.85</span></td><td>13.83</span></td><td>25.40</span></td><td>6.16</span></td><td>11.57</span></td><td>19.78</span></td></tr>
    <tr><td>ST-GFSL</span></td><td>5.04</span></td><td>9.59</span></td><td>15.38</span></td><td>6.06</span></td><td>11.92</span></td><td>19.08</span></td><td>8.05</span></td><td>14.57</span></td><td>24.52</span></td><td>6.16</span></td><td>11.81</span></td><td>19.18</span></td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></strong> </span></span></span></td></tr>
    <tr><td>CrossST</span></td><td>3.82</span></td><td>7.12</span></td><td>10.07</span></td><td><ins>4.08</ins></span></td><td>8.41</span></td><td>12.25</span></td><td><ins>4.67</ins></span></td><td><ins>9.48</ins></span></td><td>14.55</span></td><td><ins>4.03</ins></span></td><td>8.19</span></td><td>12.02</span></td></tr>
    <tr><td>MTPB</span></td><td>3.93</span></td><td>7.25</span></td><td>10.10</span></td><td>4.64</span></td><td>9.06</span></td><td>13.31</span></td><td>5.86</span></td><td>10.97</span></td><td>17.48</span></td><td>4.73</span></td><td>8.96</span></td><td>13.42</span></td></tr>
    <tr><td>STGCN-FT</span></td><td>4.26</span></td><td>8.40</span></td><td>11.88</span></td><td>4.90</span></td><td>9.95</span></td><td>15.04</span></td><td>6.15</span></td><td>12.18</span></td><td>19.99</span></td><td>4.96</span></td><td>10.02</span></td><td>15.31</span></td></tr>
    <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></strong> </span></span></span></span></td></tr>
    <tr><td>FGITrans</span></td><td>4.10</span></td><td>8.15</span></td><td>16.07</span></td><td>4.85</span></td><td>9.39</span></td><td>18.04</span></td><td>5.96</span></td><td>10.92</span></td><td>20.05</span></td><td>4.97</span></td><td>9.49</span></td><td>18.05</span></td></tr>
    <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></strong> </span></span></span></span></span></td></tr>
    <tr><td>ST-LLM+</span></td><td>3.82</span></td><td>7.53</span></td><td>10.03</span></td><td>4.40</span></td><td>8.86</span></td><td>12.42</span></td><td>5.21</span></td><td>10.40</span></td><td>15.85</span></td><td>4.49</span></td><td>8.93</span></td><td>12.78</span></td></tr>
    <tr><td>UrbanGPT</span></td><td>4.05</span></td><td>7.91</span></td><td>10.73</span></td><td>4.70</span></td><td>9.32</span></td><td>13.18</span></td><td>5.71</span></td><td>11.22</span></td><td>17.18</span></td><td>4.82</span></td><td>9.49</span></td><td>13.68</span></td></tr>
    <tr><td>UniST</span></td><td>4.14</span></td><td>8.10</span></td><td>11.04</span></td><td>4.83</span></td><td>9.57</span></td><td>13.57</span></td><td>5.86</span></td><td>11.48</span></td><td>17.71</span></td><td>4.94</span></td><td>9.72</span></td><td>14.10</span></td></tr>
  </tbody>
</table>

## ⚙️ Computational Cost and Reproducibility Support

Since our benchmark includes **23 methods from six paradigms**, fully retraining every model on all cross-city traffic forecasting datasets can be computationally expensive, especially for small-scale systems.  
To reduce the reproduction burden, we provide the following resources whenever applicable:

- **Pre-trained weights**
- **Pre-processed train/validation/test splits**
- **Lightweight evaluation mode**
- **Selective benchmarking**, so users only need to reproduce methods relevant to their own setting

> **Notes**
> - **Pre-trained weights**: users can directly load released checkpoints instead of retraining from scratch.  
> - **Pre-processed splits**: users can reuse the same standardized train/validation/test partitions as in our benchmark.  
> - **Lightweight evaluation mode**: users can evaluate a trained model on a single GPU without running the full training pipeline.  
> - The computational cost below refers to the **cost of full retraining**, while the **actual reproduction burden is substantially reduced** by the provided resources.

---

## 📊 Method-Level Computational Cost and Reproducibility Table

| Paradigm | Method | Full Retraining Cost | Pre-trained Weights | Pre-processed Splits | Lightweight Evaluation Mode | Practical Reproduction Burden | Remarks |
|---|---|---|---|---|---|---|---|
| **Single-Domain Models (Paradigm 1)** | GBRT | Low | ✅ | ✅ | ✅ | Very Low | Classical machine learning baseline, fast to verify |
|  | VAR | Low | ✅ | ✅ | ✅ | Very Low | Statistical baseline with minimal computational overhead |
|  | AGCRN | Medium | ✅ | ✅ | ✅ | Low | Adaptive graph learning adds moderate training cost |
|  | AllDeepSet | Medium | ✅ | ✅ | ✅ | Low | Standard deep model with manageable runtime |
|  | DCRNN | Medium | ✅ | ✅ | ✅ | Low | Recurrent diffusion structure increases training time |
|  | DyHSL | Medium | ✅ | ✅ | ✅ | Low | Hidden structure learning adds moderate overhead |
|  | GRU | Low | ✅ | ✅ | ✅ | Very Low | Simple recurrent baseline, efficient to reproduce |
|  | GWNet | Medium | ✅ | ✅ | ✅ | Low | Widely used spatio-temporal baseline |
|  | STGCN | Medium | ✅ | ✅ | ✅ | Low | Stable and relatively efficient graph baseline |
|  | STG-NCDE | High | ✅ | ✅ | ✅ | Medium | Differential-equation-based optimization is heavier |
| **Alignment-Based Transfer (Paradigm 2)** | DASTNet | Medium | ✅ | ✅ | ✅ | Low | Transfer alignment introduces moderate additional cost |
|  | D2MHyper | High | ✅ | ✅ | ✅ | Medium | Hyper-network/domain alignment makes retraining heavier |
|  | DAGN | Medium | ✅ | ✅ | ✅ | Low | Transfer-aware graph modeling with manageable evaluation |
|  | ST-DAAN | High | ✅ | ✅ | ✅ | Medium | Adversarial adaptation is more expensive to retrain |
| **Meta-Learning-Based Transfer (Paradigm 3)** | MAML | Very High | ✅ | ✅ | ✅ | Medium | Meta-train/meta-test loops are costly, but evaluation is lightweight |
|  | ST-GFSL | Very High | ✅ | ✅ | ✅ | Medium | Few-shot/meta-learning pipeline is expensive to retrain |
| **Pre-Training-Based Transfer (Paradigm 4)** | CrossST | High | ✅ | ✅ | ✅ | Low | Pre-training is expensive, but fine-tuning/evaluation is much easier |
|  | MTPB | High | ✅ | ✅ | ✅ | Medium | Multi-stage transfer training increases total runtime |
|  | STGCN-FT | Medium | ✅ | ✅ | ✅ | Low | Fine-tuning from a pre-trained backbone is relatively efficient |
| **Knowledge-Distillation-Based Transfer (Paradigm 5)** | FGITrans | High | ✅ | ✅ | ✅ | Medium | Teacher-student training is expensive, but released checkpoints reduce burden |
| **Foundation Models / LLM-Based Transfer (Paradigm 6)** | ST-LLM+ | Very High | ✅ | ✅ | ✅ | Medium | LLM-based transfer is expensive to train, but evaluation is feasible on a single GPU |
|  | UrbanGPT | Very High | ✅ | ✅ | ✅ | High | Foundation-model adaptation has the highest overall retraining cost |
|  | UniST | High | ✅ | ✅ | ✅ | Medium | Unified large-scale transfer framework with relatively heavy optimization |

---

## 📈 Paradigm-Level Summary

| Paradigm | Representative Cost | Pre-trained Weights | Pre-processed Splits | Lightweight Evaluation Mode | Practical Recommendation |
|---|---|---|---|---|---|
| Single-Domain Models (Paradigm 1) | Low to Medium | ✅ | ✅ | ✅ | Suitable for quick verification and small systems |
| Alignment-Based Transfer (Paradigm 2) | Medium to High | ✅ | ✅ | ✅ | Good trade-off between transfer ability and reproduction burden |
| Meta-Learning-Based Transfer (Paradigm 3) | Very High | ✅ | ✅ | ✅ | Expensive to retrain from scratch; recommended to use released checkpoints |
| Pre-Training-Based Transfer (Paradigm 4) | Medium to High | ✅ | ✅ | ✅ | Pre-training is costly, but downstream evaluation is efficient |
| Knowledge-Distillation-Based Transfer (Paradigm 5) | High | ✅ | ✅ | ✅ | Distillation adds training cost; checkpoints substantially reduce reproduction burden |
| Foundation Models / LLM-Based Transfer (Paradigm 6) | High to Very High | ✅ | ✅ | ✅ | Most resource-demanding in full training, but still evaluable in lightweight mode |

---

## 🧭 Recommended Usage Under Limited Resources

| Scenario | Recommended Strategy |
|---|---|
| Very limited compute budget | Directly run **lightweight evaluation** using released checkpoints |
| Limited GPU memory / training time | Use **pre-trained weights + pre-processed splits** and reproduce only selected methods |
| Need representative baselines | Start from **GRU, STGCN, DCRNN, GWNet, DASTNet, CrossST** |
| Need full benchmark comparison | Reuse our released artifacts instead of retraining all methods from scratch |

---

## 🔓 Released Resources

To make the benchmark reproducible without requiring full retraining of all 23 methods, we release:

- **Pre-trained weights** for all benchmarked methods
- **Pre-processed train/validation/test splits**
- **Lightweight evaluation scripts** for quick verification
- **Standardized benchmark pipeline** for selective reproduction

Therefore, users do **not** need to retrain every method from scratch.  
Instead, they can **directly evaluate relevant methods on a single GPU within hours** in most cases.

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

**Note：** Empirical thresholds are derived from systematic experiments. Leave-one-city-out validation on 6 unseen pairs shows the recommended paradigm achieves top-2 accuracy in 83% of cases.

<table>
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
      <td align="left">
      Large distribution shift
      <img src="https://latex.codecogs.com/svg.latex?(\Delta\mathcal{M}_{\text{shift}}%20%3E%2025\%)" alt="(Delta M shift > 25%)">
      </td>
      <td align="left">Optimal accuracy</td>
      <td align="left">Alignment</td>
      <td align="left">D2MHyper</td>
      <td align="left">Needs source data; Unstable training</td>
      <td align="left">
        High
        <img src="https://latex.codecogs.com/svg.latex?\Delta\mathcal{M}_{\text{shift}}" alt="Delta M shift">
        (Figure 4(b))
      </td>
    </tr>
    <tr>
      <td align="left">
        Extreme data scarcity<br>
        (target training days &lt; 3)
      </td>
      <td align="left">Fast adaptation</td>
      <td align="left">Meta-learning</td>
      <td align="left">ST-GFSL</td>
      <td align="left">High meta-training cost; Task-sensitive</td>
      <td align="left">
        High latency (Figure 3);<br>
        Robustness (Section 4.2.2)
      </td>
    </tr>
    <tr>
      <td align="left">Multi-source data available</td>
      <td align="left">Zero-shot robustness</td>
      <td align="left">Pre-training</td>
      <td align="left">CrossST</td>
      <td align="left">High pre-training resource cost</td>
      <td align="left">
        High memory use (Figure 3);<br>
        Robustness (Section 4.2.2)
      </td>
    </tr>
    <tr>
      <td align="left">
        Deployment efficiency critical<br>
        (latency &lt; 0.5s)
      </td>
      <td align="left">Efficient inference</td>
      <td align="left">Distillation</td>
      <td align="left">FGITrans</td>
      <td align="left">Teacher-dependent</td>
      <td align="left">Low latency, small size (Figure 3)</td>
    </tr>
    <tr>
      <td align="left">
        Privacy constraints<br>
        (no data sharing)
      </td>
      <td align="left">Privacy-preserving performance</td>
      <td align="left">Federated learning</td>
      <td align="left">FedCTPM</td>
      <td align="left">Communication cost; Utility gap</td>
      <td align="left">
        Communication overhead and
        <img src="https://latex.codecogs.com/svg.latex?\mathcal{G}_{\text{util}}" alt="G_util">
        (Section 4.2.4)
      </td>
    </tr>
    <tr>
      <td align="left">
        Ample resources<br>
        (high compute budget)
      </td>
      <td align="left">Competitive zero-shot accuracy</td>
      <td align="left">Foundation model<br>(zero-shot/fine-tune)</td>
      <td align="left">ST-LLM+, UrbanGPT, UniST</td>
      <td align="left">5–10× higher latency;<br>10–20× larger GPU memory</td>
      <td align="left">
        MAE 16.71–17.89 vs. CrossST 16.25<br>
        (PeMS03→PeMS08)
      </td>
    </tr>
  </tbody>
</table>
