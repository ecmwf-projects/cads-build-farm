import os
import logging
import sys

import git


logger = logging.getLogger(__name__)


def pull_branch(repo_name, repo_branch):
    repo = git.Repo(repo_name)

    if repo.active_branch.name != repo_branch:
        if repo_branch not in repo.branches:
            repo.git.fetch()
            repo.git.checkout("-b", repo_branch, repo.remote().refs[repo_branch])
        repo.git.checkout(repo_branch)

    repo.git.pull()


def main(argv=sys.argv):
    logging.basicConfig(level=logging.INFO)

    current_dir = os.path.abspath(".")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(script_dir)

    for name_branch in argv[1:]:
        repo_name, _, repo_branch = name_branch.partition(":")
        repo_branch = repo_branch or "main"

        try:
            pull_branch(repo_name, repo_branch)
            logger.info(f"{repo_name} now on branch {repo_branch}")
        except Exception:
            logger.exception(f"Cannot pull repo {repo_name!r}")

    os.chdir(current_dir)


if __name__ == "__main__":
    main()
