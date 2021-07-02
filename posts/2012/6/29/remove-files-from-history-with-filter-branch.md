<!--
.. title: Remove files from history with filter-branch
.. slug: remove-files-from-history-with-filter-branch
.. date: 2012-06-29 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Let's suppose we work on a [project](http://code.google.com/p/chromiumembedded/) with a billion of files;
at start we thought was fine versioning all of them so to not have problems, but after a while, since we
have to share our work with others, we end with a repo of 1GB and more size that is not so nice to work with.

What to do? simple, use ``filter-branch``: this command allows to modify the story of your repository,
change commit messages, authorship and, more surgically, remove files. In my case I want to maintain only
a subset of the original files so I started with obtaining all the files traced by git


    $ git ls-files > to-remove.txt

Now I edit with my preferred editor (``vim`` what else) the file obtained in order to remove the files
I want to maintain under versioning and launch the following **dangerous** command


    $ git filter-branch --tree-filter 'cat /absolute/path/to/to-remove.txt | \
        xargs rm -f ' HEAD

It's important to note that this takes several minutes to complete (it depends on repository size and
its history of course) so take a coffee meanwhile. The absolute path is necessary in order to avoid "not found" error messages.

When the process is completed the repository is checkout-ed in the new rewritten branch and the original ``HEAD``
is referenced in the file ``.git/refs/original/refs/heads/master``; if something went wrong read the original reference with


    $ cat .git/refs/original/refs/heads/master 
    382f89ae33a875d83507b276f0550ae315e408e1

and checkout that and repeat.