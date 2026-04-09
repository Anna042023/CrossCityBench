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

### PeMS08 → PeMS03

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
    <tr><td>D2MHyper</td><td><ins>16.10</ins></td><td><ins>24.20</ins></td><td><ins>12.60</ins></td><td><ins>17.85</ins></td><td><ins>27.05</ins></td><td><ins>13.35</ins></td><td><ins>22.70</ins></td><td>34.50</td><td><ins>17.55</ins></td><td><ins>18.42</ins></td><td><ins>27.90</ins></td><td><ins>14.12</ins></td></tr>
    <tr><td>DAGN</td><td>17.68</td><td>25.30</td><td>13.20</td><td>18.60</td><td>27.70</td><td>14.70</td><td>22.85</td><td>35.05</td><td>18.05</td><td>19.28</td><td>28.85</td><td>15.28</td></tr>
    <tr><td>ST-DAAN</td><td>19.25</td><td>28.20</td><td>12.90</td><td>23.05</td><td>34.05</td><td>15.90</td><td>30.55</td><td>44.80</td><td>20.65</td><td>23.55</td><td>34.68</td><td>15.98</td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
    <tr><td>MAML</td><td>21.15</td><td>29.50</td><td>20.30</td><td>25.40</td><td>34.70</td><td>26.20</td><td>34.00</td><td>45.60</td><td>38.10</td><td>26.05</td><td>35.60</td><td>27.40</td></tr>
    <tr><td>ST-GFSL</td><td>20.65</td><td>29.20</td><td>16.80</td><td>24.50</td><td>34.15</td><td>20.50</td><td>31.60</td><td>43.80</td><td>28.80</td><td>24.85</td><td>34.72</td><td>21.20</td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
    <tr><td>CrossST</td><td><strong>14.38</strong></td><td><strong>22.50</strong></td><td><strong>9.25</strong></td><td><strong>15.40</strong></td><td><strong>24.35</strong></td><td><strong>10.10</strong></td><td><strong>17.05</strong></td><td><strong>26.80</strong></td><td><strong>11.10</strong></td><td><strong>15.42</strong></td><td><strong>24.22</strong></td><td><strong>10.05</strong></td></tr>
    <tr><td>MTPB</td><td>23.00</td><td>32.70</td><td>15.90</td><td>25.35</td><td>35.80</td><td>16.25</td><td>28.85</td><td>41.00</td><td>19.20</td><td>25.65</td><td>36.50</td><td>16.93</td></tr>
    <tr><td>STGCN-FT</td><td>19.00</td><td>28.05</td><td>14.68</td><td>21.95</td><td>32.35</td><td>17.65</td><td>27.90</td><td>40.40</td><td>21.05</td><td>22.95</td><td>33.75</td><td>17.59</td></tr>
    <tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr>
    <tr><td>FGITrans</td><td>15.35</td><td>29.20</td><td>19.85</td><td>15.45</td><td>29.50</td><td>19.90</td><td>15.65</td><td>30.05</td><td>20.05</td><td>15.48</td><td>29.58</td><td>19.93</td></tr>
    <tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr>
    <tr><td>ST-LLM+</td><td>16.60</td><td>25.60</td><td>13.20</td><td>18.05</td><td>28.05</td><td>14.45</td><td>21.60</td><td><ins>32.80</ins></td><td>17.60</td><td>18.75</td><td>28.82</td><td>15.08</td></tr>
    <tr><td>UrbanGPT</td><td>18.35</td><td>27.85</td><td>14.45</td><td>20.75</td><td>31.45</td><td>15.90</td><td>25.70</td><td>38.95</td><td>19.80</td><td>21.60</td><td>32.75</td><td>16.72</td></tr>
    <tr><td>UniST</td><td>19.10</td><td>28.85</td><td>14.90</td><td>21.70</td><td>32.80</td><td>16.55</td><td>26.85</td><td>40.40</td><td>20.55</td><td>22.55</td><td>34.02</td><td>17.33</td></tr>
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

### METR-LA → PeMS-BAY

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
    <tr><td>DAGN</td><td><ins>3.35</ins></td><td><ins>6.12</ins></td><td><ins>7.95</ins></td><td><ins>3.62</ins></td><td><ins>6.95</ins></td><td><ins>9.35</ins></td><td><ins>4.32</ins></td><td><ins>8.15</ins></td><td><ins>11.85</ins></td><td><ins>3.67</ins></td><td><ins>6.99</ins></td><td><ins>9.50</ins></td></tr>
    <tr><td>ST-DAAN</td><td>3.48</td><td>6.58</td><td>8.82</td><td>4.12</td><td>8.32</td><td>11.75</td><td>5.45</td><td>10.42</td><td>16.75</td><td>4.20</td><td>8.28</td><td>11.98</td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
    <tr><td>MAML</td><td>4.45</td><td>8.35</td><td>13.00</td><td>5.35</td><td>10.15</td><td>16.35</td><td>6.90</td><td>11.95</td><td>21.05</td><td>5.40</td><td>9.97</td><td>16.38</td></tr>
    <tr><td>ST-GFSL</td><td>4.42</td><td>8.27</td><td>12.70</td><td>5.33</td><td>10.28</td><td>15.78</td><td>7.05</td><td>12.55</td><td>20.35</td><td>5.40</td><td>10.17</td><td>15.90</td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
    <tr><td>CrossST</td><td>3.13</td><td>6.10</td><td>8.33</td><td>3.58</td><td>7.24</td><td>10.12</td><td>4.09</td><td>8.34</td><td>12.02</td><td>3.53</td><td>7.04</td><td>9.92</td></tr>
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

### Taiyuan → Fuzhou

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
    <tr><td>D2MHyper</td><td><strong>1.82</strong></td><td><strong>3.36</strong></td><td><strong>5.02</strong></td><td><strong>2.09</strong></td><td><strong>3.85</strong></td><td><strong>5.78</strong></td><td><strong>2.78</strong></td><td><strong>5.52</strong></td><td><strong>8.62</strong></td><td><strong>2.16</strong></td><td><strong>4.07</strong></td><td><strong>6.17</strong></td></tr>
    <tr><td>DAGN</td><td><ins>2.40</ins></td><td><ins>4.30</ins></td><td><ins>5.98</ins></td><td><ins>2.60</ins></td><td><ins>4.88</ins></td><td><ins>7.02</ins></td><td><ins>3.10</ins></td><td><ins>5.72</ins></td><td><ins>8.90</ins></td><td><ins>2.64</ins></td><td><ins>4.91</ins></td><td><ins>7.15</ins></td></tr>
    <tr><td>ST-DAAN</td><td>2.48</td><td>4.62</td><td>6.62</td><td>2.94</td><td>5.84</td><td>8.82</td><td>3.88</td><td>7.30</td><td>12.55</td><td>3.00</td><td>5.80</td><td>8.98</td></tr>
    <tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr>
    <tr><td>MAML</td><td>3.18</td><td>5.85</td><td>9.75</td><td>3.82</td><td>7.10</td><td>12.25</td><td>4.92</td><td>8.36</td><td>15.80</td><td>3.86</td><td>6.98</td><td>12.28</td></tr>
    <tr><td>ST-GFSL</td><td>3.16</td><td>5.80</td><td>9.55</td><td>3.80</td><td>7.20</td><td>11.85</td><td>5.05</td><td>8.80</td><td>15.25</td><td>3.86</td><td>7.12</td><td>11.92</td></tr>
    <tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr>
    <tr><td>CrossST</td><td>2.24</td><td>4.28</td><td>6.25</td><td>2.56</td><td>5.08</td><td>7.60</td><td>2.93</td><td>5.85</td><td>9.02</td><td>2.53</td><td>4.94</td><td>7.45</td></tr>
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

