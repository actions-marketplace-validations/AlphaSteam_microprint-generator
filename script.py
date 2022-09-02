import os
import requests
from microprint_generator import generate_raster_microprint_from_text, generate_svg_microprint_from_text 
from pathlib import Path
import re
class Api:

    def __init__(self, repo, owner, token):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/actions/"

    def get(self, url):
        return requests.get(self.base_url + url, headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github+json"
            })

        
def get_job_by_name(job_name, job_list):

    for _, job_obj in enumerate(job_list):
        if job_obj["name"] == job_name:
            return job_obj


def get_job_id(api, job_name, run_id):

    all_jobs = api.get(f"runs/{run_id}/jobs").json()

    all_jobs = all_jobs["jobs"]

    job = get_job_by_name(job_name, all_jobs)

    return job["id"]


def setup_api():

    repository = os.environ['INPUT_REPOSITORY'].split("/")
    
    owner = repository[0]

    repo = repository[1]

    token = os.environ['INPUT_GITHUB_TOKEN']

    return Api(repo, owner, token)


def get_logs(api):
    
    job_name = os.environ['INPUT_JOB_NAME']
        
    run_id = os.environ['GITHUB_RUN_ID']

    current_job_id = get_job_id(api, job_name, run_id)
    
    current_job_logs = api.get(f"jobs/{current_job_id}/logs").text

    save_path = Path(os.environ['INPUT_LOG_PATH']) / (os.environ['INPUT_LOG_FILENAME'] + ".txt")

    if os.environ['INPUT_SAVE_LOG'] == "true":
        with open(save_path, 'w') as file:
            file.write(current_job_logs)

    return current_job_logs
    
def remove_ansi_escape_sequences(text):

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    return ansi_escape.sub('', text)
    
def main():
    api = setup_api()

    logs = get_logs(api)

    logs = remove_ansi_escape_sequences(logs)

    microprint_filename = Path(os.environ['INPUT_MICROPRINT_PATH']) 

    scale = int(os.environ['INPUT_MICROPRINT_SCALE'])

    if os.environ['INPUT_MICROPRINT_RENDER_METHOD'] == "svg":
        microprint_filename = microprint_filename / (os.environ['INPUT_MICROPRINT_FILENAME'] +".svg")

        generate_svg_microprint_from_text(logs, output_filename=microprint_filename, scale=scale)
    else:
        microprint_filename = microprint_filename / (os.environ['INPUT_MICROPRINT_FILENAME'] +".png")

        generate_raster_microprint_from_text(logs, output_filename=microprint_filename, scale=scale)

if __name__ == "__main__":
    main()

