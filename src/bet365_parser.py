from selenium import webdriver
import pickle
import os


class B365Parser():
	
	UPCOMING_MATCH_PATH = os.path.join('..', 'dataset', 'upcoming_matches')
	GECKO_DRIVER_PATH = os.path.join('..', 'lib', 'geckodriver-v0.24.0-linux64', 'geckodriver')
	SITE_DOMAIN = "https://www.bet365.com.au"
	
	def __init__(self):
		self.browser = webdriver.Firefox(executable_path = B365Parser.GECKO_DRIVER_PATH)		
	
	@staticmethod
	def load_upcoming_matches():
		return pickle.load(open(os.path.join(B365Parser.UPCOMING_MATCH_PATH, 'upcoming_matches.pickle'), 'rb'))

	# This method converts team names to be suitable with dataset
	@staticmethod
	def rename_team(team):
		
		if team == 'Man Utd':
			return 'Man United'
		elif team == 'Sheff Utd':
			return 'Sheffield United'
		elif team == 'Wolverhampton':
			return 'Wolves'
		elif team == 'Inter Milan':
			return 'Inter'
		elif team == 'AC Milan':
			return 'Milan'
		elif team == 'Athletic Bilbao':
			return 'Ath Bilbao'
		elif team == 'Real Sociedad':
			return 'Sociedad'
		elif team == 'Atletico Madrid':
			return 'Ath Madrid'
		elif team == 'CD Alaves':
			return 'Alaves'
		elif team == 'Celta Vigo':
			return 'Celta'
		elif team == 'Real Betis':
			return 'Betis'
		elif team == 'Espanyol':
			return 'Espanol'
		elif team == 'Eintracht Frankfurt':
			return 'Ein Frankfurt'
		elif team == 'Borussia Dortmund':
			return 'Dortmund'
		elif team == 'Bayer Leverkusen':
			return 'Leverkusen'
		elif team == 'Cologne':
			return 'FC Koln'
		elif team == "Borussia M'gladbach":
			return "M'gladbach"
		elif team == 'Hertha Berlin':
			return 'Hertha'
		elif team == 'TSG Hoffenheim':
			return 'Hoffenheim'
		elif team == 'SC Freiburg':
			return 'Freiburg'
		elif team == 'Schalke':
			return 'Schalke 04'
		elif team == 'PSG':
			return 'Paris SG'
		elif team == 'Istanbul Basaksehir':
			return 'Buyuksehyr'
		elif team == 'Gazisehir Gaziantep FK':
			return 'Gaziantep'
		elif team == 'Caykur Rizespor':
			return 'Rizespor'
		elif team == 'Goztepe':
			return 'Goztep'
		else:
			return team

	def get_element(self, el_text, el_class):
		while True:
			try:
				elements = self.browser.find_elements_by_css_selector(el_class)
				for element in elements:
					if element.text == el_text:
						return element
			except Exception as e:
				print(e)
				continue
				
	def get_match_data(self, number_of_match):
		data = []

		while True:
			try:
				matches = self.browser.find_elements_by_css_selector('.sl-CouponParticipantWithBookCloses .sl-CouponParticipantWithBookCloses_Name')
				
				if len(matches) >= number_of_match:
					for i in range(number_of_match):
						home_team, away_team = matches[i].text.split(' v ')
						data.append([B365Parser.rename_team(home_team), B365Parser.rename_team(away_team)])
					break
						
			except Exception as e:
				print(e)
				continue


		odds_col = self.browser.find_elements_by_css_selector('div .sl-MarketCouponValuesExplicit33')

		for col in odds_col:
			odds = col.find_elements_by_css_selector('span[class=gll-ParticipantOddsOnly_Odds]')	
			if len(odds) >= number_of_match:
				for i in range(number_of_match):
					data[i].append(float(odds[i].text))
		
		
		return data

	def update_upcoming_matches(self):
		
		print(f'[INFO] Connecting to {B365Parser.SITE_DOMAIN}') 
		self.browser.get(B365Parser.SITE_DOMAIN)

		upcoming_matches = {}

		self.browser.find_element_by_css_selector('#TopPromotionBetNow').click()
		self.get_element('Soccer', '.wn-Classification').click()
		self.get_element('England Premier League', '.sm-CouponLink_Label').click()
		
		print('[INFO] Parsing England Premier League') 
		upcoming_matches['england'] = self.get_match_data(10)
		
		self.browser.back()
		
		self.get_element('Italy', '.sm-Market_GroupName').click()
		self.get_element('Italy Serie A', '.sm-CouponLinkSelectable .sm-CouponLink_Label').click()
		
		print('[INFO] Parsing Italy Serie A')
		upcoming_matches['italy'] = self.get_match_data(10)
		
		self.browser.back()
		
		self.get_element('Spain', '.sm-Market_GroupName').click()
		self.get_element('Spain Primera Liga', '.sm-CouponLinkSelectable .sm-CouponLink_Label').click()
		
		print('[INFO] Parsing Spain Primera Liga')
		upcoming_matches['spain'] = self.get_match_data(10)

		self.browser.back()
		
		self.get_element('Germany', '.sm-Market_GroupName').click()
		self.get_element('Germany Bundesliga I', '.sm-CouponLinkSelectable .sm-CouponLink_Label').click()
		
		print('[INFO] Parsing Germany Bundesliga')
		upcoming_matches['germany'] = self.get_match_data(9)

		self.browser.back()
		
		self.get_element('France', '.sm-Market_GroupName').click()
		self.get_element('France Ligue 1', '.sm-CouponLinkSelectable .sm-CouponLink_Label').click()
		
		print('[INFO] Parsing France Ligue 1')
		upcoming_matches['france'] = self.get_match_data(10)

		self.browser.back()

		self.get_element('Europe', '.sm-Market_GroupName').click()
		self.get_element('Turkey Super Lig', '.sm-CouponLinkSelectable .sm-CouponLink_Label').click()
		
		print('[INFO] Parsing Turkey Super Lig')
		upcoming_matches['turkey'] = self.get_match_data(9)
		
		print('[INFO] Saved upcoming matches')
		upcoming_out = open(os.path.join(B365Parser.UPCOMING_MATCH_PATH, 'upcoming_matches.pickle'), "wb")
		pickle.dump(upcoming_matches, upcoming_out)
		upcoming_out.close()
		
		self.browser.quit()

if __name__ == '__main__':
	parser = B365Parser()
	parser.update_upcoming_matches()

