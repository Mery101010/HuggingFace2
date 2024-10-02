from transformers.tools import HfAgent
import subprocess
import os
import git
import venv

#initialize the agent with a valid model endpoint
agent = HfAgent(url_endpoint="https://api-inference.huggingface.co/models/openai/gpt-3.5-turbo")

#cloning repository
def clone_repository(repo_url, dest_dir):
    try:
        git.Repo.clone_from(repo_url, dest_dir)
        return True
    except Exception as e:
        return f"Failed to clone repository: {e}"

#setting up the virtual environment
def setup_virtual_env(repo_dir):
    venv_dir = os.path.join(repo_dir, "venv")
    venv.create(venv_dir, with_pip=True)
    return venv_dir

#installing dependencies
def install_dependencies(venv_dir, repo_dir):
    requirements_file = os.path.join(repo_dir, "requirements.txt")
    pip_executable = os.path.join(venv_dir, "bin", "pip")

    if os.path.exists(requirements_file):
        try:
            subprocess.run([pip_executable, "install", "-r", requirements_file], check=True)
            return True
        except Exception as e:
            return f"Failed to install dependencies: {e}"
    return "requirements.txt not found."

#handling missing files
def handle_missing_files(repo_dir):
    required_files = ["requirements.txt", "main.py", "data/"]
    for file in required_files:
        if not os.path.exists(os.path.join(repo_dir, file)):
            if file == "requirements.txt":
                with open(os.path.join(repo_dir, "requirements.txt"), "w") as f:
                    f.write("numpy\npandas\nscikit-learn")
            elif file == "data/":
                os.makedirs(os.path.join(repo_dir, "data"))

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
        return result.stdout, result.stderr
    except Exception as e:
        return f"Failed to run the model: {e}", ""

def evaluate_model(output):
    if "Accuracy:" in output:
        accuracy = float(output.split("Accuracy:")[1].split()[0])
        return accuracy
    return None

#creating a leaderboard
leaderboard = []

def process_repository(repo_url):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_dir = os.path.join("/tmp", repo_name)

    #cloning the repository or skip if it already exists
    clone_result = clone_repository(repo_url, repo_dir)
    if isinstance(clone_result, str):  # error message
        print(clone_result)

    #handling missing files, this will create the default files if they are missing
    handle_missing_files(repo_dir)

    #setting up the virtual environment
    venv_dir = setup_virtual_env(repo_dir)
    
    # Install dependencies
    install_result = install_dependencies(venv_dir, repo_dir)
    if isinstance(install_result, str):  # error message
        print(install_result)

    #running the model, regardless of whether the repo was just cloned or skipped
    output, error = run_model(venv_dir, repo_dir)
    if error:
        print(f"Error in {repo_name}: {error}")
        return

    #evaluating the model output
    accuracy = evaluate_model(output)
    if accuracy is not None:
        leaderboard.append((repo_name, accuracy))
    else:
        print(f"Failed to evaluate {repo_name}")

#example repositories
repositories = [
    "https://github.com/lukecavabarrett/pna.git", 
    "https://github.com/benedekrozemberczki/karateclub.git"
]

for repo in repositories:
    process_repository(repo)

#sorting the leaderboard
leaderboard.sort(key=lambda x: x[1], reverse=True)

#displaying the leaderboard
print("\nLeaderboard:")
for rank, (repo_name, accuracy) in enumerate(leaderboard, start=1):
    print(f"{rank}. {repo_name}: {accuracy:.2f}")
