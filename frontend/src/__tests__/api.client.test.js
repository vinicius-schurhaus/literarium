/**
 * Tests for the axios API client:
 * - Bearer token injection (verificado pelo header real recebido via MSW)
 * - Silent JWT refresh on 401
 * - auth:logout event dispatch when refresh fails
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from './msw/server'

describe('API client token injection', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetModules()
  })

  it('sends Authorization header when access_token is set', async () => {
    localStorage.setItem('access_token', 'test-access-token')

    let received = null
    server.use(
      http.get('*/api/ping/', ({ request }) => {
        received = request.headers.get('authorization')
        return HttpResponse.json({ ok: true })
      })
    )

    const { default: api } = await import('@/api/client')
    await api.get('/ping/')

    expect(received).toBe('Bearer test-access-token')
  })

  it('does not send Authorization header without token', async () => {
    localStorage.removeItem('access_token')

    let received = 'unset'
    server.use(
      http.get('*/api/ping/', ({ request }) => {
        received = request.headers.get('authorization')
        return HttpResponse.json({ ok: true })
      })
    )

    const { default: api } = await import('@/api/client')
    await api.get('/ping/')

    expect(received).toBeNull()
  })
})

describe('API client 401 refresh flow', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetModules()
  })

  it('refreshes the token on 401 and retries the request', async () => {
    localStorage.setItem('access_token', 'expired')
    localStorage.setItem('refresh_token', 'valid-refresh')

    let calls = 0
    server.use(
      http.post('*/api/auth/token/refresh/', () =>
        HttpResponse.json({ access: 'new-access' })
      ),
      http.get('*/api/protegido/', ({ request }) => {
        calls += 1
        const auth = request.headers.get('authorization')
        if (auth === 'Bearer expired') {
          return new HttpResponse(null, { status: 401 })
        }
        return HttpResponse.json({ ok: true })
      })
    )

    const { default: api } = await import('@/api/client')
    const resp = await api.get('/protegido/')

    expect(resp.data).toEqual({ ok: true })
    expect(calls).toBe(2) // primeira (401) + retry com novo token
    expect(localStorage.getItem('access_token')).toBe('new-access')
  })

  it('dispatches auth:logout when there is no refresh token', async () => {
    localStorage.setItem('access_token', 'expired')

    const handler = vi.fn()
    window.addEventListener('auth:logout', handler)

    server.use(
      http.get('*/api/protegido/', () => new HttpResponse(null, { status: 401 }))
    )

    const { default: api } = await import('@/api/client')
    await api.get('/protegido/').catch(() => {})
    window.removeEventListener('auth:logout', handler)

    expect(handler).toHaveBeenCalled()
  })
})
