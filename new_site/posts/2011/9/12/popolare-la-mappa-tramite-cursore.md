<!--
.. title: Popolare la mappa tramite cursore
.. slug: popolare-la-mappa-tramite-cursore
.. date: 2011-09-12 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

.. code-block:: java

	/**
	 * This uses a Cursor in order to populate the Maps with the Overlay
	 */
	private class NectarItemizedOverlay extends ItemizedOverlay<OverlayItem> {
		private ArrayList<OverlayItem> mOverlays = new ArrayList<OverlayItem>();
		private Context mContext;
		private Cursor mCursor;

		public NectarItemizedOverlay(Drawable defaultMarker) {
			super(boundCenterBottom(defaultMarker));
		}

		public NectarItemizedOverlay(Drawable defaultMarker, Context context, Cursor c) {
			// Note that you will need to add bounds to the marker in order for it to draw correctly.
			// Typically this is done with boundCenterBottom, as in super(boundCenterBottom(marker)).
			super(boundCenterBottom(defaultMarker));

			mContext = context;
			mCursor = c;

			/* Utility method to perform all processing on a new ItemizedOverlay.
			 * Subclasses provide Items through the createItem(int) method.
			 * The subclass should call this as soon as it has data, before anything else gets called. 
			 */
			populate();
		}

		public void addOverlay(OverlayItem overlay) {
			mOverlays.add(overlay);
		}

		@Override
		protected OverlayItem createItem(int i) {
			mCursor.moveToPosition(i);
			String[] coords = mCursor.getString(3).split(",");

			int lat = new Integer(coords[0]).intValue();
			int lng = new Integer(coords[1]).intValue();

			Log.i("DEBUG", "found coord " + lat + ", " + lng);

			GeoPoint point = new GeoPoint(lat, lng);

			OverlayItem oi = new OverlayItem(point, mCursor.getString(2), "Bau");

			return oi;
		}

		public void update() {
			//populate();
		}

		@Override
		public int size() {
			return mCursor.getCount();
		}
	}