### Fuzhou → Taiyuan

<table> <thead> <tr> <th rowspan="2">Methods (Paradigms)</th> <th colspan="3">15 min</th> <th colspan="3">30 min</th> <th colspan="3">60 min</th> <th colspan="3">Average</th> </tr> <tr> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> </tr> </thead> <tbody><tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr> <tr><td>GBRT</td><td>7.02</td><td>12.50</td><td>13.70</td><td>7.85</td><td>14.35</td><td>15.30</td><td>9.05</td><td>16.05</td><td>17.20</td><td>7.81</td><td>14.12</td><td>15.13</td></tr> <tr><td>VAR</td><td>6.68</td><td>11.95</td><td>12.45</td><td>7.55</td><td>13.18</td><td>13.98</td><td>8.85</td><td>14.92</td><td>16.68</td><td>7.55</td><td>13.30</td><td>14.20</td></tr> <tr><td>AGCRN</td><td>4.42</td><td>8.48</td><td>7.88</td><td>5.16</td><td>10.12</td><td>9.76</td><td>6.44</td><td>12.16</td><td>12.68</td><td>5.18</td><td>10.24</td><td>9.95</td></tr> <tr><td>AllDeepSet</td><td>2.74</td><td>5.16</td><td>7.72</td><td>3.29</td><td>6.34</td><td>9.40</td><td>4.11</td><td>8.13</td><td>12.47</td><td>3.27</td><td>6.31</td><td>9.48</td></tr> <tr><td>DCRNN</td><td>2.78</td><td>5.42</td><td>7.56</td><td>3.27</td><td>6.49</td><td>9.81</td><td>4.17</td><td>7.82</td><td>13.03</td><td>3.27</td><td>6.42</td><td>9.85</td></tr> <tr><td>DyHSL</td><td>2.60</td><td>4.99</td><td>7.00</td><td>3.01</td><td>6.18</td><td>9.05</td><td>3.80</td><td>7.56</td><td>11.76</td><td>3.06</td><td>6.18</td><td>9.04</td></tr> <tr><td>GRU</td><td>2.91</td><td>5.62</td><td>7.87</td><td>3.42</td><td>6.90</td><td>10.32</td><td>4.55</td><td>8.23</td><td>14.01</td><td>3.49</td><td>6.77</td><td>10.44</td></tr> <tr><td>GWNet</td><td>2.66</td><td>5.06</td><td>8.33</td><td>3.25</td><td>6.15</td><td>10.32</td><td>4.07</td><td>7.77</td><td>14.01</td><td>3.23</td><td>6.10</td><td>10.45</td></tr> <tr><td>STGCN</td><td>2.74</td><td>5.16</td><td>7.77</td><td>3.20</td><td>6.44</td><td>9.76</td><td>4.11</td><td>8.03</td><td>12.53</td><td>3.23</td><td>6.41</td><td>9.82</td></tr> <tr><td>STG-NCDE</td><td>2.98</td><td>5.42</td><td>6.29</td><td>3.90</td><td>8.05</td><td>8.79</td><td>5.47</td><td>11.04</td><td>12.48</td><td>3.79</td><td>7.94</td><td>8.60</td></tr><tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr> <tr><td>DASTNet</td><td>2.98</td><td>5.90</td><td>7.82</td><td>3.63</td><td>7.48</td><td>10.17</td><td>4.78</td><td>9.09</td><td>13.65</td><td>3.66</td><td>7.13</td><td>10.16</td></tr> <tr><td>D2MHyper</td><td><strong>1.86</strong></td><td><strong>3.43</strong></td><td><strong>5.13</strong></td><td><strong>2.14</strong></td><td><strong>3.93</strong></td><td><strong>5.91</strong></td><td><strong>2.84</strong></td><td><strong>5.64</strong></td><td><strong>8.81</strong></td><td><strong>2.21</strong></td><td><strong>4.16</strong></td><td><strong>6.30</strong></td></tr> <tr><td>DAGN</td><td><ins>2.45</ins></td><td><ins>4.39</ins></td><td><ins>6.11</ins></td><td><ins>2.66</ins></td><td><ins>4.98</ins></td><td><ins>7.18</ins></td><td><ins>3.17</ins></td><td><ins>5.84</ins></td><td><ins>9.10</ins></td><td><ins>2.70</ins></td><td><ins>5.02</ins></td><td><ins>7.31</ins></td></tr> <tr><td>ST-DAAN</td><td>2.53</td><td>4.72</td><td>6.77</td><td>3.00</td><td>5.97</td><td>9.02</td><td>3.97</td><td>7.46</td><td>12.83</td><td>3.07</td><td>5.93</td><td>9.19</td></tr><tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr> <tr><td>MAML</td><td>3.25</td><td>5.98</td><td>9.97</td><td>3.90</td><td>7.25</td><td>12.52</td><td>5.03</td><td>8.54</td><td>16.15</td><td>3.94</td><td>7.13</td><td>12.56</td></tr> <tr><td>ST-GFSL</td><td>3.23</td><td>5.93</td><td>9.76</td><td>3.88</td><td>7.36</td><td>12.12</td><td>5.16</td><td>8.99</td><td>15.59</td><td>3.94</td><td>7.27</td><td>12.19</td></tr><tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr> <tr><td>CrossST</td><td>2.29</td><td>4.37</td><td>6.39</td><td>2.62</td><td>5.19</td><td>7.77</td><td>2.99</td><td>5.98</td><td>9.22</td><td>2.59</td><td>5.05</td><td>7.62</td></tr> <tr><td>MTPB</td><td>2.52</td><td>4.48</td><td>6.41</td><td>2.97</td><td>5.60</td><td>8.44</td><td>3.76</td><td>6.77</td><td>11.10</td><td>3.02</td><td>5.52</td><td>8.51</td></tr> <tr><td>STGCN-FT</td><td>2.74</td><td>5.19</td><td>7.53</td><td>3.14</td><td>6.13</td><td>9.54</td><td>3.94</td><td>7.51</td><td>12.68</td><td>3.17</td><td>6.16</td><td>9.72</td></tr><tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr> <tr><td>FGITrans</td><td>2.64</td><td>5.04</td><td>10.18</td><td>3.12</td><td>5.80</td><td>11.43</td><td>3.82</td><td>6.75</td><td>12.70</td><td>3.19</td><td>5.86</td><td>11.44</td></tr><tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr> <tr><td>ST-LLM+</td><td>2.45</td><td>4.65</td><td>6.36</td><td>2.82</td><td>5.47</td><td>7.87</td><td>3.34</td><td>6.42</td><td>10.04</td><td>2.87</td><td>5.51</td><td>8.10</td></tr> <tr><td>UrbanGPT</td><td>2.59</td><td>4.88</td><td>6.80</td><td>3.01</td><td>5.75</td><td>8.36</td><td>3.66</td><td>6.93</td><td>10.89</td><td>3.09</td><td>5.86</td><td>8.68</td></tr> <tr><td>UniST</td><td>2.65</td><td>5.00</td><td>7.00</td><td>3.09</td><td>5.91</td><td>8.61</td><td>3.75</td><td>7.08</td><td>11.23</td><td>3.17</td><td>6.00</td><td>8.95</td></tr></tbody> </table>

