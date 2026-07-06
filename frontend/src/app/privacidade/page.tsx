import Link from "next/link";

export const metadata = {
  title: "Privacidade e termos — Amanda Valéria",
  description:
    "Termos de uso, política de privacidade (LGPD) e consentimento de teleatendimento.",
};

// Versão vigente dos documentos. Deve acompanhar CURRENT_CONSENT_VERSIONS
// no backend (apps/accounts/services.py).
const VERSAO = "1.0";
const ATUALIZADO_EM = "06/07/2026";

export default function PrivacidadePage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Link href="/" className="text-sm text-plum underline">
        ← Voltar ao início
      </Link>

      <h1 className="mt-4 font-display text-4xl text-plum">Privacidade e termos</h1>
      <p className="mt-2 text-sm text-ink/60">
        Versão {VERSAO} · atualizada em {ATUALIZADO_EM}
      </p>

      <section id="termos" className="mt-10 scroll-mt-24">
        <h2 className="font-display text-2xl text-plum">1. Termos de uso</h2>
        <div className="mt-3 space-y-3 text-ink/80">
          <p>
            Esta plataforma é de uso pessoal e intransferível, destinada ao
            acompanhamento psicoterapêutico com a psicóloga Amanda Valéria. Ao
            utilizá-la, você concorda em:
          </p>
          <ul className="list-disc space-y-1 pl-6">
            <li>Manter seu login e senha em sigilo — a conta é individual;</li>
            <li>Usar o chat e demais recursos apenas para fins do seu atendimento;</li>
            <li>
              Não gravar, fotografar ou compartilhar as sessões de vídeo sem
              autorização expressa;
            </li>
            <li>Manter seus dados de contato atualizados.</li>
          </ul>
          <p>
            A plataforma não é um serviço de emergência. Em crise, utilize a
            página <Link href="/paciente/sos" className="text-plum underline">SOS · Apoio</Link>{" "}
            ou ligue para o CVV (188).
          </p>
        </div>
      </section>

      <section id="privacidade" className="mt-10 scroll-mt-24">
        <h2 className="font-display text-2xl text-plum">
          2. Política de privacidade (LGPD)
        </h2>
        <div className="mt-3 space-y-3 text-ink/80">
          <p>
            Tratamos seus dados conforme a Lei Geral de Proteção de Dados (Lei
            13.709/2018). Dados de saúde são <strong>dados sensíveis</strong> (art.
            11) e recebem proteção reforçada.
          </p>
          <h3 className="font-medium text-ink">Quais dados coletamos</h3>
          <ul className="list-disc space-y-1 pl-6">
            <li>Cadastro: nome, e-mail, telefone, data de nascimento;</li>
            <li>
              Clínicos: registros de humor, anotações, mensagens do chat,
              prontuário (registrado pela psicóloga), agenda e histórico de sessões;
            </li>
            <li>Financeiros: cobranças e status de pagamento (não armazenamos dados de cartão);</li>
            <li>Técnicos: registros de acesso (data, hora e IP) para segurança e auditoria.</li>
          </ul>
          <h3 className="font-medium text-ink">Como protegemos</h3>
          <ul className="list-disc space-y-1 pl-6">
            <li>
              Conteúdo clínico (humor, anotações, mensagens e prontuário) é{" "}
              <strong>criptografado</strong> no banco de dados;
            </li>
            <li>Acesso restrito por papel: outro paciente nunca vê seus dados;</li>
            <li>Conexão sempre por HTTPS; backups diários protegidos.</li>
          </ul>
          <h3 className="font-medium text-ink">Seus direitos (art. 18)</h3>
          <ul className="list-disc space-y-1 pl-6">
            <li>
              <strong>Acesso e portabilidade:</strong> baixe seus dados a qualquer
              momento no botão “Baixar meus dados”, na sua área;
            </li>
            <li>
              <strong>Correção:</strong> solicite ajustes de cadastro pelo chat;
            </li>
            <li>
              <strong>Eliminação:</strong> pode ser solicitada ao fim do
              acompanhamento. Atenção: o prontuário psicológico deve ser mantido
              por no mínimo <strong>5 anos</strong> (Resolução CFP 01/2009), por
              obrigação legal da profissional.
            </li>
          </ul>
          <h3 className="font-medium text-ink">Retenção</h3>
          <p>
            Seus dados são mantidos enquanto durar o acompanhamento e, após o
            encerramento, apenas pelo prazo legal aplicável (prontuário: 5 anos).
            Controladora dos dados: Amanda Valéria (psicóloga responsável).
          </p>
        </div>
      </section>

      <section id="teleatendimento" className="mt-10 scroll-mt-24">
        <h2 className="font-display text-2xl text-plum">
          3. Consentimento de teleatendimento
        </h2>
        <div className="mt-3 space-y-3 text-ink/80">
          <p>
            As sessões online seguem as resoluções do Conselho Federal de
            Psicologia sobre atendimento mediado por tecnologia. Ao consentir,
            você declara estar ciente de que:
          </p>
          <ul className="list-disc space-y-1 pl-6">
            <li>
              A qualidade da sessão depende da sua conexão; em caso de queda, a
              sessão pode ser retomada ou remarcada;
            </li>
            <li>
              Cabe a você garantir um ambiente privado e sem interrupções durante
              o atendimento;
            </li>
            <li>As sessões não são gravadas por nenhuma das partes;</li>
            <li>
              O teleatendimento pode não ser indicado em situações de crise —
              nesses casos, a psicóloga poderá orientar atendimento presencial ou
              rede de urgência.
            </li>
          </ul>
        </div>
      </section>

      <p className="mt-12 border-t border-plum-200 pt-6 text-sm text-ink/60">
        Dúvidas sobre privacidade? Fale com a Amanda pelo chat da plataforma ou
        pelos canais de contato do site.
      </p>
    </main>
  );
}
