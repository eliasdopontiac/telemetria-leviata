const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const nodemailer = require('nodemailer');

const configPath = path.join(__dirname, 'config_online.json');
let config = {};

try {
  if (fs.existsSync(configPath)) {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }
} catch (e) {
  console.warn('[Notificador] Não foi possível carregar config_online.json:', e.message);
}

// Procura o executável cloudflared.exe com caminhos absolutos
let cloudflaredPath = path.resolve(__dirname, '../node/cloudflared.exe');
if (!fs.existsSync(cloudflaredPath)) {
  cloudflaredPath = path.resolve(__dirname, '../cloudflared.exe');
}
if (!fs.existsSync(cloudflaredPath)) {
  cloudflaredPath = path.resolve(__dirname, 'cloudflared.exe');
}

console.log(`[Túnel] Localização do executável: ${cloudflaredPath}`);
if (!fs.existsSync(cloudflaredPath)) {
  console.error('[Túnel] ERRO: cloudflared.exe não encontrado em:', cloudflaredPath);
}

console.log('===============================================================');
console.log(' 🌐 TÚNEL CLOUDFLARE COM NOTIFICAÇÃO AUTOMÁTICA POR E-MAIL');
console.log('===============================================================');

async function enviarEmailNotificacao(urlGerada) {
  const emailCfg = config.email_notificacao;
  if (!emailCfg || !emailCfg.habilitado || !emailCfg.usuario || !emailCfg.senha_app || !emailCfg.destinatario) {
    console.log('\n[Notificador] E-mail não configurado ou desabilitado em config_online.json.');
    console.log('👉 Se desejar receber links por e-mail, preencha as credenciais em config_online.json.\n');
    return;
  }

  // Suporte a múltiplos destinatários (array ou string separada por vírgula)
  let listaDestinatarios = emailCfg.destinatario;
  if (Array.isArray(listaDestinatarios)) {
    listaDestinatarios = listaDestinatarios.join(', ');
  }

  try {
    const transporter = nodemailer.createTransport({
      host: emailCfg.smtp_host || 'smtp.gmail.com',
      port: emailCfg.smtp_port || 465,
      secure: emailCfg.smtp_secure !== false,
      auth: {
        user: emailCfg.usuario,
        pass: (emailCfg.senha_app || '').replace(/\s+/g, '')
      }
    });

    const info = await transporter.sendMail({
      from: `"Telemetria Leviatã" <${emailCfg.usuario}>`,
      to: listaDestinatarios,
      subject: `🚤 Link Online da Telemetria Leviatã: ${urlGerada}`,
      text: `Olá equipe,\n\nO servidor da Estação Base Web foi iniciado e o túnel seguro está ativo!\n\n🔗 LINK PÚBLICO:\n${urlGerada}\n\nO operador do Computador B pode colar este endereço no botão "Online Sync" para sincronizar a telemetria em tempo real.\n\n---\nEquipe Leviatã 2026`,
      html: `
        <div style="font-family: sans-serif; background: #0b0f19; color: #f8fafc; padding: 24px; border-radius: 12px; max-width: 540px;">
          <h2 style="color: #00e5ff; margin-top: 0;">🚤 Telemetria Leviatã 2026 - Online</h2>
          <p>O servidor central do Computador A foi inicializado com sucesso e o túnel seguro está pronto para transmissão ao vivo.</p>
          <div style="background: rgba(0, 229, 255, 0.1); border: 1px solid #00e5ff; border-radius: 8px; padding: 14px; text-align: center; margin: 20px 0;">
            <p style="margin: 0 0 8px 0; font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Link Público da Transmissão</p>
            <a href="${urlGerada}" style="color: #00e5ff; font-weight: bold; font-size: 16px; word-break: break-all;">${urlGerada}</a>
          </div>
          <p style="font-size: 13px; color: #94a3b8;">
            Cole este link no painel do <strong>Computador B (Botão Online Sync)</strong> para iniciar a sincronização com tolerância a falhas.
          </p>
        </div>
      `
    });

    console.log(`[E-mail] Notificação enviada com sucesso para: ${emailCfg.destinatario}`);
  } catch (err) {
    console.error('[E-mail] Erro ao enviar notificação por e-mail:', err.message);
  }
}

// Inicia processo do cloudflared
console.log(`Iniciando túnel para http://localhost:3001 ...`);
const tunnelProc = spawn(cloudflaredPath, ['tunnel', '--url', 'http://localhost:3001'], {
  stdio: ['ignore', 'pipe', 'pipe'],
  windowsHide: true
});

let urlDetectada = null;

function processarLinha(linha) {
  const match = linha.match(/https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/);
  if (match && !urlDetectada) {
    urlDetectada = match[0];
    console.log('\n===============================================================');
    console.log(` 🚀 LINK PÚBLICO ATIVO: ${urlDetectada}`);
    console.log('===============================================================\n');

    enviarEmailNotificacao(urlDetectada);
  }
}

tunnelProc.stdout.on('data', d => {
  d.toString().split('\n').forEach(processarLinha);
});

tunnelProc.stderr.on('data', d => {
  d.toString().split('\n').forEach(processarLinha);
});

tunnelProc.on('error', err => {
  console.error('[Túnel] Não foi possível iniciar cloudflared:', err.message);
  console.log('Certifique-se de que cloudflared.exe está presente na pasta node/ ou no PATH.');
});

tunnelProc.on('exit', code => {
  console.log(`[Túnel] Processo encerrado com código ${code}.`);
});
