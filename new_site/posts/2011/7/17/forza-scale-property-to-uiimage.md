<!--
.. title: Forza scale property to UIImage
.. slug: forza-scale-property-to-uiimage
.. date: 2011-07-17 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Ogni UIImage ha una proprietà **read only** chiamata ``scale`` descritta come segue nella documentazione Apple:

::

 If you load an image from a file whose name includes the @2x modifier,
 the scale is set to 2.0. If the filename does not include the modifier
 but is in the PNG or JPEG format and has an associated DPI value, a
 corresponding scale factor is computed and reflected in this property.
 You can also specify an explicit scale factor when initializing an image
 from a Core Graphics image. All other images are assumed to have a scale
 factor of 1.0.

 If you multiply the logical size of the image (stored in the size property)
 by the value in this property, you get the dimensions of the image in pixels.
 Availability

Caricando normalmente una immagine non è possibile impostare questo valore se non usando il modificatore ``@2x`` nel nome del file, ma in alcuni casi questo non è possibile. Per risolvere il problema si deve andare a creare una immagine con un valore di ``scale`` apposito come descritto con il pezzo di codice seguente

.. code-block:: objc

 +(UIImage*)getUIImageFromPath:(NSString*)file withScale:(CGFloat)scale{
	UIImage* tmpImage =
		[UIImage imageWithCGImage:
			[UIImage imageWithData:
				[NSData dataWithContentsOfFile:file]] CGImage] scale:scale orientation:UIImageOrientationUp];

    return tmpImage;
 }