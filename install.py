import subprocess
import sys
import os

def ensure_virtual_environment():
    venv_dir = ".venv"
    # Check if .venv exists; if not, create it.
    if not os.path.exists(venv_dir):
        print("Virtual environment (.venv) not found. Creating one...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        print("Virtual environment created.")

    # Determine the path to the virtual environment's python executable.
    if os.name == "nt":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")

    # If the current interpreter is not the one from the virtual environment, re-launch.
    if os.path.abspath(sys.executable) != os.path.abspath(venv_python):
        print("Re-launching the script using the virtual environment's interpreter...")
        subprocess.check_call([venv_python] + sys.argv)
        sys.exit(0)

def ensure_env_file():
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"{env_file} not found. Creating one...")
        openai_api_key = input("Please enter your OPENAI_API_KEY: ")
        with open(env_file, "w") as f:
            f.write(f"OPENAI_API_KEY={openai_api_key}\n")
        print(f"{env_file} has been created with your OPENAI_API_KEY.")
    else:
        print(f"{env_file} file already exists.")

def install_requirements():
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        print("Installing dependencies from requirements.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as error:
            print(f"An error occurred during installation: {error}")
            sys.exit(1)
    else:
        print("requirements.txt not found. Please ensure it exists in the project directory.")
        sys.exit(1)

def run_gradio_app():
    print("Launching the Gradio app...")
    subprocess.check_call([sys.executable, "voicebot.py"])

if __name__ == "__main__":
    ensure_virtual_environment()
    ensure_env_file()
    install_requirements()
    run_gradio_app()
