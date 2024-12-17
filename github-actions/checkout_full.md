# Checkout a Repo with Full Branch History

Today I learned that using the `actions/checkout@v4` action in github/gitea will not include the full chain of commits. I was initially resolving this by building my own action that would pull the full repo. It turns out that this action has the ability to specify the depth of fetch as follows:

```
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Check out repo
      uses: actions/checkout@v3
      # We need full history to introspect created/updated:
      with:
        fetch-depth: 0
        path: main
```

For each additional action, we need to `cd main` to go into the branch.