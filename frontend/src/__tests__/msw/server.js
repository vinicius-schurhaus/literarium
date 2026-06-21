import { setupServer } from 'msw/node'
import { handlers } from './handlers'

// Servidor MSW para os testes (ambiente node/jsdom).
export const server = setupServer(...handlers)
