# PROJECT TEMPLATE

## Folder Structure

    01_Docs/          — contracts, briefs, specifications, deliverable docs
    02_CAD_Working/   — working CAD files, not for release
    03_CAD_Release/   — approved/released CAD, versioned by filename
    04_ID/            — visual assets, renders, branding, presentations
    05_Notes/         — markdown notes, research, references
    06_Code/          — all scripts, tools, and code assets

---

## Starting a New Project

**1. Duplicate this folder**

Copy 001_TEMPLATE and rename it using the project serial convention:

    [CLIENT]-[YEAR]-[Project_Name]
    e.g. ZAN-2025-Zandfoort_aan_Zee

**2. Initialize a git repo**

Open PowerShell inside the new project folder:

    cd path\to\CLIENT-YEAR-Project_Name
    git init

**3. Create a repo on GitHub**

Go to github.com, create a new empty repository named to match your
project serial. Then connect it locally:

    git remote add origin https://github.com/YOURUSERNAME/REPO-NAME.git

**4. Make your first commit**

    git add .
    git commit -m "project init"
    git push -u origin main

**5. Edit this README**

Replace these instructions with a description of the actual project.
Keep the folder structure section and update it if the structure
diverges from the template.

---

## Git Conventions

Only 06_Code/ and markdown files in 05_Notes/ are tracked by git.
All CAD, renders, and binary assets are ignored — see .gitignore.

Commit messages should describe what changed, not just that something
changed. Good: "add zero-crossing extraction per row". Bad: "update".

Commit often. A commit after every working session is a reasonable
minimum habit.

---

## Backup

Git is version control, not backup. CAD files, assets, and anything
not tracked by git should be covered by OneDrive or equivalent.
Make sure this project folder is inside your synced directory.

---

*Delete everything above this line when the project is underway.*