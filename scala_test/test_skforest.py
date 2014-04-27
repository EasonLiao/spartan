from datasource import load_data
from sklearn.ensemble import RandomForestClassifier
import time

x, y = load_data('cf10')

f = RandomForestClassifier(n_estimators=20 , bootstrap=False)

st = time.time()
f.fit(x, y)
print time.time() - st

