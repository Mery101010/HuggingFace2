import os
import git
import subprocess
import venv

#cloning the repository
def clone_repository(repo_url, dest_dir):
    if os.path.exists(dest_dir):
        print(f"Directory {dest_dir} already exists. Skipping clone.")
        return True

    try:
        git.Repo.clone_from(repo_url, dest_dir)
        print(f"Repository cloned to {dest_dir}")
        return True
    except Exception as e:
        return f"Failed to clone repository: {e}"

#setting up  the virtual environment
def setup_virtual_env(repo_dir):
    venv_dir = os.path.join(repo_dir, "venv")
    try:
        venv.create(venv_dir, with_pip=True)
        print("Virtual environment set up.")
        return venv_dir
    except Exception as e:
        return f"Failed to set up virtual environment: {e}"

#installing dependencies from requirements.txt
def install_dependencies(venv_dir, repo_dir):
    requirements_file = os.path.join(repo_dir, "requirements.txt")
    pip_executable = os.path.join(venv_dir, "bin", "pip")

    if os.path.exists(requirements_file):
        try:
            subprocess.run([pip_executable, "install", "-r", requirements_file], check=True)
            print("Dependencies installed.")
            return True
        except Exception as e:
            return f"Failed to install dependencies: {e}"
    else:
        return "requirements.txt not found, skipping dependency installation."

#handling missing files (if requirements.txt or data is missing)
def handle_missing_files(repo_dir):
    #ensuring a requirements.txt exists
    requirements_file = os.path.join(repo_dir, "requirements.txt")
    if not os.path.exists(requirements_file):
        with open(requirements_file, "w") as f:
            f.write("numpy\npandas\nscikit-learn")  # Example default packages
        print("Created a default requirements.txt file.")

    #ensuring a data directory exists
    data_dir = os.path.join(repo_dir, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print("Created a data directory.")

#finding the main file 
def find_main_file(repo_dir):
    possible_main_files = ["main.py", "app.py", "run.py", "model.py"]
    for filename in possible_main_files:
        if os.path.exists(os.path.join(repo_dir, filename)):
            return filename
    raise FileNotFoundError("Main file not found.")

#running the model
def run_model(venv_dir, repo_dir):
    main_file = find_main_file(repo_dir)
    python_exec = os.path.join(venv_dir, "bin", "python")
    try:
        result = subprocess.run(
            [python_exec, os.path.join(repo_dir, main_file)], capture_output=True, text=True
        )
        print(f"Model output from {main_file}:\n{result.stdout}")
        print(f"Errors (if any):\n{result.stderr}")
        return result.stdout, result.stderr
    except Exception as e:
        return f"Failed to run the model: {e}", ""


#evaluating the model output
def evaluate_model(output):
    if "Accuracy:" in output:
        accuracy = float(output.split("Accuracy:")[1].split()[0])
        return accuracy
    return None

#processing the repository and evaluate it
def process_repository(repo_url):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_dir = os.path.join("/tmp", repo_name)

    #cloning the repository
    clone_result = clone_repository(repo_url, repo_dir)
    if isinstance(clone_result, str):  # Error message
        print(clone_result)
        return

    #handling missing files if necessary
    handle_missing_files(repo_dir)

    #setting up the virtual environment
    venv_dir = setup_virtual_env(repo_dir)
    if isinstance(venv_dir, str):  # Error message
        print(venv_dir)
        return

    #installing dependencies
    install_result = install_dependencies(venv_dir, repo_dir)
    if isinstance(install_result, str):  # Error message
        print(install_result)
    
    #running the model
    output, error = run_model(venv_dir, repo_dir)
    if error:
        print(f"Error in {repo_name}: {error}")
        return

    #evaluating the model
    accuracy = evaluate_model(output)
    if accuracy is not None:
        leaderboard.append((repo_name, accuracy))
    else:
        print(f"Failed to evaluate {repo_name}")

#creating a leaderboard for the repositories
leaderboard = []

#example repos
repositories = [
    "https://github.com/IllinoisGraphBenchmark/IGB-Datasets.git", 
    # "https://github.com/benedekrozemberczki/karateclub.git"
]

for repo in repositories:
    process_repository(repo)

#sorting the leaderboard by accuracy
leaderboard.sort(key=lambda x: x[1], reverse=True)

#displaying the leaderboard
print("\nLeaderboard:")
for rank, (repo_name, accuracy) in enumerate(leaderboard, start=1):
    print(f"{rank}. {repo_name}: {accuracy:.2f}")
