from typing import NamedTuple, Self
from fractions import Fraction


class 订单详情(NamedTuple):
    概率: Fraction
    需要秒基础工时: int
    消耗赤金: int
    获得龙门币: int


class 贸易站数据:
    def __init__(self, 订单列表: list[订单详情]) -> None:
        self.订单列表: list[订单详情] = 订单列表

    @property
    def 每秒基础工时获得龙门币(self) -> Fraction:
        return (sum(订单.概率 * 订单.获得龙门币 for 订单 in self.订单列表)
                / sum(订单.概率 * 订单.需要秒基础工时 for 订单 in self.订单列表))  # type: ignore

    @property
    def 每天基础工时获得龙门币(self) -> Fraction:
        return self.每秒基础工时获得龙门币 * 86400

    @property
    def 每秒基础工时消耗赤金(self) -> Fraction:
        return sum(订单.概率 * 订单.消耗赤金 for 订单 in self.订单列表) / sum(订单.概率 * 订单.需要秒基础工时 for 订单 in self.订单列表)  # type: ignore

    @property
    def 每天基础工时消耗赤金(self) -> Fraction:
        return self.每秒基础工时消耗赤金 * 86400

    @property
    def 平均每赤金获得龙门币(self) -> Fraction:
        return self.每秒基础工时获得龙门币 / self.每秒基础工时消耗赤金

    @property
    def 每秒基础工时节省赤金(self) -> Fraction:
        return self.每秒基础工时获得龙门币 / 500 - self.每秒基础工时消耗赤金

    @property
    def 每天基础工时节省赤金(self) -> Fraction:
        return self.每秒基础工时节省赤金 * 86400

    @property
    def 每秒基础工时印钱(self) -> Fraction:
        return self.每秒基础工时获得龙门币 - self.每秒基础工时消耗赤金 * 500

    @property
    def 每天基础工时印钱(self) -> Fraction:
        return self.每秒基础工时印钱 * 86400

    @property
    def 生产1龙门币需要的秒基础工时(self) -> Fraction:
        return 1 / self.每秒基础工时获得龙门币 + 4320 / self.平均每赤金获得龙门币

    @property
    def 钱书基础工时成本比(self) -> Fraction:
        return self.生产1龙门币需要的秒基础工时 / Fraction(54, 5)

    @classmethod
    def new(cls, 贸易站等级: int, 但书: int | None, 龙舌兰: int | None, 裁缝: str | None) -> Self:
        需要秒基础工时列表: list[int] = [8640, 12600, 16560]
        if 贸易站等级 == 1:
            订单概率列表: list[Fraction] = [Fraction(100, 100)]
        elif 贸易站等级 == 2:
            订单概率列表 = [Fraction(60, 100), Fraction(40, 100)]
        elif 贸易站等级 == 3:
            if 裁缝 is None:
                订单概率列表 = [Fraction(30, 100), Fraction(50, 100), Fraction(20, 100)]
            elif 裁缝 in ('α', 'alpha'):
                订单概率列表 = [Fraction(15, 100), Fraction(30, 100), Fraction(55, 100)]
            elif 裁缝 in ('β', 'beta'):
                订单概率列表 = [Fraction(5, 100), Fraction(10, 100), Fraction(85, 100)]
            else:
                raise ValueError
        else:
            raise ValueError
        获得龙门币列表: list[int] = [1000, 1500, 2000]
        消耗赤金列表: list[int] = [2, 3, 4]
        if 但书 is None:
            pass
        elif 但书 in (0, 1):
            获得龙门币列表[0] += 500
            获得龙门币列表[1] += 500
            消耗赤金列表[0] += 1
            消耗赤金列表[1] += 1
        elif 但书 == 2:
            获得龙门币列表[0] += 1000
            获得龙门币列表[1] += 1000
            消耗赤金列表[0] += 2
            消耗赤金列表[1] += 2
        else:
            raise ValueError
        if 龙舌兰 is None:
            pass
        elif 龙舌兰 in (0, 1):
            获得龙门币列表[2] += 250
        elif 龙舌兰 == 2:
            获得龙门币列表[2] += 500
        else:
            raise ValueError
        订单列表: list[订单详情] = []
        for 概率, 需要秒基础工时, 消耗赤金, 获得龙门币 in zip(订单概率列表, 需要秒基础工时列表, 消耗赤金列表, 获得龙门币列表):
            订单列表.append(订单详情(概率, 需要秒基础工时, 消耗赤金, 获得龙门币))
        return cls(订单列表)
