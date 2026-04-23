# 📖 Installation Guide - Ossama's App

## 🖥️ Windows Installation

### Step 1: Download Python
- Visit [python.org](https://www.python.org/downloads/)
- Download **Python 3.11 or higher**
- Run the installer
- ✅ **IMPORTANT:** Check the box "Add Python to PATH"
- Click **"Install Now"**

### Step 2: Download the Project
**Option A:  Manual Download**

- Click the green **"Code"** button on GitHub
- Click **"Download ZIP"**
- Extract the folder
- Open Command Prompt in that folder

**Option B : Using Git (Recommended)**
```bash
git clone https://github.com/OSSAMA-dev7/OssamasApp.git
cd OssamasApp
```

### Step 3: Create Virtual Environment
- Open Command Prompt and type:

```Bash

python -m venv venv
venv\Scripts\activate.bat
```
- You should see (venv) at the start of your command line.

### Step 4: Install Required Packages
````Bash

pip install --upgrade pip
pip install -r requirements.txt
````

### Step 5: Download Voice Models

- You need ONE or BOTH of these:

**English Model (Recommended - Fast)**

- Download: **vosk-model-small-en-us-0.15.zip**
  
- from [ALPHAei.com](https://alphacephei.com/vosk/models)
  
- Extract the ZIP file
  
- Rename the extracted folder to: **model_en**

- Move it to your project folder: **C:\path\to\OssamasApp\model_en**
  
**Arabic Model**

- Download: **vosk-model-ar-mgb2-0.4.zip**
  
  - from [ALPHAei.com](https://alphacephei.com/vosk/models)
    
- Extract the ZIP file
  
- Rename the extracted folder to: **model_ar**
  
- Move it to your project folder: **C:\path\to\OssamasApp\model_ar**
  
- Your folder should look like:


OssamasApp/

  ├── ossamas_app.py

  ├── model_en/    (English)

  ├── model_ar/          (Arabic)

  ├── requirements.txt

  ├── README.md

  └── venv/

### Step 6: Run the App
````Bash

python ossamas_app.py
````
**The app window will open! 🎉**

### 🍎 Mac/Linux Installation
## Step 1: Install Python (if not installed)
````Bash

brew install python3.11    # Mac
sudo apt-get install python3.11    # Linux
````
## Step 2: Download the Project
````Bash

git clone https://github.com/OSSAMA-dev7/OssamasApp.git
cd OssamasApp

````
Step 3: Create Virtual Environment
````Bash

python3.11 -m venv venv
source venv/bin/activate
````
### Step 4: Install Packages
````Bash

pip install --upgrade pip
pip install -r requirements.txt
````
## Step 5: Download Models
***Same as Windows (Steps above)***

## Step 6: Run the App
````Bash

python ossamas_app.py
````

