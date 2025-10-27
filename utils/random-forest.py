import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.ensemble import RandomForestRegressor

path = "2010_2015.xlsx"#"data.xlsx"
# 1. Загружаем данные
df = pd.read_excel(path, index_col=0, engine='openpyxl')
print("Исходные данные:")
print(df, "\n")

# Проверим, что в df уже есть строка 'Уровень преступности'
if "Уровень преступности" not in df.index:
    raise ValueError("В таблице нет строки 'Уровень преступности'!")

# 2. Подготовка данных
data = df.T
X = data.drop(columns=["Уровень преступности"])
y = data["Уровень преступности"]

# 3. Обучение моделей
tree = DecisionTreeRegressor(random_state=0)
forest = RandomForestRegressor(n_estimators=100, random_state=0)
tree.fit(X, y)
forest.fit(X, y)

# 4. Важность факторов
importance_tree = pd.Series(tree.feature_importances_, index=X.columns)
importance_forest = pd.Series(forest.feature_importances_, index=X.columns)

print("Важность факторов (Decision Tree)")
print(importance_tree.sort_values(ascending=False), "\n")

print("Важность факторов (Random Forest)")
print(importance_forest.sort_values(ascending=False), "\n")

# 5. Сохраняем и визуализируем
importance_df = pd.DataFrame({
    "Показатель": importance_forest.index,
    "Важность (Random Forest)": np.round(importance_forest.values, 3)
}).sort_values("Важность (Random Forest)", ascending=False)

importance_df.to_excel("важные.xlsx", index=False)
print("Результаты сохранены в файл: важные.xlsx")

plt.figure(figsize=(10, 6))
importance_forest.sort_values().plot(kind="barh", color="skyblue")
plt.title("Важность факторов, влияющих на уровень преступности (Random Forest)")
plt.xlabel("Значимость")
plt.ylabel("Показатели")
plt.tight_layout()
plt.show()
plot_tree(forest.estimators_[0], feature_names=X.columns, filled=True, rounded=True)
plt.show()
# 6. Вывод самого важного показателя
most_important = importance_df.iloc[0]["Показатель"]
print(f"\nНаибольшее влияние на уровень преступности оказывает показатель: {most_important}")