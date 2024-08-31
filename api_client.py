from abc import ABC, abstractmethod
from datetime import datetime
import requests


class APIClient(ABC):
    def __init__(self, token) -> None:
        self.token = token
        self.auth_header = {'Authorization': f'Bearer {self.token}'}
        self.user_name, self.user_id = self._get_user()
        self.projects_id = self._get_projects()

    def _get(self, url, headers={}, params={}, data={}):
        response = requests.get(url,
                                headers=self.auth_header | headers,
                                params=params,
                                data=data)
        response.raise_for_status()
        return response.json()

    def _post(self, url, headers={}, params={}, data={}, json={}):
        response = requests.post(url,
                                 headers=self.auth_header | headers,
                                 params=params,
                                 data=data,
                                 json=json)
        response.raise_for_status()
        return response.json()

    @property
    @abstractmethod
    def service(self) -> str:
        '''return service name (must be specified in SUPPORTED_SERVICES)'''
        pass

    @abstractmethod
    def _get_user(self) -> str:
        '''return username and user id on service'''
        pass

    @abstractmethod
    def _get_projects(self) -> dict:
        '''return dict {repo_name: repo_id, ...}'''
        pass

    @abstractmethod
    def get_last_commit_date(self, repo, branch) -> datetime:
        '''return last commit datetime'''
        pass

    @abstractmethod
    def get_project_link(self, project_name) -> str:
        '''returns link to the project'''
        return f'https://{self.domain}/{self.user_name}/{project_name}'

    @abstractmethod
    def get_token_repo_url(self, project_name) -> str:
        '''return link to repository with token auth'''
        return f"https://{self.user_name}:{self.token}@{self.domain}/{self.user_name}/{project_name}"

    @abstractmethod
    def create_project(self, project_name, project_link) -> str:
        '''
        creates project
        project_name - name of project
        project_link - link to origin project
        returns created repo url
        '''
        pass
