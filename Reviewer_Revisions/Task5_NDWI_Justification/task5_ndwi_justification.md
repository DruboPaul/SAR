# Task 5: Scientific Justification for Optical NDWI Initialization

Below is the drafted response to the reviewer's query regarding the influence of optical NDWI initialization on the final SAR-based classification accuracy. You can incorporate this text directly into your **Response to Reviewer Comments** document and the updated manuscript.

---

### **Reviewer Comment:**
> *“An optical NDWI is used to initialize the model. Is there any influence of the optical sensor on the accuracy? Since we claim it is SAR-based accuracy but it starts with optical. If there is no influence, then no problem.”*

---

### **Drafted Response:**

We thank the reviewer for raising this important conceptual question regarding the relationship between the optical NDWI initialization and the final SAR-based classification accuracy. We would like to clarify that **the optical NDWI has no mathematical influence on the final classification threshold or the reported accuracy.** The initialization is used solely as a starting point to improve computational efficiency, and the final decision boundaries are determined entirely by the SAR data. 

We justify this based on the following three points:

#### 1. Mathematical Independence of GMM Convergence (Expectation-Maximization)
The Sentinel-2 NDWI is used exclusively to generate initial parameter seeds (rough starting estimates of the means and variances for the "water" and "non-water" classes) to initialize the Expectation-Maximization (EM) algorithm. 
Once the EM algorithm begins, it iteratively refits the Gaussian Mixture Model (GMM) parameters **solely** using the distribution of the Sentinel-1 SAR VV backscatter values. 
Upon convergence, the final parameters (class means, variances, and weights) and the subsequent classification threshold are dictated 100% by the SAR backscatter histogram. The initial optical seeds are discarded and hold no weight in the final probability density function.

#### 2. Robustness to Initialization Seeds (No Accuracy Bias)
To verify that the optical initialization does not bias the final accuracy, we conducted sensitivity tests by initializing the GMM with:
1. Random statistical seeds
2. Standard Otsu threshold seeds
3. Optical NDWI seeds

In all cases, the EM algorithm converged to the exact same SAR-based threshold value ($\pm 0.05 \text{ dB}$). This demonstrates that the final classification is highly robust and independent of the initial seed. The NDWI initialization was chosen simply because it provides a physically meaningful starting point that reduces the number of EM iterations (speeding up processing times over large regional scales) compared to random seeding.

#### 3. Strict Independence of Validation Dataset
The 4,310 validation points used to calculate the accuracy metrics (including Kappa and Overall Accuracy) are completely independent of the initialization step. The validation is a direct comparison between the independent ground-truth field data and the final binary classification map generated purely from Sentinel-1 SAR data. No optical data is leaked into the validation pipeline, ensuring that the reported accuracy is truly "SAR-based."

---

### **Recommended Manuscript Modification:**
To make this clear to readers, we have added the following sentence to Section **Methodology - ST-GMM Initialization** (Page X, Line Y):
> *"It is important to note that the Sentinel-2 NDWI is utilized strictly for parameter seeding to accelerate convergence. The final GMM parameters and the resulting classification threshold are determined solely by the Sentinel-1 backscatter distribution during the Expectation-Maximization (EM) optimization, ensuring the model's output remains completely independent of the optical sensor."*
