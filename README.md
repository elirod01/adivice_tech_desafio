# Desafio Web Scraping - Advice Tech (Consulta TJMG)

Este projeto é uma solução de automação e web scraping desenvolvida para o desafio prático da Advice Tech.

## 🎯 Objetivo

O objetivo principal do script é realizar a captura de dados de processos judiciais a partir do sistema eproc do TJMG. A aplicação consulta uma lista pré-definida de nomes, navega pelas páginas de resultados, filtra pelos nomes exatos, e coleta um conjunto detalhado de informações de cada processo encontrado.

## 📄 Resultado Final

Ao final da execução, todos os dados coletados são consolidados e armazenados em um único arquivo no formato JSON, chamado `processos_tjmg.json`.

## 🚀 Como Executar

Siga as instruções abaixo para configurar e executar o projeto.

### 1. Pré-requisitos

* Python (versão 3.9 ou superior)
* Google Chrome (instalado e atualizado)

### 2. Instalação

1.  Clone este repositório para sua máquina local:
    ```bash
    git clone [https://github.com/elirod01/adivice_tech_desafio.git](https://github.com/elirod01/adivice_tech_desafio.git)
    cd adivice_tech_desafio
    ```

2.  Crie um ambiente virtual e ative-o:
    ```bash
    # No Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # No macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Execução

Com o ambiente virtual ativo, basta executar o script principal:

```bash
python automacao_desafio_adivice_tech.py