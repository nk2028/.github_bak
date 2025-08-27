import json
import requests

def get_repos(username):
    repos = []
    page = 1
    while True:
        response = requests.get(f'https://api.github.com/users/{username}/repos?page={page}')
        if response.status_code != 200:
            break
        data = json.loads(response.text)
        if not data:
            break
        repos.extend(data)
        page += 1
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
    repos = get_repos(username)
    markdown = generate_markdown(repos)
    with open('profile/README.md', 'w', encoding='utf-8') as f:
        f.write(markdown)

if __name__ == '__main__':
    main()
