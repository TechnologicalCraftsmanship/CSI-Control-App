# 🧠 Training Script

This folder contains `training.py`, the core machine learning pipeline for the CSI Control App. This script is responsible for loading the dataset, preprocessing the raw I/Q Channel State Information (CSI), dynamically building model architectures (CNNs, BiLSTMs, MLPs, etc.), and evaluating their performance.

## 🚀 Usage

You can run the script using standard Python. It utilizes `argparse` to allow flexible configuration of hyperparameters, models, and data strategies without modifying the code.

**Example:**
`python training.py --models_to_run cnn --preprocess_mode amplitude_centered --split_strategy stratified_by_class`

## ⚙️ Parameters & Arguments

Below is a quick reference for all available command-line arguments:

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **`--models_to_run`** | String | `'all'` | Comma-separated model names (e.g., `bilstm,cnn,mlp,zein_lightweight_cnn`) or `'all'`. |
| **`--preprocess_mode`** | String | `'amplitude_centered'` | CSI data transformation (e.g., `raw`, `amplitude_centered`, `phase_sanitized`, `amplitude_stats_pdp_plus_phase`). |
| **`--split_strategy`** | String | `'stratified_by_class'` | Train/Val/Test splitting logic (e.g., `stratified_by_class`, `by_file`, `spatial_checkerboard`). |
| **`--label_mode`** | String | `'primary_status'` | Target feature to predict (e.g., `primary_status`, `full_scenario`, `position_based`). |
| **`--chunksize_to_run`** | String | `'all'` | Comma-separated sequence lengths/timesteps (e.g., `64,128`) or `'all'`. |
| **`--units_to_run`** | String | `'all'` | Comma-separated layer widths/units (e.g., `128,256`) or `'all'`. |
| **`--max_samples_per_class`**| Int | `96000` | Limits the number of samples per class per file to ensure dataset balancing. |
| **`--dataset_index`** | String | None | Comma-separated user file indices to load (e.g., `'1,3'` loads `csi_U1.csv` and `csi_U3.csv`). |
| **`--positions_to_keep`** | String | `'all'` | Comma-separated list of spatial positions to filter and keep (e.g., `'1_1,1_2'`). |
| **`--force_balancing_per_position`**| Flag | `False` | Forces class balancing to be applied per individual physical position. |
| **`--ommit_positional_features`** | Flag | `False` | Prevents the one-hot encoded grid positions from being injected into the input features. |
| **`--calibration_ratio`** | Float | `0.0` | Ratio of Test data leaked into Training for calibration testing (0.0 = strict mode). |
| **`--low_vram`** | Flag | `False` | Enables `tf.data.Dataset` batch streaming to reduce GPU memory consumption. |
| **`--disable_shuffle_train_val`** | Flag | `False` | Disables the shuffling of Train and Validation data blocks. |
| **`--sanity_check`** | Flag | `False` | Shuffles data *before* splitting to force data leakage (useful to check if the model *can* overfit). |
| **`--run_id`** | String | `''` | Optional identifier appended to the generated results folder and text reports. |
