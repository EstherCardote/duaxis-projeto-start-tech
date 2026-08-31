import pandas as pd


def obter_periodo_base(
    dataframe,
    coluna_data
):

    dados = dataframe.copy()

    dados[coluna_data] = pd.to_datetime(
        dados[coluna_data]
    )

    data_minima = (
        dados[coluna_data]
        .min()
        .to_period("M")
    )

    data_maxima = (
        dados[coluna_data]
        .max()
        .to_period("M")
    )

    return {
        "data_minima": data_minima,
        "data_maxima": data_maxima
    }

def resolver_periodo(
    data_minima,
    data_maxima,
    data_inicio=None,
    data_fim=None,
    meses_padrao=3
):

    if data_fim is None:

        periodo_fim = data_maxima

    else:

        periodo_fim = pd.Period(
            data_fim,
            freq="M"
        )


    if data_inicio is None:

        periodo_inicio = (
            periodo_fim
            - (meses_padrao - 1)
        )

    else:

        periodo_inicio = pd.Period(
            data_inicio,
            freq="M"
        )


    if periodo_inicio > periodo_fim:

        raise ValueError(
            "A data inicial não pode ser posterior "
            "à data final."
        )


    if periodo_inicio < data_minima:

        raise ValueError(
            "A data inicial está fora do histórico disponível."
        )


    if periodo_fim > data_maxima:

        raise ValueError(
            "A data final está fora do histórico disponível."
        )


    return {
        "periodo_inicio": periodo_inicio,
        "periodo_fim": periodo_fim
    }

if __name__ == "__main__":

    data_minima = pd.Period(
        "2023-08",
        freq="M"
    )

    data_maxima = pd.Period(
        "2026-07",
        freq="M"
    )

    resultado = resolver_periodo(
        data_minima=data_minima,
        data_maxima=data_maxima,
        data_inicio="2026-01",
        data_fim="2026-03"
    )

    print(resultado)