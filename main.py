import yaml
from scipy import optimize
from itertools import accumulate
import math

from 贸易站 import 贸易站数据


无人机相当于秒基础工时 = 180
每秒基础工时生产作战记录 = 1000 / (3 * 3600)
每秒基础工时生产赤金 = 1 / (72 * 60)
消耗1无人机获得作战记录 = 无人机相当于秒基础工时 * 每秒基础工时生产作战记录
消耗1无人机获得赤金 = 无人机相当于秒基础工时 * 每秒基础工时生产赤金

# 变量 = [
#     运行时长比例[i] for i in range(排班表数量),
#     无人机加速作战记录比例[i] for i in range(排班表数量),
#     无人机加速赤金比例[i] for i in range(排班表数量),
#     无人机加速龙门币比例[i][j] for i in range(排班表数量) for j in range(候选排班表[i]['贸易站数量']),
# ]


def main():
    with open('配置 混合.yaml', 'r', encoding='utf-8') as fp:
        data = yaml.safe_load(fp)

    钱书价值比 = data['钱书价值比']
    龙门币价值 = data['龙门币价值']
    作战记录价值 = 龙门币价值 / 钱书价值比
    信用价值 = data['信用价值']
    公开招募刷新价值 = data['公开招募刷新价值']
    目标钱书比 = data['目标钱书比']
    目标赤金 = data['目标赤金']
    溢出价值折算系数 = data['溢出折算系数']

    候选排班表: list[dict] = []
    排班表数量 = len(data['候选排班表'])
    for 排班表 in data['候选排班表']:
        排班表名称 = 排班表['排班表名称']
        贸易站数量 = len(排班表['贸易站列表'])
        if 贸易站数量 != len(排班表['至少分配无人机用于加速']['龙门币']):
            raise ValueError(f'{排班表名称}的贸易站数量与至少分配无人机用于加速龙门币的贸易站数量不一致')

        贸易站列表: list[贸易站数据] = [
            贸易站数据.new(贸易站['贸易站等级'], 贸易站['但书'], 贸易站['龙舌兰'], 贸易站['裁缝'])
            for 贸易站 in 排班表['贸易站列表']
        ]
        候选排班表.append({
            '排班表名称': 排班表名称,
            '贸易站数量': 贸易站数量,
            '贸易站列表': 贸易站列表,
            '每日产出': 排班表['每日产出'],
            '至少分配无人机用于加速': 排班表['至少分配无人机用于加速'],
        })

    变量个数 = sum(3 + 排班表['贸易站数量'] for 排班表 in 候选排班表)
    无人机加速龙门币比例变量的起始位置 = list(accumulate(
        (候选排班表[i]['贸易站数量'] for i in range(排班表数量)),
        initial=3 * 排班表数量
    ))

    def 运行时长比例下标(排班表序号):
        return 排班表序号

    def 无人机加速作战记录比例下标(排班表序号):
        return 1 * 排班表数量 + 排班表序号

    def 无人机加速赤金比例下标(排班表序号):
        return 2 * 排班表数量 + 排班表序号

    def 无人机加速龙门币比例下标(排班表序号, 贸易站序号):
        return 无人机加速龙门币比例变量的起始位置[排班表序号] + 贸易站序号

    def 运行时长比例(变量, 排班表序号):
        return 变量[运行时长比例下标(排班表序号)]

    def 无人机加速作战记录比例(变量, 排班表序号):
        return 变量[无人机加速作战记录比例下标(排班表序号)]

    def 无人机加速赤金比例(变量, 排班表序号):
        return 变量[无人机加速赤金比例下标(排班表序号)]

    def 无人机加速龙门币比例(变量, 排班表序号, 贸易站序号):
        return 变量[无人机加速龙门币比例下标(排班表序号, 贸易站序号)]

    def 作战记录产出函数(变量, 排班表序号):
        return (
            候选排班表[排班表序号]['每日产出']['作战记录']
            + 候选排班表[排班表序号]['每日产出']['无人机'] * 消耗1无人机获得作战记录 * 无人机加速作战记录比例(变量, 排班表序号)
        )

    def 作战记录综合产出函数(变量):
        return sum(
            作战记录产出函数(变量, 排班表序号) * 运行时长比例(变量, 排班表序号)
            for 排班表序号 in range(排班表数量)
        )

    def 赤金产出函数(变量, 排班表序号):
        return (
            候选排班表[排班表序号]['每日产出']['赤金']
            + 候选排班表[排班表序号]['每日产出']['无人机'] * 消耗1无人机获得赤金 * 无人机加速赤金比例(变量, 排班表序号)
            - sum(
                候选排班表[排班表序号]['每日产出']['无人机']
                * 贸易站.每秒基础工时消耗赤金 * 无人机相当于秒基础工时
                * 无人机加速龙门币比例(变量, 排班表序号, 贸易站序号)
                for 贸易站序号, 贸易站 in enumerate(候选排班表[排班表序号]['贸易站列表'])
            )
        )

    def 赤金综合产出函数(变量):
        return sum(
            赤金产出函数(变量, 排班表序号) * 运行时长比例(变量, 排班表序号)
            for 排班表序号 in range(排班表数量)
        )

    def 龙门币产出函数(变量, 排班表序号):
        return (
            候选排班表[排班表序号]['每日产出']['龙门币']
            + sum(
                候选排班表[排班表序号]['每日产出']['无人机']
                * 贸易站.每秒基础工时获得龙门币 * 无人机相当于秒基础工时
                * 无人机加速龙门币比例(变量, 排班表序号, 贸易站序号)
                for 贸易站序号, 贸易站 in enumerate(候选排班表[排班表序号]['贸易站列表'])
            )
        )

    def 龙门币综合产出函数(变量):
        return sum(
            龙门币产出函数(变量, 排班表序号) * 运行时长比例(变量, 排班表序号)
            for 排班表序号 in range(排班表数量)
        )

    def 信用综合产出函数(变量):
        return sum(
            排班表['每日产出']['信用'] * 运行时长比例(变量, 排班表序号)
            for 排班表序号, 排班表 in enumerate(候选排班表)
        )

    def 公开招募刷新综合产出函数(变量):
        return sum(
            排班表['每日产出']['公开招募刷新'] * 运行时长比例(变量, 排班表序号)
            for 排班表序号, 排班表 in enumerate(候选排班表)
        )

    def 基建综合产出(变量):
        作战记录综合产出 = 作战记录综合产出函数(变量)
        龙门币综合产出 = 龙门币综合产出函数(变量)
        信用综合产出 = 信用综合产出函数(变量)
        公开招募刷新综合产出 = 公开招募刷新综合产出函数(变量)

        符合钱书比的部分_以作战记录计 = min(作战记录综合产出, 龙门币综合产出 / 目标钱书比)
        溢出的作战记录 = 作战记录综合产出 - 符合钱书比的部分_以作战记录计
        溢出的龙门币 = 龙门币综合产出 - 符合钱书比的部分_以作战记录计 * 目标钱书比
        return (
            符合钱书比的部分_以作战记录计 * 作战记录价值
            + 符合钱书比的部分_以作战记录计 * 目标钱书比 * 龙门币价值
            + (溢出的作战记录 * 作战记录价值 + 溢出的龙门币 * 龙门币价值) * 溢出价值折算系数
            + 信用综合产出 * 信用价值
            + 公开招募刷新综合产出 * 公开招募刷新价值
        )

    def 目标函数(变量):
        return -基建综合产出(变量)

    变量初值 = [0.0] * 变量个数
    产赤金最多的排班表序号 = max(range(排班表数量), key=lambda i: 候选排班表[i]['每日产出']['赤金'])
    变量初值[运行时长比例下标(产赤金最多的排班表序号)] = 1
    for 排班表序号, 排班表 in enumerate(候选排班表):
        变量初值[无人机加速赤金比例下标(排班表序号)] = 1  # 先假设全力造赤金，因为这样更易于满足赤金平衡的约束条件

    变量范围 = [(0, 1)] * 变量个数
    for 排班表序号, 排班表 in enumerate(候选排班表):
        变量范围[运行时长比例下标(排班表序号)] = (0, 1)
        变量范围[无人机加速作战记录比例下标(排班表序号)] = (排班表['至少分配无人机用于加速']['作战记录'] / 排班表['每日产出']['无人机'], 1)
        变量范围[无人机加速赤金比例下标(排班表序号)] = (排班表['至少分配无人机用于加速']['赤金'] / 排班表['每日产出']['无人机'], 1)
        for 贸易站序号 in range(排班表['贸易站数量']):
            变量范围[无人机加速龙门币比例下标(排班表序号, 贸易站序号)] = (
                排班表['至少分配无人机用于加速']['龙门币'][贸易站序号] / 排班表['每日产出']['无人机'],
                1
            )

    约束条件 = []
    约束条件.append(optimize.NonlinearConstraint(赤金综合产出函数, lb=目标赤金, ub=math.inf))
    运行时长约束向量 = [0] * 变量个数
    for 排班表序号 in range(排班表数量):
        运行时长约束向量[运行时长比例下标(排班表序号)] = 1
    约束条件.append(optimize.LinearConstraint(运行时长约束向量, 1, 1))
    for 排班表序号, 排班表 in enumerate(候选排班表):
        无人机分配约束向量 = [0] * 变量个数
        无人机分配约束向量[无人机加速作战记录比例下标(排班表序号)] = 1
        无人机分配约束向量[无人机加速赤金比例下标(排班表序号)] = 1
        for 贸易站序号 in range(排班表['贸易站数量']):
            无人机分配约束向量[无人机加速龙门币比例下标(排班表序号, 贸易站序号)] = 1
        约束条件.append(optimize.LinearConstraint(无人机分配约束向量, 1, 1))

    result: optimize.OptimizeResult = optimize.minimize(目标函数, 变量初值, bounds=变量范围, constraints=约束条件)
    assert result.success
    结果 = result.x

    print(f'基建综合产出：{基建综合产出(结果):.4f}')
    print(f'作战记录综合产出：{作战记录综合产出函数(结果):.4f}')
    print(f'赤金综合产出：{赤金综合产出函数(结果):.4f}')
    print(f'龙门币综合产出：{龙门币综合产出函数(结果):.4f}')
    print(f'信用综合产出：{信用综合产出函数(结果):.4f}')
    print(f'公开招募刷新综合产出：{公开招募刷新综合产出函数(结果):.4f}')
    for 排班表序号, 排班表 in enumerate(候选排班表):
        print()
        print(f'=====  {排班表['排班表名称']}  =====')
        print(f'运行时长比例：{运行时长比例(结果, 排班表序号):.2%}')
        print(f'无人机加速作战记录比例：{无人机加速作战记录比例(结果, 排班表序号):.2%}')
        print(f'无人机加速赤金比例：{无人机加速赤金比例(结果, 排班表序号):.2%}')
        print('无人机加速龙门币比例：')
        for 贸易站序号 in range(排班表['贸易站数量']):
            print(f'    贸易站 {贸易站序号}：{无人机加速龙门币比例(结果, 排班表序号, 贸易站序号):.2%}')

        print(f'每日产出作战记录：{作战记录产出函数(结果, 排班表序号):.4f}')
        print(f'每日产出赤金：{赤金产出函数(结果, 排班表序号):.4f}')
        print(f'每日产出龙门币：{龙门币产出函数(结果, 排班表序号):.4f}')
        # print(f'每日产出信用：{排班表['每日产出']['信用']:.4f}')
        # print(f'每日产出公开招募刷新：{排班表['每日产出']['公开招募刷新']:.4f}')


if __name__ == '__main__':
    main()
