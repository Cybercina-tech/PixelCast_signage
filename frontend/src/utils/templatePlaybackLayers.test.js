import { describe, it, expect } from 'vitest'
import { buildPlaybackLayers, resolveWidgetRotation } from './templatePlaybackLayers.js'

describe('resolveWidgetRotation', () => {
  it('prefers root rotation from editor config', () => {
    expect(resolveWidgetRotation({ rotation: 45 }, { rotation: 10 })).toBe(45)
  })

  it('falls back to style rotation', () => {
    expect(resolveWidgetRotation({}, { rotation: 30 })).toBe(30)
  })

  it('returns 0 when unset', () => {
    expect(resolveWidgetRotation({}, {})).toBe(0)
  })
})

describe('buildPlaybackLayers', () => {
  it('merges config widget rotation into content_json for playback', () => {
    const template = {
      width: 1920,
      height: 1080,
      layers: [],
      config_json: {
        widgets: [
          {
            id: 'w1',
            type: 'text',
            name: 'Rotated',
            x: '10%',
            y: '10%',
            width: '20%',
            height: '10%',
            zIndex: 1,
            visible: true,
            rotation: 33,
            style: { color: '#fff' },
          },
        ],
      },
    }

    const layers = buildPlaybackLayers(template)
    const widget = layers[0]?.widgets?.[0]
    expect(widget?.content_json?.rotation).toBe(33)
    expect(widget?.rotation).toBe(33)
  })
})
