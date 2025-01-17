from enum import Enum
import inspect
import os
import time
from typing import Any, Callable

class level(Enum):
    debug = 10
    info = 20
    warning = 30
    error = 40

class Logger:
    def __init__(self, filename: str | None = None, *, print: Callable[[Any], Any] = print, level: level = level.warning) -> None:
        """
        filename: 写入日志文件的位置, 留空则不写入
        print: 用于打印日志的函数, 留空则使用默认的print来打印日志
        level: 日志等级, 默认为WARNING
        """
        self.filename = filename
        self.print = print
        self.log_level = level

    def _write_file(self, level: level, msg: Any):
        if not self.filename is None:
            stack = inspect.stack()
            stack.reverse()
            stack_str: str = ''
            for i in stack[:-3]:
                stack_str += f'[{os.path.basename(i[1]).replace('.py', '')}/{i[2] if i[3] == '<module>' else i[3]}]'
            with open(self.filename, 'ab') as f:
                write = f'[{time.strftime("%Y_%m_%d_%H-%M-%S", time.localtime())}][{level.name.upper()}]{stack_str}{msg}\n'
                try:
                    bwrite = write.encode('gbk')
                except UnicodeEncodeError:
                    bwrite = write.encode()
                f.write(bwrite)

    def _print_log(self, level: level, *args: Any):
        if len(args) == 1:
            args = args[0]
        if level.value >= self.log_level.value:
            self.print(args)

    def debug(self, *args: Any):
        if len(args) == 1:
            args = args[0]
        self._print_log(level.debug, args)
        self._write_file(level.debug, args)

    def info(self, *args: Any):
        if len(args) == 1:
            args = args[0]
        self._print_log(level.info, args)
        self._write_file(level.info, args)
        
    def warning(self, *args: Any):
        if len(args) == 1:
            args = args[0]
        self._print_log(level.warning, args)
        self._write_file(level.warning, args)
    
    def error(self, *args: Any):
        if len(args) == 1:
            args = args[0]
        self._print_log(level.error, args)
        self._write_file(level.warning, args)

logger = None

class NeedConfigFirst(Exception):
    def __init__(self) -> None:
        super().__init__('You must use set_config() or set_logger_class() to initialize first!')

def debug(*args: Any):
    if len(args) == 1:
        args = args[0]
    if not logger is None:
        logger.debug(args)
    else:
        raise NeedConfigFirst

def info(*args: Any):
    if len(args) == 1:
        args = args[0]
    if not logger is None:
        logger.info(args)
    else:
        raise NeedConfigFirst

def warning(*args: Any):
    if len(args) == 1:
        args = args[0]
    if not logger is None:
        logger.warning(args)
    else:
        raise NeedConfigFirst

def error(*args: Any):
    if len(args) == 1:
        args = args[0]
    if not logger is None:
        logger.error(args)
    else:
        raise NeedConfigFirst

def set_config(filename: str | None = None, *, print: Callable[[Any], Any] = print, level: level = level.warning):
    """
    设置(or初始化)Logger
    filename: 写入日志文件的位置, 留空则不写入
    print: 用于打印日志的函数, 留空则使用默认的print来打印日志
    level: 日志等级, 默认为WARNING
    """
    global logger
    logger = Logger(filename=filename, print=print, level=level)

def set_logger_class(klass: Logger):
    global logger
    logger = klass