from __future__ import annotations

import unittest

from game.core.items import *


class DebugItem(Item):
    sprite = None

    def __init__(self: Item, **data: Any) -> None:
        default_data = {"location": None}

        super().__init__(**data, **default_data)


class ItemTestCase(unittest.TestCase):
    def test_abstract_properties(self: ItemTestCase):
        class UndefinedPropertiesItem(DebugItem):  # Lacks weight property
            pass

        with self.assertRaises(TypeError):
            instance = UndefinedPropertiesItem()

    def test_total_weight(self: ItemTestCase):
        class StackableTest(StackableItem, DebugItem):
            unit_weight = 10.0
            max_stack_amount = 10

        stackable_item = StackableTest(stack_amount=5)

        class UnstackableTest(DebugItem):
            weight = 20.0

        unstackable_item = UnstackableTest()

        self.assertEqual(stackable_item.unit_weight, 10.0)
        self.assertEqual(stackable_item.weight, 50.0)
        self.assertEqual(unstackable_item.weight, 20.0)
