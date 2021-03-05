"""Ridiculous use of pytest"""
import os
from datetime import date, timedelta
from typing import List, Tuple, Union

import pytest
from pytest import approx
import myfitnesspal

from myfitnesspal.day import Day
from myfitnesspal.meal import Meal


def get_past_days(
        count: int,
        mfp_client: myfitnesspal.Client) -> List[Day]:
    """Get our meals for the past 7 days"""
    days: Day = []
    seven_ago = date.today() - timedelta(days=count)
    for i in range(count):
        current_day = seven_ago + timedelta(days=i)
        days.append(mfp_client.get_date(
            current_day.year,
            current_day.month,
            current_day.day
        ))
    return days


def build_meals(days: Day) -> List[Tuple[Day, Meal]]:
    """Build a List of meals with their day to make parametrize work"""
    meals = []
    for day in days:
        for meal in day.meals:
            meals.append((day, meal, ))
    return meals


CLIENT: myfitnesspal.Client = myfitnesspal.Client(os.getenv('MFP_USERNAME'))
WEEK: List[myfitnesspal.day.Day] = get_past_days(1, CLIENT)
MEALS: List[Tuple[Day, Meal]] = build_meals(WEEK)
TOLERANCES = {
    'carbohydrates': 15,
    'protein': 15,
    'fat': 5,
}

WORKOUT_DAY = {
    'Waking': {
        'carbohydrates': 25.0,
        'fat': 15.0,
        'protein': 36.0,
    },
    'Meal 2': {
        'carbohydrates': 55.0,
        'fat': 15.0,
        'protein': 36.0,
    },
    'Meal 3': {
        'carbohydrates': 70.0,
        'fat': 15.0,
        'protein': 36.0,
    },
    'Workout Meal': {
        'carbohydrates': 15.0,
        'fat': 0.0,
        'protein': 35.0,
    },
    'Meal 5': {
        'carbohydrates': 55.0,
        'fat': 15.0,
        'protein': 36.0,
    },
    'Bedtime': {
        'carbohydrates': 0.0,
        'fat': 15.0,
        'protein': 36.0,
    },
}

REST_DAY = {
    'Waking': {
        'carbohydrates': 30.0,
        'fat': 15.0,
        'protein': 42.0,
    },
    'Meal 2': {
        'carbohydrates': 30.0,
        'fat': 15.0,
        'protein': 42.0,
    },
    'Meal 3': {
        'carbohydrates': 30.0,
        'fat': 15.0,
        'protein': 42.0,
    },
    'Workout Meal': {
        'carbohydrates': 0.0,
        'fat': 0.0,
        'protein': 0.0,
    },
    'Meal 5': {
        'carbohydrates': 30.0,
        'fat': 15.0,
        'protein': 42.0,
    },
    'Bedtime': {
        'carbohydrates': 0.0,
        'fat': 15.0,
        'protein': 42.0,
    },
}


def meal_name(meal: Meal) -> str:
    """Pretty up the meal name"""
    return meal.name.replace('\xa0', ' ').title()


def idfn(val: Union[Day, Meal]) -> str:
    """Figure out how to pretty print these objects without using __str__"""
    if isinstance(val, (Day, )):
        return val.date.strftime('%D')
    if isinstance(val, (Meal, )):
        return f"Meal: {meal_name(val)}"

    return str(val)


@pytest.mark.parametrize("day,meal", MEALS, ids=idfn)
def test_day(day: Day, meal: Meal):
    """Test if a day met the requirements"""
    name = meal_name(meal)
    if day.date.weekday() % 2 == 1:
        goals = REST_DAY[name]
    else:
        goals = WORKOUT_DAY[name]

    for macro in ['carbohydrates', 'fat', 'protein']:
        actual = meal.totals.get(macro, 0)
        expected = goals[macro]
        err_txt = f"meal {name}'s macro ({macro}) was not in range. {expected} vs {actual}"
        assert actual == approx(expected, abs=TOLERANCES[macro]), err_txt
