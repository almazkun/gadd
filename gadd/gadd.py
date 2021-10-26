import git
import sys

def main():

    repo = git.Repo()

    # the below gives us all commits
    changed_files = repo.git.diff("--name-only", "--cached")
    print(changed_files)
if __name__ == "__main__":
    main()