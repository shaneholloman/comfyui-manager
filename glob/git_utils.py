import os
import configparser


GITHUB_ENDPOINT = os.getenv('GITHUB_ENDPOINT')


def is_git_repo(path: str) -> bool:
    """ Check if the path is a git repository. """
    # NOTE: Checking it through `git.Repo` must be avoided.
    #       It locks the file, causing issues on Windows.
    return os.path.exists(os.path.join(path, '.git'))


def get_commit_hash(fullpath):
    git_head = os.path.join(fullpath, '.git', 'HEAD')
    if os.path.exists(git_head):
        with open(git_head) as f:
            line = f.readline()

            if line.startswith("ref: "):
                ref = os.path.join(fullpath, '.git', line[5:].strip())
                if os.path.exists(ref):
                    with open(ref) as f2:
                        return f2.readline().strip()
                else:
                    return "unknown"
            else:
                return line

    return "unknown"


def git_url(fullpath):
    """
    resolve version of unclassified custom node based on remote url in .git/config
    """
    git_config_path = os.path.join(fullpath, '.git', 'config')

    if not os.path.exists(git_config_path):
        return None

    config = configparser.ConfigParser()
    config.read(git_config_path)

    for k, v in config.items():
        if k.startswith('remote ') and 'url' in v:
            return v['url']

    return None


def normalize_url(url) -> str:
    if 'github' in url or (GITHUB_ENDPOINT is not None and GITHUB_ENDPOINT in url):
        author = os.path.basename(os.path.dirname(url))
        repo_name = os.path.basename(url)
        url = f"https://github.com/{author}/{repo_name}"

    return url


def get_url_for_clone(url):
    url = normalize_url(url)

    if GITHUB_ENDPOINT is not None and url.startswith('https://github.com/'):
        url = GITHUB_ENDPOINT + url[18:] # url[18:] -> remove `https://github.com`

    return url
    