import pandas as pd
import plotly.express as px

def avg_mthly_employ(city: str, filepath: str):
    '''
    This function creates plots for the average monthly employment per year.
    '''
    def filter_df(city: str, df):
        '''
        Filters df by city
        '''
        df = df[df['City'] == city]
        return df
    def plots(df):
        '''
        Plots data using plotly
        '''
        empl_data_plot = px.bar(df, x=df.index, y='Average Monthly Employment', labels={'DATE': 'Year'}, text='Average Monthly Employment')
        empl_data_plot.update_traces(textposition='outside')
        empl_data_plot.show()
        return empl_data_plot
    empl_data = pd.read_csv(filepath, na_values=["***", ".", "NA"])
    empl_data['DATE'] = empl_data['DATE'].str.pad(width=6, side="left", fillchar="0")
    empl_data['DATE'] = pd.to_datetime(empl_data.DATE, format='%y-%b')
    empl_data.set_index('DATE', inplace=True)
    empl_data = empl_data.fillna(0)
    empl_data['Total Employment'] = empl_data.loc[:, 'Agriculture, Forestry, Fishing and Hunting':].sum(axis=1)
    empl_data = empl_data[empl_data["Total Employment"] != 0]

    empl_data = filter_df(city, empl_data)
    empl_data = empl_data.resample("1Y").mean().round()
    empl_data.rename(columns={'Total Employment': 'Average Monthly Employment'}, inplace=True)
    empl_data.index = empl_data.index.strftime('%Y')
    plots(empl_data)

def unemployment_composition(city: str, filepath: str):
    def filter_df(city: str, df):
        '''
        Filters df by city
        '''
        df = df[df['City'] == city]
        return df
    def plots(df):
        '''
        Plots data using plotly
        '''
        empl_data_plot = px.bar(df, x=df.index, y='Change in Employment Composition', labels={'index': 'Sector'}, text='Change in Employment Composition')
        empl_data_plot.update_traces(textposition='outside')
        empl_data_plot.show()
        return empl_data_plot
    empl_data = pd.read_csv(filepath, na_values=["***", ".", "NA"])
    empl_data['DATE'] = empl_data['DATE'].str.pad(width=6, side="left", fillchar="0")
    empl_data['DATE'] = pd.to_datetime(empl_data.DATE, format='%y-%b')
    empl_data.set_index('DATE', inplace=True)
    empl_data = empl_data.fillna(0)
    empl_data = filter_df(city, empl_data)
    empl_data = empl_data[empl_data.index.year > 2019]
    empl_data = empl_data[empl_data.index.month == 3]
    change_df = pd.DataFrame()
    change_df.index = empl_data.columns[1:]
    change_df['Change in Employment Composition'] = empl_data.loc['2020-03-01', 'Agriculture, Forestry, Fishing and Hunting':] - empl_data.loc['2021-03-01', 'Agriculture, Forestry, Fishing and Hunting':]
    change_df = change_df[change_df['Change in Employment Composition'] != 0.0]
    plots(change_df)
