# Git Ignore Rules Can Live Outside .gitignore

I used to treat `.gitignore` as *the* ignore file in Git. It is really just the shared, version-controlled layer. Git also has repo-local and user-global ignore files, which are useful for different kinds of noise.

The practical split:

- `.gitignore`: committed with the repo. Use it for generated files everyone working on the project should ignore.
- `.git/info/exclude`: local to one clone. Use it for one-off files that are only part of my workflow in that repo.
- `~/.config/git/ignore`: the default global ignore file. Use it for machine-wide junk like `.DS_Store`.

The global location can be overridden:

```shell
git config --global core.excludesFile ~/.gitignore_global
```

Unset the override to go back to the default:

```shell
git config --global --unset core.excludesFile
```

The best debugging command is:

```shell
git check-ignore -v .DS_Store
```

The `-v` output tells you the source file, line number, pattern, and path that matched. That makes it a quick way to answer: "which ignore rule is responsible for this?"

One extra gotcha: ignore rules apply to intentionally untracked files. If a file is already tracked, adding it to an ignore file will not make Git stop tracking it. Remove it from the index first, for example:

```shell
git rm --cached path/to/file
```

References:

- [gitignore documentation](https://git-scm.com/docs/gitignore)
- [git check-ignore documentation](https://git-scm.com/docs/git-check-ignore)
