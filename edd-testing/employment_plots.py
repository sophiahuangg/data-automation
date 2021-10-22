import pandas as pd
import plotly.express as px

def avg_mthly_employ(city: str, save: bool, save_path: str, data_path: str):
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
    empl_data = pd.read_csv(data_path, na_values=["***", ".", "NA"])
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
    fig = plots(empl_data)
    if save:
        fig.write_image(save_path)

def change_employment_composition(city: str, filepath: str):
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
        empl_data_plot = px.bar(df, x=df.index, y='Change in Employment Share', labels={'index': 'Sector'}, text='Change in Employment Share')
        empl_data_plot.update_traces(textposition='outside')
        empl_data_plot.show()
        return empl_data_plot
    def consolidate_industries(df: pd.DataFrame):
        """Returns a dataframe that has the 12 consolidated industries we want"""
        df["Logistics"] = df["Wholesale Trade"] + df["Transportation and Warehousing"] + df["Utilities"]
        df["FIRE"] = df["Finance and Insurance"] + df["Real Estate and Rental and Leasing"]
        df["Professional and Business Services"] = df["Professional, Scientific, and Technical Services"] + df["Management of Companies and Enterprises"] + df["Administrative and Support and Waste Management and Remediation Services"]
        df["Leisure and Hospitality"] = df["Arts, Entertainment, and Recreation"] + df["Accommodation and Food Services"]
        df["Education and Health Services"] = df["Educational Services"] + df["Health Care and Social Assistance"]
        df["Government"] = df["Federal Government"] + df["State Government"] + df["Local Government"]
        df["Mining and Natural Resources"] = df["Mining, Quarrying, and Oil and Gas Extraction"] + df["Agriculture, Forestry, Fishing and Hunting"]
        
        cols_to_select = ["DATE", "City", "Logistics", "Construction", "Manufacturing",
                        "Retail Trade", "Information", "FIRE",
                        "Professional and Business Services", "Leisure and Hospitality",
                        "Education and Health Services", "Government",
                        "Mining and Natural Resources"]
        
        res = df[cols_to_select]
        return res
    empl_data = pd.read_csv(filepath, na_values=["***", ".", "NA"])
    empl_data['DATE'] = empl_data['DATE'].str.pad(width=6, side="left", fillchar="0")
    empl_data['DATE'] = pd.to_datetime(empl_data.DATE, format='%y-%b')
    empl_data = empl_data.fillna(0)
    empl_data = filter_df(city, empl_data)
    empl_data = consolidate_industries(empl_data)
    empl_data = empl_data[empl_data['DATE'].dt.year > 2019]
    empl_data = empl_data[empl_data['DATE'].dt.month == 3]
    empl_data['Total Employment'] = empl_data.iloc[:, 2:].sum(axis=1)
    for sector in empl_data.columns[2:]:
        empl_data[sector + ' '] = empl_data[sector]/empl_data['Total Employment']
    change_df = pd.DataFrame()
    change_df.index = empl_data.columns[2:]
    change_df['Change in Employment Share'] = empl_data.iloc[0, 14:] - empl_data.iloc[1, 14:]
    change_df = change_df[change_df['Change in Employment Share'] != 0.0]
    change_df = change_df.dropna()
    change_df['Change in Employment Share'] = change_df['Change in Employment Share'] * 100
    plots(change_df)

