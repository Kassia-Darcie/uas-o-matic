import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

logger = logging.getLogger('selenium')
handler = logging.FileHandler('selenium.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Iniciando o navegador
driver = webdriver.Chrome()

# Navegando para uma página
driver.get("https://pucgoiasgraduacao.grupoa.education/plataforma")

# Colocando o navegador em tela cheia
driver.maximize_window()
time.sleep(2)

if driver.current_url == "https://pucgoiasgraduacao.grupoa.education/plataforma/auth/signin":
    user_input =driver.find_element(By.NAME, 'field-username')
    user_input.send_keys('93730241249')
    password_input = driver.find_element(By.NAME, 'field-password')
    password_input.send_keys('283201581561K@s$ia')

    enviar =driver.find_element(By.NAME, 'btn-login')
    enviar.click()
    
# Obtendo as máterias
wait = WebDriverWait(driver, 30)
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'information-card__slots')))
materias = driver.find_elements(By.CLASS_NAME, 'information-card__slots')

materias[0].click()
wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'wrapper-topics')))
time.sleep(2)

# Expande o painel "Aulas - Unidades de Aprendizagem"
try:
    print("Tentando expandir o painel 'Aulas - Unidades de Aprendizagem'...")
    # Encontra o painel 
    panel_header = wait.until(EC.presence_of_element_located((
        By.XPATH, "//h3[contains(text(), 'Aulas - Unidades de Aprendizagem')]/ancestor::button"
    )))
    print("Painel encontrado!")
    
    # Scroll com margem para garantir visibilidade
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'})", panel_header)
    time.sleep(1)
    
    # Tenta clicar usando JavaScript (geralmente mais confiável quando há problemas de interceptação)
    print("Tentando clicar no painel usando JavaScript...")
    driver.execute_script("arguments[0].click();", panel_header)
    print("Clique JavaScript executado")
    
    # Alternativa: use Actions se o JavaScript não funcionar

    
    time.sleep(2)

    
    # Obter os ids das uas
    try:
        uas = driver.find_elements(By.CSS_SELECTOR, '.v-expansion-panel-content__wrap .draggable a')
        uas_ids = []
        if not uas:
            raise Exception("Nenhuma UA encontrada.")
        for ua in uas:
            #driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'})", ua)
            uas_ids.append(ua.get_attribute('id'))
        print(uas_ids)
        
    except Exception as ua_error:
        print(f"Erro ao obter ou clicar nas UAs: {type(ua_error).__name__}: {ua_error}")
        # Adiciona detalhes do erro
        import traceback
        print(f"Detalhes do erro:\n{traceback.format_exc()}")
        # Captura uma screenshot para diagnóstico
        driver.save_screenshot("ua_error_screenshot.png")
        
    driver.get(f'https://pucgoiasgraduacao.grupoa.education/plataforma/course/3533257/content/{uas_ids[0]}')
    pdf_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="banner-wrapper"]/button')))
    while not pdf_btn.is_displayed():
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'})", pdf_btn)
    print('Encontrou o livro')
    
    
    # pdf_url = pdf_btn.get_attribute('data')
    # print(f"URL do PDF: {pdf_url}")
except Exception as e:
    print(f"Erro ao interagir com a página: {type(e).__name__}: {e}")
    # Adiciona detalhes do erro
    import traceback
    print(f"Detalhes do erro:\n{traceback.format_exc()}")
    # Captura uma screenshot para diagnóstico
    driver.save_screenshot("error_screenshot.png")
    
time.sleep(10)