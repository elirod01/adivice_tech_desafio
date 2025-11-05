# --- Importações necessárias ---
# 1. Bibliotecas Padrão (stdlib)
import json
import time
import html
import os
from subprocess import CREATE_NO_WINDOW
from typing import List, Dict, Any, Optional

# --- Importações de Terceiros (third-party) ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth


class Teste_Tech:
    """
    Classe de automação para coletar dados processuais do TJMG
    como parte do desafio da Advice Tech.

    A lógica de navegação principal é:
    1. Pesquisar um nome na Página 1.
    2. Na Página 2 (lista), filtrar pelos nomes exatos.
    3. Para cada nome exato, clicar (Nível 1).
    4. Na Página 3 (detalhe), clicar no número do processo (Nível 2).
    5. Na Página 4 (dados), coletar as informações.
    6. Retornar à Página 1, re-pesquisar, e ir para o próximo da lista.
    """

    def __init__(self):
        """Inicializa a classe, definindo todos os seletores e URLs."""
        self.navegador: webdriver.Chrome = None
        self.URL_BASE = "https://eproc-consulta-publica-1g.tjmg.jus.br/eproc/externo_controlador.php?acao=processo_consulta_publica"

        # --- Seletores (Encapsulados para fácil manutenção) ---

        # Página 1: Pesquisa
        self.ID_CHECKBOX_FONETICA = "chkFonetica"
        self.ID_CAMPO_NOME = "txtStrParte"
        self.ID_BOTAO_PESQUISAR = "sbmNovo"

        # Página 2: Lista de Resultados
        self.XPATH_TABELA_PAGE2 = '//*[@id="divInfraAreaTabela"]'
        self.XPATH_LINHAS_DADOS_PAGE2 = '//*[@id="divInfraAreaTabela"]/table/tbody/tr[./td]'
        self.XPATH_LINK_NOME_PAGE2 = ".//td[1]/a"  # Relativo à linha

        # Página 3: Detalhes do Processo (1 resultado)
        self.XPATH_LINHA_DADOS_PAGE3 = "//th[contains(text(), 'Nº Processo')]/ancestor::table/tbody/tr[./td][1]"
        self.XPATH_LINK_PROCESSO_PAGE3 = ".//td[1]/a"  # Relativo à linha

        # Página 4: Coleta de Dados Finais
        self.XPATH_WAIT_PAGE4 = "//*[contains(text(), 'Nº do Processo:')]"
        self.ID_NUM_PROCESSO = "txtNumProcesso"
        self.ID_DATA_AUTUACAO = "txtAutuacao"
        self.ID_SITUACAO = "txtSituacao"
        self.ID_JUIZ = "txtMagistrado"
        self.ID_CLASSE = "txtClasse"
        self.ID_ORGAO_JULGADOR = "txtOrgaoJulgador"
        self.XPATH_LINHAS_ASSUNTOS = '//*[@id="fldAssuntos"]/table/tbody/tr'
        self.XPATH_LINHAS_PARTES = '//*[@id="fldPartes"]/table/tbody/tr'
        self.XPATH_VALOR_CAUSA = "//*[contains(text(), 'Valor da Causa:')]/ancestor::td/following-sibling::td[1]"
        self.XPATH_LINHAS_EVENTOS = '//*[@id="divInfraAreaProcesso"]/table/tbody/tr[./td]'

        # --- Lista de Nomes (constante) ---
        self.NOMES_A_CONSULTAR = [
            "ADILSON DA SILVA",
            "JOÃO DA SILVA MORAES",
            "RICARDO DE JESUS",
            "SERGIO FIRMINO DA SILVA",
            "HELENA FARIAS DE LIMA",
            "PAULO SALIM MALUF",
            "PEDRO DE SÅ"
        ]

    def _configurar_driver(self) -> None:
        """Configura e inicializa o driver do Chrome com opções e stealth."""
        print("Configurando o driver...")
        options = Options()
        options.add_argument("start-maximized")
        # options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        from subprocess import CREATE_NO_WINDOW
        instalacao_chrome = ChromeDriverManager().install()
        pasta = os.path.dirname(instalacao_chrome)
        caminho_chromedriver = os.path.join(pasta, "chromedriver.exe")
        servico = ChromeService(caminho_chromedriver)
        servico.creation_flags = CREATE_NO_WINDOW

        self.navegador = webdriver.Chrome(service=servico, options=options)

        stealth(self.navegador,
                languages=["en-US", "en"], vendor="Google Inc.",
                platform="Win32", webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine", fix_hairline=True)

    def _clicar_checkbox_fonetica(self) -> None:
        """Verifica e desmarca o checkbox 'Pesquisa Fonética'."""
        try:
            checkbox = WebDriverWait(self.navegador, 10).until(
                EC.visibility_of_element_located((By.ID, self.ID_CHECKBOX_FONETICA))
            )
            if checkbox.is_selected():
                checkbox.click()
                print("Checkbox 'Pesquisa Fonética' desmarcado.")
        except Exception as e:
            print(f"Aviso: Não foi possível desmarcar o checkbox fonético: {e}")

    def _ir_para_pagina_1_e_pesquisar(self, nome: str) -> bool:
        """
        Navega para a URL base, preenche a pesquisa e espera a página de
        resultados carregar. Retorna True se a Página 2 carregar, False caso contrário.
        """
        try:
            self.navegador.get(self.URL_BASE)

            self._clicar_checkbox_fonetica()

            campo_nome = WebDriverWait(self.navegador, 10).until(
                EC.visibility_of_element_located((By.ID, self.ID_CAMPO_NOME))
            )
            campo_nome.clear()
            campo_nome.send_keys(nome)

            botao_pesquisar = WebDriverWait(self.navegador, 10).until(
                EC.element_to_be_clickable((By.ID, self.ID_BOTAO_PESQUISAR))
            )
            botao_pesquisar.click()

            # --- Espera de Sincronização ---
            print("Esperando página de resultados carregar...")
            WebDriverWait(self.navegador, 10).until(
                EC.staleness_of(botao_pesquisar)
            )
            # Espera a tabela da Página 2 aparecer
            WebDriverWait(self.navegador, 10).until(
                EC.presence_of_element_located((By.XPATH, self.XPATH_TABELA_PAGE2))
            )
            print("Tabela de resultados encontrada.")
            return True
        except Exception as e:
            if "TimeoutException" in str(e):
                print(f"Nenhum processo encontrado para '{nome}' (Timeout na espera da tabela).")
            else:
                print(f"Erro ao pesquisar na Página 1: {e}")
            return False

    def _processar_clique_pagina_3(self) -> bool:
        """
        Na Página 3 (detalhe do nome), encontra e clica no link do número do processo
        para ir à Página 4. Retorna True em sucesso, False em falha.
        """
        try:
            linha_detalhe = WebDriverWait(self.navegador, 10).until(
                EC.presence_of_element_located((By.XPATH, self.XPATH_LINHA_DADOS_PAGE3))
            )
            link_processo = linha_detalhe.find_element(By.XPATH, self.XPATH_LINK_PROCESSO_PAGE3)
            link_processo.click()
            return True
        except Exception as e:
            print(f"Erro ao clicar no link da Página 3 (Nível 2): {e}")
            return False

    def _coletar_dados_finais(self) -> Optional[Dict[str, Any]]:
        """
        Coleta todos os dados da página final (Página 4) e os retorna
        em um dicionário estruturado.
        """
        dados_coletados = {}
        try:
            WebDriverWait(self.navegador, 10).until(
                EC.presence_of_element_located((By.XPATH, self.XPATH_WAIT_PAGE4))
            )
            print("Iniciando coleta de dados finais...")

            # --- 1. Dados da Capa ---
            dados_coletados['numero_processo'] = self.navegador.find_element(By.ID, self.ID_NUM_PROCESSO).text
            dados_coletados['data_autuacao'] = self.navegador.find_element(By.ID, self.ID_DATA_AUTUACAO).text
            dados_coletados['situacao'] = self.navegador.find_element(By.ID, self.ID_SITUACAO).text
            dados_coletados['juiz'] = self.navegador.find_element(By.ID, self.ID_JUIZ).text
            dados_coletados['classe_acao'] = self.navegador.find_element(By.ID, self.ID_CLASSE).text

            # --- 1b. Órgão Julgador (com dados do hover) ---
            try:
                elem_orgao = self.navegador.find_element(By.ID, self.ID_ORGAO_JULGADOR)
                partes = elem_orgao.get_attribute("onmouseover").split("'")
                html_decodificado = html.unescape(partes[1])
                contato_final = html_decodificado.replace("<div>", "").replace("</div>", " | ").strip().strip(
                    "|").strip()
                dados_coletados['orgao_julgador'] = {"nome": elem_orgao.text, "contato": contato_final}
            except Exception:
                dados_coletados['orgao_julgador'] = {
                    "nome": self.navegador.find_element(By.ID, self.ID_ORGAO_JULGADOR).text, "contato": None}

            # --- 2. Assuntos (Lista) ---
            dados_coletados['assuntos'] = []
            for linha in self.navegador.find_elements(By.XPATH, self.XPATH_LINHAS_ASSUNTOS):
                try:
                    codigo = linha.find_element(By.XPATH, ".//td[1]").text
                    if "Código" not in codigo:  # Pula cabeçalho
                        dados_coletados['assuntos'].append({
                            "codigo": codigo,
                            "descricao": linha.find_element(By.XPATH, ".//td[2]").text,
                            "principal": linha.find_element(By.XPATH, ".//td[3]").text
                        })
                except Exception:
                    pass  # Pula cabeçalho

            # --- 3. Partes (Objeto) ---
            # *** CORREÇÃO DE BUG DE INDENTAÇÃO ESTAVA AQUI ***
            dados_coletados['partes'] = {"autor": [], "reu": [], "outros": []}
            tipo_parte = "outros"
            for linha in self.navegador.find_elements(By.XPATH, self.XPATH_LINHAS_PARTES):
                try:
                    titulo = linha.find_element(By.XPATH, ".//th").text.upper()
                    if "AUTOR" in titulo or "REQUERENTE" in titulo:
                        tipo_parte = "autor"
                    elif "REU" in titulo or "REQUERIDO" in titulo:
                        tipo_parte = "reu"
                    else:
                        tipo_parte = "outros"
                except:
                    try:
                        nome_parte = linha.find_element(By.XPATH, ".//td[1]").text.strip()
                        if nome_parte:
                            dados_coletados['partes'][tipo_parte].append(nome_parte)
                    except:
                        pass

            # --- 4. Informações Adicionais (Objeto) ---
            dados_coletados['informacoes_adicionais'] = {}
            try:
                valor_causa = self.navegador.find_element(By.XPATH, self.XPATH_VALOR_CAUSA).text
                dados_coletados['informacoes_adicionais']['valor_da_causa'] = valor_causa
            except Exception:
                dados_coletados['informacoes_adicionais']['valor_da_causa'] = None

            # --- 5. Eventos (Lista) ---
            dados_coletados['eventos'] = []
            linhas_eventos = self.navegador.find_elements(By.XPATH, self.XPATH_LINHAS_EVENTOS)
            print(f"Encontradas {len(linhas_eventos)} linhas de DADOS de evento.")

            for linha in linhas_eventos:
                try:
                    dados_coletados['eventos'].append({
                        "data_hora": linha.find_element(By.XPATH, ".//td[2]").text,
                        "descricao": linha.find_element(By.XPATH, ".//td[3]").text
                    })
                except Exception as e:
                    print(f"Pulando linha de dados de evento mal formatada: {e}")

            print(f"Dados coletados com sucesso para: {dados_coletados['numero_processo']}")
            return dados_coletados

        except Exception as e:
            print(f"Erro fatal ao coletar dados finais: {e}")
            return None

    def _salvar_json(self, dados: List[Dict[str, Any]], nome_arquivo: str) -> None:
        """Salva a lista de resultados em um arquivo JSON formatado."""
        print(f"\n--- Coleta Finalizada ---")
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            print(f"Sucesso! {len(dados)} registros totais salvos em '{nome_arquivo}'")
        except Exception as e_json:
            print(f"Erro ao salvar JSON: {e_json}")

    def executar_consulta(self):
        """
        Método principal (orquestrador) que executa todo o fluxo de
        automação, desde configurar o driver até salvar os resultados.
        """
        try:
            self._configurar_driver()
            resultados_finais = []

            # === LOOP EXTERNO (Por Nomes) ===
            for nome in self.NOMES_A_CONSULTAR:
                print(f"\n--- Consultando nome: {nome} ---")

                # 1. Pesquisa e chega na Página 2
                if not self._ir_para_pagina_1_e_pesquisar(nome):
                    continue  # Pula para o próximo nome se a pesquisa falhar

                # 2. Conta resultados na Página 2
                try:
                    linhas_tabela = self.navegador.find_elements(By.XPATH, self.XPATH_LINHAS_DADOS_PAGE2)
                    num_resultados = len(linhas_tabela)

                    if num_resultados == 0:
                        print("Tabela encontrada, mas 0 processos listados.")
                        continue

                    print(f"Encontrados {num_resultados} processos. Iniciando coleta...")

                except Exception as e:
                    print(f"Erro ao contar resultados na Página 2: {e}")
                    continue

                # 3. === LOOP INTERNO (Por Resultados) ===
                for i in range(num_resultados):
                    print(f"Processando resultado {i + 1} de {num_resultados}...")

                    # 4. Re-encontra elementos
                    try:
                        WebDriverWait(self.navegador, 10).until(
                            EC.presence_of_element_located((By.XPATH, self.XPATH_TABELA_PAGE2))
                        )
                        linhas_atualizadas = self.navegador.find_elements(By.XPATH, self.XPATH_LINHAS_DADOS_PAGE2)
                        if i >= len(linhas_atualizadas):
                            print("Erro de índice após recarregar, parando loop para este nome.")
                            break
                        linha_para_clicar = linhas_atualizadas[i]
                    except Exception as e_stale:
                        print(f"Erro crítico ao re-encontrar lista (StaleElement?): {e_stale}")
                        break  # Aborta o loop interno para este nome

                    # 5. Filtra e Clica (Page 2)
                    try:
                        link_nome_elemento = linha_para_clicar.find_element(By.XPATH, self.XPATH_LINK_NOME_PAGE2)
                        nome_na_tabela = link_nome_elemento.text.strip().upper()

                        if nome_na_tabela != nome:
                            print(f"Pulando: '{nome_na_tabela}' (não é exato)")
                            continue

                        print(f"Clicando no nome exato: {nome_na_tabela}")
                        link_nome_elemento.click()
                    except Exception as e_filter:
                        print(f"Pulando linha (erro ao filtrar/clicar): {e_filter}")
                        continue

                    # 6. Clica (Page 3)
                    if not self._processar_clique_pagina_3():
                        continue

                        # 7. Coleta (Page 4)
                    dados = self._coletar_dados_finais()
                    if dados:
                        dados["nome_consultado"] = nome
                        resultados_finais.append(dados)

                    # 8. Volta para Página 1 e Re-pesquisa (prepara próxima iteração 'i')
                    print("Retornando à lista de resultados (re-pesquisando)...")
                    if not self._ir_para_pagina_1_e_pesquisar(nome):
                        print("Falha ao recarregar a lista. Abortando este nome.")
                        break  # Quebra o loop interno

            # Fim do Loop Externo
            self._salvar_json(resultados_finais, "processos_tjmg.json")

        except Exception as e_geral:
            print(f"Erro fatal na execução: {e_geral}")

        finally:
            if self.navegador:
                print("Fechando o navegador.")
                self.navegador.quit()


if __name__ == "__main__":
    # O script usa Python, conforme requisito
    bot = Teste_Tech()
    bot.executar_consulta()