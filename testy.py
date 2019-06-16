import pickle


data = {'away': ['brenna', 'dani', 'jules'], 'here': ['grace']}

f = open('./tmp.pkl', 'wb')

pickle.dump(data, f)
f.close()