def employment_composition(city: str, data_path: str):
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
        empl_data_plot = px.bar(df, x=df.index, y='Employment Share', labels={'index': 'Sector'}, text='Employment Share')
        empl_data_plot.update_traces(textposition='outside')
        empl_data_plot.show()
        return empl_data_plot
    def consolidate_industries(df: pd.DataFrame):
        """Returns a dataframe that has the 12 consolidated industries we want"""
        df["Logistics"] = df["Wholesale Trade"] + df["Transportation and Warehousing"] + df["Utilities"]
        df["FIRE"] = df["Finance and Insurance"] + df["Real Estate and Rental and Leasing"]
        df["Professional and Business Services"] = df["Professional, Scientific, and Technical Services"] + df["Management of Companies and Enterprises"] + df["Administrative and Support and Waste Management and Remediation Services"]
        df["Leisure and Hospitality"] = df["Arts, Entertainment, and Recreation"] + df["Accommodation and Food Services"]
        df["Education and Health Services"] = df["Educational Services"] + df["Health Care and Social Assistance"]
        df["Government"] = df["Federal Government"] + df["State Government"] + df["Local Government"]
        df["Mining and Natural Resources"] = df["Mining, Quarrying, and Oil and Gas Extraction"] + df["Agriculture, Forestry, Fishing and Hunting"]
        
        cols_to_select = ["DATE", "City", "Logistics", "Construction", "Manufacturing",
                        "Retail Trade", "Information", "FIRE",
                        "Professional and Business Services", "Leisure and Hospitality",
                        "Education and Health Services", "Government",
                        "Mining and Natural Resources"]
        
        res = df[cols_to_select]
        return res
    empl_data = pd.read_csv(data_path, na_values=["***", ".", "NA"])
    empl_data['DATE'] = empl_data['DATE'].str.pad(width=6, side="left", fillchar="0")
    empl_data['DATE'] = pd.to_datetime(empl_data.DATE, format='%y-%b')
    empl_data = empl_data.fillna(0)
    empl_data = filter_df(city, empl_data)
    empl_data = consolidate_industries(empl_data)
    empl_data = empl_data[empl_data['DATE'].dt.year > 2020]
    empl_data = empl_data[empl_data['DATE'].dt.month == 3]
    empl_data['Total Employment'] = empl_data.iloc[:, 2:].sum(axis=1)
    for sector in empl_data.columns[2:]:
        empl_data[sector + ' '] = empl_data[sector]/empl_data['Total Employment']
    empl_share_df = pd.DataFrame()
    empl_share_df.index = empl_data.columns[14:]
    empl_share_df['Employment Share'] = empl_data.iloc[0, 14:]
    empl_share_df = empl_share_df.drop(index='Total Employment ')
    empl_share_df = empl_share_df.sort_values('Employment Share', ascending=True)
    plots(empl_share_df)
employment_composition('Cathedral City', '../data-automation/data/CV_EMPL.csv')

def chge_empl_share_prepk_sector(city: str, data_path: str):
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
        empl_data_plot = px.bar(df, x=df.index, y='Employment Share', labels={'index': 'Sector'}, text='Employment Share')
        empl_data_plot.update_traces(textposition='outside')
        empl_data_plot.show()
        return empl_data_plot
    def consolidate_industries(df: pd.DataFrame):
        """Returns a dataframe that has the 12 consolidated industries we want"""
        df["Logistics"] = df["Wholesale Trade"] + df["Transportation and Warehousing"] + df["Utilities"]
        df["FIRE"] = df["Finance and Insurance"] + df["Real Estate and Rental and Leasing"]
        df["Professional and Business Services"] = df["Professional, Scientific, and Technical Services"] + df["Management of Companies and Enterprises"] + df["Administrative and Support and Waste Management and Remediation Services"]
        df["Leisure and Hospitality"] = df["Arts, Entertainment, and Recreation"] + df["Accommodation and Food Services"]
        df["Education and Health Services"] = df["Educational Services"] + df["Health Care and Social Assistance"]
        df["Government"] = df["Federal Government"] + df["State Government"] + df["Local Government"]
        df["Mining and Natural Resources"] = df["Mining, Quarrying, and Oil and Gas Extraction"] + df["Agriculture, Forestry, Fishing and Hunting"]
        
        cols_to_select = ["DATE", "City", "Logistics", "Construction", "Manufacturing",
                        "Retail Trade", "Information", "FIRE",
                        "Professional and Business Services", "Leisure and Hospitality",
                        "Education and Health Services", "Government",
                        "Mining and Natural Resources"]
        
        res = df[cols_to_select]
        return res
    empl_data = pd.read_csv(data_path, na_values=["***", ".", "NA"])
    empl_data['DATE'] = empl_data['DATE'].str.pad(width=6, side="left", fillchar="0")
    empl_data['DATE'] = pd.to_datetime(empl_data.DATE, format='%y-%b')
    empl_data = empl_data.fillna(0)
    empl_data = filter_df(city, empl_data)
    empl_data = consolidate_industries(empl_data)
    empl_data['Total Employment'] = empl_data.iloc[:, 2:].sum(axis=1)
    for sector in empl_data.columns[2:]:
        empl_data[sector + ' '] = empl_data[sector]/empl_data['Total Employment']
    empl_share_df = pd.DataFrame()
    empl_share_df.index = empl_data.columns[14:]
    empl_share_df['Employment Share'] = empl_data.iloc[0, 14:]