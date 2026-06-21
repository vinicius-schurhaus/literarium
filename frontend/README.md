# Literarium — Frontend

Aplicação React (Vite) que consome a API do backend Django. Esta pasta contém
apenas o cliente web; o backend e as instruções gerais de execução estão no
[README principal](../README.md) na raiz do repositório.

## Desenvolvimento

```bash
npm install   # primeira vez
npm run dev   # http://localhost:5173
```

O backend precisa estar rodando em `http://localhost:8000`. Em dev, o proxy do
Vite encaminha `/api` e `/media` para lá, então não é preciso configurar URLs.

## Scripts

| Comando | Descrição |
|---|---|
| `npm run dev` | Servidor de desenvolvimento com hot reload. |
| `npm run build` | Build de produção em `dist/`. |
| `npm run preview` | Serve o build de produção localmente. |
| `npm run lint` | ESLint. |
| `npm test` | Testes (Vitest). |
| `npm run test:coverage` | Testes com relatório de cobertura. |

## Estrutura

```
src/
├── api/          # Clientes HTTP (axios) por recurso
├── auth/         # Contexto de autenticação e rotas protegidas
├── components/   # Componentes reutilizáveis (ui, layout, livros, resenhas…)
├── contexts/     # Contextos React
├── pages/        # Páginas (portal do aluno e área de gestão em staff/)
└── theme/        # Tema da aplicação
```

## Variável de ambiente

Em produção, defina `VITE_API_URL` com a URL da API (ex.: `https://.../api`).
Veja `.env.example`.
