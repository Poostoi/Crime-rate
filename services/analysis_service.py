import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import plot_tree
from datetime import datetime

class AnalysisService:

    @staticmethod
    def get_available_files():
        """Получить список Excel файлов из папки files"""
        files_dir = 'files'
        if not os.path.exists(files_dir):
            return []

        excel_files = [f for f in os.listdir(files_dir) if f.endswith('.xlsx')]
        return sorted(excel_files)

    @staticmethod
    def run_analysis(filename):
        """Запустить анализ Random Forest на выбранном файле"""
        filepath = os.path.join('files', filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл {filename} не найден")

        df = pd.read_excel(filepath, index_col=0, engine='openpyxl')

        if "Уровень преступности" not in df.index:
            raise ValueError("В таблице нет строки 'Уровень преступности'")

        data = df.T
        X = data.drop(columns=["Уровень преступности"])
        y = data["Уровень преступности"]

        forest = RandomForestRegressor(n_estimators=100, random_state=0)
        forest.fit(X, y)

        importance_forest = pd.Series(forest.feature_importances_, index=X.columns)

        importance_df = pd.DataFrame({
            "Показатель": importance_forest.index,
            "Важность": np.round(importance_forest.values, 3)
        }).sort_values("Важность", ascending=False)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plot_dir = 'static/plots'
        os.makedirs(plot_dir, exist_ok=True)

        importance_plot_path = os.path.join(plot_dir, f'importance_{timestamp}.png')
        tree_plot_path = os.path.join(plot_dir, f'tree_{timestamp}.png')

        plt.figure(figsize=(10, 6))
        importance_forest.sort_values().plot(kind="barh", color="skyblue")
        plt.title("Важность факторов, влияющих на уровень преступности")
        plt.xlabel("Значимость")
        plt.ylabel("Показатели")
        plt.tight_layout()
        plt.savefig(importance_plot_path, dpi=100, bbox_inches='tight')
        plt.close()

        plt.figure(figsize=(20, 10))
        plot_tree(forest.estimators_[0], feature_names=X.columns, filled=True, rounded=True)
        plt.title("Дерево решений (первое из ансамбля)")
        plt.tight_layout()
        plt.savefig(tree_plot_path, dpi=100, bbox_inches='tight')
        plt.close()

        most_important = importance_df.iloc[0]["Показатель"]

        return {
            'importance_data': importance_df.to_dict('records'),
            'importance_plot': importance_plot_path.replace('static/', ''),
            'tree_plot': tree_plot_path.replace('static/', ''),
            'most_important': most_important,
            'n_features': len(X.columns),
            'n_samples': len(X)
        }