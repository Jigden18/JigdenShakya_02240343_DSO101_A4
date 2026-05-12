# JigdenShakya_02240343_DSO101_A4

A Student Grade Tracker REST API built with Flask, tested with pytest, and deployed automatically to Render through a GitHub Actions CI/CD pipeline.

**Live URL:** https://jigdenshakya-02240343-dso101-a4.onrender.com

**Repository:** https://github.com/Jigden18/JigdenShakya_02240343_DSO101_A4

---

## Running the App Locally

After cloning the repository, install dependencies and start the Flask server:

```bash
pip install -r requirements.txt
python app.py
```

![Flask app running locally on port 5000](./public/Screenshot%202026-05-12%20221054.png)

---

## Running Tests Locally

Run pytest to verify all 43 unit tests pass before pushing any code:

```bash
pytest --tb=short -v
```

![All 43 pytest unit tests passing in the terminal](./public/Screenshot%202026-05-12%20221221.png)

---

## Pushing to GitHub

Add all project files, and push to the main branch:

```bash
 git add .
 git commit -m 'Assignment 4: Initial Commit'
 git push origin main
```
Confirm `app.py`, `test_app.py`, and `requirements.txt` are visible on your GitHub repo page:

![Initial project files committed and pushed to the GitHub repository](./public/Screenshot%202026-05-12%20221518.png)

---

## Creating a Web Service on Render

Connected the GitHub repository to Render and configured the service with the following settings:

| Setting | Value |
|---------|-------|
| Name | `student-grade-tracker` |
| Region | Singapore |
| Branch | `main` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python app.py` |
| Instance Type | Free |


![New Web Service configured on Render and connected to the GitHub repository](./public/Screenshot%202026-05-12%20222009.png)

---

## First Deployment on Render

Render installed the dependencies and started the Flask app. The service status changed to **Live**.

![Flask app successfully deployed and live on Render for the first time](./public/Screenshot%202026-05-12%20222336.png)

---

## Getting the Render Deploy Hook

Generated a Deploy Hook URL from the Render service settings. This URL is called by GitHub Actions to trigger automatic redeployments on every push to `main`.

![Render deploy hook URL generated from the service settings page](./public/Screenshot%202026-05-12%20222547.png)

---

## Adding the Deploy Hook Secret to GitHub

Stored the deploy hook URL as a GitHub Actions secret named `RENDER_DEPLOY_HOOK_URL` so it is never exposed in the repository. The pipeline references it as `${{ secrets.RENDER_DEPLOY_HOOK_URL }}`.

![RENDER_DEPLOY_HOOK_URL secret added to the GitHub Actions repository secrets](./public/Screenshot%202026-05-12%20223013.png)

---

## Running the CI/CD Pipeline

Pushed the workflow file `.github/workflows/ci.yml` to trigger the first full pipeline run. All three phases: Build, Test, and Deploy completed successfully.

`github/workflows/ci.yml` :
```yml
name: CI/CD Pipeline

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  build-test-deploy:
    runs-on: ubuntu-latest

    steps:
      # ── Step 1: Build ────────────────────────────────────────────────────────

      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: pip install -r requirements.txt

      # ── Step 2: Test ─────────────────────────────────────────────────────────

      - name: Run tests
        run: pytest --tb=short -v

      # ── Step 3: Deploy ───────────────────────────────────────────────────────

      - name: Deploy to Render
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: |
          echo "Deploying to Render..."
          curl -s "${{ secrets.RENDER_DEPLOY_HOOK_URL }}" | grep -q "deployId" \
            && echo "Deployment triggered successfully." \
            || echo "Deploy hook responded — check Render dashboard for status."
```

Push to Github :

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions CI/CD pipeline"
git push origin main
```

Verify the pipeline :

![GitHub Actions CI/CD pipeline running with all build, test, and deploy steps passing](./public/Screenshot%202026-05-12%20223314.png)

---

## Making a Code Change to Test Auto-Deploy

Updated the app version from `1.0` to `1.1` in `app.py` and pushed to `main` to verify the full end-to-end pipeline triggers automatically.

![Updating the app version in app.py from 1.0 to 1.1 to trigger an automatic redeployment](./public/Screenshot%202026-05-12%20223542.png)

---

## Render Automatically Redeploying

As soon as the GitHub Actions pipeline completed, Render picked up the deploy hook trigger and started a new deployment with no manual action required.

![Render dashboard showing automatic redeployment triggered by the GitHub Actions pipeline](./public/Screenshot%202026-05-12%20223944.png)

---

## Updated App Confirmed Live on Render

After redeployment, the live app on Render reflects version `1.1`, confirming the full CI/CD loop works end-to-end.

![Render deployment logs confirming the updated app version is live](./public/Screenshot%202026-05-12%20224037.png)

---

## Testing the Live API with curl

Tested all endpoints against the live Render URL to verify the API works correctly in production.


![Live API endpoints tested with curl showing correct JSON responses from the Render URL](<Screenshot 2026-05-12 224407.png>)

---

## Verifying the Changes on the Live URL

![Browser confirming the updated version 1.1 is live at the Render deployment URL](<Screenshot 2026-05-12 224443.png>)
