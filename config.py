import os
import dotenv
from os.path import abspath, dirname, join

env_filepath = join(dirname(abspath(__file__)), '.env')
dotenv.load_dotenv(env_filepath)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN', '')
