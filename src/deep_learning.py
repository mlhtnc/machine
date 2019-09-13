import matplotlib.pyplot as plt
import tensorflow as tf
import os

from dataset import Dataset


SUPPRESS_TF_LOGS = True
if SUPPRESS_TF_LOGS:
	os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
	tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)


class DeepLearning():

	MODELS_PATH = os.path.join('..', 'models')
	
	def __init__(self, league, load = True, save = False):
		self.league = league
		self.load = load
		self.save = save
		
		if load:	
			self.model = self.load_model()
		else:
			self.model = self.create_model()
			self.data = Dataset.load_training_data()

	def plot_history(self, history):
		hist = pd.DataFrame(history.history)
		hist['epoch'] = history.epoch

		plt.figure()
		plt.xlabel('Epoch')
		plt.ylabel('Accuracy')
		plt.plot(hist['epoch'], hist['acc'],
			   label='Train Accuracy')
		plt.plot(hist['epoch'], hist['val_acc'],
			   label = 'Val Accuracy')
		plt.ylim([0,1])
		plt.legend()

		plt.figure()
		plt.xlabel('Epoch')
		plt.ylabel('Sparse Categorical Cross Entropy')
		plt.plot(hist['epoch'], hist['loss'],
			   label='Train Error')
		plt.plot(hist['epoch'], hist['val_loss'],
			   label = 'Val Error')
		plt.ylim([0,10])
		plt.legend()
		plt.show()

	def create_model(self):
		model = tf.keras.models.Sequential([
		  tf.keras.layers.Dense(64, activation=tf.nn.relu, input_shape=(21, )),
		  tf.keras.layers.Dense(64, activation=tf.nn.relu),
		  tf.keras.layers.Dense(64, activation=tf.nn.relu, kernel_regularizer=tf.keras.regularizers.l2(l=0.1)),
		  tf.keras.layers.Dropout(0.2),
		  tf.keras.layers.Dense(64, activation=tf.nn.relu, kernel_regularizer=tf.keras.regularizers.l2(l=0.1)),
		  tf.keras.layers.Dense(3, activation=tf.nn.softmax)
		])
		model.compile(optimizer='adam',
					  loss='categorical_crossentropy',
					  metrics=['accuracy'])
					  
		return model

	def load_model(self):
		return tf.keras.models.load_model(os.path.join(DeepLearning.MODELS_PATH, self.league + '.h5'))

	def train_model(self, plot = False):
		
		if self.load:
			print('[ERROR] Cannot train the model when you load the saved model')
			return
		
		x, y = Dataset.preprocess(self.data[self.league])
		history = self.model.fit(x, y, epochs = 50, validation_split = 0.1)		
		
		if self.save:
			self.model.save(os.path.join(DeepLearning.MODELS_PATH, self.league + '.h5'))

		if plot:
			self.plot_history(history)

	def predict(self, data):
		return self.model.predict(data)


if __name__ == '__main__':
	
	d = DeepLearning('england', load = False, save = True)
	d.train_model(plot = True)


