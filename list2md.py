from datetime import datetime
import json
import requests
import sys


head = '''# Top Python Web Frameworks
A list of popular github projects related to Python web framework (ranked by stars automatically)
Please update **list.txt** (via Pull Request)

Tips：这是一份关于python web 框架的 github 名单，每天 UTC 时间上午 9 点自动更新 github 状态，如果有新的 web 或者 api 框架，可以 issues 或者 pr “list.txt” 文件给我。

| Project Name | Stars | Forks | Open Issues | Description | Last Commit |
| ------------ | ----- | ----- | ----------- | ----------- | ----------- |
'''
tail = '\n*Last Automatic Update: {}*'

warning = "⚠️ No longer maintained ⚠️  "

deprecated_repos = list()
repos = list()


def main():
    access_token = get_access_token()

    with open('list.txt', 'r') as f:
        for url in f.readlines():
            url = url.strip()
            if url.startswith('https://github.com/'):
                repo_api = 'https://api.github.com/repos/{}'.format(url[19:])
                print(repo_api)

                r = requests.get(repo_api, headers={'Authorization': 'token {}'.format(access_token)})
                if r.status_code != 200:
                    raise ValueError('Can not retrieve from {}'.format(url))
                repo = json.loads(r.content)

                commit_api = 'https://api.github.com/repos/{}/commits/{}'.format(url[19:], repo['default_branch'])
                print(repo_api)

                r = requests.get(commit_api, headers={'Authorization': 'token {}'.format(access_token)})
                if r.status_code != 200:
                    raise ValueError('Can not retrieve from {}'.format(url))
                commit = json.loads(r.content)

                repo['last_commit_date'] = commit['commit']['committer']['date']
                repos.append(repo)

        repos.sort(key=lambda r: r['stargazers_count'], reverse=True)
        save_ranking(repos)
   

def get_access_token():
    if len(sys.argv) > 1 and sys.argv[1] != None:
        return sys.argv[1].strip()
    else:
        with open('access_token.txt', 'r') as f:
            return f.read().strip()


def save_ranking(repos):
    with open('README.md', 'w') as f:
        f.write(head)
        for repo in repos:
            if is_deprecated(repo['url']):
                repo['description'] = warning + repo['description']
            f.write('| [{}]({}) | {} | {} | {} | {} | {} |\n'.format(repo['name'],
                                                                     repo['html_url'],
                                                                     repo['stargazers_count'],
                                                                     repo['forks_count'],
                                                                     repo['open_issues_count'],
                                                                     repo['description'],
                                                                     datetime.strptime(repo['last_commit_date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')))
        f.write(tail.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%S%Z')))


def is_deprecated(repo_url):
    return repo_url in deprecated_repos


if __name__ == '__main__':
    main()