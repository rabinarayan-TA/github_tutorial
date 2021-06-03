# GIT TUTORIAL

---

All the required command for GIT

---

## Table of Contents

1. [Comparison Scenario](#Comparison-Scenario)
2. [Branches](#Branches)
3. [Rebasing](#Rebasing)
4. [Collaboration](#collaboration)
5. [FAQs](#faqs)

### **_Comparison Scenario_**

---

```
File A :Unstaged File (in working directory)
File B :Staged file (in staging area)
File C :After commiting one file(in Repository .git Folder)
```

#### 1. **git diff** :

> comparing the differences between what's in my local working directory that has been recently modified but not yet staged, versus what's currently staged. Between **File A vs File B**

#### Note -> **_git difftool_** (for visualizing the comparison). Staging Area | Working Directory

#### 2. **git diff HEAD**:

> Git will compare the difference between the working directory and the last commit on this branch. Between **File A vs File C**

#### Note -> **_git difftool HEAD_** (for visualizing the comparison). Git Repository at Head | Working Directory

#### 3. **git diff --staged HEAD**:

> Git will compare the difference between the Staged Area and the HEAD that means last commit on this branch. Between **File B vs File C**

#### Note -> **_git difftool --staged HEAD_** (for visualizing the comparison). Git Repository at Head | Staging Area

#### 4. **git diff -- Filename**:

> Git will compare the difference for a particular Filename.

#### 5. **git log --oneline**:

> Provide list of all commit with messages.

#### 6. **git diff commit_ID HEAD**:

> compare an arbitrary commit to the last commit.

#### 7. **git diff HEAD HEAD^**:

> compare last commit to the second last commit.

#### 8. **git diff commit_ID_1 commit_ID_2**:

> compare an arbitrary commit with another arbitary commit.

#### 9. **git diff master origin/master**:

> compare the differences between the local master branch,and the remote master branch.

### **_Branches_**

---

#### 1. **git branch -a** :

> list both the local and the remote branches

#### 2. **git branch _Branch_name_**:

> Create a new branch

#### 3. **git branch -m _old_name_ _new_name_**:

> Renaming Branch name

#### 4. **git branch -d _branch_name_**:

> Delete a branch

#### 5. **git merge _branch_name_**:

> merge branch_name branch with the branch you currently on.

#### 6. **git merge --no-ff _branch_name_**:

> Use this command to merge branch_name branch to the branch you currently working on when you have more than one commit in branch_name branch. **--no-ff** is used to avoid fast forward merging .

### **_Rebasing_**

---

```
Rebasing is the process of moving or combining a sequence of commits to a new base commit. Rebasing is most useful and easily visualized in the context of a feature branching workflow.
Rebasing is changing the base of your branch from one commit to another making it appear as if you'd created your branch from a different commit. Internally, Git accomplishes this by creating new commits and applying them to the specified base. It's very important to understand that even though the branch looks the same, it's composed of entirely new commits.
```

**When _NOT_ to Use**

```
Never rebase commits that have been shared with
others. If you have already pushed commits up to
Github...DO NOT rebase them unless you are positive
no one on the team is using those commits.
```