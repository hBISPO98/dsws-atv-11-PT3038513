# Email 3 📧​

Evolução da aplicação web em Flask focada na persistência de auditoria de e-mails enviados, com registo de histórico na base de dados e criação de rota dedicada para visualização (`/emails-enviados`).

---

## 🚀 O que mudou? (Versão Anterior vs. Versão Atual)

- **Registo de Auditoria de E-mails (`EmailLog`):** Criação de uma tabela dedicada no banco de dados para salvar automaticamente cada e-mail disparado com sucesso (remetente, destinatário, assunto, corpo e timestamp).


- **Rota de Histórico de Disparos (`/emails_enviados`):** Implementação de uma nova interface visual organizada em tabela para consultar o histórico completo de notificações enviadas ao administrador.


- **Feedback Visual Estático:** Substituição dos pop-ups temporários (*flash*) por mensagens fixas renderizadas logo abaixo da saudação, destacando o cargo com formatação em negrito (`<strong>`).

---

## ⚙️ O que foi necessário implementar?

- **Persistência Automática no Envio:** Integração da lógica de criação de instâncias de `EmailLog` diretamente na função de disparo de mensagens (`send_simple_message`) quando o status HTTP retorna sucesso (`200`).


- **Gating de Envio por Checkbox:** Validação estrita para garantir que o e-mail só é disparado e contabilizado se a caixa de seleção (*"Deseja enviar e-mail para email.x@gmail?"*) estiver explicitamente marcada.


- **Gestão via Consola (Flask Shell):** Documentação e aplicação de comandos práticos para limpeza de dados e manutenção de tabelas de utilizadores e logs de e-mail.

---

## 💡 Dicas de Boas Práticas Adotadas

- **Auditoria e Rastreabilidade:** Guardar o histórico de e-mails em base de dados permite um controlo transparente e verificação de conformidade de todas as notificações do sistema.


- **Separação de Responsabilidades:** Isolar a rota de listagem de logs (`/emails_enviados`) mantém o código modular e limpo, sem sobrecarregar a página principal de gestão de utilizadores.

---

## 👩🏽‍💻 Demonstração
<div align="center">

| Tabela de Histórico de E-mails Enviados |
| :---: |
| <img src="" /> |

</div>
