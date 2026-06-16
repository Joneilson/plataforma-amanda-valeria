# Plataforma Amanda Valéria — Documento de Arquitetura

> Plataforma web para psicóloga clínica: site institucional + portal do paciente + painel de gestão (admin), com atendimento por vídeo embarcado e pagamentos online.

**Status:** planejamento (Fase de arquitetura)
**Última atualização:** 2026-06-15

---

## 1. Visão geral

Dois grandes domínios em um único produto:

1. **Site institucional (público):** SEO-first, apresenta a profissional e converte em contato/agendamento.
2. **Sistema/Portal (autenticado):** dois perfis — Paciente e Psicóloga (Admin) — com dashboards, agenda, prontuário, humor diário, anotações, chat, vídeo e pagamentos.

### Princípios

- **Privacidade por design (LGPD + CFP):** dado de saúde é sensível. Criptografia em repouso para conteúdo clínico, trilha de auditoria, consentimento explícito.
- **Separação de papéis (RBAC):** paciente nunca acessa dados de outro paciente; psicóloga tem visão de gestão.
- **API-first:** backend expõe API REST; frontend consome. Realtime via WebSocket.
- **Escalável e portável:** containerizado, serviços desacoplados (web, worker, realtime, db, cache).

---

## 2. Stack tecnológica

| Camada | Tecnologia | Observação |
|---|---|---|
| Backend | Django 5 + Django REST Framework | ORM, admin, auth, segurança by default |
| Realtime | Django Channels + Redis | Chat e notificações (WebSocket) |
| Banco | MySQL 8 | InnoDB, charset utf8mb4 |
| Tarefas assíncronas | Celery + Redis (broker) + Celery Beat | Lembretes, alertas clínicos, recibos |
| Frontend | Next.js (React + TypeScript) + Tailwind CSS | Landing SSR/SSG + app SPA |
| Vídeo | Daily.co (SDK embarcado) | Sala por agendamento; migrável p/ LiveKit |
| Pagamentos | Mercado Pago (Pix + cartão + recorrência) | Checkout + webhooks |
| E-mail | SMTP transacional (ex.: Amazon SES / Resend) | Confirmações, lembretes |
| Storage | S3 (ou compatível) | Arquivos de prontuário, áudios, recibos |
| Infra | Docker + Docker Compose | Deploy inicial Railway/Render → AWS futuramente |

---

## 3. Arquitetura de alto nível

```
                         ┌─────────────────────────────┐
                         │         Navegador            │
                         │  Next.js (Landing + App)     │
                         └───────┬─────────────┬────────┘
                       HTTPS/REST│             │WebSocket (wss)
                          (JWT)  │             │
                ┌────────────────▼───┐   ┌─────▼───────────────┐
                │  Django + DRF      │   │ Django Channels      │
                │  (API de negócio)  │   │ (chat, notificações) │
                └───┬───────┬────────┘   └─────────┬───────────┘
                    │       │                       │
        ┌───────────▼─┐  ┌──▼──────────┐      ┌─────▼──────┐
        │  MySQL 8    │  │ Celery      │      │   Redis    │
        │ (dados +    │  │ + Beat      │◄─────┤ (broker +  │
        │  cripto)    │  │ (workers)   │      │  cache +   │
        └─────────────┘  └──┬──────────┘      │  channels) │
                            │                  └────────────┘
              ┌─────────────┼────────────────┬──────────────┐
              ▼             ▼                ▼              ▼
        ┌──────────┐  ┌──────────┐    ┌──────────┐  ┌──────────┐
        │ Daily.co │  │ Mercado  │    │  E-mail  │  │   S3     │
        │ (vídeo)  │  │  Pago    │    │  (SES)   │  │ (arquivos)│
        └──────────┘  └──────────┘    └──────────┘  └──────────┘
```

---

## 4. Estrutura de pastas (monorepo)

```
plataforma/
├── docs/
│   └── ARQUITETURA.md
├── docker-compose.yml
├── .env.example
├── backend/                      # Django
│   ├── manage.py
│   ├── pyproject.toml
│   ├── config/                   # settings, urls, asgi/wsgi, celery
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   ├── asgi.py               # Channels
│   │   └── celery.py
│   └── apps/
│       ├── accounts/             # users, auth, RBAC, perfis
│       ├── patients/             # pacientes, prontuário
│       ├── scheduling/           # disponibilidade, agendamentos
│       ├── clinical/             # evolução clínica, anotações
│       ├── mood/                 # humor diário
│       ├── homework/             # tarefas terapêuticas
│       ├── messaging/            # chat (Channels)
│       ├── video/                # integração Daily.co
│       ├── payments/             # Mercado Pago
│       ├── resources/            # biblioteca de conteúdo
│       ├── notifications/        # lembretes, alertas
│       └── audit/                # trilha de auditoria (LGPD)
└── frontend/                     # Next.js
    ├── package.json
    ├── tailwind.config.ts        # design tokens da marca
    └── src/
        ├── app/
        │   ├── (public)/         # landing, sobre, contato
        │   ├── (auth)/           # login, recuperação de senha
        │   ├── (patient)/        # área do paciente
        │   └── (admin)/          # área da psicóloga
        ├── components/
        ├── lib/                  # api client, auth, utils
        └── styles/
```

