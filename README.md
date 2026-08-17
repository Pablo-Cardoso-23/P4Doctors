# P4 Doctors

> **Plataforma Web de Gestão Clínica, Agendamentos e Inteligência Financeira**

O **P4 Doctors** é uma aplicação web desenvolvida para otimizar a gestão operacional e financeira de clínicas e consultórios médicos. Substituindo rotinas manuais e planilhas descentralizadas, o sistema atua como uma retaguarda inteligente, consolidando fluxos de atendimento, agendas e faturamentos em um ambiente seguro e integrado.

---

## Arquitetura e Objetivo

O projeto foi arquitetado para resolver o problema de sobrecarga operacional de profissionais de saúde e suas equipes de apoio. Ao centralizar as informações clínicas, o sistema converte dados brutos de plantões e consultas em painéis analíticos (Dashboards) isolados por profissional, permitindo o acompanhamento do volume de trabalho e retorno financeiro em tempo real.

A aplicação adota o modelo de **Controle de Acesso Baseado em Papéis (RBAC)**, segmentando rigorosamente as permissões entre Administradores, Médicos e Secretárias(os), garantindo privacidade absoluta dos dados.

---

## Principais Funcionalidades

- **Autenticação e Segurança:** Sistema de login protegido com criptografia de senhas via algoritmo Bcrypt (hash e salt) e controle de sessão por timeout.
- **Painel Administrativo:** Gestão completa de usuários com aprovação de credenciais, inativação segura (Soft Delete) e delegação de vínculo entre secretárias e agendas médicas.
- **Gestão de Agendamentos e Webhooks:** Fluxo de criação e alteração de status de consultas. Integração nativa com automações externas (n8n) para disparo automático de e-mails transacionais utilizando Webhooks.
- **Módulo de Pacientes (CRUD):** Base de dados relacional para cadastro, edição e higienização do histórico de pacientes, com travas de integridade referencial.
- **Dashboards Analíticos:** Geração de métricas financeiras automatizadas, filtrando atendimentos particulares, convênios e plantões de forma isolada para o médico autenticado.

---

## Tecnologias Utilizadas

O sistema adota uma arquitetura em camadas focada em escalabilidade e facilidade de manutenção.

**Frontend e Interface:**
- **Python 3**
- **Streamlit:** Framework para a construção da interface web reativa (suporte dinâmico a Light/Dark mode).
- **Pandas:** Manipulação e consolidação de dataframes para os painéis analíticos.

**Backend e Persistência:**
- **PostgreSQL:** Banco de dados relacional operado via **Supabase**.

**Segurança e Testes:**
- **Bcrypt:** Para hashização de credenciais.
- **Pytest / Pytest-Mock:** Cobertura de testes unitários simulando o banco de dados em memória.

**Automação:**
- **n8n:** Orquestração de fluxos de e-mail via nós REST e OAuth2.

---

## Instruções de Instalação e Execução

Para executar o ambiente de desenvolvimento localmente, siga as instruções abaixo:

**1. Clone o repositório:**
```bash
git clone [https://github.com/SEU_USUARIO/p4_doctors.git](https://github.com/SEU_USUARIO/p4_doctors.git)
cd p4_doctors
```

**2. Crie e ative um ambiente virtual:**
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate
```

**3. Instale as dependências do projeto:**
```bash
pip install -r requirements.txt
```

**4. Configuração das Variáveis de Ambiente:**
Crie uma pasta oculta chamada .streamlit na raiz do projeto e dentro dela crie um arquivo chamado secrets.toml. Insira as credenciais do seu banco de dados e da sua automação:
```bash
# Arquivo: .streamlit/secrets.toml
[supabase]
url = "SUA_URL_DO_SUPABASE"
key = "SUA_CHAVE_PUBLICA_DO_SUPABASE"

N8N_WEBHOOK_URL = "SUA_URL_DO_WEBHOOK_N8N"
```

**5. Execute a aplicação:**
```bash
streamlit run src/main.py
````