### NYCTaxi → CHIBike

<table> <thead> <tr> <th rowspan="2">Methods (Paradigms)</th> <th colspan="3">15 min</th> <th colspan="3">30 min</th> <th colspan="3">60 min</th> <th colspan="3">Average</th> </tr> <tr> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> </tr> </thead> <tbody><tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr> <tr><td>GBRT</td><td>8.12</td><td>14.85</td><td>15.80</td><td>9.05</td><td>17.10</td><td>17.65</td><td>10.45</td><td>19.25</td><td>19.90</td><td>9.04</td><td>16.82</td><td>17.50</td></tr> <tr><td>VAR</td><td>7.75</td><td>14.20</td><td>14.45</td><td>8.75</td><td>15.68</td><td>16.15</td><td>10.20</td><td>17.85</td><td>19.25</td><td>8.73</td><td>15.84</td><td>16.42</td></tr> <tr><td>AGCRN</td><td>5.12</td><td>10.08</td><td>9.12</td><td>6.00</td><td>12.05</td><td>11.25</td><td>7.48</td><td>14.55</td><td>14.65</td><td>6.02</td><td>12.19</td><td>11.47</td></tr> <tr><td>AllDeepSet</td><td>3.18</td><td>6.14</td><td>8.95</td><td>3.82</td><td>7.55</td><td>10.85</td><td>4.78</td><td>9.70</td><td>14.40</td><td>3.80</td><td>7.51</td><td>10.95</td></tr> <tr><td>DCRNN</td><td>3.23</td><td>6.44</td><td>8.78</td><td>3.80</td><td>7.72</td><td>11.30</td><td>4.85</td><td>9.32</td><td>15.05</td><td>3.80</td><td>7.64</td><td>11.15</td></tr> <tr><td>DyHSL</td><td>3.03</td><td>5.93</td><td>8.12</td><td>3.50</td><td>7.35</td><td>10.45</td><td>4.42</td><td>9.00</td><td>13.58</td><td>3.56</td><td>7.36</td><td>10.42</td></tr> <tr><td>GRU</td><td>3.38</td><td>6.68</td><td>9.12</td><td>3.98</td><td>8.20</td><td>11.90</td><td>5.28</td><td>9.80</td><td>16.15</td><td>4.06</td><td>8.06</td><td>12.05</td></tr> <tr><td>GWNet</td><td>3.09</td><td>6.02</td><td>9.65</td><td>3.78</td><td>7.32</td><td>11.90</td><td>4.73</td><td>9.25</td><td>16.15</td><td>3.76</td><td>7.27</td><td>12.06</td></tr> <tr><td>STGCN</td><td>3.18</td><td>6.14</td><td>9.00</td><td>3.72</td><td>7.66</td><td>11.25</td><td>4.78</td><td>9.55</td><td>14.45</td><td>3.76</td><td>7.63</td><td>11.32</td></tr> <tr><td>STG-NCDE</td><td>3.46</td><td>6.44</td><td>7.28</td><td>4.54</td><td>9.58</td><td>10.15</td><td>6.36</td><td>13.15</td><td>14.40</td><td>4.41</td><td>9.45</td><td>9.92</td></tr><tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr> <tr><td>DASTNet</td><td>3.46</td><td>7.02</td><td>9.05</td><td>4.22</td><td>8.90</td><td>11.75</td><td>5.55</td><td>10.82</td><td>15.75</td><td>4.26</td><td>8.50</td><td>11.72</td></tr> <tr><td>D2MHyper</td><td><strong>2.16</strong></td><td><strong>4.08</strong></td><td><strong>5.95</strong></td><td><strong>2.48</strong></td><td><strong>4.68</strong></td><td><strong>6.85</strong></td><td><strong>3.30</strong></td><td><strong>6.71</strong></td><td><strong>10.20</strong></td><td><strong>2.56</strong></td><td><strong>4.95</strong></td><td><strong>7.30</strong></td></tr> <tr><td>DAGN</td><td><ins>2.85</ins></td><td><ins>5.23</ins></td><td><ins>7.08</ins></td><td><ins>3.09</ins></td><td><ins>5.93</ins></td><td><ins>8.32</ins></td><td><ins>3.68</ins></td><td><ins>6.95</ins></td><td><ins>10.55</ins></td><td><ins>3.14</ins></td><td><ins>5.98</ins></td><td><ins>8.47</ins></td></tr> <tr><td>ST-DAAN</td><td>2.94</td><td>5.62</td><td>7.85</td><td>3.48</td><td>7.10</td><td>10.42</td><td>4.60</td><td>8.88</td><td>14.85</td><td>3.56</td><td>7.06</td><td>10.63</td></tr><tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr> <tr><td>MAML</td><td>3.77</td><td>7.11</td><td>11.55</td><td>4.53</td><td>8.63</td><td>14.48</td><td>5.84</td><td>10.16</td><td>18.65</td><td>4.58</td><td>8.50</td><td>14.52</td></tr> <tr><td>ST-GFSL</td><td>3.75</td><td>7.05</td><td>11.30</td><td>4.51</td><td>8.76</td><td>14.00</td><td>5.99</td><td>10.70</td><td>18.00</td><td>4.58</td><td>8.66</td><td>14.08</td></tr><tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr> <tr><td>CrossST</td><td>2.66</td><td>5.20</td><td>7.40</td><td>3.04</td><td>6.18</td><td>9.00</td><td>3.48</td><td>7.12</td><td>10.68</td><td>3.01</td><td>6.01</td><td>8.83</td></tr> <tr><td>MTPB</td><td>2.93</td><td>5.33</td><td>7.43</td><td>3.46</td><td>6.66</td><td>9.78</td><td>4.37</td><td>8.05</td><td>12.85</td><td>3.51</td><td>6.57</td><td>9.85</td></tr> <tr><td>STGCN-FT</td><td>3.18</td><td>6.17</td><td>8.73</td><td>3.65</td><td>7.30</td><td>11.05</td><td>4.58</td><td>8.95</td><td>14.68</td><td>3.69</td><td>7.34</td><td>11.25</td></tr><tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr> <tr><td>FGITrans</td><td>3.06</td><td>5.99</td><td>11.80</td><td>3.62</td><td>6.90</td><td>13.25</td><td>4.44</td><td>8.02</td><td>14.72</td><td>3.71</td><td>6.97</td><td>13.25</td></tr><tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr> <tr><td>ST-LLM+</td><td>2.85</td><td>5.53</td><td>7.38</td><td>3.28</td><td>6.51</td><td>9.12</td><td>3.88</td><td>7.64</td><td>11.63</td><td>3.34</td><td>6.56</td><td>9.38</td></tr> <tr><td>UrbanGPT</td><td>3.02</td><td>5.81</td><td>7.90</td><td>3.50</td><td>6.84</td><td>9.70</td><td>4.25</td><td>8.25</td><td>12.60</td><td>3.59</td><td>6.97</td><td>10.05</td></tr> <tr><td>UniST</td><td>3.09</td><td>5.95</td><td>8.13</td><td>3.59</td><td>7.03</td><td>9.98</td><td>4.36</td><td>8.44</td><td>12.98</td><td>3.68</td><td>7.14</td><td>10.35</td></tr></tbody> </table>

