import os
from pathlib import Path

# --- 1. BASE ANCHORS AND DIRECTORIES ---
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
# Defining this here ensures add_logo.py finds it immediately
UTILS_DIR = BASE_PATH 

# Hardcoded to C: Drive to remove USB dependency
DRIVE_ROOT = "C:\\"
GIT_FOLDER = os.path.join(DRIVE_ROOT, "git")

# --- 2. REPOSITORY AND TOOL PATHS ---
TEMPLATES_PROJ = os.path.join(GIT_FOLDER, "ages-alwb-templates", "net.ages.liturgical.workbench.templates")

# Removed USB tool detection; hardcoded to C: drive resource path
TOOLS_BASE = os.path.join(DRIVE_ROOT, "ALWB_Additional_Resources")

# --- 3. GENERATION AND TEMPLATE SETTINGS ---
ATEM_DIRECTORY = os.path.join(TEMPLATES_PROJ, "c-generator-settings")
CLIENTS_BASE = os.path.join(TEMPLATES_PROJ, "b-preferences")
BASE_TEMPLATES_DIR = os.path.join(TEMPLATES_PROJ, "a-templates", "Dated-Services")
SRC_GEN_BASE = os.path.join(TEMPLATES_PROJ, "src-gen", "website")
COVERS_DIR = os.path.join(GIT_FOLDER, "ages-alwb-templates", "net.ages.liturgical.workbench.templates", "a-templates", "Pdf_Covers")

# --- 4. CONFIGURATION AND STATE FILES ---
ATEM_FILE = os.path.join(ATEM_DIRECTORY, "generator.atem")
MASTER_ARES = os.path.join(ATEM_DIRECTORY, "pref.master.templates.ares")
TARGET_FILE = os.path.join(ATEM_DIRECTORY, "pref.generation_alwb.ares")

CONFIG_DIR = os.path.join(DRIVE_ROOT, "_ALWB_py_utils_config")
CONTEXT_FILE = os.path.join(CONFIG_DIR, "client_context.txt")
STATUS_PRESET_FILE = os.path.join(CONFIG_DIR, "status_preset.txt")

# --- 5. ENVIRONMENT AND EXECUTABLES ---
# Hardcoded to C: Drive paths (MOTHERSHIP)
WORKSPACE_IDENTIFIER = r"C:\ALWB_WORKSPACES\Workspace-git-Oxygen02"
ECLIPSE_EXE = r"C:\Users\AGES user\eclipse\java-oxygen2\eclipse\eclipse.exe"
JAVA_HOME = r"C:\Program Files\Java\jre1.8.0_461"

JAVA_EXE = os.path.join(JAVA_HOME, "bin", "java.exe")

# --- 6. ALIASES AND COMPATIBILITY ---
BASE_DIR = CLIENTS_BASE             
PRESET_STATUS = STATUS_PRESET_FILE  
GENERATOR_FILE = ATEM_FILE          
LOGO_ICON_PATH = os.path.join(BASE_PATH, "logo.png")

# Path objects for Dashboard compatibility
DERIVED_WEBSITE_BASE = Path(SRC_GEN_BASE) 
SCAN_PATH = Path(SRC_GEN_BASE) / "test" / "dcs" / "h" / "s"