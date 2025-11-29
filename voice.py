import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 195)				#скорость речи


def speaker(text):
	'''Озвучка текста'''
	engine.say(text)
	engine.runAndWait()