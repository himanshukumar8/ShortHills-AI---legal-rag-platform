# GitHub Release Guide

## 1. Local Git Initialization
The repository is currently NOT initialized as a Git repository locally. You must execute the following exact commands in your terminal at `d:\Projects\ShorthillsAI` to initialize and stage the codebase.

```bash
git init
git add .
git commit -m "Initial Release: Legal RAG Platform"
git branch -M main
```

## 2. Remote Origin Configuration
Before you can push, you must create a new repository on GitHub (e.g., `ShorthillsAI-Legal-RAG`). Once created, GitHub will provide you with a remote URL.

Replace `<YOUR_REPOSITORY_URL>` below with your actual GitHub HTTPS or SSH URL.

```bash
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

## 3. Tagging the Release
To formally stamp this commit as the v1.0.0 release for production deployment:

```bash
git tag -a v1.0.0 -m "Initial Release"
git push origin v1.0.0
```

## 4. Pre-Push Checklist
- Verify no secrets exist in the source code.
- Verify `demo/` screenshots are captured and replaced the placeholders in the README.
- Verify `.gitignore` is preventing `data/raw/` and `data/embeddings/` from staging.
