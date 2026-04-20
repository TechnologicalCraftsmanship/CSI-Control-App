import os
import argparse
#if running local, there is a env at D:\research_data\venv_3_10\Scripts\activate.bat
os.environ["TF_USE_LEGACY_KERAS"] = "1" 

is_windows = os.name == 'nt'

DEFAULT_CALIBRATION_RATIO = 0.0  # Strict Medium Mode by default
DEFAULT_LOW_VRAM = False
SKIPPING_ALREADY_GENERATED = True
DEFAULT_LABEL_MODE = 'primary_status'
DEFAULT_PREPROCESS_MODE = 'amplitude_centered'
DEFAULT_SPLIT_STRATEGY = 'stratified_by_class'
DEFAULT_MODELS_TO_RUN = 'all'
DEFAULT_CHUNKSIZE = 'all'
DEFAULT_UNITS = 'all'
DEFAULT_SANITY_CHECK = True
DROPOUT_RATE = 0.3
EPOCHS = 100
DEFAULT_OMMITTING_POSITIONAL_FEATURES = False  # Wont use positional features for any models if set to true
DEFAULT_MAX_SAMPLES_PER_CLASS = 96000 #16000  # Max samples per class per file for balancing
DEFAULT_POSITIONS_TO_KEEP = 'all'  # Keep all positions by default
RESTORE_BEST_MODEL = True
RESTORE_BEST_MODEL_METRIC = 'val_loss'  # Metric to monitor for restoring best model
#RESTORE_BEST_MODEL_METRIC = 'val_accuracy'  # Metric to monitor for restoring best model
TRAINING_PATIENCE = 15  # Increased patience for better convergence
DEFAULT_FORCE_BALANCING_PER_POSITION = True  # Replaced by the argument if the argument is sent
SHUFFLE_TRAIN_VAL = True  #for now it is efffective only for by_file
SHUFFLE_TRAIN_VAL_BLOCK = 512 
# The "0" positions to be used STRICTLY for TESTING
SPATIAL_CHECKERBOARD_TEST_POSITIONS = ['3_2']


preprocess_choices= [
    'amplitude_stats_pdp_plus_phase', 'amplitude_stats_pdp', 'raw', 'amplitude_centered', 'phase_sanitized'
]#  , 'amplitude_centered_plus_phase', 'multi_branch_fusion', 'amplitude_plus_phase', 'amplitude_stats_pdp_plus_phase',  'amplitude', 'amplitude_filtered', had worse results and are being removed just to easy parsing

split_strategies = ['stratified_by_class', 'stratified_by_class_no_shuffle', 'by_file', 'by_file_separated_val', 'spatial_checkerboard']

label_modes = ['full_scenario', 'position_based', 'position_primary_status', 'primary_status', 'position_all_status']

files = [
        'csi_U1.csv','csi_U2.csv','csi_U3.csv','csi_U4.csv','csi_U5.csv'
        ]

#all_models = ['cnn_deep_attention_bilstm', 'bilstm', 'cnn', 'mlp', 'zein_lightweight_cnn'] #'multi_branch_model', 'cnn_attention_bilstm', 'cnn_deep_bilstm', 'cnn_bilstm', '1dcnn', 'random_forest'] <-- had wrost results than its variants
all_models = [
    'bilstm', 'cnn', 'mlp', 'zein_lightweight_cnn', 'cnn2d_deep_attention_bilstm'
] #, 'cnn_deep_attention_bilstm', 'cnn2d_deep_attention_bilstm_big', 'cnn_deep_attention_bilstm', 'multi_branch_model', 'cnn_norm_deep_attention_bilstm', 'cnn_attention_bilstm', 'cnn_deep_bilstm', 'cnn_bilstm', '1dcnn', 'random_forest'] <-- had wrost results than its variants


all_chunksizes = [64] #64,128, 256 gives worse results than 256
all_units = [256] #128,196 gives worse results than 256


parser = argparse.ArgumentParser(description="Run CSI classification experiments.")

parser.add_argument(
    '--sanity_check',
    action='store_true',
    help="Enable sanity check: Shuffles data BEFORE splitting in 'stratified_by_class' to allow overfitting (~100% acc)."
)

parser.add_argument(
    '--low_vram',
    action='store_true',
    help="Enable low VRAM mode (reduces GPU memory usage)."
)

parser.add_argument(
    '--ommit_positional_features',
    action='store_true',
    help="Ommit positional features from the input."
)

parser.add_argument(
    '--run_id',
    type=str,
    default='',
    help="Optional identifier string to append to results folder and summary files."
)


parser.add_argument(
    '--max_samples_per_class',
    type=int,
    default=DEFAULT_MAX_SAMPLES_PER_CLASS,
    help="Maximum number of samples per class per file for balancing."
)

parser.add_argument(
    '--label_mode',
    type=str,
    default=DEFAULT_LABEL_MODE,#'primary_status',#'full_scenario',
    choices=['all'] + label_modes,
    help=(
        "Defines how to process the 'cenario' label. "
        "'full_scenario': Use the full label (default). "
        "'position_based': Use A_B (position). "
        "'position_primary_status': Use A_B_EY (position + primary status). "
        "'position_all_status': Use A_B_EY_EAK (position + all statuses)."
    )
)

parser.add_argument(
    '--preprocess_mode',
    type=str,
    default=DEFAULT_PREPROCESS_MODE, # Try this one!
    choices=['all'] + preprocess_choices,
    help="Processing mode. 'amplitude_plus_phase' uses both Mag and Sanitized Phase."
)

parser.add_argument(
    '--split_strategy',
    type=str,
    default=DEFAULT_SPLIT_STRATEGY, # Try this one!
    choices=['all'] + split_strategies,
    help="Strategy for splitting the dataset into train/val/test."
)
parser.add_argument(
    '--chunksize_to_run',
    type=str,
    default=DEFAULT_CHUNKSIZE,
    # choices=['all'] + all_chunksizes,  <-- REMOVE THIS LINE
    help="Comma-separated chunksizes (e.g., '64,128') or 'all'."
)
parser.add_argument(
    '--models_to_run',
    type=str,
    default=DEFAULT_MODELS_TO_RUN, 
    # choices=['all'] + all_models,      <-- REMOVE THIS LINE
    help="Comma-separated model names (e.g., 'bilstm,cnn') or 'all'."
)
parser.add_argument(
    '--units_to_run',
    type=str,
    default=DEFAULT_UNITS, 
    # choices=['all'] + all_units,       <-- REMOVE THIS LINE
    help="Comma-separated units (e.g., '128,256') or 'all'."
)

parser.add_argument(
    '--calibration_ratio',
    type=float,
    default=DEFAULT_CALIBRATION_RATIO,
    help="Ratio of Test File to leak into Training (0.0 = Strict Medium Mode, 0.2 = Use 20% of test user for calibration)."
)

parser.add_argument(
    '--force_balancing_per_position',
    action='store_true',
    help="Enable force balancing per position regardless of split strategy."
)

parser.add_argument(
    '--positions_to_keep',
    type=str,
    default=DEFAULT_POSITIONS_TO_KEEP,
    help="Comma-separated list of positions to keep (e.g., '1_1,1_2,2_1'). Defaults to 'all' (keep 1_1 to 4_4)."
)

parser.add_argument(
    '--dataset_index',
    type=str,
    default=None,
    help="Comma-separated list of user indices to load (e.g., '1,3'). Overrides default file list. Format: csi_U#.csv"
)

parser.add_argument(
    '--disable_shuffle_train_val',
    action='store_true',
    help="Disable shuffling of training and validation data."
)

args = parser.parse_args()

if args.dataset_index:
    try:
        # Parse indices and construct filenames: csi_U1_Full.csv, etc.
        indices = [x.strip() for x in args.dataset_index.split(',')]
        files = [f"csi_U{i}.csv" for i in indices]
        print(f">>> Overriding dataset files with indices {indices}: {files}")
    except Exception as e:
        print(f"Error parsing --dataset_index: {e}")
        exit(1)



SHUFFLE_TRAIN_VAL = SHUFFLE_TRAIN_VAL if not args.disable_shuffle_train_val else False
FORCE_BALANCING_PER_POSITION = True if args.force_balancing_per_position else DEFAULT_FORCE_BALANCING_PER_POSITION
MAX_SAMPLES_PER_CLASS = args.max_samples_per_class
CALIBRATION_RATIO = args.calibration_ratio
OMMITTING_POSITIONAL_FEATURES = True if args.ommit_positional_features else DEFAULT_OMMITTING_POSITIONAL_FEATURES


if args.split_strategy == 'stratified_by_class_no_shuffle':
    args.sanity_check = False  # Shuffling is disabled, so sanity check doesn't make sense here. Disable it to avoid confusion.
    args.disable_shuffle_train_val = True  # Ensure shuffling is disabled for this strategy
    SHUFFLE_TRAIN_VAL = False
    SANITY_CHECK = False  # Shuffling is disabled, so sanity check doesn't make sense here. Disable it to avoid confusion.
    DEFAULT_SANITY_CHECK = False
    print(">>> Detected split strategy 'stratified_by_class_no_shuffle'. Shuffling and sanity check have been disabled for this run.")


# Global Flag assignment
SANITY_CHECK = args.sanity_check if args.sanity_check else DEFAULT_SANITY_CHECK
low_vram = True if args.low_vram else DEFAULT_LOW_VRAM

if not is_windows:
    # Try to find CUDA in the system, but don't force it if we are using pip packages
    cuda_path = "/usr/local/cuda-12.9"
    if os.path.exists(cuda_path):
        os.environ["CUDA_HOME"] = cuda_path
        os.environ["PATH"] = f"{cuda_path}/bin:" + os.environ.get("PATH", "")
        os.environ["LD_LIBRARY_PATH"] = f"{cuda_path}/lib64:" + os.environ.get("LD_LIBRARY_PATH", "")
        os.environ["XLA_FLAGS"] = f"--xla_gpu_cuda_data_dir={cuda_path}"
    else:
        # If no system CUDA, tell XLA to look inside your .venv for the pip-installed nvcc
        import nvidia.cuda_nvcc
        nvcc_path = os.path.dirname(nvidia.cuda_nvcc.__file__)
        os.environ["XLA_FLAGS"] = f"--xla_gpu_cuda_data_dir={nvcc_path}"

os.environ["TF_GPU_ALLOCATOR"] = "cuda_malloc_async"
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true" # Extra insuran
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"



if os.environ.get("CUDA_VISIBLE_DEVICES", "") == "":
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Default to GPU 0 if not set

# 2. Fix the XLA 'libdevice' warning
#os.environ["TF_DISABLE_CUDNN_RNN"] = "1" #no nee

# Select GPU, starting from 0. Use "-1" to force CPU.
#os.environ["CUDA_VISIBLE_DEVICES"] = "0"
#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


import joblib
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (
    LSTM, Bidirectional, Dense, Flatten, Conv1D, MaxPooling1D,
    GlobalAveragePooling1D, RepeatVector, Attention, LayerNormalization,
    Dropout, Concatenate, Input, TimeDistributed,
    BatchNormalization, Activation, Conv2D, MaxPooling2D, LeakyReLU, Reshape
)
from tensorflow.keras.utils import plot_model, to_categorical
import keras.backend as K
from random import randint
from numpy import array, argmax
import json
import time
import gc
import scipy.signal 
from scipy.stats import skew, kurtosis, iqr
import scipy.fft
from tensorflow.keras import mixed_precision


gpu_devices = tf.config.list_physical_devices('GPU')
gpu_name = "Unknown"
if gpu_devices:
    details = tf.config.experimental.get_device_details(gpu_devices[0])
    gpu_name = details.get('device_name', 'Unknown')
    print(f">>> Detected GPU: {gpu_name}")
    
