# Módulo 1 🧮

Evolução da aplicação web em Flask utilizando SQLAlchemy para persistência de dados e a API do Mailgun para envio de e-mails automáticos a cada novo utilizador cadastrado. O grande objetivo desta versão foi reorganizar o projeto através de uma arquitetura modular com Blueprints, otimizando a organização e o roteamento da aplicação.

---

## 🚀 O que mudou? (Monolito vs. Modular)

### 1. Organização por Módulos (Blueprints)
- **Configurações Separadas (`config.py`):** As configurações deixaram de estar misturadas e foram divididas por ambientes (desenvolvimento, testes e produção), facilitando a gestão do banco de dados.


- **O que é um Blueprint?** Atua como um atalho ou pacote independente que agrupa um conjunto de rotas (como as páginas principais do site). Em vez de centralizar tudo em um único ficheiro, cada módulo gere as suas próprias páginas de forma organizada.


### 2. Envio de E-mails com a API do Mailgun

- **Envio de E-mails via API do Mailgun:** Em vez de utilizar ligações SMTP tradicionais (que costumam ser bloqueadas no servidor do PythonAnywhere), a aplicação faz agora requisições diretas via web (POST / HTTPS) para a API do Mailgun. Como as portas de navegação web estão sempre abertas no servidor, esta abordagem garante que as notificações de novos utilizadores são disparadas sem travamentos ou falhas de bloqueio.


- **Multidestinatários e Dados Académicos:** Quando um novo utilizador é registado, a notificação é enviada em simultâneo para o administrador e para o aluno, incluindo no corpo da mensagem os metadados académicos obrigatórios (nome do aluno, prontuário e o nome do novo utilizador).

---

## ⚙️ O que foi necessário implementar?

- **Estrutura Modular (app/):** Separação em pacotes com função fábrica (create_app) e configurações por ambiente (config.py).


- **Blueprint Main (app/main/):** Isolação de rotas (views.py), formulários (forms.py) e erros (errors.py).


- **Envio de E-mail (app/email.py):** Integração via requisições HTTP POST com a API do Mailgun.


- **Testes (tests/):** Estrutura base de testes unitários (test_basics.py).

---

## 💡 Boas Práticas Adotadas

- **Arquitetura Modular Flexível:** O uso de Blueprints e do padrão *Application Factory* permite que novos módulos (ex.: autenticação, relatórios) sejam adicionados futuramente sem afetar as funcionalidades existentes.


**Resiliência na Comunicação Externa:** A substituição de ligações SMTP por requisições HTTP `POST` garante que o envio de notificações funcione sem impedimentos em servidores com restrições de porta (como o PythonAnywhere).
