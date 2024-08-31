from CONFIG import GITHUB_TOKEN
from api_client import APIClient
from datetime import datetime
import os


class GithubClient(APIClient):
    def __init__(self):
        self.domain = 'github.com'
        self.api_url = 'https://api.github.com'
        super().__init__(token=GITHUB_TOKEN)

    @property
    def service(self):
        return 'github'

    def _get_user(self):
        user = self._get(url=f'{self.api_url}/user')
        return user['login'], user['id']

    def _get_projects(self):
        projects = self._get(
            url=f'{self.api_url}/user/repos'
        )
        return {project['name']: project['id'] for project in projects}

    def get_last_commit_date(self, repo):
        if repo in self.projects_id:
            commits = self._get(
                url=f'{self.api_url}/repos/{self.user_name}/{repo}/commits',
                params={'per_page': 1}
            )
            if commits:
                date_str = commits[0]['commit']['committer']['date']
                date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                return date

    def get_project_link(self, project_name):
        return super().get_project_link(project_name)

    def get_token_repo_url(self, project_name) -> str:
        return super().get_token_repo_url(project_name)

    def create_project(self, project_name, project_link):
        if project_name not in self.projects_id:
            response = self._post(
                url=f'{self.api_url}/user/repos',
                json={
                    'name': project_name,
                    'description': f'Mirror of {project_link}'
                }
            )
            self.projects_id[project_name] = response['id']
            return response['html_url']


if __name__ == "__main__":
    from pprint import pprint
    github = GithubClient()
    print(github.user_id)
    print(github.user_name)
    # print(github.get_last_commit_date('NginxProxyManagerHelper'))
    # github.create_project('test_project1', 'test_original_link.com')
    # print(github.get_token_repo_url('test_project'))