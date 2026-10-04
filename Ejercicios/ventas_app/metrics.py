import pandas as pd


def importe_por_region(validos: pd.DataFrame) -> pd.DataFrame:
    return (
        validos.groupby("region", as_index=False)["importe"].sum().sort_values("importe", ascending=False)
    )


def top_productos(validos: pd.DataFrame) -> pd.DataFrame:
    return (
        validos.groupby("producto", as_index=False)["importe"].sum().sort_values("importe", ascending=False).head(3)
    )


def clientes_recurrentes(validos: pd.DataFrame) -> pd.Series:
    compras_por_cliente = validos["cliente_id"].value_counts()

    return compras_por_cliente[compras_por_cliente > 1]