'''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
df = pd.read_csv("CAR DETAILS FROM CAR DEKHO.csv")
df.head()
df.info()
df.isnull().sum()
df.describe()
plt.hist(df['selling_price'], bins=50)
plt.show()
df['fuel'].value_counts().plot(kind='bar')
plt.show()
plt.scatter(df['year'], df['selling_price'])
plt.show()
numeric = df[['year','selling_price','km_driven']]
sns.heatmap(numeric.corr(), annot=True)
plt.show()
df_encoded = pd.get_dummies(df, columns=[
    'fuel',
    'seller_type',
    'transmission',
    'owner'
])
df['brand'] = df['name'].apply(lambda x: x.split()[0])
df = df.drop('name', axis=1)
X = df_encoded.drop('selling_price', axis=1)
y = df_encoded['selling_price']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2
)
pred = model.predict(X_test)

mae = mean_absolute_error(y_test, pred)
r2 = r2_score(y_test, pred)

scores = []

for i in range(30):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2
    )

    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    r2 = r2_score(y_test, pred)

    scores.append(r2)
np.mean(scores)
np.std(scores)
joblib.dump(model, "car_price_model.pkl")



'''








