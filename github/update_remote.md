# Bulk Update Remote Origin

Our company went through a bulk migration of our client repositories to new locations. We needed to update hundreds of repositories in each of our local drives. This is how it can be done programatically.

You can save this as a .bat file and run it instead of individual updates (if you don't keep your repos in C:/Repos, change the path).

```powershell
Get-ChildItem -Directory -Path C:\Repos -Filter "C-*" | ForEach-Object {
    if (Test-Path "$($_.FullName)\.git") {
        $oldUrl = git -C "$($_.FullName)" remote get-url origin 2>$null
        if ($oldUrl) {
            $repoName = ($oldUrl.Split("/")[-1])
            $newUrl = "https://govirtualoffice@dev.azure.com/govirtualoffice/C-ClientRepos/_git/$repoName"
            git -C "$($_.FullName)" remote set-url origin $newUrl
            Write-Output "Updated $($_.FullName): $oldUrl to $newUrl"
        }
    }
}
```