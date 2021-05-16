<!--
.. title: Weird stuff happens on Visual Studio 2010
.. slug: weird-stuff-happens-on-visual-studio-2010
.. date: 2012-09-19 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

I'm working on a cross platform client and although I principally program on Linux this client must run also in Windows' OS; In order to do this I tried hard to maintain the code with less code platform-related but seems that also a simple sprintf is not correctly handled by the MS' compiler included with the **Visual Studio 2010 Express**: for example look at this code

.. code-block:: c

 // hello.cpp : Defines the entry point for the console application.
 //

 #include "stdafx.h"
 #include <time.h>

 int _tmain(int argc, _TCHAR* argv[]) {
	char query_fmt[] = "SET nome = '%s', last_modified = '%d' from note WHERE key = '%s'";
	char query[256];
	sprintf(query, query_fmt, "bau", time(NULL), "chiave");

	printf(query);
	return 0;
 }

It looks like a very elementar application that print a SQL-like string; if compiled and launched the obtained result is something like

.. code-block:: text

 $ hello.exe
 SET nome = 'bau', last_modified = '1348064101' from note WHERE key = '(null)'

How is this possible? If my understanding of C calling conventions is not fooling me, seems that the third argument of the sprintf is not the "chiave" variable but the argument of the time() function. If the time() call is executed alone like

.. code-block:: c

 int t = time(NULL);

then the expected string is printed in the terminal.