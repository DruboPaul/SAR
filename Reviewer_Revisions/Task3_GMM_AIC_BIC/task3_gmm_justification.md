# Task 3: Scientific Justification for the 2-Component GMM Model

Below is the drafted response to the reviewer's query regarding the scientific justification of the 2-component Gaussian Mixture Model (GMM) framework. This text can be incorporated into your **Response to Reviewer Comments** document and the manuscript.

---

### **Reviewer Comment:**
> *“The authors use a Gaussian Mixture Model (GMM) for threshold determination, assuming a 2-component model. How was this validated? Please provide statistical evidence (e.g., AIC/BIC scores) showing that a 2-component model is appropriate and does not overfit or underfit the backscatter distribution.”*

---

### **Drafted Response:**

We thank the reviewer for requesting a more rigorous statistical justification for our choice of a 2-component Gaussian Mixture Model (GMM). We have performed a comprehensive Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC) analysis across three geographically diverse districts in Bangladesh (Sunamganj - wetland-dominated, Dhaka - urban/industrial, Bhola - coastal island) during the monsoon peak (August).

The results of the AIC/BIC testing and our scientific justification for selecting the 2-component model are detailed below:

#### 1. AIC / BIC Scores Summary Table
The table below shows the AIC and BIC scores for GMMs fitted with 2, 3, 4, and 5 components:

| District | Components | AIC | BIC |
| :--- | :---: | :---: | :---: |
| **Sunamganj** | 2 | 569,067 | 569,115 |
| | **3** | **568,677** | **568,753** |
| | 4 | 569,078 | 569,183 |
| | 5 | 569,242 | 569,376 |
| **Dhaka** | 2 | 861,511 | 861,561 |
| | 3 | 859,024 | 859,104 |
| | 4 | 856,705 | 856,815 |
| | **5** | **855,651** | **855,791** |
| **Bhola** | 2 | 659,665 | 659,714 |
| | 3 | 644,449 | 644,526 |
| | **4** | **642,033** | **642,140** |
| | 5 | 644,254 | 644,390 |

*Note: Bold text denotes the mathematically optimal component number according to the lowest information criterion.*

---

#### 2. Physical and Operational Justification for the 2-Component Model

While the information criteria (AIC/BIC) suggest that higher-component models (e.g., 3 components for Sunamganj, 4 for Bhola, and 5 for Dhaka) provide a tighter statistical fit to the backscatter histograms, we selected the **2-component GMM** for the following reasons:

##### A. Direct Correspondence to Physical Classes (Water vs. Land)
The physical objective of our framework is **binary classification**—to separate surface water from non-water (land). In SAR backscatter space (VV band), these two classes represent distinct physical scattering mechanisms:
- **Water Component**: Low backscatter values (typically $-30\text{ dB}$ to $-16\text{ dB}$) caused by specular reflection off smooth water surfaces.
- **Non-Water Component**: High backscatter values (typically $-15\text{ dB}$ to $-5\text{ dB}$) caused by volume and surface scattering from soil, vegetation, and built structures.

A 2-component GMM maps directly to these two physical states. Using more components splits the heterogeneous land class (e.g., urban buildings, wet vegetation, bare soil) into arbitrary statistical sub-distributions, which do not correspond to our target classes and make binary thresholding highly unstable.

##### B. Threshold Identifiability and Algorithmic Stability
In a 2-component GMM, the optimal classification threshold is mathematically defined as the intersection point between the two Gaussian probability density functions (the decision boundary where the probability of belonging to water equals the probability of belonging to land). 

If we use a 3, 4, or 5-component model:
- The land class is represented by multiple overlapping Gaussians.
- Finding a single threshold becomes mathematically ambiguous because there are multiple intersection points.
- It requires arbitrary heuristic rules to decide which sub-components represent "wet land", "dry land", or "vegetated water," significantly increasing classification uncertainty and reducing the robustness of the automated processing pipeline.

##### C. Overfitting Mitigation
Fitting a 4 or 5-component GMM to local histograms requires estimating a much larger number of parameters (means, variances, and mixing weights for each component). In dry-season months or highly urbanized areas where the "water" peak is extremely small or non-existent, higher-component GMMs tend to overfit the noise in the land class, creating false "water" peaks and leading to high rates of commission errors. The 2-component GMM acts as a regularizer, forcing the model to capture the principal bimodal division of the landscape.

---

### **Recommended Manuscript Modification:**
We have added a discussion of these findings to **Section 3.2 - Statistical Thresholding (GMM)**:
> *"Although AIC and BIC testing indicates that higher-component GMMs (3 to 5 components) capture the sub-histogram variations of heterogeneous land surfaces (e.g., urban buildings, croplands, forest), we employ a 2-component GMM. This choice is physically grounded in the binary nature of the target classes (water vs. non-water) and ensures threshold stability, parameter identifiability, and robustness against local overfitting in areas with high land-surface heterogeneity."*
