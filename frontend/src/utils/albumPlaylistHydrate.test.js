import { describe, it, expect, vi } from 'vitest'
import {
  buildContentLookupFromTemplateLayers,
  hydrateAlbumPlaylistUrls,
  pickContentPlaybackUrl,
} from './albumPlaylistHydrate.js'

describe('pickContentPlaybackUrl', () => {
  it('prefers secure_url', () => {
    expect(
      pickContentPlaybackUrl({
        secure_url: 'https://cdn/a.jpg',
        file_url: 'https://old/a.jpg',
      }),
    ).toBe('https://cdn/a.jpg')
  })
})

describe('hydrateAlbumPlaylistUrls', () => {
  it('fills missing playlist urls from layer contents', async () => {
    const albumWidget = {
      type: 'album',
      style: {
        playlist: [{ content_id: 'c1', name: 'One' }],
      },
    }
    const lookup = buildContentLookupFromTemplateLayers({
      layers: [
        {
          widgets: [
            {
              contents: [
                {
                  id: 'c1',
                  type: 'image',
                  secure_url: 'https://example.com/one.jpg',
                  name: 'One',
                },
              ],
            },
          ],
        },
      ],
    })

    await hydrateAlbumPlaylistUrls([albumWidget], lookup, vi.fn())
    expect(albumWidget.style.playlist[0].url).toBe('https://example.com/one.jpg')
    expect(albumWidget.style.playlist[0].mediaType).toBe('image')
  })

  it('fetches content when not in template layers', async () => {
    const albumWidget = {
      type: 'album',
      style: {
        playlist: [{ content_id: 'c2' }],
      },
    }
    const fetchContentById = vi.fn().mockResolvedValue({
      id: 'c2',
      type: 'video',
      file_url: 'https://example.com/two.mp4',
      name: 'Two',
    })

    await hydrateAlbumPlaylistUrls([albumWidget], new Map(), fetchContentById)
    expect(fetchContentById).toHaveBeenCalledWith('c2')
    expect(albumWidget.style.playlist[0].url).toBe('https://example.com/two.mp4')
    expect(albumWidget.style.playlist[0].mediaType).toBe('video')
  })
})