### CHIBike → NYCTaxi

<table> <thead> <tr> <th rowspan="2">Methods (Paradigms)</th> <th colspan="3">15 min</th> <th colspan="3">30 min</th> <th colspan="3">60 min</th> <th colspan="3">Average</th> </tr> <tr> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> </tr> </thead> <tbody><tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr> <tr><td>GBRT</td><td>8.45</td><td>15.35</td><td>16.45</td><td>9.42</td><td>17.68</td><td>18.35</td><td>10.88</td><td>19.90</td><td>20.70</td><td>9.41</td><td>17.40</td><td>18.22</td></tr> <tr><td>VAR</td><td>8.05</td><td>14.68</td><td>15.05</td><td>9.10</td><td>16.22</td><td>16.80</td><td>10.62</td><td>18.45</td><td>20.02</td><td>9.09</td><td>16.38</td><td>17.08</td></tr> <tr><td>AGCRN</td><td>5.33</td><td>10.42</td><td>9.50</td><td>6.24</td><td>12.45</td><td>11.70</td><td>7.78</td><td>15.05</td><td>15.25</td><td>6.27</td><td>12.61</td><td>11.95</td></tr> <tr><td>AllDeepSet</td><td>3.31</td><td>6.35</td><td>9.32</td><td>3.98</td><td>7.80</td><td>11.30</td><td>4.97</td><td>10.02</td><td>14.98</td><td>3.96</td><td>7.77</td><td>11.40</td></tr> <tr><td>DCRNN</td><td>3.36</td><td>6.66</td><td>9.14</td><td>3.96</td><td>7.98</td><td>11.76</td><td>5.05</td><td>9.64</td><td>15.65</td><td>3.96</td><td>7.90</td><td>11.60</td></tr> <tr><td>DyHSL</td><td>3.15</td><td>6.13</td><td>8.46</td><td>3.65</td><td>7.60</td><td>10.88</td><td>4.60</td><td>9.30</td><td>14.13</td><td>3.71</td><td>7.62</td><td>10.85</td></tr> <tr><td>GRU</td><td>3.52</td><td>6.90</td><td>9.50</td><td>4.15</td><td>8.48</td><td>12.38</td><td>5.50</td><td>10.13</td><td>16.80</td><td>4.23</td><td>8.33</td><td>12.54</td></tr> <tr><td>GWNet</td><td>3.22</td><td>6.22</td><td>10.05</td><td>3.94</td><td>7.57</td><td>12.38</td><td>4.92</td><td>9.56</td><td>16.80</td><td>3.92</td><td>7.52</td><td>12.55</td></tr> <tr><td>STGCN</td><td>3.31</td><td>6.35</td><td>9.37</td><td>3.88</td><td>7.92</td><td>11.70</td><td>4.97</td><td>9.88</td><td>15.03</td><td>3.92</td><td>7.89</td><td>11.78</td></tr> <tr><td>STG-NCDE</td><td>3.60</td><td>6.66</td><td>7.58</td><td>4.72</td><td>9.90</td><td>10.56</td><td>6.62</td><td>13.59</td><td>14.98</td><td>4.59</td><td>9.78</td><td>10.33</td></tr><tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr> <tr><td>DASTNet</td><td>3.60</td><td>7.26</td><td>9.42</td><td>4.39</td><td>9.20</td><td>12.22</td><td>5.78</td><td>11.18</td><td>16.38</td><td>4.43</td><td>8.78</td><td>12.20</td></tr> <tr><td>D2MHyper</td><td><strong>2.25</strong></td><td><strong>4.22</strong></td><td><strong>6.19</strong></td><td><strong>2.58</strong></td><td><strong>4.84</strong></td><td><strong>7.13</strong></td><td><strong>3.43</strong></td><td><strong>6.94</strong></td><td><strong>10.62</strong></td><td><strong>2.67</strong></td><td><strong>5.12</strong></td><td><strong>7.60</strong></td></tr> <tr><td>DAGN</td><td><ins>2.97</ins></td><td><ins>5.41</ins></td><td><ins>7.37</ins></td><td><ins>3.22</ins></td><td><ins>6.14</ins></td><td><ins>8.66</ins></td><td><ins>3.83</ins></td><td><ins>7.19</ins></td><td><ins>10.98</ins></td><td><ins>3.27</ins></td><td><ins>6.19</ins></td><td><ins>8.82</ins></td></tr> <tr><td>ST-DAAN</td><td>3.06</td><td>5.81</td><td>8.17</td><td>3.62</td><td>7.34</td><td>10.85</td><td>4.79</td><td>9.18</td><td>15.45</td><td>3.71</td><td>7.30</td><td>11.06</td></tr><tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr> <tr><td>MAML</td><td>3.92</td><td>7.35</td><td>12.02</td><td>4.72</td><td>8.92</td><td>15.07</td><td>6.08</td><td>10.50</td><td>19.40</td><td>4.77</td><td>8.78</td><td>15.11</td></tr> <tr><td>ST-GFSL</td><td>3.90</td><td>7.29</td><td>11.77</td><td>4.70</td><td>9.05</td><td>14.57</td><td>6.23</td><td>11.06</td><td>18.73</td><td>4.77</td><td>8.95</td><td>14.65</td></tr><tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr> <tr><td>CrossST</td><td>2.77</td><td>5.38</td><td>7.70</td><td>3.17</td><td>6.39</td><td>9.37</td><td>3.62</td><td>7.36</td><td>11.12</td><td>3.13</td><td>6.22</td><td>9.19</td></tr> <tr><td>MTPB</td><td>3.05</td><td>5.51</td><td>7.73</td><td>3.60</td><td>6.89</td><td>10.18</td><td>4.55</td><td>8.33</td><td>13.38</td><td>3.66</td><td>6.80</td><td>10.25</td></tr> <tr><td>STGCN-FT</td><td>3.31</td><td>6.38</td><td>9.09</td><td>3.80</td><td>7.55</td><td>11.50</td><td>4.77</td><td>9.25</td><td>15.28</td><td>3.84</td><td>7.59</td><td>11.72</td></tr><tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr> <tr><td>FGITrans</td><td>3.19</td><td>6.20</td><td>12.28</td><td>3.77</td><td>7.14</td><td>13.79</td><td>4.62</td><td>8.30</td><td>15.32</td><td>3.86</td><td>7.21</td><td>13.79</td></tr><tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr> <tr><td>ST-LLM+</td><td>2.97</td><td>5.72</td><td>7.68</td><td>3.41</td><td>6.73</td><td>9.50</td><td>4.04</td><td>7.90</td><td>12.10</td><td>3.48</td><td>6.78</td><td>9.76</td></tr> <tr><td>UrbanGPT</td><td>3.14</td><td>6.01</td><td>8.22</td><td>3.64</td><td>7.07</td><td>10.10</td><td>4.43</td><td>8.53</td><td>13.12</td><td>3.74</td><td>7.21</td><td>10.46</td></tr> <tr><td>UniST</td><td>3.22</td><td>6.16</td><td>8.47</td><td>3.74</td><td>7.27</td><td>10.39</td><td>4.54</td><td>8.73</td><td>13.52</td><td>3.83</td><td>7.38</td><td>10.78</td></tr></tbody> </table>

### HZMetro → WHBT

