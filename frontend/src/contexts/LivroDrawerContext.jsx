import { createContext, useContext, useState } from 'react'

const Ctx = createContext(null)

export function LivroDrawerProvider({ children }) {
  const [livroId, setLivroId] = useState(null)
  return (
    <Ctx.Provider value={{ livroId, openLivro: setLivroId, closeLivro: () => setLivroId(null) }}>
      {children}
    </Ctx.Provider>
  )
}

export function useLivroDrawer() {
  return useContext(Ctx) ?? { livroId: null, openLivro: () => {}, closeLivro: () => {} }
}
