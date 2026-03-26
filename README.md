# P4 Doctors

> **Sistema Web de Gestão Clínica e Painel Analítico**

O **P4 Doctors** é uma aplicação web desenvolvida em Python para centralizar o registro de atendimentos clínicos e plantões médicos. O projeto nasceu para substituir o uso de planilhas manuais, oferecendo uma plataforma ágil de entrada de dados e geração automática de dashboards de produtividade e faturamento.

---

## Objetivo do Projeto

Atualmente, o registro manual de atendimentos descentraliza as informações, dificulta a extração de métricas financeiras e aumenta o risco de perda do histórico de pacientes. 

O objetivo do P4 Doctors é fornecer uma interface focada na rotina médica. O sistema permite que profissionais de saúde registrem os dados essenciais da consulta (incluindo o valor do plantão/atendimento) e visualizem imediatamente o retorno financeiro e o volume de trabalho através de painéis analíticos automatizados, eliminando a necessidade de fórmulas complexas.

---

## Funcionalidades (Escopo MVP)

- **Autenticação Segura:** Sistema de login com controle de sessão para garantir a privacidade dos dados médicos. *(Concluído)*
- **Gestão de Consultas (CRUD):** Formulário ágil para registro de pacientes, local de atendimento, tipo de consulta, relatório clínico e valor do atendimento.
- **Dashboards Analíticos:** Painel visual com indicadores chave de desempenho (KPIs), como total de consultas no mês, ganhos financeiros por local e distribuição por tipo de atendimento.
- **Histórico de Pacientes:** Tabela de listagem com barra de pesquisa e filtros otimizados para rápida recuperação de prontuários.

---

## Tecnologias Utilizadas

O sistema foi desenhado utilizando uma **Arquitetura Monolítica em Camadas**, priorizando a velocidade de desenvolvimento e a facilidade de manutenção.

* **Linguagem Principal:** Python 3
* **Frontend e Regras de UI:** [Streamlit](https://streamlit.io/)
* **Banco de Dados:** PostgreSQL (via [Supabase](https://supabase.com/)) *[Em implementação]*
* **Manipulação de Dados:** Pandas

---

## Como Executar Localmente

Siga os passos abaixo para rodar o projeto na sua máquina:

**1. Clone o repositório:**
```bash
git clone [https://github.com/SEU_USUARIO/p4_doctors.git](https://github.com/SEU_USUARIO/p4_doctors.git)
cd p4_doctors