---

## 5. Modelo de dados (MySQL)

> Convenções: PKs `id` BIGINT auto-increment; timestamps `created_at`/`updated_at`; campos marcados `🔒` = criptografados em nível de aplicação; soft-delete onde fizer sentido.

### accounts
**user**
- id, nome, email (unique), password_hash, role [PACIENTE | PSICOLOGA], telefone, ativo, last_login, created_at

**psychologist_profile** (1–1 com user role=PSICOLOGA)
- id, user_id (FK), crp, bio (text), especialidades (json), formacao (json), abordagem, foto_url, valor_sessao_padrao

### patients
**patient** (1–1 com user role=PACIENTE)
- id, user_id (FK), data_nascimento, genero, queixa_principal 🔒, contato_emergencia (json) 🔒, status [ATIVO|INATIVO|ALTA], inicio_tratamento, valor_sessao (override opcional)

### scheduling
**availability** (grade de horários da psicóloga)
- id, dia_semana (0-6), hora_inicio, hora_fim, modalidade [ONLINE|PRESENCIAL|AMBOS], ativo

**appointment** (núcleo do sistema)
- id, patient_id (FK), data_hora, duracao_min (default 50), modalidade [ONLINE|PRESENCIAL], status [AGENDADA|CONFIRMADA|REALIZADA|FALTA|CANCELADA], valor, observacao_publica, created_at
- relação 1–1 opcional com video_room e com payment

### video
**video_room**
- id, appointment_id (FK, unique), provider (default "daily"), room_name, room_url, token_paciente, token_psicologa, expira_em, gravacao_url (nullable)

### clinical
**clinical_record** (evolução clínica — visível só p/ psicóloga)
- id, patient_id (FK), appointment_id (FK, nullable), conteudo 🔒 (text), created_at, updated_at

**patient_note** (anotações pessoais do paciente)
- id, patient_id (FK), titulo, conteudo 🔒 (text), compartilhar_com_psicologa (bool), created_at, updated_at

### mood
**mood_entry** (humor diário)
- id, patient_id (FK), data (date, unique por paciente/dia), nivel (1-5), emocoes (json), tags (json: sono, trabalho, etc.), anotacao 🔒
- (variação opcional: registro pré/pós-sessão vinculado a appointment_id)

### homework
**homework** (tarefas terapêuticas)
- id, patient_id (FK), criado_por (FK user), titulo, descricao, prazo, status [PENDENTE|CONCLUIDA], concluida_em

### messaging
**conversation**
- id, patient_id (FK), psychologist_id (FK), updated_at

**message**
- id, conversation_id (FK), remetente_id (FK user), conteudo 🔒, lida (bool), created_at

### resources
**resource** (biblioteca de conteúdo)
- id, titulo, tipo [ARTIGO|AUDIO|PDF|VIDEO], url, descricao, patient_id (FK, nullable = conteúdo geral), publicado_em

### payments
**payment**
- id, appointment_id (FK, nullable), patient_id (FK), valor, status [PENDENTE|PAGO|FALHOU|ESTORNADO], metodo [PIX|CARTAO], provider (default "mercadopago"), provider_payment_id, recibo_url, pago_em, created_at

### notifications
**notification**
- id, user_id (FK), tipo, titulo, corpo, lida (bool), enviada_em, canal [APP|EMAIL|WHATSAPP]

### compliance
**consent** (LGPD / CFP)
- id, patient_id (FK), tipo [TERMO_USO|PRONTUARIO|TELEATENDIMENTO], versao, aceito_em, ip

**audit_log** (trilha de auditoria)
- id, user_id (FK), acao, recurso, recurso_id, ip, user_agent, timestamp

### Relações principais
- user 1–1 patient / psychologist_profile
- patient 1–N appointment, mood_entry, clinical_record, patient_note, homework, payment
- appointment 1–1 video_room, 1–1 payment (opcional)
- conversation 1–N message; patient 1–1 conversation (com a psicóloga)

---

## 6. API (recursos principais — REST)

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| POST | /api/auth/login | público | JWT (access + refresh) |
| POST | /api/auth/refresh | público | renovar token |
| POST | /api/auth/password-reset | público | recuperação de senha |
| GET | /api/me | autenticado | dados do usuário logado |
| GET/POST | /api/appointments | paciente/admin | listar/criar agendamentos |
| PATCH | /api/appointments/{id} | admin | status (realizada/falta/cancelada) |
| GET | /api/availability | público (slots livres) | horários disponíveis |
| GET/POST | /api/mood | paciente | humor diário |
| GET | /api/mood/insights | paciente/admin | série temporal + tendências |
| GET/POST | /api/notes | paciente | anotações pessoais |
| GET/POST | /api/clinical-records | admin | evolução clínica |
| GET/POST | /api/homework | admin cria / paciente conclui | tarefas |
| GET | /api/conversations / messages | paciente/admin | chat (histórico) |
| POST | /api/video/rooms/{appointment_id} | autenticado | gera sala + token |
| POST | /api/payments/checkout | paciente | inicia cobrança Mercado Pago |
| POST | /api/webhooks/mercadopago | externo | confirmação de pagamento |
| GET | /api/admin/metrics | admin | KPIs do dashboard |

