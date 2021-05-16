<!--
.. title: IPhone e debugging dei problemi di memoria
.. slug: iphone-e-debugging-dei-problemi-di-memoria
.. date: 2010-10-10 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Essendo il ciclo di una applicazione sviluppata per IPhone ad eventi, non è semplice riuscire a seguire come la memoria è allocata e liberata, anche tenendo conto del modo inconsueto con cui l'objective c gestisce la creazione e la morte degli oggetti. Proprio per questo è molto importante conoscere gli strumenti che permettono di ottenere informazioni riguardanti questo aspetto.

Valgrind
========

Questo è lo strumento principe utilizzato nelle altre piattaforme che dalle ultime versioni funziona anche su MacOSX e di riflesso è possibile utilizzarlo anche sulle applicazioni IPhone sfruttando il fatto che sull'emulatore viene compilato per i386 e non per ``ARM`` (invece non ancora supportato).

Seguendo le istruzioni di questo `post <http://landonf.bikemonkey.org/2008/12/24>`_ basta creare una confgurazione chiamata valgrind in cui si imposta un ``#define`` per ``gcc`` chiamato ``VALGRIND``. Dopo di che si inseriscono queste righe nel ``main()``

.. code-block:: objective-c

 #ifdef VALGRIND

 #include<unistd.h>

 #define VALGRIND_PATH "/opt/local/bin/valgrind"

 #endif

 int main(int argc, char *argv[]) {               
 #ifdef VALGRIND
       /* gli argomenti di Valgrind */
       execl(VALGRIND_PATH, VALGRIND_PATH,
        /* argomenti da passare a valgrind */"--leak-check=full",
                 //"--show-reachable=yes",
                 "--dsymutil=yes", argv[0], NULL);
 #endif
     NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
     int retVal = UIApplicationMain(argc, argv, nil, nil);
     [pool release];
 }

Ovviamente bisogna avere installato ``valgrind``, io consiglio di usare `port <http://macports.org>`_ ed installare la variante ``universal`` del port ``valgrind-devel``

.. code-block:: shell

 $ sudo port install valgrind-devel +universal


NSZombieEnabled&MallocStackLogging
==================================

Esistono inoltre per ``Cocoa`` degli `strumenti appositi per debuggare i problemi di memoria utilizzando delle variabili di ambiente a runtime <http://www.cocoadev.com/index.pl?DebuggingAutorelease>`_: ``NSZombieEnabled`` e ``MallocStackLogging``; la prima fa in maniera tale da salvare ogni oggetto disallocato in un oggetto ``NSZombie`` in maniera da sapere se qualcuno va a richiamarlo, mentre la seconda memorizza tutte le funzioni che richiamano come argomento una variabile e permette da linea di comando di ottenere una specie di backtrace tramite il comando ``malloc_history``. Per impostarle in ``XCode`` andare su ``Project > Edit Active Executable "..."`` e aggiungere ``NSZombieEnabled=YES`` e ``MallocStackLogging=YES``.

Se per esempio io imposto queste variabili, posso ottenere nel caso un cui il programma richiama una variabile disallocata, un log di questo tipo

.. code-block:: text

  2010-10-10 12:27:47.412 ShitApp[1695:207] ***-[UIImage isKindOfClass:]: message sent to deallocated instance 0x769822

il quale ci dice che la nostra applicazione ``ShitApp`` ha cercato di usare una istanza di ``UIImage`` che era stata in precedenza disallocata e ci indica anche il ``PID`` del processo (1695) e l'indirizzo di memoria di questa variabile (0x769822). Avendo queste informazioni possiamo utilizzare ``malloc_history`` in questa maniera

