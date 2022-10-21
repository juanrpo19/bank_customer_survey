# -*- coding: utf-8 -*-
"""Trabajo_Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VFxR00bmq6_uLAJ82KZMMLCMfPn5Wlch

# Introducción

## Bank Customers Survey - Marketing for Term Deposit

El conjunto de datos usando para el presente ejercicio fue tomado de la página https://www.kaggle.com/sharanmk/bank-marketing-term-deposit y contiene información relacionada con una campaña de marketing de un banco y pretende determinar si un cliente tomaría o no un depósito a término fijo.

El dataset cuenta con 45211 registros y 17 columnas de las cuales 16 son explicativas y 1 variable binaria dependiente en la que se tiene si un cliente ha tomado anteriormente el depósito o no.

La estrategia es implementar 3 clasificadores que nos permitan evaluar y comparar sus métricas y así seleccionar el mejor de ellos.

# Importación de librerías
"""

# Importar librerias

import pandas as pd
import seaborn as sns
import os
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report,confusion_matrix, f1_score, precision_score, recall_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn import svm
import warnings

"""# Definición de funciones"""

# Funciones

# Ignorar los warnings
warnings.filterwarnings("ignore")

#############################################################################################################
## Función que recibe como parametros el modelo, los datos de prueba y la predicción. Imprime las metricas f1_score y la precisión.
def calcular_metricas(model, y_test, y_pred):

  ## Calucula las metricas a evaluar del clasificador
  _f1_score = f1_score(y_test, y_pred)
  _acc_score = precision_score(y_test, y_pred)
  _recall = recall_score(y_test, y_pred)

  ## Imprimir las metricas del clasificador con los mejores parametros
  print("El f1_score de la clase positiva para " + type(model).__name__ + " balanceado: {0:.3%}".format(_f1_score))
  print("La precisión del clasificador para " + type(model).__name__ + " balanceado: {0:.3%}".format(_acc_score))
  print("La sensibilidad del clasificador para " + type(model).__name__ + " balanceado: {0:.3%}".format(_recall))
  # print("La matriz de confusión:")
  # print(confusion_matrix(y_test, y_pred))
  # print(classification_report(y_test, y_pred))
  return _f1_score, _acc_score, _recall


#############################################################################################################
## Entrenamiento y predicción de cualquier modelo
def entrenar_predecir_modelo(model, X_train, y_train, X_test, y_test):

  inicio = datetime.now()

  # Se genera el pipeline con el transformador y el clasificador 
  pipe_model = make_pipeline(_columnTransformer, model)

  # # Entrenamiento del modelo con los datos
  pipe_model.fit(X_train, y_train)

  # # Predicción del modelo
  y_pred = pipe_model.predict(X_test)

  # Llama la función calcular_metricas
  f1_score, acc_score, recall = calcular_metricas(model, y_test, y_pred)

  fin = datetime.now()

  # Imprime el tiempo de entrenamiento
  print()
  print('Tiempo de entrenamiento: {} segundos.'.format(fin - inicio))

  # Retorna las metricas calculadas
  return pipe_model,  {'model': type(model).__name__, 'f1_score': f1_score, 'accuracy': acc_score, 'recall': recall}


#############################################################################################################
## Función que convierte el listado del best_params_ en un dict para luego asignarlo dinamicamente a los paramtros del modelo
def Convertir_Lista_Parametros(lista):
  lst_best = []

  #Recorre cada uno de los paramtros de la lista.
  for best_param in lista.items():
    parametro = best_param[0].replace(best_param[0].split('__')[0] +'__','') # Los parametros vienen con el key del pipeline, por ej: 'randomforestclassifier__max_features'. En esta linea se quita el key 'randomforestclassifier__'  y solo se deja el 'max_features'.
    lst_best.append(parametro)       # Apila el nombre del parametro a lst_best
    lst_best.append(best_param[1])  # Apila el valor del parametro a lst_best

    # Convierte el listado de parametros y valores en un dict y lo retorna
    it_val = iter(lst_best)
    res_dct = dict(zip(it_val, it_val))
  return res_dct
         

#############################################################################################################
def seleccionar_mejor_clasificador(metricas):
  lista = sorted(metricas_bal, key = lambda i: i['recall'], reverse = True)[0]
  best_model = lista.get('model')
  best_recall = lista.get('recall')
  best_f1_score = lista.get('f1_score')
  best_acc = lista.get('accuracy')
  return [{'model': best_model, 'recall': best_recall, 'f1_score': best_f1_score, 'accuracy': best_acc}]

"""# Preprocesamiento de los datos

## Lectura y carga de datos
"""

# Conexión con Drive
#from google.colab import drive
#drive.mount('/content/drive')
#os.chdir("/content/drive/My Drive/Colab Notebooks/Analítica Predictiva/Final/dataset1")