<table> <thead> <tr> <th rowspan="2">Methods (Paradigms)</th> <th colspan="3">15 min</th> <th colspan="3">30 min</th> <th colspan="3">60 min</th> <th colspan="3">Average</th> </tr> <tr> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> </tr> </thead> <tbody><tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr> <tr><td>GBRT</td><td>9.25</td><td>17.20</td><td>18.30</td><td>10.32</td><td>19.78</td><td>20.45</td><td>11.92</td><td>22.25</td><td>23.05</td><td>10.30</td><td>19.45</td><td>20.30</td></tr> <tr><td>VAR</td><td>8.82</td><td>16.45</td><td>16.75</td><td>9.96</td><td>18.15</td><td>18.70</td><td>11.62</td><td>20.65</td><td>22.30</td><td>9.96</td><td>18.34</td><td>19.03</td></tr> <tr><td>AGCRN</td><td>5.82</td><td>11.65</td><td>10.55</td><td>6.82</td><td>13.95</td><td>13.00</td><td>8.50</td><td>16.85</td><td>16.95</td><td>6.85</td><td>14.12</td><td>13.28</td></tr> <tr><td>AllDeepSet</td><td>3.62</td><td>7.10</td><td>10.35</td><td>4.35</td><td>8.73</td><td>12.55</td><td>5.45</td><td>11.20</td><td>16.65</td><td>4.33</td><td>8.68</td><td>12.67</td></tr> <tr><td>DCRNN</td><td>3.68</td><td>7.45</td><td>10.15</td><td>4.33</td><td>8.93</td><td>13.05</td><td>5.52</td><td>10.78</td><td>17.40</td><td>4.33</td><td>8.83</td><td>13.00</td></tr> <tr><td>DyHSL</td><td>3.45</td><td>6.85</td><td>9.40</td><td>3.98</td><td>8.50</td><td>12.08</td><td>5.03</td><td>10.40</td><td>15.70</td><td>4.06</td><td>8.52</td><td>12.05</td></tr> <tr><td>GRU</td><td>3.85</td><td>7.72</td><td>10.55</td><td>4.53</td><td>9.48</td><td>13.75</td><td>6.02</td><td>11.33</td><td>18.68</td><td>4.63</td><td>9.33</td><td>13.95</td></tr> <tr><td>GWNet</td><td>3.52</td><td>6.95</td><td>11.15</td><td>4.30</td><td>8.45</td><td>13.75</td><td>5.38</td><td>10.68</td><td>18.68</td><td>4.29</td><td>8.40</td><td>13.95</td></tr> <tr><td>STGCN</td><td>3.62</td><td>7.10</td><td>10.40</td><td>4.23</td><td>8.85</td><td>13.00</td><td>5.45</td><td>11.05</td><td>16.70</td><td>4.29</td><td>8.82</td><td>13.08</td></tr> <tr><td>STG-NCDE</td><td>3.95</td><td>7.45</td><td>8.42</td><td>5.18</td><td>11.08</td><td>11.73</td><td>7.25</td><td>15.20</td><td>16.65</td><td>5.03</td><td>10.93</td><td>11.45</td></tr><tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr> <tr><td>DASTNet</td><td>3.95</td><td>8.12</td><td>10.45</td><td>4.82</td><td>10.30</td><td>13.58</td><td>6.35</td><td>12.50</td><td>18.20</td><td>4.87</td><td>9.82</td><td>13.55</td></tr> <tr><td>D2MHyper</td><td><strong>2.46</strong></td><td><strong>4.72</strong></td><td><strong>6.88</strong></td><td><strong>2.83</strong></td><td><strong>5.42</strong></td><td><strong>7.92</strong></td><td><strong>3.77</strong></td><td><strong>7.76</strong></td><td><strong>11.80</strong></td><td><strong>2.93</strong></td><td><strong>5.73</strong></td><td><strong>8.45</strong></td></tr> <tr><td>DAGN</td><td><ins>3.25</ins></td><td><ins>6.05</ins></td><td><ins>8.20</ins></td><td><ins>3.52</ins></td><td><ins>6.87</ins></td><td><ins>9.63</ins></td><td><ins>4.20</ins></td><td><ins>8.05</ins></td><td><ins>12.20</ins></td><td><ins>3.58</ins></td><td><ins>6.92</ins></td><td><ins>9.80</ins></td></tr> <tr><td>ST-DAAN</td><td>3.35</td><td>6.50</td><td>9.08</td><td>3.97</td><td>8.22</td><td>12.05</td><td>5.25</td><td>10.27</td><td>17.15</td><td>4.07</td><td>8.17</td><td>12.30</td></tr><tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr> <tr><td>MAML</td><td>4.30</td><td>8.22</td><td>13.35</td><td>5.17</td><td>9.98</td><td>16.75</td><td>6.67</td><td>11.75</td><td>21.58</td><td>5.23</td><td>9.82</td><td>16.80</td></tr> <tr><td>ST-GFSL</td><td>4.28</td><td>8.15</td><td>13.07</td><td>5.15</td><td>10.12</td><td>16.20</td><td>6.85</td><td>12.37</td><td>20.83</td><td>5.23</td><td>10.02</td><td>16.30</td></tr><tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr> <tr><td>CrossST</td><td>3.03</td><td>6.02</td><td>8.55</td><td>3.47</td><td>7.15</td><td>10.40</td><td>3.97</td><td>8.23</td><td>12.35</td><td>3.42</td><td>6.95</td><td>10.20</td></tr> <tr><td>MTPB</td><td>3.34</td><td>6.16</td><td>8.58</td><td>3.94</td><td>7.70</td><td>11.30</td><td>4.98</td><td>9.32</td><td>14.85</td><td>4.02</td><td>7.60</td><td>11.40</td></tr> <tr><td>STGCN-FT</td><td>3.62</td><td>7.14</td><td>10.08</td><td>4.16</td><td>8.45</td><td>12.77</td><td>5.22</td><td>10.35</td><td>16.98</td><td>4.21</td><td>8.50</td><td>13.00</td></tr><tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr> <tr><td>FGITrans</td><td>3.48</td><td>6.93</td><td>13.65</td><td>4.12</td><td>7.98</td><td>15.32</td><td>5.06</td><td>9.28</td><td>17.03</td><td>4.22</td><td>8.06</td><td>15.33</td></tr><tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr> <tr><td>ST-LLM+</td><td>3.25</td><td>6.40</td><td>8.52</td><td>3.74</td><td>7.53</td><td>10.55</td><td>4.43</td><td>8.83</td><td>13.45</td><td>3.82</td><td>7.58</td><td>10.85</td></tr> <tr><td>UrbanGPT</td><td>3.44</td><td>6.72</td><td>9.12</td><td>3.99</td><td>7.92</td><td>11.20</td><td>4.85</td><td>9.53</td><td>14.58</td><td>4.10</td><td>8.05</td><td>11.62</td></tr> <tr><td>UniST</td><td>3.52</td><td>6.88</td><td>9.38</td><td>4.10</td><td>8.13</td><td>11.53</td><td>4.98</td><td>9.75</td><td>15.03</td><td>4.20</td><td>8.25</td><td>11.98</td></tr></tbody> </table>

### WHBT → HZMetro

