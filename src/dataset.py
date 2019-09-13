from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn import preprocessing
from tqdm import tqdm
import pandas as pd
import pickle
import os


class Dataset():

	DATASET_PATH = os.path.join('..', 'dataset', 'raw')
	TRAIN_PATH = os.path.join('..', 'dataset', 'train')
	
	def __init__(self, last_n_matches):
		self.last_n_matches = last_n_matches

	@staticmethod
	def load_training_data():
		
		data = {}
		for league in os.listdir(Dataset.TRAIN_PATH):
			data[league] = pd.read_csv(os.path.join(Dataset.TRAIN_PATH, league, 'feature.csv'))
		
		return data

	@staticmethod
	def load_stats_data():
		
		data = {}
		for league in os.listdir(Dataset.TRAIN_PATH):
			data[league] = pickle.load(open(os.path.join(Dataset.TRAIN_PATH, league, 'stats.pickle'), 'rb'))
		
		return data

	@staticmethod
	def make_numerical_result(x):
		if x == 'H':
			return 1
		elif x == 'A':
			return 2
		else:
			return 0

	@staticmethod
	def preprocess(data, fit_data = None):
		
		scaler = preprocessing.StandardScaler((-1, 1))
		
		if fit_data is None:
			scaler.fit(data.drop(['result'], axis=1))
		else:
			scaler.fit(fit_data.drop(['result'], axis=1))
		
		if 'result' in data.columns:
			x = data.drop(['result'], axis=1)
			y = data['result'].apply(Dataset.make_numerical_result).values
		
			# binary encode
			onehot_encoder = OneHotEncoder(sparse=False, categories='auto')
			y = y.reshape(len(y), 1)
			y = onehot_encoder.fit_transform(y)
			
			x = scaler.transform(x)
			return x, y
		else:
			data = scaler.transform(data)
			return data

	def clean_data(self, data):
		
		return data.dropna(
			how = 'any',
			subset = [
				'B365H',
				'B365D',
				'B365A',
				'HomeTeam',
				'AwayTeam',
				'FTHG',
				'FTAG',
				'FTR',
				'HS',
				'AS',
				'HST',
				'AST'
			]
		)
		
	def balance_data(self, data):
		data_h = data[data['result'] == 'H']
		data_d = data[data['result'] == 'D']
		data_a = data[data['result'] == 'A']
		
		min_class = min(len(data_h), len(data_d), len(data_a))
		data = pd.concat(
			[
				data_h.sample(min_class, random_state = 43),
				data_d.sample(min_class, random_state = 43),
				data_a.sample(min_class, random_state = 43)
			],
			axis=0,
			ignore_index = True
		)
		
		return data

	def delete_earlier_match(self, home_team, away_team, played_matches, curr_stats):
		if home_team != None:
			home_deleted_row = played_matches[home_team].pop(0)

			if home_team == home_deleted_row['HomeTeam']:
				curr_stats[home_team]['wins'] -= 1 if home_deleted_row['FTR'] == 'H' else 0
				curr_stats[home_team]['draw'] -= 1 if home_deleted_row['FTR'] == 'D' else 0
				curr_stats[home_team]['losses'] -= 1 if home_deleted_row['FTR'] == 'A' else 0
				curr_stats[home_team]['goals'] -= home_deleted_row['FTHG']
				curr_stats[home_team]['opposition-goals'] -= home_deleted_row['FTAG']
				curr_stats[home_team]['shots'] -= home_deleted_row['HS']
				curr_stats[home_team]['shots-on-target'] -= home_deleted_row['HST']
				curr_stats[home_team]['opposition-shots'] -= home_deleted_row['AS']
				curr_stats[home_team]['opposition-shots-on-target'] -= home_deleted_row['AST'] 
			else:
				curr_stats[home_team]['wins'] -= 1 if home_deleted_row['FTR'] == 'A' else 0
				curr_stats[home_team]['draw'] -= 1 if home_deleted_row['FTR'] == 'D' else 0
				curr_stats[home_team]['losses'] -= 1 if home_deleted_row['FTR'] == 'H' else 0
				curr_stats[home_team]['goals'] -= home_deleted_row['FTAG']
				curr_stats[home_team]['opposition-goals'] -= home_deleted_row['FTHG']
				curr_stats[home_team]['shots'] -= home_deleted_row['AS']
				curr_stats[home_team]['shots-on-target'] -= home_deleted_row['AST']
				curr_stats[home_team]['opposition-shots'] -= home_deleted_row['HS']
				curr_stats[home_team]['opposition-shots-on-target'] -= home_deleted_row['HST']
			
		if away_team != None:
			away_deleted_row = played_matches[away_team].pop(0)
		
			if away_team == away_deleted_row['HomeTeam']:
				curr_stats[away_team]['wins'] -= 1 if away_deleted_row['FTR'] == 'H' else 0
				curr_stats[away_team]['draw'] -= 1 if away_deleted_row['FTR'] == 'D' else 0
				curr_stats[away_team]['losses'] -= 1 if away_deleted_row['FTR'] == 'A' else 0
				curr_stats[away_team]['goals'] -= away_deleted_row['FTHG']
				curr_stats[away_team]['opposition-goals'] -= away_deleted_row['FTAG']
				curr_stats[away_team]['shots'] -= away_deleted_row['HS']
				curr_stats[away_team]['shots-on-target'] -= away_deleted_row['HST']
				curr_stats[away_team]['opposition-shots'] -= away_deleted_row['AS']
				curr_stats[away_team]['opposition-shots-on-target'] -= away_deleted_row['AST'] 
			else:
				curr_stats[away_team]['wins'] -= 1 if away_deleted_row['FTR'] == 'A' else 0
				curr_stats[away_team]['draw'] -= 1 if away_deleted_row['FTR'] == 'D' else 0
				curr_stats[away_team]['losses'] -= 1 if away_deleted_row['FTR'] == 'H' else 0
				curr_stats[away_team]['goals'] -= away_deleted_row['FTAG']
				curr_stats[away_team]['opposition-goals'] -= away_deleted_row['FTHG']
				curr_stats[away_team]['shots'] -= away_deleted_row['AS']
				curr_stats[away_team]['shots-on-target'] -= away_deleted_row['AST']
				curr_stats[away_team]['opposition-shots'] -= away_deleted_row['HS']
				curr_stats[away_team]['opposition-shots-on-target'] -= away_deleted_row['HST'] 

	def get_statistics(self, data):
		
		stats = {
			'wins': 0,
			'draw': 0,
			'losses': 0,
			'goals': 0,
			'opposition-goals': 0,
			'shots': 0,
			'shots-on-target': 0,
			'opposition-shots': 0,
			'opposition-shots-on-target': 0
		}

		new_data = pd.DataFrame(columns=[
			'result',
			'odds-home',
			'odds-draw',
			'odds-away',
			'home-wins',
			'home-draw',
			'home-losses',
			'home-goals',
			'home-opposition-goals',
			'home-shots',
			'home-shots-on-target',
			'home-opposition-shots',
			'home-opposition-shots-on-target',
			'away-wins',
			'away-draw',
			'away-losses',
			'away-goals',
			'away-opposition-goals',
			'away-shots',
			'away-shots-on-target',
			'away-opposition-shots',
			'away-opposition-shots-on-target'
		])

		curr_stats = {}
		played_matches = {}
		
		with tqdm(total=len(data)) as pbar:
			for _, row in data.iterrows():
				home_team = row['HomeTeam']
				away_team = row['AwayTeam']
				
				if home_team not in curr_stats:
					curr_stats[home_team] = dict(stats)
					played_matches[home_team] = []
					
				if away_team not in curr_stats:
					curr_stats[away_team] = dict(stats)
					played_matches[away_team] = []
					
				if (len(played_matches[home_team]) == self.last_n_matches and
						len(played_matches[away_team]) == self.last_n_matches):
					
					new_data = new_data.append(
						{
							'result': row['FTR'],
							'odds-home': row['B365H'],
							'odds-draw': row['B365D'],
							'odds-away': row['B365A'],
							'home-wins': int(curr_stats[home_team]['wins']),
							'home-draw': int(curr_stats[home_team]['draw']),
							'home-losses': int(curr_stats[home_team]['losses']),
							'home-goals': int(curr_stats[home_team]['goals']),
							'home-opposition-goals': int(curr_stats[home_team]['opposition-goals']),
							'home-shots': int(curr_stats[home_team]['shots']),
							'home-shots-on-target': int(curr_stats[home_team]['shots-on-target']),
							'home-opposition-shots': int(curr_stats[home_team]['opposition-shots']),
							'home-opposition-shots-on-target': int(curr_stats[home_team]['opposition-shots-on-target']),
							'away-wins': int(curr_stats[away_team]['wins']),
							'away-draw': int(curr_stats[away_team]['draw']),
							'away-losses': int(curr_stats[away_team]['losses']),
							'away-goals': int(curr_stats[away_team]['goals']),
							'away-opposition-goals': int(curr_stats[away_team]['opposition-goals']),
							'away-shots': int(curr_stats[away_team]['shots']),
							'away-shots-on-target': int(curr_stats[away_team]['shots-on-target']),
							'away-opposition-shots': int(curr_stats[away_team]['opposition-shots']),
							'away-opposition-shots-on-target': int(curr_stats[away_team]['opposition-shots-on-target'])
						},
						ignore_index = True
					)
					
					self.delete_earlier_match(home_team, away_team, played_matches, curr_stats)

				elif len(played_matches[home_team]) >= self.last_n_matches:
					self.delete_earlier_match(home_team, None, played_matches, curr_stats)
				elif len(played_matches[away_team]) >= self.last_n_matches:
					self.delete_earlier_match(None, away_team, played_matches, curr_stats)

					
				curr_stats[home_team]['wins'] += 1 if row['FTR'] == 'H' else 0
				curr_stats[home_team]['draw'] += 1 if row['FTR'] == 'D' else 0
				curr_stats[home_team]['losses'] += 1 if row['FTR'] == 'A' else 0
				curr_stats[home_team]['goals'] += row['FTHG']
				curr_stats[home_team]['opposition-goals'] += row['FTAG']
				curr_stats[home_team]['shots'] += row['HS']
				curr_stats[home_team]['shots-on-target'] += row['HST']
				curr_stats[home_team]['opposition-shots'] += row['AS']
				curr_stats[home_team]['opposition-shots-on-target'] += row['AST'] 
				
				curr_stats[away_team]['wins'] += 1 if row['FTR'] == 'A' else 0
				curr_stats[away_team]['draw'] += 1 if row['FTR'] == 'D' else 0
				curr_stats[away_team]['losses'] += 1 if row['FTR'] == 'H' else 0
				curr_stats[away_team]['goals'] += row['FTAG']
				curr_stats[away_team]['opposition-goals'] += row['FTHG']
				curr_stats[away_team]['shots'] += row['AS']
				curr_stats[away_team]['shots-on-target'] += row['AST']
				curr_stats[away_team]['opposition-shots'] += row['HS']
				curr_stats[away_team]['opposition-shots-on-target'] += row['HST'] 
				
				played_matches[home_team].append(row)
				played_matches[away_team].append(row)
					
				pbar.update(1)
		
		return new_data, curr_stats

	def update(self):
		for league in os.listdir(Dataset.DATASET_PATH):
			print('[INFO] Reading league', league)
			league_dir = os.listdir(os.path.join(Dataset.DATASET_PATH, league))
			league_dir.sort()
			
			first = True
			for season in league_dir:
				print('[INFO] Reading season', season)
				data = pd.read_csv(os.path.join(Dataset.DATASET_PATH, league, season))
				data = self.clean_data(data)
				
				if first:
					league_data = data
					first = False
				else:
					league_data = league_data.append(data, ignore_index = True, sort = False)
			
			print('[INFO] Extracting feature, it may take some time...')
			feature_data, stats = self.get_statistics(league_data)
			
			print('[INFO] Balancing the data')
			feature_data = self.balance_data(feature_data)
			
			if not os.path.exists(os.path.join(Dataset.TRAIN_PATH, league)):
				os.mkdir(os.path.join(Dataset.TRAIN_PATH, league))
			
			feature_data.to_csv(os.path.join(Dataset.TRAIN_PATH, league, 'feature.csv'), encoding = 'utf-8', index = False)
			stats_out = open(os.path.join(Dataset.TRAIN_PATH, league, 'stats.pickle'), "wb")
			pickle.dump(stats, stats_out)
			stats_out.close()


if __name__ == '__main__':
	
	d = Dataset(10)
	d.update()
	









