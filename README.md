*Desenvolvido como parte do GS2025.2 - PCP - PENSAMENTO COMP. COM PYTHON*
*Feito em trio: Pedro Mendes, Leonardo, Alexandre*

# Sistema de Orientação Profissional (Career Recommender)

Este projeto implementa um sistema simples de recomendação de carreira em Python. Ele compara o perfil de habilidades de um usuário (técnicas e comportamentais) com os requisitos de diversas carreiras pré-definidas para calcular uma pontuação de compatibilidade e sugerir áreas de melhoria.

## Estrutura do Projeto

O sistema é composto por quatro classes principais que gerenciam o perfil do usuário, as definições de carreira, o armazenamento de dados e o motor de recomendação.

### 1. Classes de Modelo de Dados

| Classe | Descrição | Atributos Principais |
| :--- | :--- | :--- |
| **`Profile`** | Representa o perfil de um usuário ou aluno. | `name` (str), `technical_skills` (Dict[str, int]), `behavioral_skills` (Dict[str, int]), `notes` (str). |
| **`Career`** | Define uma carreira ou área profissional. | `title` (str), `requirements_tech` (Dict[str, int]), `requirements_beh` (Dict[str, int]), `description` (str). |

**Nota sobre Habilidades:** Tanto as habilidades do `Profile` quanto os requisitos da `Career` são definidos em uma escala de **0 a 5**, indicando o nível de proficiência ou o nível desejado.

### 2. Gerenciamento de Dados

| Classe | Descrição | Funcionalidades Principais |
| :--- | :--- | :--- |
| **`ProfileDB`** | Um banco de dados simples baseado em JSON para armazenar e gerenciar os perfis de usuários. | `load()`: Carrega perfis do arquivo `profiles.json`. `save()`: Salva perfis no arquivo. `add_profile()`: Adiciona um novo perfil e salva. `find()`: Busca um perfil pelo nome. |

O arquivo de armazenamento padrão é `profiles.json`.

### 3. Motor de Recomendação

| Classe | Descrição | Métodos Principais |
| :--- | :--- | :--- |
| **`Recommender`** | Contém a lógica central para calcular a compatibilidade e gerar recomendações. | `compatibility(profile, career)`: Calcula a pontuação de compatibilidade (0 a 1) entre um perfil e uma carreira. **Ponderação:** 70% para habilidades técnicas e 30% para comportamentais. |
| | | `recommend(profile, top_n=3)`: Retorna as `top_n` carreiras mais compatíveis, ordenadas de forma decrescente. |
| | | `improvement_areas(profile, career, top_n=5)`: Identifica as `top_n` habilidades onde o perfil tem o maior "gap" (diferença) em relação aos requisitos da carreira. |

## Execução e Interface de Linha de Comando (CLI)

O arquivo `career_recommender.py` inclui uma interface de linha de comando (`main_cli`) para interação com o sistema.

### Funções Auxiliares da CLI

| Função | Descrição |
| :--- | :--- |
| **`default_careers()`** | Cria e retorna uma lista de objetos `Career` pré-definidos (ex: Desenvolvedor de Software, Cientista de Dados). |
| **`union_skills()`** | Coleta todas as habilidades técnicas e comportamentais únicas exigidas por **todas** as carreiras pré-definidas. |
| **`prompt_skill_input()`** | Solicita ao usuário que insira o nível (0-5) para cada habilidade listada. |

### Menu de Opções

Ao executar o script, o usuário é apresentado a um menu com as seguintes opções:

1.  **Cadastrar novo perfil:** Permite ao usuário inserir seu nome e seus níveis de habilidade (0-5) para todas as habilidades mapeadas. O perfil é salvo em `profiles.json`.
2.  **Listar perfis:** Exibe os nomes de todos os perfis salvos.
3.  **Analisar perfil e gerar recomendações:**
    *   Busca um perfil salvo.
    *   Calcula e exibe as 3 carreiras mais compatíveis, com a porcentagem de compatibilidade.
    *   Para cada carreira, lista as 5 principais áreas de melhoria (gaps).
    *   Oferece a opção de salvar o relatório de recomendação em um arquivo JSON.
4.  **Mostrar perfil salvo:** Exibe os dados brutos (JSON) de um perfil específico.
5.  **Sair:** Encerra o programa.

## Como Executar

Para rodar o sistema, basta executar o arquivo Python no terminal:

```bash
python3 career_recommender.py
```

O sistema criará o arquivo `profiles.json` automaticamente na primeira vez que um perfil for cadastrado.
