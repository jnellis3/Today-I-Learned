# Setting up Python in Gitea Actions

For future reference, this is an example of how I setup the Python env.

```
    - name: Install Dependencies
      continue-on-error: false
      run: |
        cd main
        sudo apt-get install jq -y
        echo "$ACCOUNTS" > ./accounts.json
        python3 -m venv .venv
        source ./.venv/bin/activate
        pip install -r requirements.txt        
      env:
        ACCOUNTS: ${{ secrets.ACCOUNT_INFORMATION }}
```