.. code-block:: shell

 $ malloc_history 1695 0x7698222
 malloc_history Report Version:  2.0
 Process:         ShitApp [1695]
 Path:            /Users/gianluca/Library/Application Support/iPhone Simulator/4.1/Applications/E29465C3-ACEA-4776-8998-2D8D62F6931F/ShitApp.app/ShitApp
 Load Address:    0x1000
 Identifier:      ShitApp
 Version:         ??? (???)
 Code Type:       X86 (Native)
 Parent Process:  gdb-i386-apple-darwin [25033]

 Date/Time:       2010-10-08 15:59:11.303 +0200
 OS Version:      Mac OS X 10.6.4 (10F569)
 Report Version:  6


 ALLOC 0x7684870-0x7684993 [size=292]: thread_a08eb500 |start | main | UIApplicationMain | GSEventRun | GSEventRunModal | CFRunLoopRunInMode | CFRunLoopRunSpecific | __CFRunLoopRun | __CFRunLoopDoTimer | __CFRUNLOOP_IS_CALLING_OUT_TO_A_TIMER_CALLBACK_FUNCTION__ | __NSFireDelayedPerform | -[UITableView _userSelectRowAtIndexPath:] | -[UITableView _selectRowAtIndexPath:animated:scrollPosition:notifyDelegate:] | -[ViewFinishCategories tableView:didSelectRowAtIndexPath:] | -[UINavigationController pushViewController:animated:] | -[UINavigationController pushViewController:transition:forceImmediate:] | -[UINavigationController _startDeferredTransitionIfNeeded] | -[UINavigationController _startTransition:fromViewController:toViewController:] | -[UINavigationController _layoutViewController:] | -[UINavigationController _computeAndApplyScrollContentInsetDeltaForViewController:] | -[UIViewController contentScrollView] | -[UIViewController view] | -[ViewFinishes viewDidLoad] | -[ShitAppDelegate imageWithImage:scaledToSize:] | UIGraphicsBeginImageContext | UIGraphicsBeginImageContextWithOptions | CGBitmapContextCreate | CGBitmapContextCreateWithData | bitmap_context_create | bitmap_context_delegate_create | __CGBitmapContextDelegateCreate | ripl_CreateWithData | calloc | malloc_zone_calloc 
 ----
 FREE  0x7684870-0x7684993 [size=292]: thread_a08eb500 |start | main | UIApplicationMain | GSEventRun | GSEventRunModal | CFRunLoopRunInMode | CFRunLoopRunSpecific | __CFRunLoopRun | __CFRunLoopDoTimer | __CFRUNLOOP_IS_CALLING_OUT_TO_A_TIMER_CALLBACK_FUNCTION__ | __NSFireDelayedPerform | -[UITableView _userSelectRowAtIndexPath:] | -[UITableView _selectRowAtIndexPath:animated:scrollPosition:notifyDelegate:] | -[ViewFinishCategories tableView:didSelectRowAtIndexPath:] | -[UINavigationController pushViewController:animated:] | -[UINavigationController pushViewController:transition:forceImmediate:] | -[UINavigationController _startDeferredTransitionIfNeeded] | -[UINavigationController _startTransition:fromViewController:toViewController:] | -[UINavigationController _layoutViewController:] | -[UINavigationController _computeAndApplyScrollContentInsetDeltaForViewController:] | -[UIViewController contentScrollView] | -[UIViewController view] | -[ViewFinishes viewDidLoad] | -[ShitAppDelegate imageWithImage:scaledToSize:] | PopContext | _CFRelease | context_reclaim | _CFRelease | CGContextDelegateFinalize | ripc_Finalize | ripl_release | free 

 ALLOC 0x7684990-0x768499f [size=16]: thread_a08eb500 |start | main | UIApplicationMain | GSEventRun | GSEventRunModal | CFRunLoopRunInMode | CFRunLoopRunSpecific | __CFRunLoopRun | __CFRunLoopDoTimer | __CFRUNLOOP_IS_CALLING_OUT_TO_A_TIMER_CALLBACK_FUNCTION__ | __NSFireDelayedPerform | -[UITableView _userSelectRowAtIndexPath:] | -[UITableView _selectRowAtIndexPath:animated:scrollPosition:notifyDelegate:] | -[ViewFinishCategories tableView:didSelectRowAtIndexPath:] | -[UINavigationController pushViewController:animated:] | -[UINavigationController pushViewController:transition:forceImmediate:] | -[UINavigationController _startDeferredTransitionIfNeeded] | -[UINavigationController _startTransition:fromViewController:toViewController:] | -[UINavigationController _layoutViewController:] | -[UINavigationController _computeAndApplyScrollContentInsetDeltaForViewController:] | -[UIViewController contentScrollView] | -[UIViewController view] | -[ViewFinishes viewDidLoad] | +[UIImage imageWithContentsOfFile:] | +[NSObject(NSObject) alloc] | +[NSObject(NSObject) allocWithZone:] | class_createInstance | _internal_class_createInstanceFromZone | calloc | malloc_zone_calloc 


scoprendo che è stata allocata all'interno della chiamata a ``[ViewFinishes viewDidLoad]`` in particolare con una chiamata a ``[UIImage imageWithContentsOfFile:]``. Certamente non rappresenta una descrizione precisissima ma aiuta a capire dove nasce il problema considerando che in questo caso specifico il free `fuorilegge` avveniva nell'animazione, fuori dalle possibilità di debugging in quanto presente nei frameworks interni della SDK.

**UPDATE**

Scopro che è possibile usare all'interno di gdb

.. code-block:: gdb

 (gdb) info malloc-history 0x769822

per ottenere un comodo backtrace. La fonte è http://stackoverflow.com/questions/2360273/debugging-exc-bad-access-from-a-nsstring.