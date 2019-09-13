import argparse

from deep_learning import DeepLearning
from bet365_parser import B365Parser
from dataset import Dataset


def get_args():
	ap = argparse.ArgumentParser()
	ap.add_argument(
		'-lg',
		'--league',
		required = True,
		help = 'League that you want to work on it (england, spain, italy, germany, france, turkey)'
	)
	ap.add_argument(
		'-t',
		'--train',
		nargs='*',
		help = 'Add this param if you want to train network'
	)
	ap.add_argument(
		'-s',
		'--save',
		nargs='*',
		help = 'Add this param if you want to save trained network'
	)
	
	return vars(ap.parse_args())

def create_match_data(league, stats, match):
	
	home_team = match[0]
	away_team = match[1]
	b365h = match[2]
	b365d = match[3]
	b365a = match[4]
	
	data = pd.DataFrame(
		{
			'odds-home': b365h,
			'odds-draw': b365d,
			'odds-away': b365a,
			'home-wins': stats[home_team]['wins'],
			'home-draw': stats[home_team]['draw'],
			'home-losses': stats[home_team]['losses'],
			'home-goals': stats[home_team]['goals'],
			'home-opposition-goals': stats[home_team]['opposition-goals'],
			'home-shots': stats[home_team]['shots'],
			'home-shots-on-target': stats[home_team]['shots-on-target'],
			'home-opposition-shots': stats[home_team]['opposition-shots'],
			'home-opposition-shots-on-target': stats[home_team]['opposition-shots-on-target'],
			'away-wins': stats[away_team]['wins'],
			'away-draw': stats[away_team]['draw'],
			'away-losses': stats[away_team]['losses'],
			'away-goals': stats[away_team]['goals'],
			'away-opposition-goals': stats[away_team]['opposition-goals'],
			'away-shots': stats[away_team]['shots'],
			'away-shots-on-target': stats[away_team]['shots-on-target'],
			'away-opposition-shots': stats[away_team]['opposition-shots'],
			'away-opposition-shots-on-target': stats[away_team]['opposition-shots-on-target']
		},
		index=[0]
	)
	
	return Dataset.preprocess(data, Dataset.load_training_data()[league])

def run(args):
	
	league = args['league']
		
	if args['train'] != None:
		dl = DeepLearning(league, load = False, save = args['save'] != None)
		dl.train_model(plot = True)
	else:
		dl = DeepLearning(league, load = True, save = args['save'] != None)
		upcoming_matches = B365Parser.load_upcoming_matches()[league]
		stats = Dataset.load_stats_data()[league]
		
		str_match = 'Teams'
		str_home = 'Home'
		str_draw = 'Draw'
		str_away = 'Away'
		
		print(f'{str_match:<30}{str_home:>11}{str_draw:>11}{str_away:>11}')
		for match in upcoming_matches:
			match_data = create_match_data(league, stats, match)
			pred = dl.predict(match_data) * 100.0
			
			teams = match[0] + ' v ' + match[1]
			print(f'{teams:<30}{pred[0][0]:>10.2f}%{pred[0][1]:>10.2f}%{pred[0][2]:>10.2f}%')

if __name__ == '__main__':
	
	args = get_args()
	run(args)
	
