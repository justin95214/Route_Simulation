import logging
import inspect
import log_package as lp

#log 설정
logger = lp.log_setting(logging)

def autolog():
    "Automatically log the current function details."
    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logger.debug("%s: %s in %s:%i" % (
        "SUCCESS",
        func.co_name,
        func.co_filename,
        func.co_firstlineno
    ))

def autolog_info():
    "Automatically log the current function details."
    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logger.info("%s: %s in %s:%i" % (
        "SUCCESS",
        func.co_name,
        func.co_filename,
        func.co_firstlineno
    ))

def error_autolog():
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logger.error("%s: %s in %s:%i" % (
        "ERROR",
        func.co_name,
        func.co_filename,
        func.co_firstlineno
    ))
    send_alert_email(func.co_name)

def error_autolog_big_alert():
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logger.error("%s: %s in %s:%i" % (
        "ERROR",
        func.co_name,
        func.co_filename,
        func.co_firstlineno
    ))

