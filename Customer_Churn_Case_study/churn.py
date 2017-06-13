import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve
from pandas.tools.plotting import scatter_matrix
from sklearn import metrics

def clean_data(df):
    df['churn'] =1 * (df.last_trip_date >= '2014-06-01')
    df.phone = pd.get_dummies(df.phone) # Android: 1, IPhone: 0
    df.rename(index = str, columns = {'phone': 'Android'}, inplace=True)# change the name

    df = pd.concat([df, pd.get_dummies(df.city, drop_first=True)], axis=1)
    df.drop('city', inplace=True, axis = 1)

    pull_date = pd.to_datetime('2014-07-01')
    df['acc_age'] = (pull_date - pd.to_datetime(df['signup_date']) ) / np.timedelta64(1,'D')
    df.drop(['signup_date','last_trip_date'], inplace=True, axis = 1)

    # Dummy luxury car
    df['luxury_car_user'] = 1 * (df['luxury_car_user'])

    # Create new columns by splitting the ratings into groups (high rating,low rating, no rating) Thresholds
    rat_by_t = df['avg_rating_by_driver'].median(axis=0)
    rat_of_t = df['avg_rating_of_driver'].median(axis=0)

    df['Rate_by_High'] = 1 * (df['avg_rating_by_driver'] >= rat_by_t)
    df['Rate_by_Low'] = 1 * (df['avg_rating_by_driver'] < rat_by_t)
    df['Rate_of_High'] = 1 * (df['avg_rating_of_driver'] >= rat_of_t)
    df['Rate_of_Low'] = 1 * (df['avg_rating_of_driver'] < rat_of_t)
    df.drop(['avg_rating_by_driver','avg_rating_of_driver'], inplace=True, axis = 1)
    #df.dropna(how = 'any', inplace= True)
    return df


def printscores(model,y_final, y_final_pred):
    print 'Model: ', model.__class__.__name__
    print 'training accuarcy score:',model.score(X_train, y_train)
    print 'final test accuracy score: ',model.score(X_final, y_final)
    print 'final test precision score:', metrics.precision_score(y_final,y_final_pred)
    print 'final test recall score:', metrics.recall_score(y_final,y_final_pred)
    print metrics.confusion_matrix(y_final,y_final_pred)

def plot_feat_imp(model):
    imp = model.feature_importances_
    idx = np.argsort(imp)
    plt.barh(range(len(imp)), imp[idx])
    plt.yticks(np.arange(len(imp))+0.5, X_train.columns[idx])
    plt.show()


if __name__ == '__main__':
    #load training dataset
    df = pd.read_csv("data/churn_train.csv")
    #Plot histograms for ratings by/of drivers
    df.hist(['avg_rating_by_driver','avg_rating_of_driver'],grid=False,figsize=(15,7))
    plt.xlabel('Rating')
    plt.show()

    churn = clean_data(df)
    y = churn.churn
    X = churn.drop(['churn'], axis = 1)
    X_train, X_test, y_train, y_test = train_test_split(X,y, random_state = 1)

    #load testing dataset
    testdf = pd.read_csv('data/churn_test.csv')
    testdf = clean(testdf)
    y_final = testdf.churn
    X_final = testdf.drop(['churn'], axis = 1)


    churn.describe()
    scatter_matrix(churn, alpha=0.2, figsize=(20, 20), diagonal='kde')
    plt.show()

    #Logistic Regression
    logreg = LogisticRegression().fit(X_train, y_train)
    logpred = logreg.predict(X_final)
    printscores(logreg, y_final,logpred)

    #Random Forest
    rf = RandomForestClassifier(n_estimators=50,n_jobs=-1,oob_score=True,max_depth=10)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_final)
    printscores(rf, y_final,rf_pred)

    #Grid Search for random forest:
    parameters = [{'n_estimators': list(range(25, 201, 25)),
               'max_features': list(range(2, X_train.shape[1], 2)),
                'max_depth': list(range(10,101,10))}]
    clf = GridSearchCV(RandomForestClassifier(), parameters, cv=5, scoring='accuracy', n_jobs=-1)
    clf.fit(X_train, y_train)
    print clf.best_params_

    #Gradient Boosting:
    gb = GradientBoostingClassifier()
    gb.fit(X_train, y_train)
    gb_pred = gb.predict(X_final)
    printscores(gb,y_final, gb_pred)

    #Plot feature importance:
    plot_feat_imp(rf)
    plt.savefig('RF_feat_imp')
    plot_feat_imp(gb)
    plt.savefig('GB_feat_imp')

    #partial dependence plots:
    imp = gb.feature_importances_
    idx = np.argsort(imp)
    print X_train.columns
    print X_train.columns[idx]
    print idx
    plot_partial_dependence(gb,X_train,idx[::-1],
                            feature_names=X_train.columns,
                            figsize=(20,20))

    plt.savefig('partial_dependence.jpg')
    plt.show()
