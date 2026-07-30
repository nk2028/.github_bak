import json
import os
from pathlib import Path

import requests

def get_repos(username, token=None):
    repos = []
    page = 1
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

    while True:
        response = requests.get(f'https://api.github.com/users/{username}/repos', headers=headers, params={'page': page, 'per_page': 100}, timeout=30)
        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            raise RuntimeError(f'GitHub API request failed on page {page}: {response.status_code} {response.reason}') from error

        data = json.loads(response.text)
        if not isinstance(data, list):
            raise RuntimeError('GitHub API returned an unexpected response')
        if not data:
            break
        repos.extend(data)
        page += 1

    if not repos:
        raise RuntimeError('GitHub returned no repositories; refusing to overwrite profile/README.md')

    return repos

def get_repo_str(repo):
    return f'- **{repo["stargazers_count"]}** [{repo["full_name"]}]({repo["html_url"]}): {repo["description"]}\n'

def generate_markdown(repos):
    original_repos = []
    archived_repos = []
    forked_repos = []

    for repo in repos:
        if not repo['fork']:
            if not repo['archived']:
                original_repos.append(repo)
            else:
                archived_repos.append(repo)
        else:
            forked_repos.append(repo)

    sorted_original_repos = sorted(original_repos, key=lambda x: x['stargazers_count'], reverse=True)
    sorted_archived_repos = sorted(archived_repos, key=lambda x: x['stargazers_count'], reverse=True)
    sorted_forked_repos = sorted(forked_repos, key=lambda x: x['stargazers_count'], reverse=True)

    markdown = '## Original Repositories\n\n'
    for repo in sorted_original_repos:
        markdown += get_repo_str(repo)

    markdown += '\n## Archived Repositories\n\n'
    for repo in sorted_archived_repos:
        markdown += get_repo_str(repo)

    markdown += '\n## Forked Repositories\n\n'
    for repo in sorted_forked_repos:
        markdown += get_repo_str(repo)

    return markdown

def main():
    username = 'nk2028'
    repos = get_repos(username, os.environ.get('GITHUB_TOKEN'))
    markdown = generate_markdown(repos)
    readme = Path('profile/README.md')
    readme.write_text(markdown, encoding='utf-8')

if __name__ == '__main__':
    main()
