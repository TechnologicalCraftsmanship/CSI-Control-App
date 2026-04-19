# Dataset Description

This folder contains the raw Channel State Information (CSI) datasets used in the experiments of the CSI Control App.

## 📦 Available Files

The dataset is organized into five compressed files, each corresponding to a different user. Each `.zip` file contains a single `.csv` file with the exact same name.

* `csi_U1.zip` $\rightarrow$ `csi_U1.csv`
* `csi_U2.zip` $\rightarrow$ `csi_U2.csv`
* `csi_U3.zip` $\rightarrow$ `csi_U3.csv`
* `csi_U4.zip` $\rightarrow$ `csi_U4.csv`
* `csi_U5.zip` $\rightarrow$ `csi_U5.csv`

> **⚠️ Important:** All `.zip` files must be extracted before use.

## 🧪 Scenario Encoding

Each data sample includes a field called `cenario`, which encodes the experimental setup using the following format:

`C_R_Ux_State_AV_EAV`

**Where:**
* $C$ $\rightarrow$ Chair column index
* $R$ $\rightarrow$ Chair row index
* $U_x$ $\rightarrow$ User identifier (e.g., `U1`, `U2`, ..., `U5`)
* $State$ $\rightarrow$ State of the chair:
  * $EP$ $\rightarrow$ Standing
  * $ES$ $\rightarrow$ Seated
  * $EV$ $\rightarrow$ Empty
* $AV\\_EAV$ $\rightarrow$ Reserved for future extensions (e.g., additional users or states)

### 📌 Example

**`3_2_U4_EP_AV_EAV`**

* **Column:** 3
* **Row:** 2
* **User:** U4
* **State:** Standing (EP)

## 📊 Data Fields

Each `.csv` file contains the following columns:

`csv
"id","data_hora","cenario","type","seq","mac","rssi","rate","sig_mode","mcs","bandwidth","smoothing","not_sounding","aggregation","stbc","fec_coding","sgi","noise_floor","ampdu_cnt","channel","secondary_channel","local_timestamp","ant","sig_len","rx_state","len","first_word","data"`

## 🧾 Field Description

| Field | Description |
| :--- | :--- |
| **`id`** | Unique packet identifier |
| **`data_hora`** | Timestamp (ISO 8601 format) |
| **`cenario`** | Encoded experimental scenario |
| **`type`** | Data type (e.g., `CSI_DATA`) |
| **`seq`** | Sequence number |
| **`mac`** | MAC address of the transmitter |
| **`rssi`** | Received Signal Strength Indicator |
| **`rate`** | Transmission rate |
| **`sig_mode`** | Signal mode |
| **`mcs`** | Modulation and Coding Scheme |
| **`bandwidth`** | Channel bandwidth |
| **`smoothing`** | Smoothing applied |
| **`not_sounding`** | Not sounding flag |
| **`aggregation`** | Aggregation status |
| **`stbc`** | Space-Time Block Coding |
| **`fec_coding`** | Forward Error Correction coding |
| **`sgi`** | Short Guard Interval |
| **`noise_floor`** | Noise floor measurement |
| **`ampdu_cnt`** | A-MPDU count |
| **`channel`** | Primary channel |
| **`secondary_channel`** | Secondary channel |
| **`local_timestamp`** | Local device timestamp |
| **`ant`** | Antenna index |
| **`sig_len`** | Signal length |
| **`rx_state`** | Receiver state |
| **`len`** | Length of the CSI payload |
| **`first_word`** | First word of the CSI data |
| **`data`** | Raw CSI data array |
