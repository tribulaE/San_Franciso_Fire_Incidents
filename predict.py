import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error


#Loading the csv file for fire incidents in San Franciso
data = pd.read_csv('Fire_Incidents_20260806.csv')


#Making a new column and assigning it to prop loss
#Removing the comma out of the string then trainsiting it to a number 
#Then making the column a int from string
data['prop loss'] = pd.Series(data['Estimated Property Loss'].str.replace(',', ''))
data['prop loss'] = pd.to_numeric(data['prop loss'])

#Filtering out the zeros from the column
data = data[data['prop loss'] > 0]


#Removing the space from each column to get the exact numbers we need
data['situation_code'] = data['Primary Situation'].str.extract(r'^(\d+)', expand=False).fillna('Uknown')
data['property_code']  = data['Property Use'].str.extract(r'^(\d+)', expand=False)
data['Area Fire'] = data['Area of Fire Origin'].str.extract(r'^(\d+)', expand=False).fillna('Uknown')


#Group property code by top prop loss from median and count
#Keeping the median that has at least 30 fires or more then applying to the top 10 
summary = data.groupby('property_code')['prop loss'].agg(['median', 'count'])
result = summary[summary['count'] >= 30]
top_10_prop_type = result.sort_values('median', ascending=False).head(10)


#------ Bar Chart --------


#Getting names from the top 10 fires using the original column then put that back into the names list
#Which will be used in the chart
names = [data[data['property_code'] == code]['Property Use'].iloc[0] for code  in top_10_prop_type.index]

 
plt.barh(names, top_10_prop_type['median'], align='center')
plt.xlabel('Median Loss ($)', fontsize=20)
plt.ylabel('Property Type', fontsize=18)
plt.title('Typical fire loss by property type')
plt.tight_layout()
plt.show()


#------ Predict The Model ------

model = LinearRegression()

#Using log to transform the raw dollars from property loss, in order to get a better shape that will fit into the model
y = np.log10(data['prop loss'])

X = data[['situation_code', 'property_code', 'Area Fire']]

#One hot encode
X = pd.get_dummies(X, drop_first=True)

#Training and testing the X, y
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#Fitting the model
model.fit(X_train, y_train)

#Predict and score
pred = model.predict(X_test)
print('R2: ', r2_score(y_test, pred))
print('MAE:', mean_absolute_error(y_test, pred))