# Lectura de datos
df_original = pd.read_csv("bank_customer_survey.csv", sep = ",")

# Copia del dataset original
df_copia = df_original.copy()
print(df_copia.shape)
print(df_copia.columns)

"""## Balanceo de los datos"""

# Separación de los datos 'X' y 'y'
y = df_copia['y']
X = df_copia.drop('y', axis = 1)

# El dataset está desbalanceado en la variable 'y' (target). Se debe hacer un balanceo de los datos para que el modelo no se sobreentrene.
grafica = sns.countplot(df_copia['y'], palette='Set2')
grafica

#### Balanceo del dataset


# Separa la información en dos dataframes para cada uno de las opciones de la columna 'y'
x_0 = df_copia[df_copia['y']==0]
x_1 = df_copia[df_copia['y']==1]

# Crea el dataframe balanceado para la clase mayoritaria 
x_sample_0 = x_0.sample(x_1.shape[0])

# Dataframe con la clase minoritaria
x_sample_1 = x_1.copy()

# Dataframe balanceado con ambas clases
X_balanceado = pd.concat([x_sample_0, x_sample_1]) 

print(X_balanceado.columns)
print(X_balanceado['y'].value_counts())

grafica = sns.countplot(X_balanceado['y'], palette='Set3')

"""## Creación del transformador de los datos"""

# Creación de listas por tipos de datos. Aquí se puede incluir mas tipos de datos

lst_texto = X.select_dtypes(include='object').columns
lst_numeros = X.select_dtypes(include='int64').columns

# Creación del transformador de los datos. La trsnformación de los datos se hace de la siguiente forma:
# Para los datos categoricos se usa el OneHotEncoder() y se le pasa el listado lst_texto que contiene las columnas de tipo caracter
# Para los datos numericos se usa el StandardScaler() y se le pasa el listado lst_numeros que contiene las columnas de tipo número

transformer_data = [('cat', OneHotEncoder(), lst_texto), ('num', StandardScaler(), lst_numeros)]
_columnTransformer = ColumnTransformer(transformers=transformer_data)

"""## Partición de los datos"""

# Separación de los datos en train y test. Aquí los datos están aún desblanceados.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state=0)

# Generación del dataframe balanceado

y_balanceado = X_balanceado['y']
X_balanceado = X_balanceado.drop('y', axis = 1)

print(X_balanceado.shape)
print(y_balanceado.shape)

# Partición de los datos del dataframe balanceado

X_train_bal, X_test_bal, y_train_bal, y_test_bal = train_test_split(X_balanceado, y_balanceado, test_size=0.2, random_state=4522)

print(X_train_bal.shape)
print(y_train_bal.shape)
print(X_test_bal.shape)
print(y_test_bal.shape)

"""# Clasificador RandomForestClassifier

## Clasificador con datos desbalanceados
"""

# Generación del clasificador RandomForestClassifier para los datos desblanceados
rf_sin_bal = RandomForestClassifier(random_state=4522, class_weight='balanced', n_estimators=10)

# Calculo de las metricas para el modelo RandomForestClassifier para los datos desblanceados
metricas_rf_sin_bal = entrenar_predecir_modelo(rf_sin_bal, X_train, y_train, X_test, y_test)
metricas_rf_sin_bal

"""## Validación cruzada para RandomForestClassifier"""

### Creación del clasificador con validación cruzada.

# Crea el clasificador para el pipeline de los datos balanceados
rf_bal = RandomForestClassifier(random_state = 4522)

# El pipeline contiene 2 pasos: uno para la trasformación de los datos (_columnTransformer) y otro para la clasificación (rf_bal)
model_rf_bal = make_pipeline(_columnTransformer, rf_bal)


# Lista de parametros para el validador. Para que el pipeline sea capaz de identicar a cual de los pasos pertenece el parametro dentro de la validación 
# cruzada, se debe anteponer el identificador de cada objeto, en este caso 'randomforestclassifier__'.
# Con el comando sorted(model_rf_bal.get_params().keys()) se listan parametros del pipeline.

param_gridcv_rf = { 
    'randomforestclassifier__n_estimators': [200, 500],
    'randomforestclassifier__max_features': ['auto', 'sqrt', 'log2'],
    'randomforestclassifier__max_depth' :   [4,5,6,7,8],
    'randomforestclassifier__criterion' :   ['gini', 'entropy']
}


param_gridcv_rf = { 
    'randomforestclassifier__n_estimators': [200,300],
    'randomforestclassifier__max_features': ['auto'],
    'randomforestclassifier__max_depth' :   [2,4],
    'randomforestclassifier__criterion' :   ['gini']
}


