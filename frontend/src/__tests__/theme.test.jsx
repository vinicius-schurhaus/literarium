import { describe, it, expect, beforeEach } from 'vitest'
import { render, act } from '@testing-library/react'
import { ThemeProvider, useTheme } from '@/theme/ThemeContext'

// A interface do Literarium é "light-only": o ThemeProvider força tema claro,
// remove a classe .dark e limpa qualquer preferência salva.
function ThemeConsumer() {
  const { isDark, toggle } = useTheme()
  return (
    <div>
      <span data-testid="mode">{isDark ? 'dark' : 'light'}</span>
      <button onClick={toggle}>toggle</button>
    </div>
  )
}

describe('ThemeProvider (light-only)', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('defaults to light', () => {
    const { getByTestId } = render(
      <ThemeProvider><ThemeConsumer /></ThemeProvider>
    )
    expect(getByTestId('mode').textContent).toBe('light')
  })

  it('ignores stored dark preference and stays light', () => {
    localStorage.setItem('theme', 'dark')
    const { getByTestId } = render(
      <ThemeProvider><ThemeConsumer /></ThemeProvider>
    )
    expect(getByTestId('mode').textContent).toBe('light')
    expect(localStorage.getItem('theme')).toBeNull()
  })

  it('removes the .dark class from <html>', () => {
    document.documentElement.classList.add('dark')
    render(<ThemeProvider><ThemeConsumer /></ThemeProvider>)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('toggle is a no-op (theme remains light)', () => {
    const { getByRole, getByTestId } = render(
      <ThemeProvider><ThemeConsumer /></ThemeProvider>
    )
    act(() => getByRole('button').click())
    expect(getByTestId('mode').textContent).toBe('light')
  })
})
