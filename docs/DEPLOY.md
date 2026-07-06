# Deploy em produção (VPS)

> Guia para subir a Plataforma Amanda Valéria em um VPS com Docker, HTTPS e backups.
> Última atualização: 2026-07-06.

## 1. Pré-requisitos

- VPS Linux (2 GB RAM ou mais) com Docker + Docker Compose instalados
- Domínio apontando para o IP do VPS (registro A), ex.: `app.amandavaleria.com.br`
- Conta SMTP para envio de e-mails (lembretes de sessão e reset de senha)

## 2. Variáveis de produção no `.env`

Além das variáveis já usadas em dev, defina:

```env
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<string longa e aleatória — NUNCA o default>
DJANGO_ALLOWED_HOSTS=app.amandavaleria.com.br

# OBRIGATÓRIA em produção — o backend recusa subir sem ela:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FIELD_ENCRYPTION_KEY=<chave Fernet>

DOMAIN=app.amandavaleria.com.br
FRONTEND_URL=https://app.amandavaleria.com.br
BACKEND_URL=https://app.amandavaleria.com.br
CORS_ALLOWED_ORIGINS=https://app.amandavaleria.com.br
NEXT_PUBLIC_API_URL=https://app.amandavaleria.com.br

# SMTP (ex.: Brevo, Resend, Gmail workspace)
EMAIL_HOST=smtp.exemplo.com
EMAIL_PORT=587
EMAIL_HOST_USER=usuario
EMAIL_HOST_PASSWORD=senha
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=Amanda Valéria <contato@amandavaleria.com.br>
```

> ⚠️ Guarde a `FIELD_ENCRYPTION_KEY` em local seguro fora do servidor.
> Perder essa chave = perder acesso ao conteúdo clínico cifrado.
> Trocar a chave NÃO recifra dados antigos (eles ficam ilegíveis).

## 3. Primeiro certificado TLS (uma vez)

O Nginx só sobe com certificado existente. Emita o primeiro assim:

```bash
# 1. Suba só o nginx na porta 80 com um server temporário, OU use standalone:
docker compose -f docker-compose.prod.yml run --rm -p 80:80 \
  certbot certonly --standalone -d app.amandavaleria.com.br \
  --email contato@amandavaleria.com.br --agree-tos --no-eff-email

# 2. Agora suba tudo:
docker compose -f docker-compose.prod.yml up -d --build
```

A renovação é automática (serviço `certbot` tenta a cada 12h via webroot).
Após uma renovação, recarregue o nginx: `docker compose -f docker-compose.prod.yml exec nginx nginx -s reload`
(ou agende um cron mensal para isso).

## 4. Backups

O serviço `backup` gera um dump gzip diário em `./backups/` com retenção de
30 dias (`ops/backup.sh`). **Copie esses arquivos para fora do VPS** (rclone
para um bucket/Drive, por exemplo) — backup no mesmo disco não protege contra
perda do servidor.

Restaurar um backup:

```bash
gunzip < backups/amanda-2026-07-06_0300.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db \
  mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"
```

## 5. Criar a conta da psicóloga

```bash
docker compose -f docker-compose.prod.yml exec backend \
  python manage.py createsuperuser
# superusuário recebe role=PSICOLOGA automaticamente
```

## 6. Checklist pós-deploy

- [ ] `https://` abre com cadeado (TLS ok) e `http://` redireciona
- [ ] Login funciona e `/admin/` acessível só para a psicóloga
- [ ] Chat (WebSocket) conecta — testar mensagem entre dois navegadores
- [ ] Lembrete: criar atendimento para amanhã e conferir e-mail em até 1h
- [ ] `backups/` contém um dump após o primeiro dia
- [ ] `INFINITYPAY_LINK_CREDITO` preenchido (cartão) e `PIX_KEY` correta
