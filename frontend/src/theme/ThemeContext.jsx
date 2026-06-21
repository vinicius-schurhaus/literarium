import { createContext, useContext, useEffect } from 'react'

const ThemeContext = createContext({ isDark: false, toggle: () => {} })

export function ThemeProvider({ children }) {
  useEffect(() => {
    // A interface é sempre clara; garante que nenhuma preferência antiga force o tema escuro.
    document.documentElement.classList.remove('dark')
    localStorage.removeItem('theme')
  }, [])

  return (
    <ThemeContext.Provider value={{ isDark: false, toggle: () => {} }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
