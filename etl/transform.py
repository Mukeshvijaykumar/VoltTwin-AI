import pandas as pd


class Transform:

    def clean_weather(self, df):

        df = df.drop_duplicates()

        df = df.fillna(0)

        return df


    def clean_grid(self, df):

        df = df.drop_duplicates()

        df = df.fillna(0)

        return df