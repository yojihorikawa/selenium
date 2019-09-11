from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import json
import datetime



def start_parse():
	options = Options()
	options.add_argument('--headless')
	options.add_argument('--disable-gpu')
	#options.add_argument('--window-size=800,600')
	options.add_argument('--no-sandbox')

	#これをやらないと
	#selenium.common.exceptions.WebDriverException: Message: unknown error: session deleted because of page crash
	#from unknown error: cannot determine loading status
	#と出てしまう。
	options.add_argument('--disable-dev-shm-usage')     

	driver = webdriver.Chrome(chrome_options=options)

	driver2 = webdriver.Chrome(chrome_options=options)

	now = datetime.datetime.now()
	endTime = now - datetime.timedelta(days=1)
	cmpTime = now

	#トークン取得(JSON)
	#https://tracker.icon.foundation/v3/token/list?page=1&count=100
	req = requests.get("https://tracker.icon.foundation/v3/token/list?page=1&count=100")
	parsedJson = json.loads(req.text)
	# print(len(parsedJson["data"]))

	hasMaxPage = False
	maxPage = 10000
	crntPage = 1
	for data in parsedJson["data"]:
		tokenCx = data["contractAddr"]

		#test
		tokenCx = "cx82e9075445764ef32f772d11f5cb08dae71d463b" #184

		#トランザクション取得（Selenium）
		#https://tracker.icon.foundation/tokentx/cx9ab3078e72c8d9017194d17b34b1a47b661945ca/1?count=100
		txDataList = []
		while (crntPage <= maxPage):
			print("crntPage #" + str(crntPage) + "/" + str(maxPage))
			txListUrl = "https://tracker.icon.foundation/tokentx/" + tokenCx + "/" + str(crntPage) + "?count=100"
			driver.get(txListUrl)

			#page load check
			elem = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located(
					(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div[2]/div/div/div/ul/li[3]/p[2]")))

			#max pageの取得
			if hasMaxPage == False:
	#			elem = driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[1]/div[2]/div/div/div/ul/li[3]/p[2]")
				maxPage = int(elem.text.replace("/ ",""))
				print(maxPage)
				hasMaxPage = True

			txData = {}
			elemNum = 1
			#TxHashのリスト取得。
			#/html/body/div[1]/div/div[1]/div[1]/div[2]/div/div/div/div[1]/table/tbody/tr[1]/td[1]/a/span
			for elem in driver.find_elements_by_xpath("/html/body/div[1]/div/div[1]/div[1]/div[2]/div/div/div/div[1]/table/tbody/tr"):
				# 日付が指定期間以外になったらbreak
				if cmpTime < endTime:
					break

				txHash = elem.find_element_by_xpath("td[1]/a/span").text
				print("Element #" + str(elemNum))

				driver2.get("https://tracker.icon.foundation/transaction/"+txHash)

				#date
				dateElem = WebDriverWait(driver2, 10).until(
					EC.presence_of_element_located(
						(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div[2]/div[1]/div/div/div/table/tbody/tr[4]/td[2]")))
				#from
				fromElem = WebDriverWait(driver2, 10).until(
					EC.presence_of_element_located(
						(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div[2]/div[1]/div/div/div/table/tbody/tr[5]/td[2]/span[1]/a")))
				#to
				toElem = WebDriverWait(driver2, 10).until(
					EC.presence_of_element_located(
						(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div[2]/div[1]/div/div/div/table/tbody/tr[6]/td[2]/span[1]/a")))
				#amount (icx)
				amount = WebDriverWait(driver2, 10).until(
					EC.presence_of_element_located(
						(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div[2]/div[1]/div/div/div/table/tbody/tr[7]/td[2]")))
				#token amount
				tokenAmnt = WebDriverWait(driver2, 10).until(
					EC.presence_of_element_located(
						(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div[2]/div[1]/div/div/div/table/tbody/tr[8]/td[2]/p")))

				txData['txHash'] = txHash
				txData['datetime'] = dateElem.text.split("(")[0]
				cmpTime = datetime.datetime.strptime(txData['datetime'], '%Y-%m-%d %H:%M:%S')


				txData['from'] = fromElem.text
				txData['to'] = toElem.text
				txData['amount'] = amount.text.split(" ")[0]
				txData['tokenAmount'] = tokenAmnt.text.split("(")[0].split(" ")[0]
				txData['tokenType'] = tokenAmnt.text.split("(")[0].split(" ")[1]
				txData['tokenTxFrom'] = tokenAmnt.text.split("(")[1].split(" ")[2]
				txData['tokenTxTo'] = tokenAmnt.text.split("(")[1].split(" ")[4]
				print(txData)
	#			print(txHash + ", " + dateElem.text + ", " + fromElem.text + ", " + toElem.text + ", " + amount.text + ", " + tokenAmnt.text)

				elemNum += 1
			crntPage += 1
		#test
		break
	driver.quit()


if __name__ == '__main__':
	start_parse()
