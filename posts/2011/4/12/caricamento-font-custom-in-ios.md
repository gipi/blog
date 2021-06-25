<!--
.. title: Caricamento font custom in IOS
.. slug: caricamento-font-custom-in-ios
.. date: 2011-04-12 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Per rendere una applicazione Iphone completa spesso è necessario dotarla di un carattere tipografico che si addica allo stile; per fare questo non è difficile, basta sapere come fare (un po' come tutto nella vita) ed è questo il modo in cui mi sono ritrovato ad implementarlo

Nel codice che segue la funzione più importante è GSFontAddFromFile ed il particolare da tenere a mente è che al momento di richiamare il font bisogna indicare il nome vero e proprio di questo e non il nome del file; proprio per questo in questa funzione viene dumpato il nome di tutti i font disponibili proprio prima di uscire (in produzione disabilitatelo siccome è praticamente inutile se non per debugging iniziale).

.. code-block:: objective-c

 + (NSUInteger) loadFonts {
	NSUInteger newFontCount = 0;
	NSBundle *frameworkBundle = [NSBundle bundleWithIdentifier:@"com.apple.GraphicsServices"];
	const char *frameworkPath = [[frameworkBundle executablePath] UTF8String];
	if (frameworkPath) {
		void *graphicsServices = dlopen(frameworkPath, RTLD_NOLOAD | RTLD_LAZY);
		if (graphicsServices) {
			NSLog(@"GraphicsServices ON");
			BOOL (*GSFontAddFromFile)(const char *) =
				dlsym(graphicsServices, "GSFontAddFromFile");
			if (GSFontAddFromFile)
				for (NSString *fontFile in [[NSBundle mainBundle]
					pathsForResourcesOfType:@"ttf" inDirectory:nil]) {
					NSLog(@"loaded font file %@", fontFile);
					newFontCount += GSFontAddFromFile([fontFile UTF8String]);
				}
		}
	}

	//NSLog(@"Available Font Families: %@", [UIFont familyNames]);
	for (NSString* familia in [UIFont familyNames]) {
		NSLog(@"Family: %@", familia);
		for (NSString* fontName in [UIFont fontNamesForFamilyName:familia]) {
			NSLog(@" %@", fontName);
		}
	}

	return newFontCount;
 }



Liberamente tratto da http://discussions.apple.com/thread.jspa?threadID=2226259