# --- GPU Memory Management ---
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    try:
        # Enable memory growth for the first GPU
        tf.config.experimental.set_memory_growth(physical_devices[0], True)
        print(f"Enabled memory growth for GPU: {physical_devices[0]}")
    except RuntimeError as e:
        # Memory growth must be set before models are built
        print(f"Could not set memory growth: {e}")
# --- End GPU Management ---

# --- NÚMERO MÁXIMO DE AMOSTRAS (TIMESTEPS) POR CLASSE ---
# Isso ajuda a balancear o dataset antes de criar as sequências


# --- Helper function to create sequences with Stride ---
def create_sequences(X_data, y_data, chunksize, step=None):
    """
    Creates sequences from time-series data with an optional step (stride).
    step: If None, defaults to max(1, chunksize // 8) to save RAM.
    """
    # Auto-calculate a safe step if none provided to prevent OOM
    if step is None:
        # 87% overlap (chunksize // 8) is usually enough for data augmentation
        # For chunk=256, step becomes 32. RAM usage drops 32x (25GB -> 0.8GB).
        step = max(1, chunksize // 8)
    
    Xs, ys = [], []
    # Use the step in the range
    for i in range(0, len(X_data) - chunksize, step):
        sequence = X_data[i:(i + chunksize)]
        label = y_data[i + chunksize - 1]
        Xs.append(sequence)
        ys.append(label)
    return np.array(Xs), np.array(ys)

class MyModel:
    # --- MUDANÇA 1: Adicionar label_mode ao __init__ ---
    def __init__(self, model_name, chunksize, units, epochs, batch_size, num_filters, kernel_size, 
                 label_mode='full_scenario', split_strategy='stratified_by_class', 
                 preprocess_mode='raw', dropout_rate=0.3, run_id='', 
                 positions_to_keep='all', dataset_index=None):
        # Detect if we are running on the P40 (Index 2)
        # # SAFER CHECK: Detect if GPU 2 (P40) is among the selected devices
        visible_gpus = os.environ.get("CUDA_VISIBLE_DEVICES", "")
        self.is_p40 = "2" in visible_gpus and len(visible_gpus.split(',')) == 1
                
        # Use 'mixed_float16' for your 3060/4060 Ti
        # Note: P40 (Pascal) doesn't have Tensor Cores, so it won't benefit as much
        if not self.is_p40:
            policy = mixed_precision.Policy('mixed_float16')
            mixed_precision.set_global_policy(policy)
            print(">>> Mixed Precision Enabled: Optimized for newer GPUs.")

        if self.is_p40:
            self.rec_drop = 0.01
            print(">>> P40 Detected: Disabling optimized cuDNN RNN kernels for stability.")
        else:
            self.rec_drop = 0.0

        self.model_name = model_name
        self.chunksize = chunksize
        self.units = units
        self.epochs = epochs
        self.batch_size = batch_size
        self.num_filters = num_filters
        self.kernel_size = kernel_size  
        self.label_mode = label_mode  # <-- Armazenar o modo de label
        self.split_strategy = split_strategy # <-- Armazenar a estratégia
        self.preprocess_mode = preprocess_mode # <--- Store it
        self.dropout_rate = dropout_rate
        self.run_id = run_id
        self.positions_to_keep = positions_to_keep # <--- STORE IT
        self.dataset_index = dataset_index # <--- Store it

        # NEW: Dictionary to store feature indices for slicing
        self.feature_slices = {}

        self.input_shape = None
        self.n_features = None
        self.num_classes = None
        self.labels = None
        self.label_indices = None

        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.X_test = None
        self.y_test = None

        #self.scaler = MinMaxScaler() # OLD
        self.scaler = StandardScaler() # NEW: Better for centered data
        self.label_encoder = LabelEncoder()

        # --- MODIFICAÇÃO: Criar subpasta única para todos os resultados ---
        
        # 1. Gerar o timestamp
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        

        # Update folder name to include the mode so results don't overwrite
        folder_name = (
            f"{self.model_name}_"
            f"C{self.chunksize}_"
            f"U{self.units}_"
            f"E{self.epochs}_"
            f"L-{self.label_mode}_"
            f"S-{self.split_strategy}_"
            f"P-{self.preprocess_mode}_"  # <--- Added underscore separator
            f"Pos-{self.positions_to_keep}" # <--- Added Positions arg
            #f"_{self.timestamp}"
        )

        # <--- ADDED LOGIC: Append dataset_index if present --->
        if getattr(self, 'dataset_index', None):
             # Replace commas with hyphens for the folder name
             clean_idx = self.dataset_index.replace(',', '-')
             folder_name += f"_Data-{clean_idx}"

        # <--- CHANGED LOGIC: Use explicit _Run- tag --->
        if self.run_id:
            folder_name += f"_Run-{self.run_id}"

        
        self.base_path = f"results/{folder_name}"
        
        self.model_path = f"{self.base_path}/{self.model_name}_model.h5"
        self.plot_path = f"{self.base_path}/model_plot.png"
        self.report_path = f"{self.base_path}/classification_report.txt"
        self.cm_plot_path = f"{self.base_path}/confusion_matrix.png"
        self.cm_text_path = f"{self.base_path}/confusion_matrix.txt"

        os.makedirs(self.base_path, exist_ok=True)
        # --- FIM DA MODIFICAÇÃO ---
        os.makedirs("models", exist_ok=True)
    def block_shuffle(self, X, y, block_size=1024, random_state=42):
        """
        Shuffles data in large contiguous blocks to preserve local temporal structure
        while randomizing the global order.
        """
        n_samples = len(X)
        n_blocks = int(np.ceil(n_samples / block_size))
        
        # Create a list of block indices [0, 1, 2, ..., N]
        block_indices = np.arange(n_blocks)
        
        # Shuffle the blocks
        np.random.seed(random_state)
        np.random.shuffle(block_indices)
        
        X_shuffled = []
        y_shuffled = []
        
        for i in block_indices:
            start_idx = i * block_size
            end_idx = min((i + 1) * block_size, n_samples)
            
            X_shuffled.append(X[start_idx:end_idx])
            y_shuffled.append(y[start_idx:end_idx])
            
        return np.concatenate(X_shuffled, axis=0), np.concatenate(y_shuffled, axis=0)
    def preprocess_iq_data(self, iq_data, mode='raw', source_ids=None):
        """
        iq_data: Shape (N_samples, N_features) where features are [I, Q, I, Q...]
        mode: 'raw', 'amplitude', 'phase_sanitized', 'amplitude_plus_phase'
        source_ids: Array of file IDs (needed for filtering/centering)
        """
        if mode == 'raw':
            return iq_data

        print(f"Preprocessing IQ data: Mode = {mode}...")
        
        # 1. Separate I and Q
        I = iq_data[:, 0::2]
        Q = iq_data[:, 1::2]
        
        # 2. Helper: Calculate Amplitude
        amplitude = np.sqrt(I**2 + Q**2)

        # 3. Helper: Calculate Sanitized Phase
        # We cannot use raw np.angle because of CFO/SFO (random rotations).
        # We must Unwrap -> Fit Linear Line -> Subtract Line.
        def get_sanitized_phase(I_data, Q_data):
            # A. Create Complex Numbers
            complex_data = I_data + 1j * Q_data
            
            # B. Get Raw Phase and Unwrap it (fix 2pi jumps)
            raw_phase = np.angle(complex_data)
            unwrapped_phase = np.unwrap(raw_phase, axis=1)
            
            # C. Linear Fit to remove Sampling Frequency Offset (SFO)
            # We assume subcarriers are linearly spaced.
            n_subcarriers = unwrapped_phase.shape[1]
            x_axis = np.arange(n_subcarriers)
            
            sanitized_phase = np.zeros_like(unwrapped_phase)
            
            # Vectorized linear detrending (faster than looping)
            # Slope k = (Cov(x,y) / Var(x))
            # Here we cheat slightly for speed: simple slope between first and last subcarrier
            # (Standard implementation in many CSI papers)
            slope = (unwrapped_phase[:, -1] - unwrapped_phase[:, 0]) / (n_subcarriers - 1)
            intercept = np.mean(unwrapped_phase, axis=1) - slope * np.mean(x_axis)
            
            # Reshape for broadcasting
            slope = slope.reshape(-1, 1)
            intercept = intercept.reshape(-1, 1)
            
            # Subtract the linear error
            linear_trend = (slope * x_axis) + intercept
            clean_phase = unwrapped_phase - linear_trend
            
            return clean_phase

        # --- FILTERING HELPER (From previous step) ---
        def apply_filter(data, s_ids):
            b, a = scipy.signal.butter(3, 0.1) 
            filtered = np.zeros_like(data)
            unique_files = np.unique(s_ids)
            for fid in unique_files:
                idx = np.where(s_ids == fid)[0]
                filtered[idx] = scipy.signal.filtfilt(b, a, data[idx], axis=0)
            return filtered

        # --- NEW HELPER: FEATURE EXTRACTION ---
        def get_stats_and_pdp(amp_data, I_data, Q_data):
            # A. Statistical Features (Across Subcarriers)
            # Input shape: (Samples, 64_Subcarriers) -> Output: (Samples, 1)
            print("Calculating Statistical Features...")
            mean = np.mean(amp_data, axis=1, keepdims=True)
            std = np.std(amp_data, axis=1, keepdims=True)
            # Mean Absolute Deviation
            mad = np.mean(np.abs(amp_data - mean), axis=1, keepdims=True) 
            minimum = np.min(amp_data, axis=1, keepdims=True)
            maximum = np.max(amp_data, axis=1, keepdims=True)
            iqr_val = iqr(amp_data, axis=1, keepdims=True)
            energy = np.sum(np.square(amp_data), axis=1, keepdims=True)
            # Skew/Kurtosis require casting to handle precision issues sometimes
            skew_val = skew(amp_data, axis=1).reshape(-1, 1)
            kurt_val = kurtosis(amp_data, axis=1).reshape(-1, 1)

            stats_block = np.concatenate([mean, std, mad, minimum, maximum, iqr_val, energy, skew_val, kurt_val], axis=1)
            
            # B. Power Delay Profile (IFFT of CSI)
            # CSI is Frequency domain. IFFT gives Time Domain (Multipath components)
            print("Calculating PDP (IFFT)...")
            complex_csi = I_data + 1j * Q_data
            # IFFT along the subcarrier axis (axis 1)
            pdp_time_domain = np.fft.ifft(complex_csi, axis=1)
            pdp_magnitude = np.abs(pdp_time_domain)
            
            # Combine: [Amplitude (Original), PDP (Multipath), Stats (Distribution)]
            # You can choose to exclude Amplitude if you want to force generalizatio
            # Returns 137 features (initial tests demonstrated better results with all features)
            return np.concatenate((amp_data, pdp_magnitude, stats_block), axis=1)
            # Returns 73 features (Removes the location-specific "fingerprint")
            #return np.concatenate((pdp_magnitude, stats_block), axis=1)
        # --- PROCESSING LOGIC ---

        if mode == 'amplitude':
            return amplitude

        elif mode == 'amplitude_filtered':
            if source_ids is None: return amplitude
            return apply_filter(amplitude, source_ids)

        elif mode == 'amplitude_centered':
            # Just return the filtered amplitude. The StandardScaler will center it later!
            if source_ids is None: return amplitude
            return apply_filter(amplitude, source_ids)
                

        elif mode == 'phase_sanitized':
            # Just the phase
            return get_sanitized_phase(I, Q)

        elif mode == 'amplitude_plus_phase':
            # Both Amplitude and Phase stacked side-by-side
            # This doubles the feature count (e.g., 64 + 64 = 128 features per timestep)
            amp_data = amplitude
            
            # Optionally filter amplitude? Let's keep it raw for this mix or apply filter:
            if source_ids is not None:
                 amp_data = apply_filter(amplitude, source_ids)

            phase_data = get_sanitized_phase(I, Q)
            
            # Concatenate: [Amp_Sub1, Amp_Sub2... Phase_Sub1, Phase_Sub2...]
            return np.concatenate((amp_data, phase_data), axis=1)

        elif mode == 'amplitude_centered_plus_phase':
            filtered = apply_filter(amplitude, source_ids) if source_ids is not None else amplitude
            
            # --- FIX: No per-file centering here anymore! ---
            centered = filtered 
                
            phase_data = get_sanitized_phase(I, Q)
            return np.concatenate((centered, phase_data), axis=1)

        # --- NEW MODE IMPLEMENTATION ---
        elif mode == 'amplitude_stats_pdp':
            # 1. Filter Amplitude first (clean signal)
            clean_amp = apply_filter(amplitude, source_ids) if source_ids is not None else amplitude
            
            # --- FIX: Pass clean amplitude forward without session-wise mean centering ---
            centered_amp = clean_amp

            # 3. Extract Features
            return get_stats_and_pdp(centered_amp, I, Q)

        # --- NEW MODE: Stats + PDP + Phase ---
        elif mode == 'amplitude_stats_pdp_plus_phase':
            # 1. Prepare Amplitude (Filtered)
            clean_amp = apply_filter(amplitude, source_ids) if source_ids is not None else amplitude
            
            # --- FIX: Pass clean amplitude forward without session-wise mean centering ---
            centered_amp = clean_amp

            # 2. Get Stats + PDP + Amplitude
            base_features = get_stats_and_pdp(centered_amp, I, Q)
            
            # 3. Get Phase
            phase_data = get_sanitized_phase(I, Q)
            
            # 4. Combine
            return np.concatenate((base_features, phase_data), axis=1)

        # --- NEW MULTI-BRANCH MODE ---
        elif mode == 'multi_branch_fusion':
            # 1. Prepare Base Amplitude (Filtered)
            clean_amp = apply_filter(amplitude, source_ids) if source_ids is not None else amplitude
            
            # --- FIX: Pass clean amplitude forward without session-wise mean centering ---
            centered_amp = clean_amp

            # 2. Branch A (Temporal): Amplitude Centered + Phase Sanitized
            phase_data = get_sanitized_phase(I, Q)
            feat_temporal = np.concatenate((centered_amp, phase_data), axis=1)

            # 3. Branch B (Spatial): Amplitude + PDP + Stats
            feat_spatial = get_stats_and_pdp(centered_amp, I, Q)

            # 4. Concatenate both sets side-by-side
            return np.concatenate((feat_temporal, feat_spatial), axis=1)
        return iq_data
    def multi_branch_model(self):
        inputs = Input(shape=self.input_shape)
        
        # Retrieve slice indices
        s = self.feature_slices
        if not s:
            raise ValueError("Feature slices not defined! Did you use 'multi_branch_fusion' mode?")

        # --- 1. SLICING LAYERS (The "Y" Split) ---
        # Lambda layers allow us to split the single input tensor back into 3 streams
        
        # Branch 1 Input: Position (One-Hot)
        # Shape: (Batch, Time, N_Pos) -> We usually just need one timestep for position, 
        # but since it repeats, we can take the average or just process the sequence.
        x_pos = tf.keras.layers.Lambda(lambda x: x[:, :, s['pos_start']:s['pos_end']])(inputs)
        
        # Branch 2 Input: Temporal (Amp + Phase)
        x_temp = tf.keras.layers.Lambda(lambda x: x[:, :, s['temp_start']:s['temp_end']])(inputs)
        
        # Branch 3 Input: Spatial (Amp + PDP + Stats)
        x_spat = tf.keras.layers.Lambda(lambda x: x[:, :, s['spat_start']:s['spat_end']])(inputs)


        # --- BRANCH A: CONTEXT (Position) ---
        # Position is static over time. We can flatten and use a small MLP.
        # GlobalAveragePooling reduces (Batch, Time, Pos) -> (Batch, Pos)
        b_pos = GlobalAveragePooling1D()(x_pos) 
        b_pos = Dense(16, activation='relu')(b_pos)
        b_pos = Dense(8, activation='relu')(b_pos)
        # Output: Context Embedding Vector (Size 8)


        # --- BRANCH B: TEMPORAL (BiLSTM) ---
        # Best for Phase/Doppler shifts
        b_temp = Bidirectional(LSTM(self.units, return_sequences=False, recurrent_dropout=self.rec_drop))(x_temp)
        # Output: Temporal Feature Vector (Size Units*2)


        # --- BRANCH C: SPATIAL (CNN + Attention) ---
        # Best for Multipath Profiles (PDP)
        b_spat = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(x_spat)
        b_spat = MaxPooling1D(pool_size=2)(b_spat)
        b_spat = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(b_spat)
        b_spat = MaxPooling1D(pool_size=2)(b_spat)
        
        # Attention on Spatial Features
        # We want the CNN to find the "Activity Burst" in the PDP data
        # Using a small LSTM here to summarize the spatial sequence for attention
        spat_lstm = Bidirectional(LSTM(self.units // 2, return_sequences=True, recurrent_dropout=self.rec_drop))(b_spat)
        spat_att = Attention()([spat_lstm, spat_lstm])
        b_spat = GlobalAveragePooling1D()(spat_att)


        # --- FUSION (The Merge) ---
        merged = Concatenate()([b_pos, b_temp, b_spat])
        
        # Final Classification Block
        x = Dense(self.units, activation='relu')(merged)
        x = Dropout(self.dropout_rate)(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs, outputs)
        return model
    
    def load_data(self, database_name='csi_all', add_positional_features=False):
        """
        Carrega dados, aplica balanceamento (sub-sampling) por classe,
        processa features (I/Q + Meta) e codifica labels.
        Retorna os arrays processados prontos para a divisão estratificada.
        """
        # --- ETAPA 1: Carregamento e Marcação por Arquivo (Sem Mudanças) ---
        if isinstance(database_name, list):
            print(f"Carregando e mesclando {len(database_name)} arquivos...")
            df_list = []
            file_ids = {} # Para mapear nome do arquivo para ID
            
            for i, filename in enumerate(database_name):
                filepath = f'../Dataset/{filename}' 
                try:
                    df = pd.read_csv(filepath)
                    df['source_file'] = i # Adiciona um ID numérico do arquivo
                    df_list.append(df)
                    file_ids[filename] = i
                    print(f"Carregado: {filepath} ({len(df)} linhas) como Fonte {i}")
                except Exception:
                    return None, None, None, None
            if not df_list: return None, None, None, None
            df_full = pd.concat(df_list, ignore_index=True)
        elif isinstance(database_name, str):
            filepath = f'../Dataset/{database_name}.csv'
            try:
                df_full = pd.read_csv(filepath)
                df_full['source_file'] = 0 # ID de origem 0 se for arquivo único
            except FileNotFoundError:
                print(f"Error: Could not find file {filepath}")
                return None, None, None
        else:
            print("Erro: 'database_name' deve ser uma string (nome base) ou uma lista de strings (nomes de arquivos CSV).")
            return None, None, None
        
         # --- NEW FILTER: KEEP SPECIFIC POSITIONS ---
        target_positions = []
        if self.positions_to_keep != 'all':
            print(f"Filtering dataset to keep only positions: {self.positions_to_keep}")

            # Parse the string "1_1,1_2" into a list ['1_1', '1_2']
            target_positions = [p.strip() for p in self.positions_to_keep.split(',')]
            
            # <--- ADDED LOGIC START: Force Test Positions for Checkerboard --->
            if self.split_strategy == 'spatial_checkerboard':
                print(f"Spatial Checkerboard active: Auto-adding test positions {SPATIAL_CHECKERBOARD_TEST_POSITIONS} to filter list.")
                for p in SPATIAL_CHECKERBOARD_TEST_POSITIONS:
                    if p not in target_positions:
                        target_positions.append(p)
            # <--- ADDED LOGIC END --->
            
            # Extract position "R_C" from "R_C_Activity..."
            # We use a temporary column for robust filtering
            df_full['temp_pos_id'] = df_full['cenario'].apply(lambda x: "_".join(x.split('_')[:2]))
            
            # Filter
            original_count = len(df_full)
            df_full = df_full[df_full['temp_pos_id'].isin(target_positions)]
            
            # Clean up
            df_full = df_full.drop(columns=['temp_pos_id'])
            
            print(f"Position Filter Applied: {original_count} -> {len(df_full)} samples kept.")
            
            if len(df_full) == 0:
                print("Error: No data remaining after filtering positions!")
                return None, None, None
        # -------------------------------------------
        if add_positional_features:
            def get_position_feature(cenario_str):
                try:
                    parts = cenario_str.split('_')
                    if len(parts) < 2: return None
                    # Returns "1_1", "1_2", etc.
                    return f"{parts[0]}_{parts[1]}" 
                except:
                    return None
            
            print("Extracting Positional Features (Grid ID) for injection...")
            df_full['position_feature'] = df_full['cenario'].apply(get_position_feature)
            
        # --- MUDANÇA DE POSIÇÃO: Processar labels ANTES do balanceamento ---
        print(f"Processando labels com o modo: {self.label_mode}")# 1. CREATE A NEW COLUMN FOR POSITION IF NEEDED
        
        # 2. STANDARD LABEL PROCESSING (Existing Code)
        print(f"Processando labels com o modo: {self.label_mode}")
        if self.label_mode == 'full_scenario':
             df_full['processed_label'] = df_full['cenario']
        else:
            def get_label(cenario_str):
                try:
                    parts = cenario_str.split('_')
                    if len(parts) < 6: return None
                    
                    if self.label_mode == 'position_based':
                        return f"{parts[0]}_{parts[1]}"
                    elif self.label_mode == 'position_primary_status':
                        return f"{parts[0]}_{parts[1]}_{parts[3]}"
                    elif self.label_mode == 'primary_status':
                        return f"{parts[3]}" # Just "Sitting", "Standing", "Empty"
                    elif self.label_mode == 'position_all_status':
                        return f"{parts[0]}_{parts[1]}_{parts[3]}_{parts[5]}"
                except Exception:
                    return None
                return None

            df_full['processed_label'] = df_full['cenario'].apply(get_label)

        # Clean up NaNs
        original_len = len(df_full)
        df_full = df_full.dropna(subset=['processed_label'])
        
        # IF mode is primary_status, also drop rows where position extraction failed
        if add_positional_features:
            df_full = df_full.dropna(subset=['position_feature'])
        removed_count = original_len - len(df_full)
        if removed_count > 0:
            print(f"Aviso: Removidas {removed_count} linhas com formato de 'cenario' inválido para o modo {self.label_mode}.")
        if len(df_full) == 0:
            print("Erro: Não há dados restantes após processar os labels.")
            return None, None, None
        # --- FIM DA MUDANÇA DE POSIÇÃO ---

        # --- MODIFICAÇÃO FINAL: ETAPA 2: BALANCEAMENTO POR CLASSE E POR ARQUIVO (SEM SHUFFLE) ---
        print(f"Balanceando dados: Sub-sampling para MAX_SAMPLES_PER_CLASS = {MAX_SAMPLES_PER_CLASS} POR CLASSE E POR ARQUIVO.")
        
        # 1. Aplicar o limite por grupo (classe + arquivo)
        # This GUARANTEES CONTIGUITY within each block of data extracted from the original files.
        #df_balanced = df_full.groupby(['processed_label', 'source_file']).head(MAX_SAMPLES_PER_CLASS).reset_index(drop=True)

        if self.split_strategy == 'spatial_checkerboard' or FORCE_BALANCING_PER_POSITION:
            # Divide the global limit by 16 (approx number of positions) to keep total size similar
            # e.g., 16000 / 16 = 1000 samples per chair.
            if target_positions == []:
                num_positions = 16 # Default if not filtered
            else:
                num_positions = len(target_positions)
            per_scenario_limit = max(500, MAX_SAMPLES_PER_CLASS // num_positions)
            
            print(f"ATTENTION: Balancing per 'cenario' (Limit {per_scenario_limit}) to preserve spatial diversity.")
            
            # Group by 'cenario' (which includes position info like 1_1_Empty)
            df_balanced = df_full.groupby(['processed_label', 'source_file', 'cenario']).head(per_scenario_limit).reset_index(drop=True)
            
        else:
            # Standard behavior for other strategies
            print(f"Balanceando dados: Sub-sampling para MAX_SAMPLES_PER_CLASS = {MAX_SAMPLES_PER_CLASS} POR CLASSE E POR ARQUIVO.")
            df_balanced = df_full.groupby(['processed_label', 'source_file']).head(MAX_SAMPLES_PER_CLASS).reset_index(drop=True)

        # --- DEBUG PRINT: DETAILED DISTRIBUTION ---
        print("\n" + "="*60)
        print(f"--- [DEBUG] Dataset Distribution (Max Samples: {MAX_SAMPLES_PER_CLASS}) ---")
        
        # 1. Extract Position Helper (e.g. '1_3')
        # We use a temporary copy to avoid SettingWithCopy warnings on the main df
        debug_df = df_balanced.copy()
        debug_df['pos_id'] = debug_df['cenario'].apply(lambda x: "_".join(x.split('_')[:2]))
        
        # 2. Create Pivot Table (Rows: Position, Cols: Class, Values: Count)
        # This shows exactly what the model is seeing
        dist_table = debug_df.pivot_table(
            index='pos_id', 
            columns='processed_label', 
            aggfunc='size', 
            fill_value=0
        )
        
        # 3. Print
        print(dist_table)
        print("-" * 60)
        
        # 4. Check for Missing Positions
        # If you expected 4 positions but only see 1, the 'head()' limit killed the others.
        if self.positions_to_keep != 'all':
            expected = set(self.positions_to_keep.split(','))
            found = set(dist_table.index.unique())
            missing = expected - found
            if missing:
                print(f"!!! WARNING: The following positions were requested but have 0 samples:\n{missing}")
                print("   -> This usually means MAX_SAMPLES_PER_CLASS is too low, cutting off the file before reaching these rows.")
        
        print("="*60 + "\n")
        # ------------------------------------------

        # --- START DEBUG PRINT ---
        # Extracts "1_3" from "1_3_Sitting..." in the 'cenario' column
        debug_positions = df_balanced['cenario'].apply(lambda x: "_".join(x.split('_')[:2])).unique()
        print(f">>> DEBUG: Positions included in balanced set: {sorted(debug_positions)}")
        # --- END DEBUG PRINT ---
        # --- CRITICAL FIX: DO NOT SORT BY LABEL FOR TIME SERIES ---
        # Sorting breaks the temporal sequence if a file contains transitions (e.g., A -> B -> A).
        # We strictly want to keep the original time order (index).
        # df_balanced = df_balanced.sort_values(by='processed_label').reset_index(drop=True) 
        # ----------------------------------------------------------

        print(f"Amostras originais (full): {len(df_full)}, Amostras balanceadas (final): {len(df_balanced)}")
        # --- FIM DA MODIFICAÇÃO FINAL ---
        #"""Original
        metadata_cols_to_keep = [
            'rssi', 
            #'rate', 
            #'sig_mode', 
            'mcs', 
            'stbc',
            'sgi',
            #'bandwidth',
            'noise_floor', 
            #'channel'
        ]
        #"""
        """
        metadata_cols_to_keep = [
            #'rssi', 
            #'rate', 
            #'sig_mode', 
            #'mcs', 
            #'stbc',
            #'sgi',
            #'bandwidth',
            #'noise_floor', 
            #'channel'
        ]
        """
        
        # Usa o df_balanced em vez do df_full
        cols_to_use = ['processed_label','data', 'cenario', 'source_file'] + metadata_cols_to_keep
        if add_positional_features:
            cols_to_use.append('position_feature')  
        try:
            df = df_balanced[cols_to_use]
        except KeyError as e:
            print(f"Erro: O CSV não contém uma das colunas necessárias: {e}")
            return None, None, None
            
        df = df.dropna()
        if len(df) == 0:
            print("Erro: Não há dados restantes após remover NaNs.")
            return None, None, None


        print("Processando a string de dados I/Q...")
        try:
            X_data_iq_list = df['data'].apply(json.loads).to_list()
            #X_data_iq = np.array(X_data_iq_list, dtype=float)
            X_data_iq = np.array(X_data_iq_list, dtype=np.int8)
        except Exception as e:
            print(f"Erro ao processar a coluna 'data'. É uma string de array JSON válida? Erro: {e}")
            return None, None, None


        source_file_data = df['source_file'].values
        position_data = df['cenario'].apply(lambda x: "_".join(x.split('_')[:2])).values

        print("Processando metadados...")
        # Apenas RSSI permanece, convertido para float32
        X_data_meta = df[metadata_cols_to_keep].astype(np.float32)
        X_data_meta = X_data_meta.values
        
        # --- INJECTION START: POSITION FEATURES ---
        X_data_pos = None
        if add_positional_features:
            print("Encoding Positional Features (One-Hot)...")
            # Use Pandas get_dummies for One-Hot Encoding
            # shape: (N_samples, N_positions) e.g., (80000, 16)
            pos_dummies = pd.get_dummies(df['position_feature'], prefix='pos')
            X_data_pos = pos_dummies.values.astype(np.float32)
            print(f"Position features shape: {X_data_pos.shape}")
        # --- INJECTION END ---

# --- START PREPROCESSING INSERTION ---
        # Converter X_data_iq para float32 ANTES do processamento
        X_data_iq_float32 = X_data_iq.astype(np.float32)
        del X_data_iq 
        gc.collect()
        


        # ADDED: Apply Preprocessing (Amplitude/Filter)
        # Note: We need 'preprocess_mode' in __init__ (see Step 4)
        X_data_processed = self.preprocess_iq_data(
            X_data_iq_float32, 
            mode=self.preprocess_mode, 
            source_ids=source_file_data
        )


        
        if self.preprocess_mode != 'raw':
            del X_data_iq_float32 # Save memory if we created a new array
            gc.collect()
            print(f"New feature shape after processing: {X_data_processed.shape}")
        else:
            X_data_processed = X_data_iq_float32
            del X_data_iq_float32

        '''
        print("Combinando features processadas e metadados...")
        if X_data_pos is not None:
            # Concatenate: [CSI_Processed, Metadata, Position_OneHot]
            X_data_combined = np.concatenate((X_data_processed, X_data_meta, X_data_pos), axis=1)
            print("Positional features added to input vector.")
        else:
            X_data_combined = np.concatenate((X_data_processed, X_data_meta), axis=1)
        del X_data_processed
        # --- END PREPROCESSING INSERTION ---
        del X_data_meta
        gc.collect()
        '''
        print("Combinando features processadas e metadados para Multi-Branch...")
        
        # --- LOGIC FOR MULTI-BRANCH INDICES ---
        if self.preprocess_mode == 'multi_branch_fusion':
            # 1. Position Features (Start at 0)
            n_pos = X_data_pos.shape[1] if X_data_pos is not None else 0
            
            # 2. Temporal Features (Amp + Phase)
            # We know Amp=64, Phase=64 -> 128 features
            # (Dynamically calculated based on subcarriers just in case)
            n_subcarriers = 64 # Assuming 64 for standard CSI
            n_temporal = n_subcarriers * 2 
            
            # 3. Spatial Features (Amp + PDP + Stats)
            # Amp(64) + PDP(64) + Stats(9) = 137
            n_spatial = X_data_processed.shape[1] - n_temporal 
            
            # Save slices for the model to use
            self.feature_slices = {
                'pos_start': 0,
                'pos_end': n_pos,
                'temp_start': n_pos,
                'temp_end': n_pos + n_temporal,
                'spat_start': n_pos + n_temporal,
                'spat_end': n_pos + n_temporal + n_spatial
            }
            print(f"Multi-Branch Slices defined: {self.feature_slices}")
        else:
            # Standard mode (no slicing needed)
            self.feature_slices = {}

        # --- CONCATENATION ---
        # Order: [Position | Temporal_Block | Spatial_Block | Metadata(optional)]
        # Note: We put Position FIRST for easier slicing
        
        parts_to_concat = []
        if X_data_pos is not None:
             parts_to_concat.append(X_data_pos)
        
        parts_to_concat.append(X_data_processed)
        parts_to_concat.append(X_data_meta)
        
        X_data_combined = np.concatenate(parts_to_concat, axis=1)
        del X_data_processed
        # --- END PREPROCESSING INSERTION ---
        del X_data_meta


        print("Finalizando preparação das features (sem escalonar)...")
        # REMOVIDO: self.scaler.fit_transform() para evitar vazamento de dados (data leakage)
        X_data_unscaled = X_data_combined.astype(np.float32)
        del X_data_combined
        gc.collect()
        self.n_features = X_data_unscaled.shape[1]

        print("Codificando labels...")
        # --- MUDANÇA 4: Usar a coluna 'processed_label' ---
        y_data_encoded = self.label_encoder.fit_transform(df['processed_label'])
        # --- FIM DA MUDANÇA 4 ---
        
        self.num_classes = len(self.label_encoder.classes_)
        self.labels = self.label_encoder.classes_
        self.label_indices = list(range(self.num_classes)) 
        
        print(f"Dados carregados com sucesso.")
        print(f"Número total de features (I/Q + Meta): {self.n_features}")
        print(f"Número de classes: {self.num_classes}")
        print(f"Classes (primeiras 5): {self.labels[:5]}...")

        # Retorna os dados processados (mas AINDA NÃO ESCALADOS)
        return X_data_unscaled, y_data_encoded, source_file_data, position_data
    
    def split_data(self, files=None,add_positional_features=False):
        """
        Carrega, balança e divide os dados.
        """
        X_data_unscaled, y_data_encoded, source_file_data, position_data = self.load_data(
            database_name=files, add_positional_features=add_positional_features
        )

        if X_data_unscaled is None:
            return False

        X_train_list, y_train_list = [], []
        X_val_list, y_val_list = [], []
        X_test_list, y_test_list = [], []

        # --- STRATEGY 1: SPATIAL CHECKERBOARD (HARDEST) ---
        if self.split_strategy == 'spatial_checkerboard':
            print("Creating sequences with division 'spatial_checkerboard' (Hard)...")
            # Old:
            # 0 X 0 X
            # X X X X
            # 0 X 0 X
            # X X X X 
            
            
            print(f"Test Positions (Unseen in training): {SPATIAL_CHECKERBOARD_TEST_POSITIONS}")
            
            # Identify which samples belong to Test vs Train
            # We use boolean indexing on the position_data array
            is_test_sample = np.isin(position_data, SPATIAL_CHECKERBOARD_TEST_POSITIONS)
            
            # Separate Raw Data indices
            test_indices = np.where(is_test_sample)[0]
            train_indices = np.where(~is_test_sample)[0]

            print("\n--- [DEBUG] Checking Spatial Split Class Distribution ---")
            unique_test, counts_test = np.unique(y_data_encoded[test_indices], return_counts=True)
            print("Classes caught in TEST set (Spatial):")
            if len(unique_test) == 0:
                print("  (No samples in Test set)")
            else:
                for idx, count in zip(unique_test, counts_test):
                    print(f"  Class '{self.labels[idx]}': {count}")

            print(f"Total Samples: {len(X_data_unscaled)}")
            print(f"Test Samples (Spatial Holdout): {len(test_indices)}")
            print(f"Train/Val Samples: {len(train_indices)}")
        
            current_step = max(1, self.chunksize // 4) 
            # --- 1. Process Test Set ---
            if len(test_indices) > 0:
                X_test_raw = X_data_unscaled[test_indices]
                y_test_raw = y_data_encoded[test_indices]
                # Note: We must treat this carefully. Ideally, we shouldn't just concat all test samples 
                # if they come from disjoint files/times, but create_sequences assumes contiguity.
                # Ideally, we loop unique files inside the test set.
                unique_test_files = np.unique(source_file_data[test_indices])
                
                for fid in unique_test_files:
                    # Filter for this specific file AND being a test position
                    idx = np.where((source_file_data == fid) & (is_test_sample))[0]
                    X_seq, y_seq = create_sequences(X_data_unscaled[idx], y_data_encoded[idx], self.chunksize, step=current_step)
                    if len(X_seq) > 0:
                        X_test_list.append(X_seq)
                        y_test_list.append(y_seq)
            
            # --- 2. Process Train/Val Set ---
            unique_train_files = np.unique(source_file_data[train_indices])
            
            for fid in unique_train_files:
                # Filter for this file AND being a train position
                idx = np.where((source_file_data == fid) & (~is_test_sample))[0]
                
                # Create sequences
                X_seq_full, y_seq_full = create_sequences(X_data_unscaled[idx], y_data_encoded[idx], self.chunksize, step=current_step)
                
                if len(X_seq_full) == 0: continue
                
                # Split 80/20 for Train/Val per file chunk to maintain some temporal order
                split_point = int(len(X_seq_full) * 0.8)
                
                X_train_list.append(X_seq_full[:split_point])
                y_train_list.append(y_seq_full[:split_point])
                
                X_val_list.append(X_seq_full[split_point:])
                y_val_list.append(y_seq_full[split_point:])

            # --- 3. Concatenate ---
            if X_test_list:
                self.X_test = np.concatenate(X_test_list, axis=0)
                self.y_test = np.concatenate(y_test_list, axis=0)
            else:
                print("Error: No test sequences found for spatial holdout.")
                return False
                
            if X_train_list:
                self.X_train = np.concatenate(X_train_list, axis=0)
                self.y_train = np.concatenate(y_train_list, axis=0)
                self.X_val = np.concatenate(X_val_list, axis=0)
                self.y_val = np.concatenate(y_val_list, axis=0)
            else:
                return False

        # --- STRATEGY 2: BY FILE (MEDIUM) ---
        elif self.split_strategy == 'by_file':
            print("Creating sequences with division 'by_file'...")
            all_file_ids = np.unique(source_file_data)
            
            # Ensure file IDs are sorted to guarantee the "last one" is actually the last one loaded
            all_file_ids.sort() 

            # Identify Split IDs
            test_file_id = all_file_ids[-1] # The last file loaded
            train_val_file_ids = all_file_ids[:-1] # All previous files
            
            print(f"Test File ID: {test_file_id}")
            print(f"Train/Val File IDs: {train_val_file_ids}")

            # 1. PROCESS ALL FILES
            train_val_sequences = []
            train_val_labels = []
            
            test_sequences = []
            test_labels = []
            current_step = max(1, self.chunksize // 4) 
            
            for file_id in all_file_ids:
                # Extract RAW data for this specific file
                file_indices = np.where(source_file_data == file_id)[0]
                X_file_raw = X_data_unscaled[file_indices]
                y_file_raw = y_data_encoded[file_indices]

                # Create sequences
                X_seq, y_seq = create_sequences(X_file_raw, y_file_raw, self.chunksize, step=current_step)
                
                if len(X_seq) == 0:
                    continue

                # Distribute to correct list based on ID
                if file_id == test_file_id:
                    test_sequences.append(X_seq)
                    test_labels.append(y_seq)
                else:
                    train_val_sequences.append(X_seq)
                    train_val_labels.append(y_seq)
            
            # 2. CONCATENATE AND ASSIGN
            
            # --- Test Set ---
            if len(test_sequences) > 0:
                self.X_test = np.concatenate(test_sequences, axis=0)
                self.y_test = np.concatenate(test_labels, axis=0)
                del test_sequences, test_labels
            else:
                print("Error: No sequences generated for Test file.")
                return False

            # --- Train/Val Set ---
            if len(train_val_sequences) > 0:
                X_train_val = np.concatenate(train_val_sequences, axis=0)
                y_train_val = np.concatenate(train_val_labels, axis=0)

                # TO SHUFFLE, UNCOMMENT THESE LINES:
                if SHUFFLE_TRAIN_VAL:
                    print(f"Block Shuffling Train/Val (Block Size: 1024)...")
                    X_train_val, y_train_val = self.block_shuffle(X_train_val, y_train_val, block_size=SHUFFLE_TRAIN_VAL_BLOCK, random_state=42)

                
                # CHANGED: Removed shuffle. Using direct 80/20 split to preserve order.
                train_end_seq = int(len(X_train_val) * 0.8)
                
                self.X_train = X_train_val[:train_end_seq]
                self.y_train = y_train_val[:train_end_seq]
                
                self.X_val = X_train_val[train_end_seq:]
                self.y_val = y_train_val[train_end_seq:]
                del train_val_sequences, train_val_labels
                del X_train_val, y_train_val
            else:
                 print("Error: No sequences generated for Train/Val files.")
                 return False
        elif self.split_strategy == 'by_file_separated_val':
            print("Creating sequences with division 'by_file_separated_val'...")
            print("(Train: Files 0..N-3 | Val: File N-2 | Test: File N-1)")

            if CALIBRATION_RATIO > 0:
                print(f"!!! CALIBRATION MODE ENABLED: Leaking {CALIBRATION_RATIO*100}% of Test User into Training !!!")

            all_file_ids = np.unique(source_file_data)
            all_file_ids.sort() 

            if len(all_file_ids) < 3:
                print("Error: Strategy 'by_file_separated_val' requires at least 3 source files.")
                return False

            # Identify Split IDs
            test_file_id = all_file_ids[-1]
            val_file_id = all_file_ids[-2]
            # Train files are implicitly the rest

            print(f"Test File ID: {test_file_id}")
            print(f"Val File ID: {val_file_id}")
            print(f"Train File IDs: {all_file_ids[:-2]}")

            train_sequences, train_labels = [], []
            val_sequences, val_labels = [], []
            test_sequences, test_labels = [], []
            current_step = max(1, self.chunksize // 4) 
            
            for file_id in all_file_ids:
                # Extract RAW data
                file_indices = np.where(source_file_data == file_id)[0]
                X_file_raw = X_data_unscaled[file_indices]
                y_file_raw = y_data_encoded[file_indices]

                # Create sequences
                X_seq, y_seq = create_sequences(X_file_raw, y_file_raw, self.chunksize, step=current_step)
                
                if len(X_seq) == 0: continue

                # Distribute based on ID
                if file_id == test_file_id:# === CALIBRATION LOGIC ===
                    if CALIBRATION_RATIO > 0.0:
                        # Calculate split point
                        calib_size = int(len(X_seq) * CALIBRATION_RATIO)
                        
                        # First part goes to TRAIN (Calibration)
                        train_sequences.append(X_seq[:calib_size])
                        train_labels.append(y_seq[:calib_size])
                        
                        # Remaining part stays in TEST
                        test_sequences.append(X_seq[calib_size:])
                        test_labels.append(y_seq[calib_size:])
                    else:
                        # Standard strict mode
                        test_sequences.append(X_seq)
                        test_labels.append(y_seq)
                    # =========================
                elif file_id == val_file_id:
                    val_sequences.append(X_seq)
                    val_labels.append(y_seq)
                else:
                    train_sequences.append(X_seq)
                    train_labels.append(y_seq)
            
            # Concatenate arrays
            if train_sequences and val_sequences and test_sequences:
                self.X_train = np.concatenate(train_sequences, axis=0)
                self.y_train = np.concatenate(train_labels, axis=0)
                
                self.X_val = np.concatenate(val_sequences, axis=0)
                self.y_val = np.concatenate(val_labels, axis=0)
                
                self.X_test = np.concatenate(test_sequences, axis=0)
                self.y_test = np.concatenate(test_labels, axis=0)
                del train_sequences, train_labels
                del val_sequences, val_labels
                del test_sequences, test_labels
            else:
                print("Error: One of the sets (Train/Val/Test) is empty. Check file contents.")
                return False
        # --- NEW BLOCK END ---
        # --- STRATEGY 4: STRATIFIED BY CLASS (PER FILE) ---
        elif self.split_strategy == 'stratified_by_class' or self.split_strategy == 'stratified_by_class_no_shuffle':

            print("Criando sequências estratificadas por classe (e por arquivo)...")
            
            # Obter todos os IDs de arquivos únicos no dataset
            unique_files = np.unique(source_file_data)

            for class_idx in self.label_indices:
                # Iterate over unique files WITHIN this class to maintain per-user temporal logic
                for file_id in unique_files:
                    
                    # Find indices matching BOTH the class and the specific file
                    class_file_indices = np.where((y_data_encoded == class_idx) & (source_file_data == file_id))[0]

                    # Check for minimum length needed for a 70/10/20 split and sequence creation
                    if len(class_file_indices) < (self.chunksize * 5): 
                        continue

                    # 1. GET THE RAW TIME SERIES DATA FOR THIS SPECIFIC CLASS AND USER
                    X_class_file = X_data_unscaled[class_file_indices]
                    y_class_file = y_data_encoded[class_file_indices]
                    
                    # =========================================================
                    # Branch between Sanity Check and Standard Split
                    # =========================================================
                    
                    if SANITY_CHECK:
                        # --- SANITY CHECK MODE (High Leakage) ---
                        current_step = max(1, self.chunksize // 4) 
                        X_seq_all, y_seq_all = create_sequences(X_class_file, y_class_file, self.chunksize, step=current_step)
                        
                        if len(X_seq_all) > 0:
                            # SHUFFLE sequences (Mixes time steps randomly -> Data Leakage)
                            X_seq_all, y_seq_all = shuffle(X_seq_all, y_seq_all, random_state=42)
                            
                            train_end = int(len(X_seq_all) * 0.7)
                            val_end = int(len(X_seq_all) * 0.8)
                            
                            X_train_list.append(X_seq_all[:train_end])
                            y_train_list.append(y_seq_all[:train_end])
                            
                            X_val_list.append(X_seq_all[train_end:val_end])
                            y_val_list.append(y_seq_all[train_end:val_end])
                            
                            X_test_list.append(X_seq_all[val_end:])
                            y_test_list.append(y_seq_all[val_end:])
                    
                    else:
                        # --- STANDARD MODE (Strict Temporal Split Per User/Class) ---
                        # 2. SPLIT THE RAW DATA TEMPORALLY FIRST (No Leakage)
                        train_end_raw = int(len(X_class_file) * 0.7)
                        val_end_raw = int(len(X_class_file) * 0.8) 
                        
                        # Training block
                        X_train_raw = X_class_file[:train_end_raw]
                        y_train_raw = y_class_file[:train_end_raw]
                        
                        # Validation block
                        X_val_raw = X_class_file[train_end_raw:val_end_raw]
                        y_val_raw = y_class_file[train_end_raw:val_end_raw]
                        
                        # Test block
                        X_test_raw = X_class_file[val_end_raw:]
                        y_test_raw = y_class_file[val_end_raw:]

                        # 3. CREATE SEQUENCES SEPARATELY
                        current_step = max(1, self.chunksize // 4) 
                        X_train_seq, y_train_seq = create_sequences(X_train_raw, y_train_raw, self.chunksize, step=current_step)
                        X_val_seq, y_val_seq = create_sequences(X_val_raw, y_val_raw, self.chunksize, step=current_step)
                        X_test_seq, y_test_seq = create_sequences(X_test_raw, y_test_raw, self.chunksize, step=current_step)

                        # 4. APPEND
                        if len(X_train_seq) > 0:
                            X_train_list.append(X_train_seq)
                            y_train_list.append(y_train_seq)
                        if len(X_val_seq) > 0:
                            X_val_list.append(X_val_seq)
                            y_val_list.append(y_val_seq)
                        if len(X_test_seq) > 0:
                            X_test_list.append(X_test_seq)
                            y_test_list.append(y_test_seq)
                        

            # Combina todas as sequências de classe em um único dataset
            if X_train_list and X_val_list and X_test_list:
                self.X_train = np.concatenate(X_train_list, axis=0)
                self.y_train = np.concatenate(y_train_list, axis=0)
                del X_train_list, y_train_list

                self.X_val = np.concatenate(X_val_list, axis=0)
                self.y_val = np.concatenate(y_val_list, axis=0)
                del X_val_list, y_val_list

                self.X_test = np.concatenate(X_test_list, axis=0)
                self.y_test = np.concatenate(y_test_list, axis=0)
                del X_test_list, y_test_list
            else:
                print("Erro: Nenhuma sequência foi criada para um dos conjuntos. Verifique a estratégia ou o chunksize.")
                return False
        # --- FIM DA LÓGICA CONDICIONAL ---

        #if not X_train_list or not X_test_list: # <-- Ver se ambos têm dados
        #    print("Erro: Nenhuma sequência foi criada para treino ou teste. Verifique a estratégia de divisão ou o chunksize.")
        #    return False

        #print("Limpando arrays originais da memória...")
        #del X_data_unscaled
        #del y_data_encoded
        #del source_file_data
        gc.collect()
        # --- FIM DA MUDANÇA ---

        # --- ETAPA CRÍTICA: Embaralhar as sequências ---
        # Isso mistura as classes para que o modelo não aprenda em ordem
        #print("Embaralhando sequências de treino e validação...")
        #self.X_train, self.y_train = shuffle(self.X_train, self.y_train, random_state=42)
        #self.X_val, self.y_val = shuffle(self.X_val, self.y_val, random_state=42)
        # O conjunto de teste não precisa ser embaralhado

        # =====================================================================
        # --- NEW FIX: DATA LEAKAGE PREVENTION (SCALE AFTER SPLIT) ---
        # =====================================================================
        print("Escalando features (Apenas no conjunto de TREINO)...")
        
        # 1. Reshape Train to 2D: (Batch * Time, Features)
        b_train, t_steps, n_feats = self.X_train.shape
        X_train_2d = self.X_train.reshape(-1, n_feats)
        
        # 2. Fit and Transform Train (The scaler Learns ONLY from this data)
        self.X_train = self.scaler.fit_transform(X_train_2d).reshape(b_train, t_steps, n_feats)
        
        # 3. Transform Val (Using the mean/std learned from Train)
        if hasattr(self, 'X_val') and self.X_val is not None and len(self.X_val) > 0:
            b_val = self.X_val.shape[0]
            X_val_2d = self.X_val.reshape(-1, n_feats)
            self.X_val = self.scaler.transform(X_val_2d).reshape(b_val, t_steps, n_feats)
            
        # 4. Transform Test (Using the mean/std learned from Train)
        if hasattr(self, 'X_test') and self.X_test is not None and len(self.X_test) > 0:
            b_test = self.X_test.shape[0]
            X_test_2d = self.X_test.reshape(-1, n_feats)
            self.X_test = self.scaler.transform(X_test_2d).reshape(b_test, t_steps, n_feats)
        # =====================================================================

        self.input_shape = (self.chunksize, self.n_features)

        print(f"Sequências de Treino: {self.X_train.shape}")
        print(f"Sequências de Validação: {self.X_val.shape}")
        print(f"Sequências de Teste: {self.X_test.shape}")
        
        # Verificar a distribuição do conjunto de teste (opcional, mas bom para depuração)
        print("Distribuição de classes do conjunto de teste (amostra):")
        unique, counts = np.unique(self.y_test, return_counts=True)
        # Mostra as primeiras 10 classes e suas contagens no conjunto de teste
        print(dict(zip(self.label_encoder.inverse_transform(unique[:10]), counts[:10])))
        
        return True

    def define_model(self):
        if self.model_name == 'bilstm':
            return self.bilstm()
        elif self.model_name == 'cnn_attention_bilstm':
            return self.cnn_attention_bilstm()
        elif self.model_name == 'cnn':
            return self.cnn()
        elif self.model_name == 'cnn_deep_bilstm':
            return self.cnn_deep_bilstm()
        elif self.model_name == 'cnn_deep_attention_bilstm': # <--- ADD THIS
            return self.cnn_deep_attention_bilstm()
        elif self.model_name == '1dcnn':
            print("Using '1dcnn' (aliased to 'cnn' model)")
            return self.cnn()
        elif self.model_name == 'cnn_bilstm':
            return self.cnn_bilstm()
        elif self.model_name == 'mlp':
            return self.mlp()
        elif self.model_name == 'zein_lightweight_cnn':
            return self.zein_lightweight_cnn()
        elif self.model_name == 'cnn_norm_deep_attention_bilstm':
            return self.cnn_norm_deep_attention_bilstm()
        elif self.model_name == 'cnn2d_deep_attention_bilstm':
            return self.cnn2d_deep_attention_bilstm()
        elif self.model_name == 'cnn2d_deep_attention_bilstm_big':
            return self.cnn2d_deep_attention_bilstm_big()
        elif self.model_name == 'random_forest':
            # Map 'units' to 'n_estimators' (number of trees)
            # n_jobs=-1 uses all CPU cores
            return RandomForestClassifier(n_estimators=self.units, n_jobs=-1)
        elif self.model_name == 'multi_branch_model':
            return self.multi_branch_model()
        else:
            raise ValueError(f"Unknown model name: {self.model_name}")

    def cnn(self):
        inputs = Input(shape=self.input_shape)
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(inputs)
        x = MaxPooling1D(pool_size=2)(x)
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(x)
        x = MaxPooling1D(pool_size=2)(x)
        x = Flatten()(x)
        x = Dense(self.units, activation='relu')(x)
        x = Dropout(self.dropout_rate)(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        model = Model(inputs, outputs)
        return model
    def zein_lightweight_cnn(self):
        """
        Implementation of HAR-LightCNN from:
        Zein et al., 2024. "CSI-Based Human Activity Recognition via Lightweight CNN Model and Data Augmentation"
        """
        inputs = Input(shape=self.input_shape)
        
        # Zein treats the input as an image: (Time, Subcarriers/Features, Channels=1)
        x = Reshape((self.chunksize, self.n_features, 1))(inputs)
        
        # --- 1st Conv Block ---
        x = Conv2D(filters=32, kernel_size=(3, 3), padding='same')(x)
        x = LeakyReLU(alpha=0.3)(x)
        x = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding='same')(x)
        x = BatchNormalization()(x)
        
        # --- 2nd Conv Block ---
        x = Conv2D(filters=32, kernel_size=(3, 3), padding='same')(x)
        x = LeakyReLU(alpha=0.3)(x)
        x = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding='same')(x)
        x = BatchNormalization()(x)
        
        # --- 3rd Conv Block ---
        x = Conv2D(filters=32, kernel_size=(2, 2), padding='same')(x)
        x = LeakyReLU(alpha=0.3)(x)
        x = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)
        x = BatchNormalization()(x)
        
        # --- FC Block ---
        x = Flatten()(x)
        x = Dense(64, activation='relu')(x)
        x = Dropout(0.3)(x) # Paper specifies 30% dropout here
        
        # --- Output Block ---
        outputs = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs, outputs)
        return model    
    def cnn_deep_bilstm(self):
        inputs = Input(shape=self.input_shape)
        
        # --- CNN BLOCK 1 (Spatial Features Low-Level) ---
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(inputs)
        x = MaxPooling1D(pool_size=2)(x)
        # Optional: Dropout here often helps if Block 1 overfits
        # x = Dropout(0.1)(x) 
        
        # --- CNN BLOCK 2 (Spatial Features High-Level) ---
        # This is the layer the original cnn_bilstm was missing
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(x)
        x = MaxPooling1D(pool_size=2)(x)
        
        # --- BiLSTM BLOCK (Temporal correlations of High-Level Features) ---
        # return_sequences=False because we want the final decision of the sequence, not a sequence of decisions
        x = Bidirectional(LSTM(self.units, return_sequences=False, recurrent_dropout=self.rec_drop))(x)
        
        # --- CLASSIFIER ---
        x = Dropout(self.dropout_rate)(x)
        x = Dense(self.units, activation='relu')(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs, outputs)
        return model
    def cnn_deep_attention_bilstm(self):
        inputs = Input(shape=self.input_shape)
        
        # --- BLOCK 1: Deep Spatial Feature Extraction ---
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(inputs)
        x = MaxPooling1D(pool_size=2)(x)
        # x = Dropout(0.1)(x) # Optional: Enable if overfitting
        
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(x)
        x = MaxPooling1D(pool_size=2)(x)
        
        # --- BLOCK 2: Temporal Sequence Learning ---
        # Note: return_sequences=True is REQUIRED for Attention
        lstm_out = Bidirectional(LSTM(self.units, return_sequences=True, recurrent_dropout=self.rec_drop))(x)
        
        # --- BLOCK 3: Attention Mechanism ---
        # Self-attention: query=lstm_out, value=lstm_out
        attention_out = Attention()([lstm_out, lstm_out])
        
        # --- BLOCK 4: Classification ---
        # Pool the attention weighted sequence into a single vector
        x = GlobalAveragePooling1D()(attention_out)
        
        x = Dropout(self.dropout_rate)(x)
        x = Dense(self.units, activation='relu')(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs, outputs)
        return model
    def cnn_norm_deep_attention_bilstm(self):
        inputs = Input(shape=self.input_shape)
        
        # --- BLOCK 1: Zein-Stabilized Spatial Feature Extraction (1D) ---
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, padding='same')(inputs)
        x = LeakyReLU(alpha=0.3)(x)
        x = MaxPooling1D(pool_size=2)(x)
        x = BatchNormalization()(x)
        
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, padding='same')(x)
        x = LeakyReLU(alpha=0.3)(x)
        x = MaxPooling1D(pool_size=2)(x)
        x = BatchNormalization()(x)
        
        # --- BLOCK 2: Temporal Sequence Learning ---
        lstm_out = Bidirectional(LSTM(self.units, return_sequences=True, recurrent_dropout=self.rec_drop))(x)
        
        # --- BLOCK 3: Attention Mechanism ---
        attention_out = Attention()([lstm_out, lstm_out])
        
        # --- BLOCK 4: Classification ---
        x = GlobalAveragePooling1D()(attention_out)
        
        x = Dropout(self.dropout_rate)(x)
        x = Dense(self.units, activation='relu')(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs, outputs)
        return model
    def cnn2d_deep_attention_bilstm(self):
        inputs = Input(shape=self.input_shape)
        
        # 1. Reshape for 2D CNN (Time, Subcarriers, Channels=1)
        x = Reshape((self.chunksize, self.n_features, 1))(inputs)
        
        # --- BLOCK 1: Zein's 2D Spatial Extraction ---
        # Note: We use fixed 3x3 kernels here because the dynamic kernel_size=20 
        # is too large for the subcarrier dimension in a 2D matrix.
        x = Conv2D(filters=32, kernel_size=(3, 3), padding='same')(x)
        x = LeakyReLU(alpha=0.3)(x)
        x = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding='same')(x)
        x = BatchNormalization()(x)
        
        # --- BLOCK 2: Zein's 2D Spatial Extraction ---
        x = Conv2D(filters=64, kernel_size=(3, 3), padding='same')(x) # Increased filters for depth
        x = LeakyReLU(alpha=0.3)(x)
        x = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding='same')(x)
        x = BatchNormalization()(x)
        
        # --- TRANSITION: 2D Spatial to 1D Temporal Sequence ---
        # TimeDistributed(Flatten) squashes the remaining spatial features into a flat array 
        # while keeping the chronological Time dimension perfectly intact for the BiLSTM!
        x = TimeDistributed(Flatten())(x)
        
        # --- BLOCK 3: Temporal Sequence Learning ---
        lstm_out = Bidirectional(LSTM(self.units, return_sequences=True, recurrent_dropout=self.rec_drop))(x)
        
        # --- BLOCK 4: Attention Mechanism ---
        attention_out = Attention()([lstm_out, lstm_out])
        
        # --- BLOCK 5: Classification ---
        x = GlobalAveragePooling1D()(attention_out)
        x = Dropout(self.dropout_rate)(x)
        x = Dense(self.units, activation='relu')(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs, outputs)
        return model
    def cnn2d_deep_attention_bilstm_big(self):
        inputs = Input(shape=self.input_shape)
        
        # 1. Reshape for 2D CNN (Time, Subcarriers, Channels=1)
        x = Reshape((self.chunksize, self.n_features, 1))(inputs)
        
        # --- DYNAMIC KERNEL CALCULATION ---
        # Calculate 2D kernel size using square root to match 1D parameter count
        k_2d = int(self.kernel_size ** 0.5)
        
        # Ensure it is an odd number (standard practice for CNNs)
        if k_2d % 2 == 0:
            k_2d += 1
            
        # Ensure the absolute minimum is 3x3
        k_2d = max(3, k_2d)
        
        # --- BLOCK 1: Scaled-up 2D Spatial Extraction ---
        x = Conv2D(filters=self.num_filters, kernel_size=(k_2d, k_2d), padding='same')(x)
        x = LeakyReLU(alpha=0.3)(x)
        x = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)
        x = BatchNormalization()(x)
        
        # --- BLOCK 2: Scaled-up 2D Spatial Extraction ---
        x = Conv2D(filters=self.num_filters, kernel_size=(k_2d, k_2d), padding='same')(x) 
        x = LeakyReLU(alpha=0.3)(x)
        x = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='same')(x)
        x = BatchNormalization()(x)
        
        # --- TRANSITION: 2D Spatial to 1D Temporal Sequence ---
        x = TimeDistributed(Flatten())(x)
        
        # --- BLOCK 3: Temporal Sequence Learning ---
        lstm_out = Bidirectional(LSTM(self.units, return_sequences=True, recurrent_dropout=self.rec_drop))(x)
        
        # --- BLOCK 4: Attention Mechanism ---
        attention_out = Attention()([lstm_out, lstm_out])
        
        # --- BLOCK 5: Classification ---
        x = GlobalAveragePooling1D()(attention_out)
        x = Dropout(self.dropout_rate)(x)
        x = Dense(self.units, activation='relu')(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs, outputs)
        return model
    def cnn_bilstm(self):
        inputs = Input(shape=self.input_shape)
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(inputs)
        x = MaxPooling1D(pool_size=2)(x)
        x = Bidirectional(LSTM(self.units, return_sequences=False, recurrent_dropout=self.rec_drop))(x)
        x = Dropout(self.dropout_rate)(x)
        x = Dense(self.units, activation='relu')(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        model = Model(inputs, outputs)
        return model

    def bilstm(self):
        inputs = Input(shape=self.input_shape)
        x = Bidirectional(LSTM(self.units, return_sequences=True, recurrent_dropout=self.rec_drop))(inputs)
        x = Bidirectional(LSTM(self.units, return_sequences=False, recurrent_dropout=self.rec_drop))(x)
        x = Dropout(self.dropout_rate)(x) # <-- TYPO FIX: Was 0.s5
        x = Dense(self.units, activation='relu')(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        model = Model(inputs, outputs)
        return model

    def cnn_attention_bilstm(self):
        inputs = Input(shape=self.input_shape)
        # CNN part
        x = Conv1D(filters=self.num_filters, kernel_size=self.kernel_size, activation='relu')(inputs)
        x = MaxPooling1D(pool_size=2)(x)
        # BiLSTM part
        lstm_out = Bidirectional(LSTM(self.units, return_sequences=True, recurrent_dropout=self.rec_drop))(x)
        # Attention part
        # Using a simple Attention layer
        attention_out = Attention()([lstm_out, lstm_out])
        # Flatten or Global Pooling
        x = GlobalAveragePooling1D()(attention_out)
        x = Dropout(self.dropout_rate)(x)
        x = Dense(self.units, activation='relu')(x)
        outputs = Dense(self.num_classes, activation='softmax')(x)
        model = Model(inputs, outputs)
        return model
        
    def mlp(self):
        ##Para corrigir o mlp, precisamos estabilizar o fluxo de gradiente. A melhor maneira de fazer isso é com Batch Normalization. Isso normaliza a saída de uma camada antes de passá-la para a próxima, garantindo que as ativações relu não "morram" (fiquem todas negativas).
        inputs = Input(shape=self.input_shape)
        x = Flatten()(inputs)

        # Camada 1
        # Usar use_bias=False pois o BatchNormalization já tem um parâmetro de offset (beta)
        x = Dense(self.units, use_bias=False)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Dropout(self.dropout_rate)(x)

        # Camada 2
        x = Dense(self.units // 2, use_bias=False)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Dropout(self.dropout_rate)(x)

        outputs = Dense(self.num_classes, activation='softmax')(x)
        model = Model(inputs, outputs)
        return model

    def train_model(self):
        model = self.define_model()

        # --- RANDOM FOREST BRANCH ---
        if self.model_name == 'random_forest':
            print("Training Random Forest...")
            print(f"Input shape (3D): {self.X_train.shape}")
            
            # Flatten time series: (Samples, Time, Features) -> (Samples, Time * Features)
            X_train_flat = self.X_train.reshape(self.X_train.shape[0], -1)
            X_val_flat = self.X_val.reshape(self.X_val.shape[0], -1)
            
            print(f"Flattened shape (2D): {X_train_flat.shape}")

            # Train
            model.fit(X_train_flat, self.y_train)
            
            # Simple validation check
            val_acc = model.score(X_val_flat, self.y_val)
            print(f"Random Forest Validation Accuracy: {val_acc:.4f}")
            
            # Save using joblib (Keras save won't work)
            joblib.dump(model, self.model_path.replace('.h5', '.joblib'))
            
            # Return None for history
            return None, model
        # ----------------------------

        model.compile(optimizer='adam',
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])
        
        if low_vram:
            # Memory usage vs speed trade-off
            SHUFFLE_BUFFER = 1000
            # NEW: Stream data to GPU batch-by-batch to save memory
            train_ds = tf.data.Dataset.from_tensor_slices((self.X_train, self.y_train))
            train_ds = train_ds.shuffle(buffer_size=min(len(self.X_train), SHUFFLE_BUFFER)) \
                            .batch(self.batch_size) \
                            .prefetch(tf.data.AUTOTUNE)
            
            val_ds = tf.data.Dataset.from_tensor_slices((self.X_val, self.y_val)) \
                            .batch(self.batch_size) \
                            .prefetch(tf.data.AUTOTUNE)
        

        print(model.summary())
        
        

        # Save model plot
        try:
            plot_model(model, to_file=self.plot_path, show_shapes=True, show_layer_names=True)
        except Exception as e:
            print(f"Warning: Could not plot model (is graphviz installed?). Error: {e}")

        checkpoint = ModelCheckpoint(self.model_path,
                                     monitor=RESTORE_BEST_MODEL_METRIC,       # Change to val_loss
                                     save_best_only=True,
                                     mode='min' if RESTORE_BEST_MODEL_METRIC == 'val_loss' else 'max',               # Change to 'min' (lower loss is better)
                                     verbose=1)
        
        early_stopping = EarlyStopping(monitor=RESTORE_BEST_MODEL_METRIC,     # Change to val_loss
                                       patience=TRAINING_PATIENCE,            # Often good to increase patience slightly for loss
                                       restore_best_weights=RESTORE_BEST_MODEL,
                                       mode='min' if RESTORE_BEST_MODEL_METRIC == 'val_loss' else 'max',             # Explicitly set mode to 'min'
                                       verbose=1)

        
        if low_vram:
            history = model.fit(
                train_ds, # Use the dataset instead of raw arrays
                epochs=self.epochs,
                validation_data=val_ds,
                callbacks=[checkpoint, early_stopping],
                verbose=1
            )
        else:
            history = model.fit(self.X_train, self.y_train,
                                epochs=self.epochs,
                                batch_size=self.batch_size,
                                validation_data=(self.X_val, self.y_val),
                                callbacks=[checkpoint, early_stopping],
                                verbose=1)
        return history, model
            


    def evaluate_model(self, model):
        # Model is passed in, no need to load from disk
        # This uses the best weights restored by EarlyStopping
        
        # --- PREDICTION LOGIC ---
        if self.model_name == 'random_forest':
            # Flatten test data
            X_test_flat = self.X_test.reshape(self.X_test.shape[0], -1)
            # Predict classes directly
            y_pred = model.predict(X_test_flat)
        else:
            # Standard Keras Prediction
            y_pred_probs = model.predict(self.X_test)
            y_pred = np.argmax(y_pred_probs, axis=1)

        # --- FIX for Classification Report ---
        # Get the integer labels [0, 1, ..., num_classes-1]
        label_indices = self.label_indices 

        # Calculate metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred, average='weighted', labels=label_indices, zero_division=0)
        

        # Generate classification report
        report_str = classification_report(self.y_test, y_pred, 
                                           labels=label_indices, 
                                           target_names=self.labels, 
                                           output_dict=False,
                                           zero_division=0)
        report_dict = classification_report(self.y_test, y_pred, 
                                            labels=label_indices, 
                                            target_names=self.labels, 
                                            output_dict=True,
                                            zero_division=0)

        print(f"\n--- Evaluation for {self.model_name} C{self.chunksize} U{self.units} ---")
        print(report_str)

        # Generate confusion matrix
        cm = confusion_matrix(self.y_test, y_pred, labels=label_indices)
        
        # Set figure size based on number of classes
        # Make it larger for many classes
        fig_size = max(12, self.num_classes // 5) 
        
        plt.figure(figsize=(fig_size, fig_size))
        
        # Determine if annotations should be shown
        show_annot = self.num_classes <= 50 
        
        sns.heatmap(cm, annot=show_annot, fmt='d', cmap='Blues', 
                    xticklabels=self.labels, 
                    yticklabels=self.labels)
        
        plt.title(f'Confusion Matrix - {self.model_name} C{self.chunksize} U{self.units}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(self.cm_plot_path)
        plt.close()
        

        # --- NEW CODE START: Save Confusion Matrix to Text ---
        with open(self.cm_text_path, "w") as f:
            f.write("Labels Order:\n")
            f.write(str(list(self.labels)) + "\n\n")
            f.write("Confusion Matrix:\n")
            # Save as readable grid
            np.savetxt(f, cm, fmt='%d', delimiter='\t')

        print(f"Confusion matrix saved to {self.cm_text_path}")


        # --- PARAMS CALCULATION ---
        if self.model_name == 'random_forest':
            # Rough estimate: Trees * Nodes per tree (not perfect, but a proxy)
            # Or just set to 0 as it's not comparable to Neural Network params
            params = sum(tree.tree_.node_count for tree in model.estimators_) * 5 # Approx vars per node
            ops = 0 
        else:
            params = model.count_params()
            ops = params * 2

        # Save text report
        with open(self.report_path, 'w') as f:
            f.write(f"Model: {self.model_name}\n")
            f.write(f"Label Mode: {self.label_mode}\n") # <-- Adicionado ao relatório
            f.write(f"Chunksize: {self.chunksize}\n")
            f.write(f"Units: {self.units}\n")
            f.write(f"Epochs: {self.epochs}\n")
            f.write(f"Batch Size: {self.batch_size}\n")
            f.write("\n--- Model Summary ---\n")
            if self.model_name == 'random_forest':
                f.write(str(model))
            else:
                model.summary(print_fn=lambda x: f.write(x + '\n'))
            f.write("\n--- Classification Report ---\n")
            f.write(report_str)
            f.write("\n--- Performance Metrics ---\n")
            f.write(f"Accuracy: {accuracy:.4f}\n")
            f.write(f"Weighted F1-Score: {f1:.4f}\n")
            f.write(f"Parameters: {params}\n")
            f.write(f"Operations (Estimated): {ops}\n")
            # <--- ADDED SECTION: PRINT ALL ARGS --->
            f.write("--- Configuration Arguments ---\n")
            for arg, value in vars(args).items():
                f.write(f"{arg}: {value}\n")
            f.write("\n")
            # <--- END ADDED SECTION --->

        # --- NEW CODE START: Delete Model File to Save Space ---
        if os.path.exists(self.model_path):
            os.remove(self.model_path)
            print(f"Deleted .h5 model file: {self.model_path}")
        
        # Also check for .joblib (for Random Forest)
        joblib_path = self.model_path.replace('.h5', '.joblib')
        if os.path.exists(joblib_path):
            os.remove(joblib_path)
            print(f"Deleted .joblib model file: {joblib_path}")
        # --- NEW CODE END ---

        return accuracy, f1, params, ops, report_dict

if __name__ == '__main__':
    print(f"Running experiments with Label Mode: {args.label_mode}")
    # --- END ARGUMENT PARSER ---

    # --- 1. PROCESS UNITS ---
    if args.units_to_run == 'all':
        units_list = all_units
    else:
        # Split by comma and convert to int
        try:
            units_list = [int(x.strip()) for x in args.units_to_run.split(',')]
        except ValueError:
            print(f"Error: Invalid unit values provided: {args.units_to_run}")
            exit(1)

    # --- 2. PROCESS CHUNKSIZES ---
    if args.chunksize_to_run == 'all':
        chunksizes = all_chunksizes
    else:
        # Split by comma and convert to int
        try:
            chunksizes = [int(x.strip()) for x in args.chunksize_to_run.split(',')]
        except ValueError:
            print(f"Error: Invalid chunksize values provided: {args.chunksize_to_run}")
            exit(1)

    # --- 3. PROCESS MODELS ---
    if args.models_to_run == 'all':
        models_to_run = all_models
    else:
        # Split by comma and strip whitespace
        models_to_run = [x.strip() for x in args.models_to_run.split(',')]
        
        # Optional: Validate that the user didn't type a model name wrong
        for m in models_to_run:
            if m not in all_models:
                print(f"Error: Unknown model '{m}'. Valid choices are: {all_models}")
                exit(1)

    # --- 4. PROCESS SPLIT STRATEGY (If you want multiple strategies too) ---
    if args.split_strategy == 'all':
        split_strategies_to_run = split_strategies
    else:
        # If you want to allow comma-separated strategies like 'by_file,spatial_checkerboard':
        split_strategies_to_run = [x.strip() for x in args.split_strategy.split(',')]


    # --- Dynamic GPU Detection and Scaling ---
    if low_vram:
        BATCH_SIZE_CALC = 4096
    else:
        BATCH_SIZE_CALC = 8192 # Default for high VRAM systems


    # Scale BATCH_SIZE_CALC based on hardware capacity
    if "L40S" in gpu_name:
        BATCH_SIZE_CALC = 32768  # 4x increase for 48GB VRAM
        low_vram = False
        print(f">>> L40S Optimization: BATCH_SIZE_CALC increased to {BATCH_SIZE_CALC}, low_vram = false")
    elif "P40" in gpu_name:
        BATCH_SIZE_CALC = 16384  # 24GB VRAM limit
        low_vram = False
        print(f">>> P40 Optimization: BATCH_SIZE_CALC set to {BATCH_SIZE_CALC}, low_vram = false")
    else:
        #BATCH_SIZE_CALC = 32768  # 4x increase for 48GB VRAM
        print(f">>> Default GPU settings applied. low_vram = {low_vram}, BATCH_SIZE_CALC = {BATCH_SIZE_CALC}")
    
    num_filters = 128
    kernel_size = 20

    all_results = {}

    label_modes_to_run = [args.label_mode] if args.label_mode != 'all' else label_modes
    preprocess_choices = [args.preprocess_mode] if args.preprocess_mode != 'all' else preprocess_choices
    

    # --- Main Experiment Loop ---
    start_time_all = time.time()
    for split_strategy in split_strategies_to_run:
        print(f"\n\n########## Starting Experiments with Split Strategy: {split_strategy} ##########")
        for label_mode in label_modes_to_run:
            print(f"\n\n########## Starting Experiments with Label Mode: {label_mode} ##########")
            for preprocess_mode in preprocess_choices:
                print(f"\n\n########## Starting Experiments with Preprocess Mode: {preprocess_mode} ##########")
                
                # IMPORTANT: If we are splitting by spatial position, we generally still want to know the 
                # primary status (Sitting/Standing/Empty). 
                # However, if you want to classify position itself, this flag might need adjustment.
                # Only add position features if we are NOT holding out positions
                add_positional_features = (label_mode == 'primary_status' and split_strategy != 'spatial_checkerboard')

                if OMMITTING_POSITIONAL_FEATURES:
                    add_positional_features = False

                for model_name in models_to_run:
                    print(f"\n{'='*30}\nRunning Model: {model_name}\n{'='*30}")
                    
                    if model_name == 'multi_branch_model' and preprocess_mode != 'multi_branch_fusion':
                        print(f"Skipping {model_name} for preprocess mode {preprocess_mode} (incompatible)")
                        continue
                    
                    # Prepare result strings for this model
                    results_acc = ""
                    results_f1 = ""
                    results_params = ""
                    results_ops = ""
                    
                    # Create labels for the results matrix
                    units_labels = "Units_List = [" + " ".join(map(str, units_list)) + "];"
                    chunksize_labels = "Chunksize_List = [" + " ".join(map(str, chunksizes)) + "];"

                    all_results[model_name] = {}

                    for chunk in chunksizes:
                        all_results[model_name][chunk] = {}
                        #if chunk >= 64: MAX_SAMPLES_PER_CLASS = 16000;
                        #else: MAX_SAMPLES_PER_CLASS = 16000;

                        #dynamic_batch_size = max(8, BATCH_SIZE_CALC // chunk) if low_vram else BATCH_SIZE
                        dynamic_batch_size = max(8, BATCH_SIZE_CALC // chunk)

                        acc_row = ""
                        f1_row = ""
                        params_row = ""
                        ops_row = ""

                        for units in units_list:
                            print(f"\n--- Starting {model_name} | Chunksize: {chunk} | Units: {units} | Label Mode: {label_mode} ---")
                            start_time_model = time.time()
                            
                            my_model = MyModel(
                                model_name=model_name,
                                chunksize=chunk,
                                units=units,
                                num_filters=num_filters,
                                kernel_size=kernel_size,
                                epochs=EPOCHS,
                                batch_size=dynamic_batch_size,
                                label_mode=label_mode,
                                split_strategy=split_strategy,
                                preprocess_mode=preprocess_mode, # <--- Pass the arg
                                dropout_rate=DROPOUT_RATE,
                                run_id=args.run_id,
                                positions_to_keep=args.positions_to_keep,
                                dataset_index=args.dataset_index # <--- PASS THE ARG HERE
                            )

                            # --- VERIFICAR SE O RELATÓRIO JÁ EXISTE --- # <<< MUDANÇA
                            if SKIPPING_ALREADY_GENERATED and os.path.exists(my_model.report_path):
                                print(f"Skipping: Report already exists at {my_model.report_path}")
                                
                                # Adiciona placeholders de falha ao relatório final (como em outros erros)
                                acc_row += "0.0 "
                                f1_row += "0.0 "
                                params_row += "0 "
                                ops_row += "0 "
                                
                                # Limpa o objeto recém-criado e pula para a próxima iteração
                                del my_model
                                gc.collect()
                                continue
                            # --- FIM DA VERIFICAÇÃO --- # <<< MUDANÇA

                            # Load and split data
                            if not my_model.split_data(files=files,add_positional_features=add_positional_features):
                                print("Skipping this configuration due to data split error.")
                                acc_row += "0.0 "
                                f1_row += "0.0 "
                                params_row += "0 "
                                ops_row += "0 "
                                
                                # --- MEMORY CLEANUP ---
                                K.clear_session()
                                del my_model
                                gc.collect()
                                # --- END MEMORY CLEANUP ---
                                continue

                            # Train model
                            try:
                                history, model = my_model.train_model() # Get model object back
                            except Exception as e:
                                print(f"Error during training: {e}")
                                acc_row += "0.0 "
                                f1_row += "0.0 "
                                params_row += "0 "
                                ops_row += "0 "
                                
                                # --- MEMORY CLEANUP ---
                                K.clear_session()
                                del my_model
                                gc.collect()
                                # --- END MEMORY CLEANUP ---
                                continue
                            
                            # Evaluate model
                            try:
                                # Pass the trained model to evaluation
                                # This uses the model with best weights restored by EarlyStopping
                                acc, f1, params, ops, report_dict = my_model.evaluate_model(model)
                            except Exception as e:
                                print(f"Error during evaluation: {e}")
                                acc, f1, params, ops, report_dict = 0, 0, 0, 0, None

                            end_time_model = time.time()
                            print(f"--- Finished {model_name} C{chunk} U{units} in {end_time_model - start_time_model:.2f}s ---")
                            
                            # Store results
                            all_results[model_name][chunk][units] = report_dict
                            acc_row += f"{acc:.4f} "
                            f1_row += f"{f1:.4f} "
                            params_row += f"{params} "
                            ops_row += f"{ops} "
                            
                            # --- !! MEMORY CLEANUP !! ---
                            K.clear_session()
                            del my_model.X_train, my_model.X_val, my_model.X_test # Explicitly free massive arrays
                            del my_model, model, history
                            gc.collect()
                            # --- !! END MEMORY CLEANUP !! ---

                        # Add the completed row to the results string
                        results_acc += f"{acc_row}\n"
                        results_f1 += f"{f1_row}\n"
                        results_params += f"{params_row}\n"
                        results_ops += f"{ops_row}\n"

                    # --- Finalize report string for this model ---
                    report = (f"{units_labels}\n{chunksize_labels}\n\n"
                            f"Accuracy = [\n{results_acc}];\n\n"
                            f"F1_Score_Weighted = [\n{results_f1}];\n\n"
                            f"Parameters = [\n{results_params}];\n\n"
                            f"Ops = [\n{results_ops}];")
                    
                    id_suffix = f"_{args.run_id}" if args.run_id else ""

                    # --- MUDANÇA: Adicionar label_mode E split_strategy ao nome do relatório final ---
                    final_report_path = f"results/FINAL_REPORT_{model_name}_P-{preprocess_mode}_L-{label_mode}_S-{split_strategy}{id_suffix}.txt"
                    with open(final_report_path, 'w') as f:
                        f.write(report)
                    print(f"\nFinal report for {model_name} (Mode: {label_mode}, Preproces: {preprocess_mode}, Split: {split_strategy}) saved to {final_report_path}")

            # --- MUDANÇA: Adicionar label_mode E split_strategy ao nome do JSON final ---
            id_suffix = f"_{args.run_id}" if args.run_id else ""
            json_path = f"results/all_model_results_P-{preprocess_mode}_L-{label_mode}_S-{split_strategy}{id_suffix}.json"
            with open(json_path, 'w') as f:
                json.dump(all_results, f, indent=4)
            print(f"All results JSON saved to {json_path}")
        
    end_time_all = time.time()
    print(f"\n{'='*30}\nAll experiments for mode (Split: {split_strategy}) finished in {end_time_all - start_time_all:.2f}s\n{'='*30}")