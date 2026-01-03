# test_goal_system.py
from src.cortex.goal_system import GoalSystem


def test_goal_init():
    gs = GoalSystem()
    assert len(gs.active_goals) == 2  # base goals


def test_emerge_goal_hunger():
    gs = GoalSystem()
    state = {"glucose": 20.0}  # 空腹
    goal = gs.emerge_goal(state)
    assert goal is not None
    assert goal.name == "seek_food"


def test_get_highest_priority():
    gs = GoalSystem()
    goal = gs.get_highest_priority_goal()
    assert goal is not None
