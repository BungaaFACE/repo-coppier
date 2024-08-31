from os.path import abspath, join, dirname
from progressbar import progressbar, Percentage, GranularBar, ETA, SimpleProgress
from tabulate import tabulate
from git import Repo, rmtree
from pprint import pprint
import argparse
import json

from api_client import APIClient
from github import GithubClient
from gitlab import GitlabClient

SUPPORTED_SERVICES = {'github': GithubClient,
                      'gitlab': GitlabClient}

PROGRESSBAR_SETTINGS = {
    'redirect_stdout': True,
    'widgets': [Percentage(), ' | (', SimpleProgress(), ') ', GranularBar(), ' ', ETA(), ]
}

project_path = dirname(abspath(__file__))
sync_list_path = join(project_path, 'repositories.json')


def load_repos() -> dict:
    try:
        with open(sync_list_path, 'r+') as repos_file:
            repositories = json.load(repos_file)
    except FileNotFoundError:
        return dict()
    return repositories


def save_repos(data: dict):
    with open(sync_list_path, 'w+') as repos_file:
        json.dump(data, repos_file)


def add_repo(service, repo_name):
    if '/' in repo_name:
        try:
            repo_name = repo_name.split('/')[-1]
            print(f'Extracted repo name {repo_name} from link')
        except Exception as e:
            print('Unsupported repo name')
            raise e

    repos = load_repos()

    if repo_name not in repos.setdefault(service, list()):
        repos[service].append(repo_name)
        save_repos(repos)
        print(f'Repository {repo_name} added')
    else:
        print(f'Repository {repo_name} already in list')


def check_repos_status(repo_list: list, o_client: APIClient, d_client: APIClient):
    repo_status = []
    print('Checking commits...')
    for repo in progressbar(repo_list, **PROGRESSBAR_SETTINGS):
        repo_data = {'repo name': f"{repo}"}

        o_date = o_client.get_last_commit_date(repo)
        d_date = d_client.get_last_commit_date(repo)

        repo_data[f'{o_client.service} commit'] = o_date or 'NOT FOUND'
        repo_data[f'{d_client.service} commit'] = d_date or 'NOT FOUND'

        if not o_date:
            repo_data['status'] = 'SKIP'
        elif not d_date:
            repo_data['status'] = 'CREATE'
        else:
            repo_data['status'] = 'UPDATE'
            if o_date <= d_date:
                repo_data['status'] = 'LATEST'

        repo_status.append(repo_data)

    print(tabulate([row.values() for row in repo_status], headers=repo_status[0].keys(), tablefmt="mixed_grid"))
    return repo_status


def sync_repos(repo_status: list[dict], o_client: APIClient, d_client: APIClient):
    print('Syncing repos...')
    for repo in progressbar(repo_status, **PROGRESSBAR_SETTINGS):
        if repo['status'] == 'CREATE':
            origin_link = o_client.get_project_link(repo['repo name'])
            url = d_client.create_project(repo['repo name'], origin_link)
            if url:
                print(f'New repo created on service {o_client.service}. Link: {url}')

        repo_path = join(project_path, 'cloned_repos', repo)
        repo = Repo.clone_from(o_client.get_token_repo_url(repo), repo_path, bare=True)
        try:
            d_remote = repo.create_remote('mirror', d_client.get_token_repo_url(repo))
            d_remote.push(mirror=True).raise_if_error()
        except Exception as e:
            print(f'Exception occured while pushing repo. Info:\n{e.with_traceback()}')
        finally:
            repo.close()
            rmtree(repo_path)


def start_programm(args):
    if args.action == 'sync' or args.action == 'status':
        repos = load_repos().get(args.origin_service, dict())
        if not repos:
            print('No added repos found.')
            return
        if args.repo:
            if args.repo in repos:
                repos = [args.repo]
            else:
                print(f'repo {args.repo} not in repos list. Use \'list\' action to check added repositories.')

        o_client: APIClient = SUPPORTED_SERVICES[args.origin_service]()
        d_client: APIClient = SUPPORTED_SERVICES[args.destination_service]()
        repo_status = check_repos_status(repos, o_client, d_client)

        if args.action == 'sync':
            sync_repos(repo_status, o_client, d_client)

    elif args.action == 'add':
        add_repo(args.service[0], args.repo[0])

    elif args.action == 'list':
        repos = load_repos()
        if args.service in SUPPORTED_SERVICES:
            repos = {args.service: repos.get(args.service, list())}
        pprint(repos)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='repo-copier.py',
                                     description='Tool copies your github repositories to gitlab')

    subparsers = parser.add_subparsers(dest='action', required=True,
                                       help='action to do: '
                                       'add - add new sync repository; '
                                       'sync - mirror repositories; '
                                       'list - list added repositories; '
                                       'status - show sync status')

    parser_sync = subparsers.add_parser('sync')
    parser_sync.add_argument("--repo", "-r", type=str, required=False,
                             help='repo name')
    parser_sync.add_argument("--origin-service", "-os", type=str, required=False,
                             help='Origin repositories service', default='github',
                             choices=SUPPORTED_SERVICES)
    parser_sync.add_argument("--destination-service", "-ds", type=str, required=False,
                             help='Destination repositories service', default='gitlab',
                             choices=SUPPORTED_SERVICES)

    parser_add = subparsers.add_parser('add')
    parser_add.add_argument("service", nargs=1,
                            type=str, help='repo service name',
                            choices=SUPPORTED_SERVICES)
    parser_add.add_argument("repo", nargs=1, type=str,
                            help='repo name')

    parser_list = subparsers.add_parser('list')
    parser_list.add_argument("service", nargs='?',
                             type=str,
                             help='repo service name',
                             choices=SUPPORTED_SERVICES)

    parser_status = subparsers.add_parser('status')
    parser_status.add_argument("--repo", "-r", type=str, required=False,
                               help='repo name')
    parser_status.add_argument("--origin-service", "-os", type=str, required=False,
                               help='Origin repositories service', default='github',
                               choices=SUPPORTED_SERVICES)
    parser_status.add_argument("--destination-service", "-ds", type=str, required=False,
                               help='Destination repositories service', default='gitlab',
                               choices=SUPPORTED_SERVICES)

    args = parser.parse_args()
    start_programm(args)