<table> <thead> <tr> <th rowspan="2">Methods (Paradigms)</th> <th colspan="3">15 min</th> <th colspan="3">30 min</th> <th colspan="3">60 min</th> <th colspan="3">Average</th> </tr> <tr> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> </tr> </thead> <tbody><tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr> <tr><td>GBRT</td><td>9.45</td><td>17.55</td><td>18.68</td><td>10.55</td><td>20.20</td><td>20.88</td><td>12.18</td><td>22.72</td><td>23.55</td><td>10.52</td><td>19.87</td><td>20.73</td></tr> <tr><td>VAR</td><td>9.02</td><td>16.80</td><td>17.10</td><td>10.18</td><td>18.55</td><td>19.10</td><td>11.88</td><td>21.10</td><td>22.78</td><td>10.18</td><td>18.74</td><td>19.45</td></tr> <tr><td>AGCRN</td><td>5.95</td><td>11.90</td><td>10.78</td><td>6.98</td><td>14.25</td><td>13.28</td><td>8.70</td><td>17.22</td><td>17.32</td><td>7.00</td><td>14.43</td><td>13.56</td></tr> <tr><td>AllDeepSet</td><td>3.70</td><td>7.25</td><td>10.58</td><td>4.45</td><td>8.92</td><td>12.82</td><td>5.57</td><td>11.45</td><td>17.02</td><td>4.42</td><td>8.87</td><td>12.95</td></tr> <tr><td>DCRNN</td><td>3.76</td><td>7.60</td><td>10.38</td><td>4.43</td><td>9.12</td><td>13.33</td><td>5.65</td><td>11.02</td><td>17.78</td><td>4.42</td><td>9.03</td><td>13.28</td></tr> <tr><td>DyHSL</td><td>3.53</td><td>7.00</td><td>9.60</td><td>4.08</td><td>8.68</td><td>12.35</td><td>5.15</td><td>10.63</td><td>16.05</td><td>4.15</td><td>8.71</td><td>12.32</td></tr> <tr><td>GRU</td><td>3.94</td><td>7.88</td><td>10.78</td><td>4.63</td><td>9.68</td><td>14.05</td><td>6.15</td><td>11.58</td><td>19.10</td><td>4.73</td><td>9.53</td><td>14.26</td></tr> <tr><td>GWNet</td><td>3.60</td><td>7.10</td><td>11.40</td><td>4.40</td><td>8.63</td><td>14.05</td><td>5.50</td><td>10.92</td><td>19.10</td><td>4.38</td><td>8.58</td><td>14.26</td></tr> <tr><td>STGCN</td><td>3.70</td><td>7.25</td><td>10.63</td><td>4.33</td><td>9.05</td><td>13.28</td><td>5.57</td><td>11.30</td><td>17.07</td><td>4.38</td><td>9.02</td><td>13.36</td></tr> <tr><td>STG-NCDE</td><td>4.04</td><td>7.60</td><td>8.60</td><td>5.30</td><td>11.32</td><td>11.98</td><td>7.42</td><td>15.55</td><td>17.02</td><td>5.14</td><td>11.18</td><td>11.70</td></tr><tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr> <tr><td>DASTNet</td><td>4.04</td><td>8.30</td><td>10.68</td><td>4.93</td><td>10.52</td><td>13.88</td><td>6.50</td><td>12.78</td><td>18.60</td><td>4.98</td><td>10.04</td><td>13.85</td></tr> <tr><td>D2MHyper</td><td><strong>2.52</strong></td><td><strong>4.82</strong></td><td><strong>7.03</strong></td><td><strong>2.90</strong></td><td><strong>5.54</strong></td><td><strong>8.10</strong></td><td><strong>3.86</strong></td><td><strong>7.93</strong></td><td><strong>12.06</strong></td><td><strong>3.00</strong></td><td><strong>5.86</strong></td><td><strong>8.64</strong></td></tr> <tr><td>DAGN</td><td><ins>3.32</ins></td><td><ins>6.18</ins></td><td><ins>8.38</ins></td><td><ins>3.60</ins></td><td><ins>7.02</ins></td><td><ins>9.85</ins></td><td><ins>4.30</ins></td><td><ins>8.23</ins></td><td><ins>12.48</ins></td><td><ins>3.66</ins></td><td><ins>7.08</ins></td><td><ins>10.02</ins></td></tr> <tr><td>ST-DAAN</td><td>3.43</td><td>6.64</td><td>9.28</td><td>4.06</td><td>8.40</td><td>12.32</td><td>5.37</td><td>10.50</td><td>17.53</td><td>4.16</td><td>8.35</td><td>12.58</td></tr><tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr> <tr><td>MAML</td><td>4.40</td><td>8.40</td><td>13.65</td><td>5.29</td><td>10.20</td><td>17.13</td><td>6.82</td><td>12.02</td><td>22.07</td><td>5.35</td><td>10.04</td><td>17.17</td></tr> <tr><td>ST-GFSL</td><td>4.38</td><td>8.33</td><td>13.36</td><td>5.27</td><td>10.35</td><td>16.57</td><td>7.00</td><td>12.65</td><td>21.30</td><td>5.35</td><td>10.25</td><td>16.67</td></tr><tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr> <tr><td>CrossST</td><td>3.10</td><td>6.15</td><td>8.74</td><td>3.55</td><td>7.31</td><td>10.63</td><td>4.06</td><td>8.42</td><td>12.63</td><td>3.50</td><td>7.11</td><td>10.43</td></tr> <tr><td>MTPB</td><td>3.42</td><td>6.30</td><td>8.77</td><td>4.03</td><td>7.87</td><td>11.55</td><td>5.09</td><td>9.53</td><td>15.18</td><td>4.11</td><td>7.77</td><td>11.66</td></tr> <tr><td>STGCN-FT</td><td>3.70</td><td>7.30</td><td>10.31</td><td>4.26</td><td>8.64</td><td>13.06</td><td>5.34</td><td>10.58</td><td>17.36</td><td>4.31</td><td>8.69</td><td>13.30</td></tr><tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr> <tr><td>FGITrans</td><td>3.56</td><td>7.08</td><td>13.95</td><td>4.21</td><td>8.16</td><td>15.66</td><td>5.18</td><td>9.49</td><td>17.41</td><td>4.32</td><td>8.24</td><td>15.67</td></tr><tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr> <tr><td>ST-LLM+</td><td>3.32</td><td>6.54</td><td>8.71</td><td>3.82</td><td>7.70</td><td>10.78</td><td>4.53</td><td>9.03</td><td>13.75</td><td>3.90</td><td>7.75</td><td>11.10</td></tr> <tr><td>UrbanGPT</td><td>3.52</td><td>6.87</td><td>9.32</td><td>4.08</td><td>8.10</td><td>11.45</td><td>4.96</td><td>9.75</td><td>14.90</td><td>4.19</td><td>8.23</td><td>11.88</td></tr> <tr><td>UniST</td><td>3.60</td><td>7.04</td><td>9.59</td><td>4.19</td><td>8.32</td><td>11.79</td><td>5.09</td><td>9.97</td><td>15.36</td><td>4.30</td><td>8.44</td><td>12.24</td></tr></tbody> </table>

### Didi-Chengdu → Shenzhen

