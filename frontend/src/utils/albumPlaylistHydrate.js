/** Resolve a playable URL from a Content API record. */
export function pickContentPlaybackUrl(content) {
  if (!content || typeof content !== 'object') return ''
  return content.secure_url || content.absolute_file_url || content.file_url || ''
}

/** Build content_id → { url, mediaType, name } from template.layers (detail API). */
export function buildContentLookupFromTemplateLayers(template) {
  const lookup = new Map()
  const layers = Array.isArray(template?.layers) ? template.layers : []
  for (const layer of layers) {
    const layerWidgets = Array.isArray(layer?.widgets) ? layer.widgets : []
    for (const widget of layerWidgets) {
      const contents = Array.isArray(widget?.contents) ? widget.contents : []
      for (const content of contents) {
        if (!content?.id) continue
        const url = pickContentPlaybackUrl(content)
        if (!url) continue
        lookup.set(String(content.id), {
          url,
          mediaType: content.type || null,
          name: content.name || '',
        })
      }
    }
  }
  return lookup
}

/**
 * Fill missing playlist item URLs on album editor widgets (for WidgetPreview).
 * @param {Array<object>} albumWidgets - editor widgets with type === 'album'
 * @param {Map<string, { url: string, mediaType?: string, name?: string }>} contentLookup
 * @param {(id: string) => Promise<object>} fetchContentById
 */
export async function hydrateAlbumPlaylistUrls(albumWidgets, contentLookup, fetchContentById) {
  if (!Array.isArray(albumWidgets) || !albumWidgets.length) return

  const missingIds = new Set()
  for (const widget of albumWidgets) {
    const playlist = Array.isArray(widget.style?.playlist) ? widget.style.playlist : []
    for (const item of playlist) {
      if (!item?.content_id || item.url) continue
      const id = String(item.content_id)
      if (!contentLookup.get(id)) missingIds.add(id)
    }
  }

  const fetched = new Map()
  if (missingIds.size && typeof fetchContentById === 'function') {
    await Promise.all(
      [...missingIds].map(async (id) => {
        try {
          const content = await fetchContentById(id)
          const url = pickContentPlaybackUrl(content)
          if (url) {
            fetched.set(id, {
              url,
              mediaType: content.type || null,
              name: content.name || '',
            })
          }
        } catch {
          // Preview can stay empty for unreachable content
        }
      }),
    )
  }

  for (const widget of albumWidgets) {
    const playlist = Array.isArray(widget.style?.playlist) ? widget.style.playlist : []
    for (const item of playlist) {
      if (!item?.content_id || item.url) continue
      const id = String(item.content_id)
      const meta = contentLookup.get(id) || fetched.get(id)
      if (!meta?.url) continue
      item.url = meta.url
      if (!item.mediaType && meta.mediaType) item.mediaType = meta.mediaType
      if (!item.name && meta.name) item.name = meta.name
    }
  }
}
