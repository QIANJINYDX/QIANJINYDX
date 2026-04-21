import requests
from huggingface_hub import HfApi

USERNAME = "AI4Protein"
README_PATH = "profile/README.md"
MODEL_LOG_FILE = "log_model_download.txt"
DATASET_LOG_FILE = "log_dataset_download.txt"

def get_github_stats(username):
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    response = requests.get(repos_url)
    repos = response.json()

    if isinstance(repos, dict) and "message" in repos:
        raise Exception(f"GitHub API error: {repos['message']}")

    total_stars = sum(repo["stargazers_count"] for repo in repos)
    total_forks = sum(repo["forks_count"] for repo in repos)
    return total_stars, total_forks

def get_downloads():
    total_model_downloads, total_dataset_downloads = 0, 0
    with open(MODEL_LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            total_model_downloads += int(line.split(',')[1])
            
    with open(DATASET_LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            total_dataset_downloads += int(line.split(',')[1])
    
    # 加上千分位
    total_model_downloads = "{:,}".format(total_model_downloads)
    total_dataset_downloads = "{:,}".format(total_dataset_downloads)
    
    return total_model_downloads, total_dataset_downloads

def update_readme(stars, forks, model_downloads, dataset_downloads):
    with open(README_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "<!-- 🔄 stars -->" in line:
            lines[i] = f"![Total Stars](https://img.shields.io/badge/Stars-{stars}-blue?logo=github&style=flat-square) <!-- 🔄 stars -->\n"
        if "<!-- 🔄 forks -->" in line:
            lines[i] = f"![Total Forks](https://img.shields.io/badge/Forks-{forks}-blue?logo=github&style=flat-square) <!-- 🔄 forks -->\n"
        if "<!-- 🔄 total_hf_models -->" in line:
            lines[i] = f"![Total Model Downloads](https://img.shields.io/badge/Total%20Model%20Downloads-{model_downloads}-orange?logo=huggingface&style=flat-square) <!-- 🔄 total_hf_models -->\n"
        if "<!-- 🔄 total_hf_datasets -->" in line:
            lines[i] = f"![Total Dataset Downloads](https://img.shields.io/badge/Total%20Dataset%20Downloads-{dataset_downloads}-orange?logo=huggingface&style=flat-square) <!-- 🔄 total_hf_datasets -->\n"
            
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    try:
        stars, forks = get_github_stats(USERNAME)
        model_downloads, dataset_downloads = get_downloads()
        update_readme(stars, forks, model_downloads, dataset_downloads)
        print(f"✅ Updated profile/README.md — Stars: {stars}, Forks: {forks}")
    except Exception as e:
        print(f"❌ Error: {e}")