<table> <thead> <tr> <th rowspan="2">Methods (Paradigms)</th> <th colspan="3">15 min</th> <th colspan="3">30 min</th> <th colspan="3">60 min</th> <th colspan="3">Average</th> </tr> <tr> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> </tr> </thead> <tbody><tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr> <tr><td>GBRT</td><td>10.65</td><td>19.80</td><td>21.10</td><td>11.88</td><td>22.78</td><td>23.55</td><td>13.72</td><td>25.62</td><td>26.55</td><td>11.86</td><td>22.40</td><td>23.38</td></tr> <tr><td>VAR</td><td>10.15</td><td>18.95</td><td>19.30</td><td>11.47</td><td>20.92</td><td>21.55</td><td>13.38</td><td>23.78</td><td>25.68</td><td>11.72</td><td>21.12</td><td>21.93</td></tr> <tr><td>AGCRN</td><td>6.70</td><td>13.42</td><td>12.15</td><td>7.85</td><td>16.05</td><td>14.98</td><td>9.80</td><td>19.40</td><td>19.52</td><td>7.88</td><td>16.26</td><td>15.28</td></tr> <tr><td>AllDeepSet</td><td>4.17</td><td>8.18</td><td>11.92</td><td>5.01</td><td>10.05</td><td>14.45</td><td>6.27</td><td>12.90</td><td>19.18</td><td>4.99</td><td>10.00</td><td>14.60</td></tr> <tr><td>DCRNN</td><td>4.24</td><td>8.58</td><td>11.68</td><td>4.98</td><td>10.28</td><td>15.03</td><td>6.35</td><td>12.42</td><td>20.03</td><td>4.99</td><td>10.18</td><td>14.98</td></tr> <tr><td>DyHSL</td><td>3.97</td><td>7.89</td><td>10.82</td><td>4.58</td><td>9.78</td><td>13.92</td><td>5.80</td><td>11.98</td><td>18.08</td><td>4.68</td><td>9.82</td><td>13.88</td></tr> <tr><td>GRU</td><td>4.44</td><td>8.89</td><td>12.15</td><td>5.22</td><td>10.92</td><td>15.83</td><td>6.93</td><td>13.05</td><td>21.50</td><td>5.33</td><td>10.75</td><td>16.05</td></tr> <tr><td>GWNet</td><td>4.05</td><td>8.01</td><td>12.85</td><td>4.95</td><td>9.73</td><td>15.83</td><td>6.20</td><td>12.30</td><td>21.50</td><td>4.94</td><td>9.68</td><td>16.05</td></tr> <tr><td>STGCN</td><td>4.17</td><td>8.18</td><td>11.98</td><td>4.88</td><td>10.20</td><td>14.98</td><td>6.27</td><td>12.72</td><td>19.23</td><td>4.94</td><td>10.18</td><td>15.05</td></tr> <tr><td>STG-NCDE</td><td>4.55</td><td>8.58</td><td>9.70</td><td>5.96</td><td>12.75</td><td>13.52</td><td>8.35</td><td>17.50</td><td>19.18</td><td>5.79</td><td>12.58</td><td>13.18</td></tr><tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr> <tr><td>DASTNet</td><td>4.55</td><td>9.35</td><td>12.05</td><td>5.55</td><td>11.85</td><td>15.65</td><td>7.30</td><td>14.40</td><td>20.98</td><td>5.60</td><td>11.32</td><td>15.62</td></tr> <tr><td>D2MHyper</td><td><strong>2.84</strong></td><td><strong>5.44</strong></td><td><strong>7.93</strong></td><td><strong>3.27</strong></td><td><strong>6.24</strong></td><td><strong>9.13</strong></td><td><strong>4.35</strong></td><td><strong>8.94</strong></td><td><strong>13.60</strong></td><td><strong>3.38</strong></td><td><strong>6.60</strong></td><td><strong>9.74</strong></td></tr> <tr><td>DAGN</td><td><ins>3.74</ins></td><td><ins>6.97</ins></td><td><ins>9.45</ins></td><td><ins>4.06</ins></td><td><ins>7.92</ins></td><td><ins>11.10</ins></td><td><ins>4.84</ins></td><td><ins>9.28</ins></td><td><ins>14.07</ins></td><td><ins>4.12</ins></td><td><ins>7.98</ins></td><td><ins>11.30</ins></td></tr> <tr><td>ST-DAAN</td><td>3.86</td><td>7.49</td><td>10.47</td><td>4.57</td><td>9.47</td><td>13.90</td><td>6.05</td><td>11.83</td><td>19.78</td><td>4.69</td><td>9.42</td><td>14.18</td></tr><tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr> <tr><td>MAML</td><td>4.95</td><td>9.47</td><td>15.38</td><td>5.95</td><td>11.50</td><td>19.30</td><td>7.68</td><td>13.53</td><td>24.85</td><td>6.03</td><td>11.32</td><td>19.35</td></tr> <tr><td>ST-GFSL</td><td>4.93</td><td>9.39</td><td>15.05</td><td>5.93</td><td>11.66</td><td>18.67</td><td>7.88</td><td>14.25</td><td>23.98</td><td>6.03</td><td>11.55</td><td>18.77</td></tr><tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr> <tr><td>CrossST</td><td>3.49</td><td>6.93</td><td>9.85</td><td>3.99</td><td>8.23</td><td>11.98</td><td>4.57</td><td>9.48</td><td>14.23</td><td>3.94</td><td>8.01</td><td>11.75</td></tr> <tr><td>MTPB</td><td>3.85</td><td>7.10</td><td>9.88</td><td>4.54</td><td>8.87</td><td>13.02</td><td>5.73</td><td>10.73</td><td>17.10</td><td>4.63</td><td>8.76</td><td>13.13</td></tr> <tr><td>STGCN-FT</td><td>4.17</td><td>8.22</td><td>11.62</td><td>4.79</td><td>9.73</td><td>14.72</td><td>6.02</td><td>11.92</td><td>19.55</td><td>4.85</td><td>9.80</td><td>14.98</td></tr><tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr> <tr><td>FGITrans</td><td>4.01</td><td>7.98</td><td>15.72</td><td>4.75</td><td>9.19</td><td>17.65</td><td>5.83</td><td>10.68</td><td>19.62</td><td>4.86</td><td>9.28</td><td>17.66</td></tr><tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr> <tr><td>ST-LLM+</td><td>3.74</td><td>7.37</td><td>9.82</td><td>4.30</td><td>8.67</td><td>12.15</td><td>5.10</td><td>10.18</td><td>15.50</td><td>4.39</td><td>8.73</td><td>12.50</td></tr> <tr><td>UrbanGPT</td><td>3.96</td><td>7.74</td><td>10.50</td><td>4.60</td><td>9.12</td><td>12.90</td><td>5.58</td><td>10.98</td><td>16.80</td><td>4.72</td><td>9.28</td><td>13.38</td></tr> <tr><td>UniST</td><td>4.05</td><td>7.93</td><td>10.80</td><td>4.72</td><td>9.37</td><td>13.28</td><td>5.73</td><td>11.23</td><td>17.32</td><td>4.84</td><td>9.51</td><td>13.80</td></tr></tbody> </table>

### Shenzhen → Didi-Chengdu

