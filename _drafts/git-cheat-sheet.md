---
layout: post
comments: true
title: "Cheat sheet: GIT"
tags: [cheat sheet, git]
---

## Edit commit

```
 -> add to the index some changes
$ git commit --amend
```

## Edit commit in an interactive rebase

```
$ git rebase --interactive <ref>^
 -> change the operation for the desired commit to "edit" and close the editor
 -> now you are in the desired commit
$ git reset HEAD^
 -> you can now commit the changes in as many commits as you want
$ git rebase --continue
```

## Rebase one commit onto

This is particular: you want to rebase the tip of ``<branch>`` to ``<upstream>``,
probably is the same as ``cherry-pick``

```
$ git rebase <branch>^ <branch> --onto <upstream>
```

## Rebase preserving merges

```
$ git rebase --preserve-merges <upstream>
```

## Merge/rebase conflict resolution

When there are conflicts a few files are created

 - ``.BASE``: the revision in common
 - ``.REMOTE``: your code
 - ``.LOCAL``: the code whose you are adapting your
 - ``.ORIG``: the file containing the markers ``<<<<``, ``=====`` and ``>>>>``

It's possible to use ``git mergetool`` in order to help with resolution, in particular
with the flag ``--tool`` is possible to indicate which tool to use.

## Notes

```
$ git notes add <ref>
$ git notes edit <ref>
$ git notes append <ref>
$ git push origin ref/notes/commits
$ git fetch origin refs/notes/*:refs/notes/*
```

## Follow function code evolution

```
$ git log -L:<function name>:<path file>
```

## Search for functions

In some cases you need to look up in which function is present
some string of your choice: the following shows the matching occurrence
of the string plus a line with the function name containing it

```
$ git grep --show-function <some string>
```

otherwise is possible to search for a string obtaining all the code
of the function containing it

```
$ git grep -W <some string>
```

## Links

 - [Git Submodules vs Git Subtrees](https://codewinsarguments.co/2016/05/01/git-submodules-vs-git-subtrees/)