# Se crea el Clasificador para validación cruzada con el pipeline que ya contiene el transformador de los datos y el clasificador. También los parametros a
# evaluar en la validación cruzada
model_rf_bal_cv = GridSearchCV(model_rf_bal, param_gridcv_rf, cv=2)

# Entrenamiento del clasificador para validación cruzada
inicio = datetime.now()
model_rf_bal_cv.fit(X_train_bal, y_train_bal)
fin = datetime.now()
print('Tiempo de entrenamiento: {} segundos.'.format(fin - inicio))

# sorted(model_rf_bal.get_params().keys())

"""## Clasificador con mejores hiperparametros"""

# Convierte dinamicamente la lista del best_params_ y asigna a cada parametro el valor calculado en la CV
parametros_rf = Convertir_Lista_Parametros(model_rf_bal_cv.best_params_)
parametros_rf

# Se crea el clasificador con los mejores parametros
rf_bal_best = RandomForestClassifier(**parametros_rf, random_state=4522)

# Se crea el pipeline con el modelo con los mejores parametros
# model_rf_bal_best = make_pipeline(_columnTransformer, rf_bal_best)

# Estimar mejores parametros
metricas_rf_bal = entrenar_predecir_modelo(rf_bal_best, X_train_bal, y_train_bal, X_test_bal, y_test_bal)
trained_model_rf_best = metricas_rf_bal[0]

trained_model_rf_best

"""# Clasificador LogisticRegression

## Clasificador con datos desbalanceados
"""

# Generación del clasificador LogisticRegresion para los datos desblanceados
lr_sin_bal = LogisticRegression(random_state=4522)

# Calculo de las metricas para el modelo RandomForestClassifier para los datos desblanceados
metricas_lr_sin_bal = entrenar_predecir_modelo(lr_sin_bal, X_train, y_train, X_test, y_test)
metricas_lr_sin_bal

"""## Validación cruzada para LogisticRegression"""

# Clasificador LogisticRegresion sin parametros 
lr_bal = LogisticRegression(random_state=4522)

# Creación del Pipeline del modelo LR
model_lr_bal = make_pipeline(_columnTransformer, lr_bal)

# Creación de la lista de parametros a evaluar en la CV
param_gridcv_lr = [
    {
        'logisticregression__penalty': ['l1', 'l2'],
        'logisticregression__C': [0.1, 1.0, 5.0, 10.0],     
        'logisticregression__solver': ['newton-cg', 'sag', 'lbfgs'],
        'logisticregression__max_iter' :   [1000, 10000, 10000]
     },
     {
        'logisticregression__penalty': ['elasticnet'],
        'logisticregression__C': [0.1, 1, 5, 10],
        'logisticregression__solver': ['saga'],
        'logisticregression__max_iter' :   [1000, 10000, 10000]
     },
]

# Paramentros para la validación cruzada
param_gridcv_lr = { 
    'logisticregression__solver': ['newton-cg', 'sag'],
    'logisticregression__max_iter' :   [1000 ]
}


# Creación del validador cruzado para el lr
model_lr_bal_cv = GridSearchCV(model_lr_bal, param_gridcv_lr, cv=10)

# Entrenamiento del modelo lr
inicio = datetime.now()
model_lr_bal_cv.fit(X_train_bal, y_train_bal)
fin =datetime.now()
print('Tiempo de entrenamiento: {} segundos.'.format(fin - inicio))

# model_lr_bal.get_params().keys()

"""## Clasificador con mejores hipermarametros"""

# Convierte dinamicamente la lista del best_params_ y asigna a cada parametro el valor calculado en la CV
parametros_lr = Convertir_Lista_Parametros(model_lr_bal_cv.best_params_)

# Clasificador con los mejores parametros
lr_bal_best = LogisticRegression(**parametros_lr, random_state = 4522)

# Crea el pipeline para el clasificador con los mejores parametros
model_lr_bal_best = make_pipeline(_columnTransformer, lr_bal_best)

# Estimar mejores parametros
metricas_lr_bal = entrenar_predecir_modelo(lr_bal_best, X_train_bal, y_train_bal, X_test_bal, y_test_bal)
metricas_lr_bal

"""# Clasificador SVM

## Clasificador con datos desbalanceados
"""

# Generación del clasificador SVM para los datos desblanceados
clf_svm_sin_bal = svm.SVC(random_state = 4522)
metricas_svm_sin_bal = entrenar_predecir_modelo(clf_svm_sin_bal, X_train, y_train, X_test, y_test)
metricas_svm_sin_bal

"""## Validación cruzada para SVM"""

# Clasificador SVM sin parametros
clf_svm = svm.SVC(random_state = 4522)  # tipo de kernel  # factor de regularización

# Creación del pipeline para la CV
model_svm_bal = make_pipeline(_columnTransformer,clf_svm)

