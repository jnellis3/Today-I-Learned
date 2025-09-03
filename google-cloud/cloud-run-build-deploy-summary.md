# Google Cloud Build & Deploy with Cloud Run via Remote Repo

Google Cloud Run allows you to build and deploy containerized applications directly from a remote repository (such as GitHub or Bitbucket) using Google Cloud Build and CI/CD pipelines. Here’s a summary of the process:

## 1. Connect Your Remote Repository
- Go to the [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers) page in the Google Cloud Console.
- Click **"Create Trigger"**.
- Select your source repository provider (e.g., GitHub, Bitbucket) and authorize access.
- Choose the repository and branch to watch for changes (e.g., `main` or `master`).

## 2. Configure the Build Trigger
- Set the trigger to run on push or pull request events.
- Specify the location of your `Dockerfile` (usually the root of the repo).
- Optionally, provide a custom `cloudbuild.yaml` for advanced build steps.

## 3. Build & Deploy to Cloud Run
- In the build steps, use Cloud Build to build the Docker image from your `Dockerfile`.
- Push the built image to Google Container Registry (GCR) or Artifact Registry.
- Deploy the image to Cloud Run using the `gcloud run deploy` command.

### Example `cloudbuild.yaml`:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-service:$COMMIT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/my-service:$COMMIT_SHA']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - run
      - deploy
      - my-service
      - --image=gcr.io/$PROJECT_ID/my-service:$COMMIT_SHA
      - --region=us-central1
      - --platform=managed
      - --allow-unauthenticated
images:
  - 'gcr.io/$PROJECT_ID/my-service:$COMMIT_SHA'
```

## 4. Monitor & Manage Deployments
- View build and deployment logs in the Cloud Build and Cloud Run sections of the Google Cloud Console.
- Roll back or redeploy as needed.

## References
- [Cloud Build Triggers Documentation](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers)
- [Deploying to Cloud Run](https://cloud.google.com/run/docs/deploying)
- [Cloud Build YAML Reference](https://cloud.google.com/build/docs/build-config-file-schema)
