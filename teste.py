import json
import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import traceback


# --- Configuração ---
# É recomendado carregar credenciais de variáveis de ambiente ou de um arquivo config
# Carrega credenciais de um arquivo config.json
config_path = os.path.join(os.getcwd(), "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
USER_LOGIN = config.get("USER_LOGIN", "")
USER_PASSWORD = config.get("USER_PASSWORD", "")
USER_LOGIN = ''
USER_PASSWORD = '' # Substitua pela sua senha
BASE_URL = "https://pucgoiasgraduacao.grupoa.education/plataforma"
is_logged_in = False

download_path = os.path.join(os.getcwd(), "downloads")
# Cria a pasta se ela não existir
if not os.path.exists(download_path):
    os.makedirs(download_path)


# --- Configuração do Logger ---
logging.basicConfig( 
                    filename='selenium.log', 
                    filemode='w', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

chrome_options = Options()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True # Manter a segurança
}
chrome_options.add_experimental_option("prefs", prefs)

# --- Inicialização do WebDriver ---

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 30)

def get_materias():
    driver.get('https://pucgoiasgraduacao.grupoa.education/plataforma/my-enrollments/courses')
    ul = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'courses-section__courses')))
    course_links = [a for a in ul.find_elements(By.XPATH, './a[contains(@data-testid, "discipline-")]')]
    courses = []   
    for link in course_links:
        course_href = link.get_attribute('href')
        course_id = course_href.split('/')[-1]
        course_name = link.get_attribute('data-testid').split('-')[1].split(' (')[0]
        courses.append({'id': course_id, 'name': course_name, 'url': course_href})
    return courses

def login():
    driver.get(f'{BASE_URL}/auth/signin')
    wait.until(EC.visibility_of_element_located((By.NAME, 'field-username'))).send_keys(USER_LOGIN)
    driver.find_element(By.NAME, 'field-password').send_keys(USER_PASSWORD)
    driver.find_element(By.NAME, 'btn-login').click()
    
    # Adiciona uma espera explícita para o carregamento da página pós-login
    # Esta linha espera até que a URL não seja mais a de login.
    wait.until_not(EC.url_contains('/auth/signin'))

    # O Selenium já gerencia os cookies da sessão, não é necessário salvá-los e recarregá-los.
    cookies = driver.get_cookies()
    return cookies

def get_course_uas(course_url, course):
    driver.get(course_url)
    # Expande o painel de UAs se necessário
    uas_panel_xpath = '//div[contains(@class, "v-expansion-panel-header")]'
    uas_panel = wait.until(EC.element_to_be_clickable((By.XPATH, uas_panel_xpath)))
    driver.execute_script("arguments[0].click();", uas_panel)
    time.sleep(2)  # Pequena espera para garantir que o painel abriu
    uas_element = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "draggable")]/a[contains(@data-testid, "topic-")]')))
    course['uas'] = []
    for ua_element in uas_element:
        logging.info(f"Unidade de Aprendizagem encontrada: {ua_element.get_attribute('data-testid')}")
        ua = {}
        ua['id'] = ua_element.get_attribute('id')
        ua['name'] = ua_element.get_attribute('data-testid').split('-')[-1]
        ua['url'] = f"{BASE_URL}/course/{course['id']}/content/{ua['id']}"
        course['uas'].append(ua)
    return course['uas']

def download_pdfs(uas, course_name,cookies):
    """
    Função para baixar o PDF de uma Unidade de Aprendizagem (UA).
    Usa a URL da página de conteúdo e os cookies da sessão autenticada.
    """
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # Fazer a requisição GET para o URL do arquivo
    for i in range(len(uas)):
        pdf_url = get_pdf_url(uas[i]['url'])
        response = session.get(pdf_url, stream=True)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Salvar o arquivo no disco
            path = os.path.abspath(f'uas-o-matic/downloads/{course_name}/{i+1}-{uas[i]['name']}.pdf')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print("Download concluído com sucesso usando requests!")
        else:
            print(f"Falha no download. Status code: {response.status_code}")


def get_pdf_url(ua_url): 
    logging.info(f"Navegando para a página de conteúdo: {ua_url}")
    driver.get(ua_url)

    pdf_btn_locator = (By.XPATH, '//div[@class="banner-wrapper"]/button')
    logging.info("Aguardando o botão do livro/PDF.")
    pdf_btn = wait.until(EC.element_to_be_clickable(pdf_btn_locator))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'})", pdf_btn)
    driver.execute_script("arguments[0].click();", pdf_btn)

    pdf_url = driver.find_element(By.XPATH, '//div[@class="object-wrapper"]/object').get_attribute('data')
    return pdf_url

