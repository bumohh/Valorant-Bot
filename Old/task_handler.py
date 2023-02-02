import asyncio
import logging

class TaskHandler():
    currentTask : asyncio.Task
    
    def __init__(self, task : asyncio.Task = None):
        self.currentTaskName = task

    def startNewTask(self, newTask : asyncio.Task):
        logging.debug("cancelling current task")
        self.currentTask.cancel()
        logging.debug("starting new task")
        self.currentTask = newTask
        
    def endTask(self):
        logging.debug("ending current task")
        self.currentTask.cancel()