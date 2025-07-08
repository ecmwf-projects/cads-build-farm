import os
import shutil
import logging

import git
import typer

logger = logging.getLogger(__name__)

app = typer.Typer()


def git_clone_repo(
    repo_url: str,
    repo_path: str,
    repo_branch: str,
    multi_options: tuple[str, ...] = ("--depth=1", "--recurse-submodules"),
    delete_remote: bool = True,
) -> str:
    if repo_branch:
        multi_options += (f"--branch {repo_branch}",)

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    repo = git.Repo.clone_from(repo_url, repo_path, multi_options=multi_options)

    if delete_remote:
        repo.delete_remote(repo.remote())

    try:
        return repo.active_branch.name
    except TypeError:
        return next((tag for tag in repo.tags if tag.commit == repo.head.commit)).name


def git_clone_repos(
    paths: list[str],
    repo_base_url: str,
    delete_remote: bool = True,
    default_branch: bool = False,
) -> None:
    for path_branch in paths:

        repo_path_name, _, repo_branch = path_branch.partition(":")
        repo_path, _, repo_name = repo_path_name.partition("@")

        repo_path = repo_path.rstrip("/")
        if not repo_name:
            repo_name = os.path.basename(repo_path)
        repo_url = f"{repo_base_url}/{repo_name}.git"

        if os.path.exists(repo_path) and not os.path.isdir(repo_path):
            logger.warning(f"{repo_path!r} is not a directory. Skipping.")
            continue

        if not repo_branch:
            repo_branch_env = f"{repo_name}_REF".upper().replace("-", "_")
            if default_branch:
                repo_branch = os.environ.get(repo_branch_env, "")
            else:
                # Crash if the environment variable is not set
                repo_branch = os.environ[repo_branch_env]

        try:
            active_branch = git_clone_repo(
                repo_url, repo_path, repo_branch, delete_remote=delete_remote
            )
            logger.info(
                f"cloned repo {repo_name!r} branch or tag {active_branch!r} "
                f"in path {repo_path!r}"
            )
        except NotADirectoryError:
            pass
        except Exception:
            logger.exception(
                f"failed to clone repo {repo_name!r} branch {repo_branch!r} "
                f"in path {repo_path!r}"
            )
            raise


@app.command()
def main(
    github_repos: list[str] = typer.Argument(..., help="GitHub repositories to clone"),
    bitbucket: list[str] = typer.Option(default=[], help="Bitbucket repository to clone"),
    default_branch: bool = typer.Option(
        default=False, help="Clone default branch if env variable is missing"
    ),
):
    logging.basicConfig(level=logging.INFO)
    github_pat = os.getenv("CADS_PAT", "")
    if github_pat:
        github_pat = f"{github_pat}@"
    git_clone_repos(
        github_repos,
        f"https://{github_pat}github.com/ecmwf-projects",
        delete_remote=False,
        default_branch=default_branch,
    )
    bitbucket_pat = os.getenv("CDS_PAT", "")
    if bitbucket_pat:
        bitbucket_pat = f"{bitbucket_pat}@"
    git_clone_repos(
        bitbucket,
        f"https://{bitbucket_pat}git.ecmwf.int/scm/cds",
        delete_remote=False,
        default_branch=default_branch,
    )


if __name__ == "__main__":
    app()