WebSocket: `/ws/chat/{conversation_id}/` e `/ws/notifications/`.

---

## 7. Segurança, LGPD e CFP

- **Autenticação:** JWT (access curto + refresh), senhas com hash forte (Django default Argon2/PBKDF2).
- **Autorização (RBAC):** permissões DRF por papel + object-level (paciente só acessa o próprio recurso).
- **Criptografia:**
  - Em trânsito: TLS obrigatório.
  - Em repouso: criptografia de campos sensíveis 🔒 (prontuário, anotações, mensagens) em nível de aplicação (ex.: Fernet com chave gerenciada/KMS), além de backups criptografados.
- **Trilha de auditoria:** todo acesso/edição a prontuário gera registro em `audit_log`.
- **Consentimento:** termos versionados (uso, prontuário, teleatendimento) aceitos e registrados (`consent`).
- **CFP (Res. 11/2018):** atendimento online requer consentimento e guarda de prontuário; e-Psi quando aplicável.
- **LGPD:** base legal (tutela da saúde), direito de acesso/exclusão, minimização de dados, DPO/contato.
- **Rate limiting** e proteção de webhooks (validação de assinatura Mercado Pago).

---

## 8. Vídeo embarcado (Daily.co)

Fluxo:
1. No horário do agendamento online, backend cria/recupera a `video_room` via API Daily.co.
2. Backend gera **tokens de acesso** (um para paciente, um para psicóloga) com expiração.
3. Frontend embute a sala com o SDK `@daily-co/daily-js` (iframe/call object) **dentro do sistema** — sem link externo.
4. Opcional: gravação (com consentimento) salva em S3, URL em `video_room.gravacao_url`.

Migração futura: a app `video/` abstrai o provider, então trocar Daily.co por LiveKit afeta só essa app.

---

## 9. Pagamentos (Mercado Pago)

Fluxo:
1. Paciente inicia pagamento de uma sessão → `POST /api/payments/checkout`.
2. Backend cria preferência/cobrança no Mercado Pago (Pix ou cartão) e registra `payment` (PENDENTE).
3. Mercado Pago notifica `POST /api/webhooks/mercadopago` → backend valida e atualiza `payment` (PAGO/FALHOU).
4. Em PAGO: Celery gera **recibo** (PDF em S3) e dispara notificação/e-mail.

Camada `payments/` abstrai o provider para futura troca/adicção (Asaas, Stripe).

---

## 10. Tarefas assíncronas (Celery Beat)

- Lembrete de sessão (e-mail/WhatsApp) 24h e 1h antes.
- Alerta clínico: paciente com humor baixo recorrente ou sem registro/comparecimento → lista de atenção da psicóloga.
- Geração de recibos pós-pagamento.
- Relatórios/KPIs agregados (cache diário).
- Aniversariantes da semana.

---

## 11. Dashboards

### Paciente
- Próximo atendimento em destaque (calendário).
- Humor diário + gráfico de evolução (insights).
- Tarefas terapêuticas pendentes.
- Atalho "Entrar na sala" (quando houver sessão online).

### Psicóloga (Admin) — KPIs
- Cards: total de atendimentos realizados, total de horas de sessão, online vs. presencial.
- Faturamento mensal + projeção + contas a receber/inadimplência.
- Taxa de faltas (no-show) e cancelamentos.
- Taxa de ocupação da agenda.
- Novos pacientes vs. recorrentes; retenção.
- Mapa de calor de horários.
- Alertas clínicos (pacientes em atenção).
- Aniversariantes da semana.

---

## 12. Plano de fases

| Fase | Entrega |
|---|---|
| 0 | Setup: monorepo, Docker, Django+MySQL+Next.js, design tokens |
| 1 | Auth & RBAC, consentimentos, auditoria |
| 2 | Site institucional (SEO, contato, CTAs) |
| 3 | Núcleo: pacientes (CRUD), agenda, dashboards |
| 4 | Ferramentas do paciente: humor, anotações, tarefas, SOS |
| 5 | Prontuário/evolução clínica + chat |
| 6 | Vídeo (Daily.co) |
| 7 | Pagamentos (Mercado Pago) + recibos + métricas avançadas |
| 8 | Hardening: criptografia, backups, testes, LGPD review, deploy |

> MVP recomendado ao fim da Fase 3.
