from CONFIG import GITLAB_TOKEN
from api_client import APIClient
from datetime import datetime
import os


class GitlabClient(APIClient):
    def __init__(self):
        self.domain = 'gitlab.com'
        self.api_url = 'https://gitlab.com/api/v4'
        super().__init__(token=GITLAB_TOKEN)

    @property
    def service(self):
        return 'gitlab'

    def _get_user(self):
        user = self._get(url=f'{self.api_url}/user')
        return user['username'], user['id']

    def _get_projects(self):
        projects = self._get(
            url=f'{self.api_url}/users/{self.user_name}/projects'
        )
        return {project['name']: project['id'] for project in projects}

    def get_last_commit_date(self, repo):
        if repo in self.projects_id:
            commits = self._get(
                url=f'{self.api_url}/projects/{self.projects_id[repo]}/repository/commits',
                params={'per_page': 1}
            )
            if commits:
                date_str = commits[0]['committed_date']
                date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
                return date

    def get_project_link(self, project_name):
        return super().get_project_link(project_name)

    def get_token_repo_url(self, project_name) -> str:
        return super().get_token_repo_url(project_name)

    def create_project(self, project_name, project_link):
        if project_name not in self.projects_id:
            response = self._post(
                url=f'{self.api_url}/projects',
                json={
                    'name': project_name,
                    'description': f'Mirror of {project_link}'
                }
            )
            self.projects_id[project_name] = response['id']
            return response['web_url']


if __name__ == "__main__":
    from pprint import pprint
    gitlab = GitlabClient()
    print(gitlab.user_id)
    print(gitlab.user_name)
    # print(gitlab.get_last_commit_date('test_project'))
    # gitlab.create_project('test_project3', 'test_origin_project_link.com')
