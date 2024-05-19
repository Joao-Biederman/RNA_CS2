import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup



# ARQUIVO DAS PARTIDAS
# Abra o arquivo em modo de leitura usando with
with open('links.txt', 'r') as arquivo:
    # Leia todas as linhas do arquivo
    campeonatoLinhas = arquivo.readlines()

# Crie uma lista para armazenar as campeonatoLinhas modificadas
partidas_txt = []
url_partidas = []

# Itere sobre cada linha
for linha in campeonatoLinhas:
    # Remova os caracteres "/" e ":" e adicione ".txt" ao final
    linha_modificada = linha.replace('/', '').replace(':', '').strip() + '.txt'
    # Adicione a linha modificada à lista
    partidas_txt.append(linha_modificada)
    url_partidas.append(linha)

# Itere sobre cada partida
for i, partida in enumerate(partidas_txt):
    # Abra o arquivo de cada partida
    caminho = "./jogos/" + partida
    with open(caminho, 'r') as arquivo:
        # Leia todas as linhas do arquivo
        rounds_partida = arquivo.readlines()
        rounds_partida_numeros = [int(linha.strip()) for linha in rounds_partida]
        #print(rounds_partida_numeros)

    # Pegue a URL base da partida correspondente
    url_base = url_partidas[i]

    for round_number in range(1, len(rounds_partida) + 1):

        # Configurando o driver
        driver = webdriver.Chrome()

        # URL da página que você deseja fazer scraping
        url = f'{url_base}/round-{round_number}'

        # Carregar a página usando o driver do Selenium
        driver.get(url)

        # Esperar até que o botão "Ok" esteja disponível e clicar nele
        try:
            ok_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Ok')]"))
            )
            ok_button.click()

            # Esperar até que o botão de reprodução esteja disponível
            play_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="widget-scoreboard"]/div[2]/div[3]/div/div/div[1]/button'))
            )

            # Clicar no botão de reprodução usando JavaScript
            driver.execute_script("arguments[0].click();", play_button)
            
            # Esperar um tempo suficiente para o vídeo começar a reproduzir
            #print("Tempo de espera: ",rounds_partida_numeros[round_number - 1])
            time.sleep(rounds_partida_numeros[round_number - 1])
            
            # Clicar no botão de pausa usando JavaScript
            driver.execute_script("arguments[0].click();", play_button)
        except Exception as e:
            print("Erro:", e)

        # Obter o conteúdo da página após o carregamento completo
        page_source = driver.page_source

        # Parsear o conteúdo HTML usando BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Encontrar todas as divs com a classe específica
        rows = soup.find_all('div', class_='table-row')

        # Extrair os nomes dos times da URL
        team_names = url.split('/')[-3].split('-vs-')
        team_names = [name.split('-')[0] for name in team_names]

        # Encontrar as informações do round atual
        current_round_div = soup.find_all('div', class_='round__teams')[round_number - 1]

        team_1_div = current_round_div.find_all('div')[0]
        team_1_span = team_1_div.find('span')
        team_1_path = [tag.name for tag in team_1_span.find_parents()]
        team_1_text = team_1_span.text.strip()
        team_1_icon = team_1_span.find('i')
        team_1_icon_name = team_1_icon.get('class')[-1] if team_1_icon else None

        team_2_div = current_round_div.find_all('div')[1]
        team_2_span = team_2_div.find('span')
        team_2_path = [tag.name for tag in team_2_span.find_parents()]
        team_2_text = team_2_span.text.strip()
        team_2_icon = team_2_span.find('i')
        team_2_icon_name = team_2_icon.get('class')[-1] if team_2_icon else None

        # arquivo
        #file_path = f"saida_round_{round_number}.txt"
        file_path = f"saida.txt"
        with open(file_path, "a") as file:
            print(url_partidas[i], file=file)
            print("-" * 50, file=file)
            # Verificar o vencedor do round atual e imprimir
            if team_1_icon_name:
                print(f"{team_names[0]} vencedor do round {round_number}", file=file, end="\n")
            elif team_2_icon_name:
                print(f"{team_names[1]} vencedor do round {round_number}", file=file, end="\n")
            else:
                print(f"Nenhum vencedor encontrado no round {round_number}", file=file, end="\n")

            # Iterar sobre as divs encontradas e imprimir seus conteúdos
            for index, row in enumerate(rows):
                # Pular o primeiro e o sétimo row
                if index == 0 or index == 6:
                    continue
                #health = row.find('div', class_='table-cell health').text.strip()
                player = row.find('div', class_='table-cell player').text.strip()
                kits = row.find('div', class_='table-cell kits').text.strip()
                armor = row.find('div', class_='table-cell armor').text.strip()
                money = row.find('div', class_='table-cell money').text.strip()
                weapon = row.find('div', class_='table-cell weapon').text.strip()
                grenades = row.find('div', class_='table-cell grenades').text.strip()

                
                
                # se tem kit ou não
                kits_div = row.find('div', class_='table-cell kits')
                if kits_div.find('span', class_='c-global-tooltips-objects__trigger'):
                    if kits_div.find('i', class_='o-icon--defuse-kit'):
                        kits = "Sim"
                    else:
                        kits = "Não"
                else:
                    kits = "Não"

                # se tem armor ou não
                armor_div = row.find('div', class_='table-cell armor')
                armor_icon = armor_div.find('i')
                if armor_icon:
                    if 'o-icon--assault-suit' in armor_icon.get('class'):
                        armor = "Kevlar + Helmet"
                    elif 'o-icon--kevlar' in armor_icon.get('class'):
                        armor = "Kevlar"
                    else:
                        armor = "No Armor"

                # verifica a arma
                weapon_div = row.find('div', class_='table-cell weapon')
                weapon_icon = weapon_div.find('i')
                weapon_name = weapon_icon.get('class')[-2].replace('o-icon--', '').upper() if weapon_icon else 'Desconhecida'
                
                # Pega as granadas
                grenades_div = row.find('div', class_='table-cell grenades')
                grenades_icons = grenades_div.find_all('i')
                grenades_list = []
                for icon in grenades_icons:
                    if 'o-icon--molotov' in icon.get('class') or 'o-icon--incendiary-grenade' in icon.get('class'):
                        grenades_list.append("Molotov")
                    elif 'o-icon--flashbang' in icon.get('class'):
                        grenades_list.append("Flashbang")
                    elif 'o-icon--smoke-grenade' in icon.get('class'):
                        grenades_list.append("Smoke")
                    elif 'o-icon--he-grenade' in icon.get('class'):
                        grenades_list.append("HE")

                grenades = ', '.join(grenades_list) if grenades_list else "Sem granadas"
                
                
                print("-" * 50, file=file, end="\n")
                #print("Health", health, file=file, end="\n")
                print("Player:", player, file=file, end="\n")
                print("Kits:", kits, file=file, end="\n")
                print("Armor:", armor, file=file, end="\n")
                print("Weapon:", weapon_name, file=file, end="\n")
                print("Grenades:", grenades, file=file, end="\n")
    # Fechar o driver do Selenium
    driver.quit()

print("Scrapping finalizado!")



