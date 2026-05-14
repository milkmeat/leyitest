import pytest
from src.utils.counter import (
    soldier_category, dominant_category, pick_counter_soldier,
    CATEGORY_BASHER, CATEGORY_SHOOTER, CATEGORY_PIERCER,
)
from src.models.player_state import Soldier


class TestSoldierCategory:
    def test_basher(self):
        assert soldier_category(4) == CATEGORY_BASHER
        assert soldier_category(1) == CATEGORY_BASHER

    def test_shooter(self):
        assert soldier_category(104) == CATEGORY_SHOOTER
        assert soldier_category(101) == CATEGORY_SHOOTER

    def test_piercer(self):
        assert soldier_category(204) == CATEGORY_PIERCER
        assert soldier_category(201) == CATEGORY_PIERCER


class TestDominantCategory:
    def test_pure_basher(self):
        assert dominant_category({4: 100000}) == CATEGORY_BASHER

    def test_pure_shooter(self):
        assert dominant_category({104: 100000}) == CATEGORY_SHOOTER

    def test_pure_piercer(self):
        assert dominant_category({204: 100000}) == CATEGORY_PIERCER

    def test_mixed_basher_dominant(self):
        assert dominant_category({4: 100, 104: 50, 204: 30}) == CATEGORY_BASHER

    def test_tie_shooter_priority(self):
        assert dominant_category({4: 100, 104: 100, 204: 100}) == CATEGORY_SHOOTER

    def test_tie_two_way_basher_vs_shooter(self):
        assert dominant_category({4: 100, 104: 100}) == CATEGORY_SHOOTER

    def test_empty_returns_shooter(self):
        assert dominant_category({}) == CATEGORY_SHOOTER

    def test_near_tie_within_5pct_uses_tiebreak(self):
        # 100 vs 96: diff=4, 5% of 196=9.8 → within threshold → tie → Shooter wins
        assert dominant_category({4: 100, 104: 96}) == CATEGORY_SHOOTER

    def test_clear_dominant_beyond_5pct(self):
        # 100 vs 80: diff=20, 5% of 180=9 → 80 < 100-9=91 → Basher clearly dominant
        assert dominant_category({4: 100, 104: 80}) == CATEGORY_BASHER

    def test_uniform_rounding_no_false_dominant(self):
        # 模拟 281000/3 的舍入场景：93666, 93666, 93668
        assert dominant_category({4: 93666, 104: 93666, 204: 93668}) == CATEGORY_SHOOTER


class TestPickCounterSoldier:
    def _soldiers(self, mapping: dict[int, int]) -> list[Soldier]:
        return [Soldier(id=sid, value=cnt) for sid, cnt in mapping.items()]

    def test_counter_basher_with_shooter(self):
        sid, cnt = pick_counter_soldier({4: 93667}, self._soldiers({104: 500000}))
        assert sid == 104
        assert cnt == 500000

    def test_counter_shooter_with_piercer(self):
        sid, cnt = pick_counter_soldier({104: 93666}, self._soldiers({204: 500000}))
        assert sid == 204

    def test_counter_piercer_with_basher(self):
        sid, cnt = pick_counter_soldier({204: 93667}, self._soldiers({4: 500000}))
        assert sid == 4

    def test_attacker_missing_category_returns_zero(self):
        sid, cnt = pick_counter_soldier({4: 93667}, self._soldiers({204: 500000}))
        assert sid == 0 and cnt == 0

    def test_picks_highest_value_in_category(self):
        sid, cnt = pick_counter_soldier(
            {4: 93667},
            self._soldiers({101: 500, 104: 10000, 105: 20000}),
        )
        assert sid == 105  # Shooter category, highest value
        assert cnt == 20000

    def test_mixed_defender_picks_counter_of_dominant(self):
        # defender: 100k Basher + 50k Piercer → dominant=Basher → counter=Shooter
        sid, cnt = pick_counter_soldier(
            {4: 100000, 204: 50000},
            self._soldiers({104: 300000, 4: 300000}),
        )
        assert sid == 104

    def test_empty_defender_returns_zero(self):
        sid, cnt = pick_counter_soldier({}, self._soldiers({104: 500000}))
        assert sid == 0 and cnt == 0

    def test_empty_attacker_returns_zero(self):
        sid, cnt = pick_counter_soldier({4: 100000}, [])
        assert sid == 0 and cnt == 0
