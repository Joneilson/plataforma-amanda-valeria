# Plataforma Amanda Valéria

Plataforma web para a psicóloga clínica Amanda Valéria (CRP 02/31074):
site institucional + portal do paciente + painel de gestão, com atendimento
por vídeo embarcado e pagamentos online.

## Arquitetura

Monorepo com backend e frontend **totalmente separados**, comunicando apenas via API REST/WebSocket.

```
plataforma/
├── backend/    Django 5 + DRF + Channels (API, regras de negócio)
├── frontend/   Next.js (React + TypeScript + Tailwind)
└── docs/       Documentação (ver docs/ARQUITETURA.md)
```

Detalhes completos em [docs/ARQUITETURA.md](docs/ARQUITETURA.md).

### Convenção de camadas (backend)

Cada app segue a mesma separação de responsabilidades:

| Arquivo | Responsabilidade |
|---|---|
| `models.py` | Estrutura de dados |
| `services.py` | Lógica de **escrita** (regras de negócio) |
| `selectors.py` | Lógica de **leitura** (consultas) |
| `api/` | Views/serializers/urls — camada fina (valida e delega) |
| `permissions.py` | Controle de acesso por papel (RBAC) |

## Stack

Django 5 · DRF · Channels · MySQL 8 · Celery · Redis · Next.js · Tailwind ·
Daily.co (vídeo) · Mercado Pago (pagamentos) · Docker.

## Como rodar (desenvolvimento)

Pré-requisitos: Docker + Docker Compose.

```bash
cp .env.example .env          # ajuste os valores
docker compose up --build
```

Serviços:

- Frontend: http://localhost:3000
- API/Backend: http://localhost:8000/api
- Admin Django: http://localhost:8000/admin

Primeiro acesso (migrações e superusuário):

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

## Roadmap

Plano em 8 fases (ver `docs/ARQUITETURA.md`).
Estado atual: **Fase 3 — núcleo** concluída → **MVP funcional**. Inclui:
gestão de pacientes (CRUD), agenda/agendamentos com transição de status,
dashboard de métricas da psicóloga e dashboard do paciente (próximo atendimento),
com menu lateral e áreas protegidas por papel.
