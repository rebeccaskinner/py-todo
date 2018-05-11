#!/usr/bin/env python

import unittest
import src.todo_server as todo

class TestTodoStatus(unittest.TestCase):
    def test_to_string(self):
        self.assertEqual("todo", todo.TodoStatus.TODO.__str__())
        self.assertEqual("in-progress", todo.TodoStatus.INPROGRESS.__str__())
        self.assertEqual("abandoned", todo.TodoStatus.ABANDON.__str__())
        self.assertEqual("done", todo.TodoStatus.DONE.__str__())
    def test_parse_string(self):
        self.assertEqual(todo.TodoStatus.parse("todo"), todo.TodoStatus.TODO)
        self.assertEqual(todo.TodoStatus.parse("in-progress"), todo.TodoStatus.INPROGRESS)
        self.assertEqual(todo.TodoStatus.parse("abandoned"), todo.TodoStatus.ABANDON)
        self.assertEqual(todo.TodoStatus.parse("done"), todo.TodoStatus.DONE)

class TestTodoItem(unittest.TestCase):
    def test_new_item_sets_summary(self):
        summary1 = "test summary"
        item = todo.TodoItem(summary1)
        self.assertEqual(summary1, item.description())
    def test_set_summary(self):
        summary1 = "test summary 1"
        summary2 = "test summary 2"
        item = todo.TodoItem(summary1)
        item.set_summary(summary2)
        self.assertEqual(summary2, item.description())
    def test_new_item_status_is_todo(self):
        item = todo.TodoItem("summary1")
        self.assertEqual(todo.TodoStatus.TODO, item.status())
    def test_set_status_sets_status(self):
        item = todo.TodoItem("summary1")
        status1 = todo.TodoStatus.ABANDON
        item.set_status(status1)
        self.assertEqual(status1, item.status())
    def test_is_complete(self):
        item = todo.TodoItem("summary1")
        item.set_status(todo.TodoStatus.TODO)
        self.assertFalse(item.is_complete())
        item.set_status(todo.TodoStatus.INPROGRESS)
        self.assertFalse(item.is_complete())
        item.set_status(todo.TodoStatus.ABANDON)
        self.assertFalse(item.is_complete())
        item.set_status(todo.TodoStatus.DONE)
        self.assertTrue(item.is_complete())
    def test_todo_sets_status(self):
        item = todo.TodoItem("summary")
        item.set_status(todo.TodoStatus.DONE)
        item.todo()
        self.assertEqual(todo.TodoStatus.TODO, item.status())
    def test_inprogress_sets_status(self):
        item = todo.TodoItem("summary")
        item.inprogress()
        self.assertEqual(todo.TodoStatus.INPROGRESS, item.status())
    def test_abandon_sets_status(self):
        item = todo.TodoItem("summary")
        item.abandon()
        self.assertEqual(todo.TodoStatus.ABANDON, item.status())
    def test_complete_sets_status(self):
        item = todo.TodoItem("summary")
        item.complete()
        self.assertEqual(todo.TodoStatus.DONE, item.status())

class TestTodoList(unittest.TestCase):
    def test_new_list(self):
        list = todo.List()
        self.assertEqual(0, list.total_count())
    def test_add_item_returns_element_index(self):
        list = todo.List()
        summary = "summary1"
        id = list.add_item(summary)
        self.assertEqual(summary, list.lookup(id).description())
    def test_remove_item_when_item_exists(self):
        list = todo.List()
        idx = list.add_item("summary")
        list.remove_item(idx)
        self.assertEqual(None, list.lookup(idx))
    def test_remove_item_when_item_not_exists(self):
        list = todo.List()
        list.remove_item(999)
    def test_list_size_increases_when_new_item_added(self):
        list = todo.List()
        list.add_item("summary")
        self.assertEqual(1, list.total_count())
    def test_list_todo_item_shows_number_of_todo_items(self):
        list = todo.List()
        list.add_item("summary")
        self.assertEqual(1, list.total_count())
    def test_list_open_items_returns_inprogress_items(self):
        list = todo.List()
        idx = list.add_item("summary")
        list.lookup(idx).inprogress()
        self.assertEqual({idx: list.lookup(idx)}, list.open_items())
        list.lookup(idx).complete()
        self.assertEqual({}, list.open_items())
    def test_list_todo_items_returns_todo_items(self):
        list = todo.List()
        idx = list.add_item("summary")
        self.assertEqual({idx: list.lookup(idx)}, list.todo_items())
        list.lookup(idx).inprogress()
        self.assertEqual({}, list.todo_items())
    def test_items_do_not_collide(self):
        list = todo.List()
        list.add_item("summary")
        self.assertEqual(1, list.total_count())
        list.add_item("summary")
        self.assertEqual(2, list.total_count())
    def test_returns_none_when_missing_element(self):
        list = todo.List()
        self.assertEqual(None, list.lookup(999))

if __name__ == '__main__':
    unittest.main()
