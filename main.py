import pandas as pd

def traiter_fichier(fichier_excel):
    df = pd.read_excel(fichier_excel)
    for index, row in df.iterrows():
        print(f"Libellé : {row['Libellé']}")

if __name__ == "__main__":
    traiter_fichier("transactions.xlsx")
