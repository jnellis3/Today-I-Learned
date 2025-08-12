# Setting up a Mirror Repository in Google Cloud

Google cloud only lets you create cloud run instances with its own gcr registry. This was causing issues for me because I wanted to host this blog on cloud run and my container is stored on GitHubs container registry. The fix is to put Cloud Run behind an Artifact Registry remote repo that points at GHCR, then deploy using the pkg.dev URL for that remote.

The next thing I want to do is see if I'm able to do the same thing from my self hosted gitea instance.

```
gcloud artifacts repositories create ghcr-remote \
  --project=PROJECT_ID \
  --repository-format=docker \
  --location=us-central1 \
  --mode=remote-repository \
  --remote-repo-config-desc="GHCR proxy" \
  --remote-docker-repo=https://ghcr.io
```