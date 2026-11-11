"""
Acest fișier conține clasa DataIngestor, utilizată pentru a citi și analiza
datele dintr-un fișier CSV ce conține statistici legate de sănătate și activitate fizică
pentru fiecare stat din SUA.
"""

import pandas as pd

class DataIngestor:
    """
    Clasa DataIngestor încarcă un fișier CSV și oferă metode pentru analiza
    statistică a valorilor de sănătate pentru fiecare stat.
    """
    def __init__(self, csv_path: str):
        """
        Inițializează instanța DataIngestor și încarcă datele din fișierul CSV.

        Parametri:
        csv_path (str): Calea către fișierul CSV.
        """
        self.df = pd.read_csv(csv_path)

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of '
            'moderate-intensity aerobic physical activity '
            'or 75 minutes a week of vigorous-intensity aerobic activity '
            '(or an equivalent combination)',

            'Percent of adults who achieve at least 150 minutes a week of '
            'moderate-intensity aerobic physical activity '
            'or 75 minutes a week of vigorous-intensity aerobic physical activity '
            'and engage in muscle-strengthening activities on 2 or more days a week',

            'Percent of adults who achieve at least 300 minutes a week of '
            'moderate-intensity aerobic physical activity '
            'or 150 minutes a week of vigorous-intensity aerobic activity '
            '(or an equivalent combination)',

            'Percent of adults who engage in muscle-strengthening activities '
            'on 2 or more days a week',
        ]

    def get_states_mean(self, question):
        """
        Returnează media valorilor pentru fiecare stat pentru o întrebare dată.

        Parametri:
        question (str): Întrebarea pentru care se calculează media.

        Returnează:
        dict: Un dicționar cu statele și media valorilor asociate.
        """
        df_filtered = self.df[self.df['Question'] == question]
        return dict(df_filtered.groupby('LocationDesc')['Data_Value'].mean().sort_values())

    def get_state_mean(self, question, state):
        """
        Returnează media valorilor pentru un stat specific și o întrebare.

        Parametri:
        question (str): Întrebarea vizată.
        state (str): Statul pentru care se calculează media.

        Returnează:
        dict: Un dicționar cu statul și media valorii.
        """
        df_filtered = self.df[(self.df['Question'] == question)
                              & (self.df['LocationDesc'] == state)]
        return dict({state: df_filtered['Data_Value'].mean()})

    def get_best5(self, question):
        """
        Returnează top 5 state cu cele mai bune valori pentru întrebarea dată.

        Parametri:
        question (str): Întrebarea pentru care se caută cele mai bune valori.

        Returnează:
        dict: Un dicționar cu top 5 state și valorile lor.
        """
        states_mean = self.get_states_mean(question)
        items = list(states_mean.items())
        if question in self.questions_best_is_min:
            return dict(items[:5])
        if question in self.questions_best_is_max:
            return dict(sorted(items, key=lambda x: x[1], reverse=True)[:5])
        return {}

    def get_worst5(self, question):
        """
        Returnează top 5 state cu cele mai slabe valori pentru întrebarea dată.

        Parametri:
        question (str): Întrebarea pentru care se caută cele mai slabe valori.

        Returnează:
        dict: Un dicționar cu top 5 state și valorile lor.
        """
        states_mean = self.get_states_mean(question)
        items = list(states_mean.items())
        if question in self.questions_best_is_min:
            return dict(items[-5:][::-1])
        if question in self.questions_best_is_max:
            return dict(sorted(items, key=lambda x: x[1])[:5])
        return {}

    def get_global_mean(self, question):
        """
        Returnează media globală a valorilor pentru o întrebare.

        Parametri:
        question (str): Întrebarea pentru care se calculează media globală.

        Returnează:
        dict: Un dicționar cu cheia 'global_mean' și valoarea medie.
        """
        df_filtered = self.df[self.df['Question'] == question]
        mean = df_filtered['Data_Value'].mean()
        return dict({"global_mean": mean})

    def get_diff_from_mean(self, question):
        """
        Calculează diferența dintre media globală și media fiecărui stat.

        Parametri:
        question (str): Întrebarea pentru care se calculează diferențele.

        Returnează:
        dict: Dicționar cu diferențele pentru fiecare stat.
        """
        global_mean = self.get_global_mean(question)
        states_mean = self.get_states_mean(question)
        return dict({state: (global_mean["global_mean"] - state_mean)
                     for state, state_mean in states_mean.items()})

    def get_state_diff_from_mean(self, question, state):
        """
        Calculează diferența dintre media globală și media unui stat specific.

        Parametri:
        question (str): Întrebarea vizată.
        state (str): Statul analizat.

        Returnează:
        dict: Dicționar cu diferența pentru acel stat.
        """
        global_mean = self.get_global_mean(question)
        state_mean = self.get_state_mean(question, state)
        return dict({state: (global_mean["global_mean"] - state_mean[state])})

    def get_mean_by_category(self, question):
        """
        Returnează media valorilor pentru fiecare categorie de stratificare,
        la nivel de stat, pentru întrebarea dată.

        Parametri:
        question (str): Întrebarea vizată.

        Returnează:
        dict: Dicționar cu medii pentru fiecare categorie.
        """
        df_filtered = self.df[self.df['Question'] == question]
        grouped = df_filtered.groupby(['LocationDesc', 'StratificationCategory1',
                                       'Stratification1'])['Data_Value'].mean()
        return dict({str(key): value for key, value in grouped.items()})

    def get_state_mean_by_category(self, question, state):
        """
        Returnează media valorilor pentru un stat, împărțite pe categorii de stratificare,
        pentru o întrebare dată.

        Parametri:
        question (str): Întrebarea vizată.
        state (str): Statul analizat.

        Returnează:
        dict: Dicționar cu media pe categorii pentru acel stat.
        """
        df_filtered = self.df[(self.df['Question'] == question)
                              & (self.df['LocationDesc'] == state)]
        grouped = df_filtered.groupby(['StratificationCategory1',
                                       'Stratification1'])['Data_Value'].mean()
        return dict({state: {str(key): value for key, value in grouped.items()}})
