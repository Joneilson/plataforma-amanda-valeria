# Retomada do projeto (após formatar o PC)

> Guia para colocar a Plataforma Amanda Valéria de volta no ar em uma máquina nova.
> Última atualização: 2026-06-18.

## 1. Estado atual do projeto

- **Fases 0, 1, 2 e 3 concluídas** (ver [ARQUITETURA.md](ARQUITETURA.md) §12 e o histórico do git).
- Fase 3 (Ferramentas do Paciente) entregue: **humor diário**, **anotações pessoais**
  (com compartilhamento), **tarefas terapêuticas** e **página SOS**.
- Conteúdo clínico sensível é cifrado em repouso via `apps/common/fields.py::EncryptedTextField`
  (Fernet); a chave vem de `FIELD_ENCRYPTION_KEY` (em dev, deriva da `SECRET_KEY`).
- **Próxima fase: Fase 4** — prontuário/evolução clínica + chat em tempo real (Channels).
- Todo o código está no GitHub: `https://github.com/Joneilson/plataforma-amanda-valeria`
  (branch `main`, até o commit `eeeff05`).

## 2. O que salvar ANTES de formatar

O código já está no GitHub, então **não** precisa copiar a pasta do projeto inteira.
Salve apenas o que **não** está versionado:

| O quê | Caminho | Por quê | Essencial? |
|---|---|---|---|
| Arquivo `.env` | `plataforma/.env` | Configuração/segredos (está no .gitignore) | **Sim** |
| Memória do Claude | `C:\Users\<voce>\.claude\projects\d--Projetos-ProjetoAmanda-plataforma\memory\` | Contexto do projeto entre sessões do Claude Code | Recomendado |
| Permissões do Claude (projeto) | `plataforma/.claude/settings.json` | Allowlist de comandos do Claude | Opcional |
| Banco de testes (Docker) | volume `plataforma_db_data` | Dados de teste do MySQL | Opcional (recriável) |

**Como salvar:** copie esses itens para um pendrive, HD externo ou nuvem
(Google Drive/OneDrive). São arquivos pequenos (o `.env` tem ~1 KB).

> O resto — `node_modules/`, `.venv/`, `.next/`, imagens Docker — é regenerável e
> **não** precisa ser salvo.

## 3. Como restaurar na máquina nova

1. **Instalar pré-requisitos:** Git, Docker Desktop e (opcional p/ lint local) Python 3.13 + Node 22.
2. **Clonar o repositório:**
   ```bash
   git clone https://github.com/Joneilson/plataforma-amanda-valeria.git
   cd plataforma-amanda-valeria
   ```
3. **Restaurar o `.env`:** copie o `.env` salvo para a raiz do projeto.
   (Se não tiver, use `cp .env.example .env` e preencha os valores.)
4. **Subir o stack:**
   ```bash
   docker compose up --build -d
   ```
5. **Migrar o banco** (o backend sobe com `runserver`, que NÃO migra sozinho):
   ```bash
   docker compose exec backend python manage.py migrate
   ```
6. **Criar a conta da psicóloga (admin):**
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```
   Crie com `role=PSICOLOGA`. Os pacientes são criados por ela dentro do sistema.
7. **Acessar:** Frontend `http://localhost:3000` · API `http://localhost:8000/api`
   · Admin Django `http://localhost:8000/admin`.

## 4. Lembretes úteis

- Restaurar o volume `plataforma_db_data` é opcional; numa máquina nova o banco
  começa vazio e os passos 5–6 recriam tudo. Contas/dados de teste antigos só
  voltam se você fizer dump/restore do volume.
- Identidade do git neste repo: `Joneilson <joneilsonjunior@gmail.com>`
  (reconfigure com `git config user.name/user.email` se necessário).
- O Claude Code não recupera a memória sozinho após formatar; se quiser manter o
  contexto, restaure a pasta `memory/` (item 2) no mesmo caminho.
