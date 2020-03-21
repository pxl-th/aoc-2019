from collections import defaultdict
from math import ceil
from functools import reduce
from lark import Lark, Transformer


class Reaction(Transformer):
    def amount(self, items):
        return [items[1].value, int(items[0].value)]

    def reaction(self, items):
        chem, amount = items[1]
        return {chem: {"amount": amount, "recipe": dict(items[0].children)}}

    def start(self, items: list) -> dict:
        return reduce(lambda x, y: {**x, **y}, items)


def produce(
    recipes: dict, produced: dict, wasted: dict, chemical: str, amount: int,
):
    info = recipes[chemical]
    if amount <= wasted[chemical]:
        wasted[chemical] -= amount
        return

    bulk_amount = info["amount"]
    amount -= wasted[chemical]
    scale = int(ceil(amount / bulk_amount))
    wasted[chemical] = scale * bulk_amount - amount

    for sub_chemical, sub_amount in info["recipe"].items():
        sub_produced = sub_amount * scale
        if sub_chemical == "ORE":
            produced["ORE"] += sub_produced
            continue
        produce(recipes, produced, wasted, sub_chemical, sub_produced)


def main():
    grammar = r"""
    start: reaction+

    reaction: requirements " => " amount
    requirements: amount (", " amount)*
    amount: NUMBER " " CHEMICAL

    CHEMICAL: LETTER+

    %import common.LETTER
    %import common.INT -> NUMBER
    %import common.WS
    %ignore WS
    """
    reactions = """
1 GZJM, 2 CQFGM, 20 SNPQ, 7 RVQG, 3 FBTV, 27 SQLH, 10 HFGCF, 3 ZQCH => 3 SZCN
4 FCDL, 6 NVPW, 21 GZJM, 1 FBTV, 1 NLSNB, 7 HFGCF, 3 SNPQ => 1 LRPK
15 FVHTD, 2 HBGFL => 4 BCVLZ
4 GFGS => 4 RVQG
5 BCVLZ, 4 LBQV => 7 TWSRV
6 DWKTF, 4 VCKL => 4 KDJV
16 WZJB => 4 RBGJQ
8 RBGJQ, 5 FCDL, 2 LWBQ => 1 MWSX
100 ORE => 7 WBRL
7 PGZGQ => 5 FVHTD
1 JCDML, 2 TWSRV => 9 JSQSB
3 WZJB, 1 NXNR => 6 XFPVS
7 JPCPK => 8 JCDML
11 LWBQ, 8 XFPVS => 9 PSPFR
2 TWSRV => 8 NVPW
2 LBQV => 1 PMJFD
2 LCZBD => 3 FBTV
1 WBQC, 1 ZPNKQ => 8 JPCPK
44 HFGCF, 41 PSPFR, 26 LMSCR, 14 MLMDC, 6 BWTHK, 3 PRKPC, 13 LRPK, 50 MWSX, 8 SZCN => 1 FUEL
1 XFPVS => 4 BJRSZ
1 GWBDR, 1 MBQC => 4 HZPRB
2 BJRSZ, 9 KDJV, 1 XFPVS => 8 SNVL
7 PMJFD, 30 SNVL, 1 BJRSZ => 2 JMTG
8 SNVL, 1 RBGJQ => 9 FCDL
2 HZPRB => 6 NLSNB
2 GRDG => 9 VCKL
1 FVHTD => 9 WZJB
130 ORE => 2 GRDG
3 WZJB, 1 GFGS, 1 NXNR => 9 SNPQ
9 VCKL => 5 WBQC
1 WBRL, 11 FPMPB => 7 PGZGQ
118 ORE => 3 LMSCR
3 SQLH, 1 PMJFD, 4 XJBL => 7 MLMDC
1 LMSCR, 10 GRDG => 2 TBDH
6 DWKTF => 2 SQLH
2 BJRSZ, 1 PGZGQ, 3 NXNR => 7 MBQC
5 PRKPC => 7 NXNR
9 SQLH => 5 LCZBD
1 FCDL => 9 CQFGM
5 PGZGQ, 1 TBDH => 8 HBGFL
15 JSQSB => 5 HFGCF
2 PGZGQ, 1 VCKL => 4 ZPNKQ
3 FBTV, 3 JMTG => 5 QLHKT
1 ZGZST, 2 LCZBD => 7 GFGS
2 RVQG => 4 ZQCH
1 ZPNKQ => 5 LBQV
3 LWBQ => 8 XJBL
1 LBQV, 9 JCDML => 3 GWBDR
8 VCKL, 6 FVHTD => 9 DWKTF
3 JCDML => 3 ZGZST
160 ORE => 5 FPMPB
3 SQLH, 22 LBQV, 5 BCVLZ => 6 PRKPC
1 WZJB => 2 GZJM
10 ZGZST => 2 LWBQ
5 TBDH, 19 NXNR, 9 QLHKT, 2 KDJV, 1 SQLH, 1 GWBDR, 6 HFGCF => 4 BWTHK
    """

    tree = Lark(grammar).parse(reactions)
    recipes: dict = Reaction().transform(tree)

    produced = defaultdict(lambda: 0)
    wasted = defaultdict(lambda: 0)
    produce(recipes, produced, wasted, "FUEL", 1)
    print(produced)


if __name__ == "__main__":
    main()
