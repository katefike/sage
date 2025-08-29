TEST_CASES = [
    (
        (dict(uid="3", email_id=1)),
        (
            dict(
                date="2022-10-06",
                type_="transfer withdrawal",
                bank="Huntington",
                merchant=None,
                payer=None,
                amount="999.51",
                account="CHECK",
                balance="1693.13",
            )
        ),
    ),
    (
        (dict(uid="14", email_id=2)),
        (
            dict(
                date="2022-10-06",
                type_="transfer deposit",
                bank="Huntington",
                merchant=None,
                payer=None,
                amount="999.51",
                account="SAVE",
                balance="20000.00",
            )
        ),
    ),
    (
        (dict(uid="5", email_id=3)),
        (
            dict(
                date="2022-09-13",
                type_="withdrawal",
                bank="Huntington",
                merchant="VENMO PAYMENT",
                payer=None,
                amount="200.00",
                account="CHECK",
                balance="14.80",
            )
        ),
    ),
    (
        (dict(uid="7", email_id=4)),
        (
            dict(
                date="2022-08-08",
                type_="withdrawal",
                bank="Huntington",
                merchant="TREASURY DIRECT TREAS DRCT",
                payer=None,
                amount="10000.00",
                account="SAVE",
                balance="14000.00",
            )
        ),
    ),
    (
        (dict(uid="9", email_id=5)),
        (
            dict(
                date="2022-10-06",
                type_="withdrawal",
                bank="Chase",
                merchant="EB *TRAUMA 2022",
                payer=None,
                amount="113.11",
                account=None,
                balance=None,
            )
        ),
    ),
    (
        (dict(uid="11", email_id=6)),
        (
            dict(
                date="2022-08-24",
                type_="transfer withdrawal",
                bank="Huntington",
                merchant=None,
                payer=None,
                amount="500.00",
                account="SAVE",
                balance="16000.00",
            )
        ),
    ),
    (
        (dict(uid="17", email_id=7)),
        (
            dict(
                date="2022-10-05",
                type_="withdrawal",
                bank="Discover",
                merchant="BOMBAY SITAR",
                payer=None,
                amount="20.18",
                account="student",
                balance=None,
            )
        ),
    ),
    (
        (dict(uid="19", email_id=8)),
        (
            dict(
                date="2022-08-24",
                type_="transfer deposit",
                bank="Huntington",
                merchant=None,
                payer=None,
                amount="500.00",
                account="CHECK",
                balance="757.06",
            )
        ),
    ),
    (
        (dict(uid="21", email_id=9)),
        (
            dict(
                date="2022-08-24",
                type_="deposit",
                bank="Huntington",
                merchant=None,
                payer="CHASE CREDIT CRD RWRD RDM",
                amount="17.09",
                account="CHECK",
                balance="257.06",
            )
        ),
    ),
    (
        (dict(uid="25", email_id=10)),
        (
            dict(
                date="2024-05-13",
                type_="withdrawal",
                bank="Huntington",
                merchant="VENMO PAYMENT",
                payer=None,
                amount="50.00",
                account="CHECK",
                balance="866.27",
            )
        ),
    ),
    (
        (dict(uid="26", email_id=11)),
        (
            dict(
                date="2024-05-18",
                type_="withdrawal",
                bank="Chase",
                merchant="CONVENTION CTR GARAG",
                payer=None,
                amount="15.00",
                account=None,
                balance=None,
            )
        ),
    ),
    (
        (dict(uid="27", email_id=11)),
        (
            dict(
                date="2024-05-21",
                type_="withdrawal",
                bank="Chase",
                merchant="CONVENTION CTR GARAG",
                payer=None,
                amount="15.00",
                account=None,
                balance=None,
            )
        ),
    ),
    (
        (dict(uid="28", email_id=12)),
        (
            dict(
                date="2024-04-16",
                type_="deposit",
                bank="Huntington",
                merchant=None,
                payer="cash",
                amount="1500.00",
                account="CHECK",
                balance="798.08",
            )
        ),
    ),
    (
        (dict(uid="29", email_id=13)),
        (
            dict(
                date="2024-04-29",
                type_="withdrawal",
                bank="Chase",
                merchant="SAVE A LOT #24664",
                payer=None,
                amount="12.97",
                account=None,
                balance=None,
            )
        ),
    ),
    (
        (dict(uid="30", email_id=14)),
        dict(
            date="2024-04-16",
            type_="withdrawal",
            bank="Huntington",
            merchant="R.I.T.A. RITA EFILE",
            payer=None,
            amount="100.00",
            account="CHECK",
            balance="-10.92",
        ),
    ),
    (
        (dict(uid="31", email_id=11)),
        (
            dict(
                date="2024-04-24",
                type_="withdrawal",
                bank="Chase",
                merchant="AMZN Mktp US",
                payer=None,
                amount="253.36",
                account=None,
                balance=None,
            )
        ),
    ),
    (
        (dict(uid="32", email_id=12)),
        (
            dict(
                date="2024-04-16",
                type_="deposit",
                bank="Huntington",
                merchant=None,
                payer="cash",
                amount="1500.00",
                account="CHECK",
                balance="798.08",
            )
        ),
    ),
    (
        (dict(uid="33", email_id=13)),
        (
            dict(
                date="2024-04-29",
                type_="withdrawal",
                bank="Chase",
                merchant="SAVE A LOT #24664",
                payer=None,
                amount="12.97",
                account=None,
                balance=None,
            )
        ),
    ),
    (
        (dict(uid="34", email_id=14)),
        (
            dict(
                date="2024-05-14",
                type_="deposit",
                bank="Huntington",
                merchant=None,
                payer="ABC DE LLC ERECT DEP",
                amount="3546.71",
                account="CHECK",
                balance="4394.84",
            )
        ),
    ),
    (
        (dict(uid="35", email_id=15)),
        (
            dict(
                date="2024-04-03",
                type_="deposit",
                bank="Chase",
                merchant=None,
                payer="RAPPI* VERIF $1.63 U",
                amount="1.63",
                account=None,
                balance=None,
            )
        ),
    ),
    (
        (dict(uid="36", email_id=16)),
        (
            dict(
                date="2024-04-29",
                type_="withdrawal",
                bank="Huntington",
                merchant="CASH APP*DEB WALKO",
                payer=None,
                amount="1500.00",
                account="CHECK",
                balance="2682.40",
            )
        ),
    ),
]