<table> <thead> <tr> <th rowspan="2">Methods (Paradigms)</th> <th colspan="3">15 min</th> <th colspan="3">30 min</th> <th colspan="3">60 min</th> <th colspan="3">Average</th> </tr> <tr> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> <th>MAE</th><th>RMSE</th><th>MAPE (%)</th> </tr> </thead> <tbody><tr><td colspan="13"><strong>Single-Domain Models (Paradigm 1)</strong></td></tr> <tr><td>GBRT</td><td>10.88</td><td>20.22</td><td>21.55</td><td>12.15</td><td>23.28</td><td>24.05</td><td>14.02</td><td>26.18</td><td>27.12</td><td>12.12</td><td>22.88</td><td>23.88</td></tr> <tr><td>VAR</td><td>10.38</td><td>19.35</td><td>19.72</td><td>11.72</td><td>21.38</td><td>22.02</td><td>13.68</td><td>24.30</td><td>26.23</td><td>11.98</td><td>21.58</td><td>22.40</td></tr> <tr><td>AGCRN</td><td>6.85</td><td>13.70</td><td>12.42</td><td>8.03</td><td>16.40</td><td>15.30</td><td>10.02</td><td>19.83</td><td>19.94</td><td>8.06</td><td>16.62</td><td>15.62</td></tr> <tr><td>AllDeepSet</td><td>4.26</td><td>8.35</td><td>12.18</td><td>5.12</td><td>10.27</td><td>14.77</td><td>6.41</td><td>13.18</td><td>19.60</td><td>5.10</td><td>10.22</td><td>14.92</td></tr> <tr><td>DCRNN</td><td>4.33</td><td>8.76</td><td>11.94</td><td>5.09</td><td>10.51</td><td>15.36</td><td>6.49</td><td>12.69</td><td>20.47</td><td>5.10</td><td>10.40</td><td>15.30</td></tr> <tr><td>DyHSL</td><td>4.06</td><td>8.06</td><td>11.06</td><td>4.68</td><td>10.00</td><td>14.23</td><td>5.93</td><td>12.24</td><td>18.48</td><td>4.78</td><td>10.04</td><td>14.18</td></tr> <tr><td>GRU</td><td>4.53</td><td>9.08</td><td>12.42</td><td>5.33</td><td>11.16</td><td>16.18</td><td>7.08</td><td>13.34</td><td>21.97</td><td>5.45</td><td>10.99</td><td>16.40</td></tr> <tr><td>GWNet</td><td>4.14</td><td>8.18</td><td>13.13</td><td>5.06</td><td>9.94</td><td>16.18</td><td>6.34</td><td>12.57</td><td>21.97</td><td>5.05</td><td>9.89</td><td>16.40</td></tr> <tr><td>STGCN</td><td>4.26</td><td>8.35</td><td>12.24</td><td>4.98</td><td>10.42</td><td>15.30</td><td>6.41</td><td>13.00</td><td>19.65</td><td>5.05</td><td>10.40</td><td>15.37</td></tr> <tr><td>STG-NCDE</td><td>4.65</td><td>8.76</td><td>9.91</td><td>6.09</td><td>13.03</td><td>13.82</td><td>8.54</td><td>17.88</td><td>19.60</td><td>5.92</td><td>12.86</td><td>13.47</td></tr><tr><td colspan="13"><strong>Alignment-Based Transfer (Paradigm 2)</strong></td></tr> <tr><td>DASTNet</td><td>4.65</td><td>9.55</td><td>12.32</td><td>5.67</td><td>12.11</td><td>15.99</td><td>7.46</td><td>14.72</td><td>21.44</td><td>5.73</td><td>11.57</td><td>15.96</td></tr> <tr><td>D2MHyper</td><td><strong>2.90</strong></td><td><strong>5.56</strong></td><td><strong>8.10</strong></td><td><strong>3.34</strong></td><td><strong>6.38</strong></td><td><strong>9.33</strong></td><td><strong>4.45</strong></td><td><strong>9.14</strong></td><td><strong>13.90</strong></td><td><strong>3.46</strong></td><td><strong>6.75</strong></td><td><strong>9.95</strong></td></tr> <tr><td>DAGN</td><td><ins>3.82</ins></td><td><ins>7.12</ins></td><td><ins>9.66</ins></td><td><ins>4.15</ins></td><td><ins>8.09</ins></td><td><ins>11.34</ins></td><td><ins>4.95</ins></td><td><ins>9.48</ins></td><td><ins>14.38</ins></td><td><ins>4.21</ins></td><td><ins>8.16</ins></td><td><ins>11.55</ins></td></tr> <tr><td>ST-DAAN</td><td>3.94</td><td>7.65</td><td>10.70</td><td>4.67</td><td>9.68</td><td>14.20</td><td>6.18</td><td>12.09</td><td>20.22</td><td>4.79</td><td>9.63</td><td>14.49</td></tr><tr><td colspan="13"><strong>Meta-Learning-Based Transfer (Paradigm 3)</strong></td></tr> <tr><td>MAML</td><td>5.06</td><td>9.67</td><td>15.72</td><td>6.08</td><td>11.75</td><td>19.73</td><td>7.85</td><td>13.83</td><td>25.40</td><td>6.16</td><td>11.57</td><td>19.78</td></tr> <tr><td>ST-GFSL</td><td>5.04</td><td>9.59</td><td>15.38</td><td>6.06</td><td>11.92</td><td>19.08</td><td>8.05</td><td>14.57</td><td>24.52</td><td>6.16</td><td>11.81</td><td>19.18</td></tr><tr><td colspan="13"><strong>Pre-Training-Based Transfer (Paradigm 4)</strong></td></tr> <tr><td>CrossST</td><td>3.57</td><td>7.08</td><td>10.07</td><td>4.08</td><td>8.41</td><td>12.25</td><td>4.67</td><td>9.69</td><td>14.55</td><td>4.03</td><td>8.19</td><td>12.02</td></tr> <tr><td>MTPB</td><td>3.93</td><td>7.25</td><td>10.10</td><td>4.64</td><td>9.06</td><td>13.31</td><td>5.86</td><td>10.97</td><td>17.48</td><td>4.73</td><td>8.96</td><td>13.42</td></tr> <tr><td>STGCN-FT</td><td>4.26</td><td>8.40</td><td>11.88</td><td>4.90</td><td>9.95</td><td>15.04</td><td>6.15</td><td>12.18</td><td>19.99</td><td>4.96</td><td>10.02</td><td>15.31</td></tr><tr><td colspan="13"><strong>Knowledge-Distillation-Based Transfer (Paradigm 5)</strong></td></tr> <tr><td>FGITrans</td><td>4.10</td><td>8.15</td><td>16.07</td><td>4.85</td><td>9.39</td><td>18.04</td><td>5.96</td><td>10.92</td><td>20.05</td><td>4.97</td><td>9.49</td><td>18.05</td></tr><tr><td colspan="13"><strong>Foundation Models/LLM-Based Transfer (Paradigm 6)</strong></td></tr> <tr><td>ST-LLM+</td><td>3.82</td><td>7.53</td><td>10.03</td><td>4.40</td><td>8.86</td><td>12.42</td><td>5.21</td><td>10.40</td><td>15.85</td><td>4.49</td><td>8.93</td><td>12.78</td></tr> <tr><td>UrbanGPT</td><td>4.05</td><td>7.91</td><td>10.73</td><td>4.70</td><td>9.32</td><td>13.18</td><td>5.71</td><td>11.22</td><td>17.18</td><td>4.82</td><td>9.49</td><td>13.68</td></tr> <tr><td>UniST</td><td>4.14</td><td>8.10</td><td>11.04</td><td>4.83</td><td>9.57</td><td>13.57</td><td>5.86</td><td>11.48</td><td>17.71</td><td>4.94</td><td>9.72</td><td>14.10</td></tr></tbody> </table>

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
