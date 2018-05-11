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
    def set_summary(self, summary):
        self._summary = summary
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
    def remove_item(self, idx):
        if idx in self._list:
            del self._list[idx]
    def add_item(self, summary):
        idx = self._idx
        self._list[idx] = TodoItem(summary)
        self._idx = self._idx + 1
        return idx
    def lookup(self, idx):
        if idx not in self._list:
            return None
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

def convertDict(item_map):
    result_map = {}
    for k, v in item_map.items():
        result_map[k] = v.json_dict()
    return result_map

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
    return (json.dumps(convertDict(list.open_items())), {"Content-Type": "application/json"})

@app.route("/complete")
def complete_items():
    return (json.dumps(convertDict(list.complete_items())), {"Content-Type": "application/json"})

@app.route("/abandoned")
def abandoned_items():
    return (json.dumps(convertDict(list.abandoned_items())), {"Content-Type": "application/json"})

@app.route("/pending")
def pending_items():
    return (json.dumps(convertDict(list.todo_items())), {"Content-Type": "application/json"})

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

@app.route("/<int:item_id>", methods=['GET','PUT','DELETE'])
def item(item_id):
    if request.method == 'GET':
        return get_item(item_id)
    elif request.method == 'PUT':
        return update_item(item_id,request.get_json(force = True))
    elif request.method == 'DELETE':
        return remove_item(item_id)

def get_item(item_id):
    item = list.lookup(item_id)
    if item is None:
        return ("no such item", 404, {})
    return (json.dumps(item.json_dict()), {"Content-Type": "application/json"})

def update_item(item_id, item_map):
    item = list.lookup(item_id)
    if item is None:
        return ("no such item", 404, {})
    if "status" in item_map:
        parsed = TodoStatus.parse(item_map["status"])
        if parsed is None:
            return ("invalid status", 400, {})
        item.set_status(parsed)
    if "summary" in item_map:
        item.set_summary(item_map["summary"])
    return (json.dumps(item.json_dict()), {"Content-Type": "application/json"})

def remove_item(item_id):
    list.remove_item(item_id)
    return ("",200,{})
