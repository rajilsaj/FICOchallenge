## FICO Educational Challenge 2026

This repository contains the work for the **FICO Educational Challenge 2026**, focused on building a machine learning system for **intent classification in customer collections conversations** using **synthetic data**.

The project follows an end-to-end ML lifecycle: data generation, model training and evaluation, and final implementation and optimization.


##  Getting Started (For Collaborators)

Follow these steps to set up the project and start contributing.

### 1. Clone the Repository
```bash
git clone https://github.com/rajilsaj/FICOchallenge.git
cd FICOchallenge
```

### 2. Google Colab & Drive Setup
The notebooks are designed to run in **Google Colab** and require a specific folder structure in your **Google Drive** to load and save data.

**Important:** Once you open a notebook in Colab from the links below, you **must** go to `File > Save a copy in Drive` to save it to your own account before running it.

#### A. Google Drive Structure
Create the following folders in your **Google Drive** (`My Drive`):

```text
My Drive/
└── FICO Analytic Challenge/
    ├── Week_05/
    ├── Week_04/
    ├── Week_03/
    ├── Week_02/
    ├── Week_01/
    ├── Model/
    └── Data/
```

#### B. Opening Notebooks in Colab
You can open the notebooks directly from GitHub using the links below:

| Notebook | Link |
| :--- | :--- |
| **Week 3: Synthetic Data** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rajilsaj/FICOchallenge/blob/main/notebooks/Week_3_Synthetic_Data.ipynb) |
| **Week 5: Data Preparation** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rajilsaj/FICOchallenge/blob/main/notebooks/Week_5_DataPreparation_forModelTraining.ipynb) |
| **Week 5: BERT Fine-tuning** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rajilsaj/FICOchallenge/blob/main/notebooks/Week_5_LLM_Classifier_Finetuning_BERT.ipynb) |
| **Week 5: Qwen Fine-tuning** | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rajilsaj/FICOchallenge/blob/main/notebooks/Week_5_LLM_Classifier_Finetuning_Qwen.ipynb) |

### 3. Running & Testing
To test the notebooks on your side:
1. **Mount Google Drive:** Every notebook starts with a cell to mount your Google Drive. Follow the authentication prompt.
2. **Verify Paths:** Ensure the paths in the "Import Libraries and Set up Folder Paths" section of each notebook match your Drive structure.
3. **Run All Cells:** Use `Runtime > Run all` in Google Colab.
4. **Output Verification:** 
   - **Week 3:** Check `Data/` for generated synthetic conversations.
   - **Week 5 (Prep):** Check `Data/` for `_train`, `_test`, and `_validation` splits.
   - **Week 5 (Training):** Check the `Model/` folder for saved weights and evaluation logs.

