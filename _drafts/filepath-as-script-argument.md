---
layout: post
comments: true
title: "Handling file path as arguments in scripts"
---

I'm always writing scripts to automate operations to be done without having
to remember all the settings.

Obviously you have to write the settings somewhere, maybe in a configuration
file, but probably your script has to act on some specific file that you want
to indicate from command line

How to handle a filepath passed as argument in your scripts? there are two
possible ways

 1. interpret it as a relative path to the current working directory
 2. interpret it as a relative path to the script containing directory
 3. interpret always as an absolute path

Of course an absolute path (i.e. a path starting with ``/``) remains
an absolute path.

I think it's pretty obvious that the second possibility doesn't make much
sense: I don't know where the fuck the script is installed and I should
remember each time I invoke it, which files there are in its directory; this
way of handling file make sense only for **configuration files** that you
expect to find in very specific path (like ``~/.<app>`` or
``/usr/share/<app>/``). The third possibility is bad UX: surely is the more
accurate way but is too expensive for the user digits all the character of the
path.

## Output

Same argument can be used for **generated** files: if the script aim is to
generate configuration files that must have precise file path then use that
paths, instead if you want to create a file to do more stuff on, use the
eventually indicated file path as relative with respect of the current working
directory.