# Lista de parametros para la CV
param_gridcv_smv =  [{'svc__kernel': ['rbf'], 
                      'svc__gamma': [1e-2, 1e-3, 1e-4],
                      'svc__C': [ 0.01, 0.1, 10, 100 ]},
                      {'svc__kernel': ['sigmoid'],
                       'svc__gamma': [1e-2, 1e-3, 1e-4],
                      'svc__C': [0.01, 0.1, 10, 100 ]},
                      {'svc__kernel': ['linear'], 
                       'svc__C': [0.01, 0.1, 10, 100]}
                     ]              


param_gridcv_smv =  [{'svc__kernel': ['rbf'], 
                      'svc__gamma': [1e-2],
                      'svc__C': [0.001, 0.1]}
                     ]              


# Creación del validador cruzado para el svm
model_svm_bal_cv = GridSearchCV(model_svm_bal, param_gridcv_smv, cv=10)

# sorted(model_svm_bal.get_params().keys())

"""## Clasificador con mejores hiperparametros"""

#Entrenamiento del modelo
inicio = datetime.now()
model_svm_bal_cv.fit(X_train_bal, y_train_bal)
fin =datetime.now()
print('Tiempo de entrenamiento: {} segundos.'.format(fin - inicio))

# Mejores parametros para el estimador
model_svm_bal_cv.best_params_

parametros_svm = Convertir_Lista_Parametros(model_svm_bal_cv.best_params_)
print(parametros_svm)
# Crea un nuevo clasificador con los mejores parametros entregados por la validación cruzada
clf_svm_best = svm.SVC(**parametros_svm, random_state = 0)

# Clasificador SVM con mejores parametros

metricas_svm_bal = entrenar_predecir_modelo(clf_svm_best, X_train_bal, y_train_bal, X_test_bal, y_test_bal)

"""# Seleccion del mejor clasificador

## Listado de métricas de los 3 clasificadores
"""

# Consolida los resultados de los 3 clasificadores
metricas_sin_bal = [metricas_rf_sin_bal, metricas_lr_sin_bal, metricas_svm_sin_bal]
df_metricas_sin_bal = pd.DataFrame.from_dict(metricas_sin_bal)

metricas_bal = [metricas_rf_bal, metricas_lr_bal, metricas_svm_bal]
df_metricas_bal = pd.DataFrame.from_dict(metricas_bal)

df_resultados = pd.DataFrame.from_dict(metricas_bal)
print("Lista de métricas de los 3 clasificadores:")
print("")
df_resultados

"""## Mejor clasificador"""

# Imprime el mejor clasificador respecto al Recall

dict_best = seleccionar_mejor_clasificador(metricas_bal)
df_best = pd.DataFrame(dict_best)
print("El mejor clasificador es:")
print("")
df_best

"""## Comparativo gráfico de los datos balanceados y desbalanceados """

# Imprime las métricas con los datos desbalanceados
plt1 = df_metricas_sin_bal.plot(x='model', y=["recall", 'accuracy','f1_score'], kind="bar")

# Imprime las métricas con los datos balanceados y con mejores parametros
plt2 = df_metricas_bal.plot(x='model', y=["recall", 'accuracy','f1_score'], kind="bar")

"""# Conclusiones

Como se puede observar, la métrica de la precisión no nos da un buen estimador para definir cuál es el mejor clasificador, ya que si tomamos como referencia este valor, se evidencia que es muy similar con y sin datos balanceados en la clase dependiente; por el contrario, si tomamos la sensibilidad (Recall) para la clase positiva (sí tomaría el depósito a término) se evidencia un incremento significativo que permite concluir que el clasificador mejoró en la predicción del valor positivo de la clase que es lo que se requiere para así aumentar la cantidad de personas que tomarían el depósito.

Finalmente se concluye que, aunque todos los clasificadores tuvieron una mejoría después de balancear los datos, el mejor estimador sería el RandomForestClassifier ya que tiene una sensibilidad más alta para la clase positiva.

"""

import pickle
# with open('clf.pickle', 'wb') as f:
#     pickle.dump(model_rf_bal_best, f, pickle.HIGHEST_PROTOCOL)
# model_rf_bal_best

pickle.dump(trained_model_rf_best, open('model_1.pkl','wb'))

df_valores = pd.DataFrame(valores) 
df_valores
a = trained_model_rf_best.predict(valores)

model = pickle.load(open('model_1.pkl','rb'))
X_train_bal

valores = [[1,
1,
1,
1,
1,
1,
1,
1,
1,
1,
1,
1,
1,
1,
1,
1]]

_classnames = ['0','1']
df_valores.columns = [X_train_bal.columns]

print(X_train_bal.head())
print(df_valores.head())
result = model.predict(df_valores)
X_train_bal.columns

print('The scikit-learn version is {}.'.format(sklearn.__version__))