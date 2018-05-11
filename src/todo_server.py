#!/usr/bin/env python

from enum import Enum
from flask import Flask
from flask import request
import sys
import json

class TodoStatus(Enum):
    TODO = 0
    INPROGRESS = 1
    ABANDON = 2
    DONE = 3
    def __str__(self):
        if self == TodoStatus.TODO:
            return "todo"
        elif self == TodoStatus.INPROGRESS:
            return "in-progress"
        elif self == TodoStatus.ABANDON:
            return "abandoned"
        elif self == TodoStatus.DONE:
            return "done"
        else:
            print("enumeration invariant failed: value out of range")
            sys.exit()
    def parse(str):
        if str == "todo":
            return  TodoStatus.TODO
        elif str == "in-progress":
            return  TodoStatus.INPROGRESS
        elif str == "abandoned":
            return  TodoStatus.ABANDON
        elif str == "done":
            return  TodoStatus.DONE
        else:
            return None

class TodoItem:
    def __init__(self, summary):
        self._summary = summary
        self._status = TodoStatus.TODO
    def status(self):
        return self._status
    def is_complete(self):
        return self._status == TodoStatus.DONE
    def set_status(self, status):
        self._status = status
    def description(self):
        return self._summary
    def todo(self):
        self._status = TodoStatus.TODO
    def inprogress(self):
        self._status = TodoStatus.INPROGRESS
    def abandon(self):
        self._status = TodoStatus.ABANDON
    def complete(self):
        self._status = TodoStatus.DONE
    def __str__(self):
        return "{}: {}".format(self._status, self._summary)
    def json_dict(self):
        return {"summary": self._summary, "status": self._status.__str__()}

class List:
    def __init__(self):
        self._list = {}
        self._idx = 0
    def total_count(self):
        return len(self._list)
    def add_item(self, summary):
        idx = self._idx
        self._list[idx] = TodoItem(summary)
        self._idx = self._idx + 1
        return idx
    def lookup(self, idx):
        return self._list[idx]
    def items_by_state(self, state):
        found = {}
        for key, item in self._list.items():
            if item.status() == state:
                found[key] = item
        return found
    def open_items(self):
        return self.items_by_state(TodoStatus.INPROGRESS)
    def todo_items(self):
        return self.items_by_state(TodoStatus.TODO)
    def abandoned_items(self):
        return self.items_by_state(TodoStatus.ABANDON)
    def complete_items(self):
        return self.items_by_state(TodoStatus.DONE)
    def items(self):
        return self._list.values()
    def json_dict(self):
        items = {}
        for k, v in self._list.items():
            items[k] = v.json_dict()
        return items

app = Flask(__name__)

list = List()

@app.route('/')
def home():
    return "Not much to see here!  See '/api' for API documentation"

@app.route('/api')
def help():
    with open("api.json") as f:
        contents = f.read()
    return (contents, {"Content-Type": "application/json"})

@app.route("/items")
def items():
    return (json.dumps(list.json_dict()), {"Content-Type": "application/json"})

@app.route("/open")
def open_items():
    return (json.dumps(list.open_items()), {"Content-Type": "application/json"})

@app.route("/complete")
def complete_items():
    return (json.dumps(list.complete_items()), {"Content-Type": "application/json"})

@app.route("/abandoned")
def abandoned_items():
    return (json.dumps(list.abandoned_items()), {"Content-Type": "application/json"})

@app.route("/pending")
def pending_items():
    return (json.dumps(list.todo_items()), {"Content-Type": "application/json"})

@app.route("/add", methods=['POST'])
def add():
    data = request.get_json(force = True)
    f = lambda x: x
    if "summary" not in data:
        return ("missing summary field", 400, {})
    if "status" in data:
        status = TodoStatus.parse(data["status"])
        if status is None:
            return ("invalid status", 400, {})
        f = lambda x: x.set_status(status)

    idx = list.add_item(data["summary"])
    f(list.lookup(idx))
    return ("{}".format(idx), {"Content-Type": "application/plaintext"})
