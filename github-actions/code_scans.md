# Performing Code and Website Scans

Today I learned how to use actions in github and gitea to scan code for secrets and to scan websites for vulnerabilities.

``` yaml
on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    - name: Secret Scanning
      uses: trufflesecurity/trufflehog@main
      with:
        extra_args: --results=verified,unknown
        base: ""
        head: ${{ github.ref_name }}
    - name: Test javascript vulnerabilities in KB 
      uses: lirantal/is-website-vulnerable@main
      with:
        scan-url: "https://kb.nellisconsulting.com"
```
