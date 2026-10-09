"""year8Char='beginningOfSpring' 年柱换年回归测试。

2026-10-09 修复 getBeginningOfSpringX：旧逻辑用 nextSolarNum < 3
判"立春前"，冬至后（12-21 起）下个节气为小寒（索引 0）被误判，
_x=1 误减一年（如 2020-12-25 公认庚子年却给出己亥）。
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cnlunar.lunar import Lunar


def _y8(dt):
    return Lunar(dt, year8Char='beginningOfSpring').year8Char


def test_spring_festival_before_lichun():
    # 2020：春节 01-25，立春 02-04
    assert _y8(datetime(2020, 1, 10, 12)) == '己亥'   # 双未过
    assert _y8(datetime(2020, 1, 30, 12)) == '己亥'   # 春节过、立春未过
    assert _y8(datetime(2020, 2, 4, 12)) == '庚子'    # 立春当天（天精度整天算新）
    assert _y8(datetime(2020, 6, 1, 12)) == '庚子'


def test_lichun_before_spring_festival():
    # 2021：立春 02-03，春节 02-12
    assert _y8(datetime(2021, 1, 10, 12)) == '庚子'   # 双未过
    assert _y8(datetime(2021, 2, 5, 12)) == '辛丑'    # 立春过、春节未过
    assert _y8(datetime(2021, 3, 1, 12)) == '辛丑'    # 双已过


def test_december_window_regression():
    # 冬至→小寒窗口：旧 bug 在此误减一年
    for d in [21, 25, 31]:
        assert _y8(datetime(2020, 12, d, 12)) == '庚子', f'2020-12-{d}'
    assert _y8(datetime(2024, 12, 25, 12)) == '甲辰'
    assert _y8(datetime(2025, 12, 31, 12)) == '乙巳'


def test_default_mode_unaffected():
    # 默认 'year' 模式（春节换年）不受本次修复影响
    assert Lunar(datetime(2020, 1, 30, 12)).year8Char == '庚子'
    assert Lunar(datetime(2020, 1, 10, 12)).year8Char == '己亥'


def test_full_sweep_against_lichun_rule():
    """2020-2030 逐日：与"立春为界"独立规则全量比对。"""
    from cnlunar.config import the60HeavenlyEarth
    bad, total = [], 0
    d = datetime(2020, 1, 1, 12)
    end = datetime(2030, 12, 31, 12)
    while d <= end:
        a = Lunar(d, year8Char='beginningOfSpring')
        lichun_md = a.thisYearSolarTermsDateList[2]  # 立春 (月, 日)，天精度
        y = d.year if (d.month, d.day) >= lichun_md else d.year - 1
        expected = the60HeavenlyEarth[(y - 4) % 60]
        total += 1
        if a.year8Char != expected:
            bad.append((d.strftime('%Y-%m-%d'), a.year8Char, expected))
        d += timedelta(days=1)
    assert total == 4018, f"样本数异常: {total}"
    assert not bad, f"分歧 {len(bad)} 例: {bad[:10]}"


if __name__ == '__main__':
    raise SystemExit(pytest.main([__file__, '-v']))

