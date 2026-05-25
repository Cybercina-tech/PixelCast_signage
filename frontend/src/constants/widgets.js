/**
 * Single source of truth for template widget types (keep in sync with backend WIDGET_TYPE_CHOICES).
 */

export const WIDGET_TYPES = Object.freeze([
  'clock',
  'date',
  'weekday',
  'countdown',
  'text',
  'marquee',
  'weather',
  'qr_action',
  'image',
  'video',
  'album',
  'webview',
  'chart',
])

/** @type {ReadonlySet<string>} */
export const WIDGET_TYPE_SET = new Set(WIDGET_TYPES)

export function isKnownWidgetType(type) {
  return WIDGET_TYPE_SET.has(type)
}

/** Library panel sections (Template Editor). */
export const WIDGET_LIBRARY_SECTIONS = Object.freeze([
  {
    id: 'date-time',
    label: 'Date & Time',
    items: [
      { type: 'clock', label: 'Add Clock', iconPath: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
      { type: 'date', label: 'Add Date', iconPath: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
      { type: 'weekday', label: 'Add Weekday', iconPath: 'M8 7V3m8 4V3m-9 9h10m-8 5h6M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
      {
        type: 'countdown',
        label: 'Add Countdown',
        iconPath:
          'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41',
      },
    ],
  },
  {
    id: 'text-live',
    label: 'Text & Live Info',
    items: [
      { type: 'text', label: 'Add Text', iconPath: 'M4 6h16M4 12h16M4 18h7' },
      { type: 'marquee', label: 'Add Marquee', iconPath: 'M4 12h16M4 7h7m6 0h3M4 17h5m8 0h3' },
      { type: 'weather', label: 'Add Weather', iconPath: 'M3 15a4 4 0 014-4h.26A6 6 0 0119 13h1a3 3 0 010 6H7a4 4 0 01-4-4z' },
      {
        type: 'qr_action',
        label: 'Add QR Action',
        iconPath:
          'M4 4h5v5H4V4zm11 0h5v5h-5V4zM4 15h5v5H4v-5zm2-9h1v1H6V6zm10 0h1v1h-1V6zm-1 10h5v1h-5v-1zm-1-5h1v3h-1v-3zm-3 0h2v1h-2v-1zm-1 2h1v1h-1v-1zm2 2h1v1h-1v-1zm-2 2h2v1h-2v-1z',
      },
    ],
  },
  {
    id: 'media',
    label: 'Media',
    items: [
      {
        type: 'image',
        label: 'Add Image',
        iconPath:
          'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
      },
      {
        type: 'video',
        label: 'Add Video',
        iconPath:
          'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z',
      },
      { type: 'album', label: 'Add Album Playlist', iconPath: 'M4 7h16M4 12h16M4 17h10m4 0h2M8 7v10M16 7v10' },
    ],
  },
  {
    id: 'web-data',
    label: 'Web & Data',
    items: [
      { type: 'webview', label: 'Add Webview', iconPath: 'M21 12H3m0 0l4-4m-4 4l4 4m14-4l-4-4m4 4l-4 4' },
      { type: 'chart', label: 'Add Chart', iconPath: 'M3 3v18h18M8 13l3-3 3 2 4-5' },
    ],
  },
])
