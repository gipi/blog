<!--
.. title: Compiling GStreamer and AndEngine using repo
.. slug: compiling-gstreamer-and-andengine-using-repo
.. date: 2013-04-13 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Today is not uncommon to work with projects having a certain numbers of subprojects as components: think to projects like **Gnome**, **KDE** etc... that have its source code maintained with some source code management.

In **git** (the tool that I use and like the most) there are two native ways to manage cases like these: one is **submodules**, i.e. maintaining a subdirectory pointing to another git repository that will be managed using the ``submodule`` command, the other is the ``subtree`` merge that indeed merge an external repository in the project of interest. Each one has its advantages and its drawbacks, first of all the added complexity; you can find endless discussion in the `git mailing list <http://blog.gmane.org/gmane.comp.version-control.git>`_ about that.

Android is one of this projects where they have to manage a certain number of components to be included (in some cases only optionally, think of vendor trees). The `AOSP <http://source.android.com/>`_  solved this problem creating its own tool: **repo**. This tool take another approach respect of the two discussed above, it uses a manifest file (maintained using git) and download the projects indicated in this file.

It's installable with a simple command

.. code-block:: text

 curl https://dl-ssl.google.com/dl/googlesource/git-repo/repo > ~/bin/repo

and can be initializated with

.. code-block:: text

 $ repo init

in a directory of your choice. Now the help is available

.. code-block:: text

 $ repo help
 usage: repo COMMAND [ARGS]
 The most commonly used repo commands are:
  abandon      Permanently abandon a development branch
  branch       View current topic branches
  branches     View current topic branches
  checkout     Checkout a branch for development
  cherry-pick  Cherry-pick a change.
  diff         Show changes between commit and working tree
  download     Download and checkout a change
  grep         Print lines matching a pattern
  info         Get info on the manifest branch, current branch or unmerged branches
  init         Initialize repo in the current directory
  list         List projects and their associated directories
  overview     Display overview of unmerged project branches
  prune        Prune (delete) already merged topics
  rebase       Rebase local branches on upstream branch
  smartsync    Update working tree to the latest known good revision
  stage        Stage file(s) for commit
  start        Start a new branch for development
  status       Show the working tree status
  sync         Update working tree to the latest revision
  upload       Upload changes for code review
 See 'repo help <command>' for more information on a specific command.
 See 'repo help --all' for a complete list of recognized commands.

For each command you can write ``repo help <command>`` and read the usage text that, (I would like to be contradicted) is the only documentation available.

What is interesting is the ``manifest``, the file describing the structure of the projects to download that must be indicate to the ``init`` command; a simple manifest could be

.. code-block:: xml

 <?xml version="1.0" encoding="UTF-8"?>
 <manifest>
    <remote
        name="projectremote"
        fetch="git://mydomain/subdirectory/"
    />
    <default
        revision="master"
        remote="projectremote"
    />
    <project path="dir1/project1" name="project1_name"/>
    <project path="dir1/project2" name="project2-name"/>
    <project path="dir2/project3" name="project3_name"/>
 </manifest>

Under the ``manifest`` tag there are some others tags like

* ``remote``: configure a remote domain from which download
* ``default``: indicate what remote and what branch is used when not indicated explicitely in the ``project`` tag
* ``project``: the ``path`` attribute is where the project will be downloaded locally, the ``name`` is used to find the project in the given remote (the actual address will be ``${remote_fetch}/${project_name}.git). The ``project`` tag accepts also ``remote`` and ``branch`` attributes to override the default.

After having initializated passing to the ``-u`` flag the ``URL`` of the repository with the manifest, you can do

.. code-block:: txt

 $ repo sync

and the source code of the projects will be downloaded. If for some reason one of the projects given an error during the ``sync`` stage, all the projects are not checked out, remember that.

Since I like to experiment with code and library, I tried `GStreamer <http://gstreamer.freedesktop.org/>`_ and `AndEngine <http://www.andengine.org/>`_: the former is a multimedia framework, composed of several plugins, the latter a 2D OpenGL Game Engine for Android with a large numbers of modules. These two projects are the optimal situation to test the use of repo and indeed I created two repositories: https://github.com/gipi/gstreamer-repo and https://github.com/gipi/AndEngine-repo; if someone tries them let me know.