cmake_minimum_required(VERSION 3.17)

project("register-loads-stores")

add_compile_definitions(SHOW_RESULTS)

add_library(register_loads_stores SHARED "register_loads_stores.cpp")
find_package(DynamoRIO)
if (NOT DynamoRIO_FOUND)
    message(FATAL_ERROR "DynamoRIO package required to build")
endif(NOT DynamoRIO_FOUND)
configure_DynamoRIO_client(register_loads_stores)
use_DynamoRIO_extension(register_loads_stores drmgr)
use_DynamoRIO_extension(register_loads_stores drutil)
use_DynamoRIO_extension(register_loads_stores drx)
use_DynamoRIO_extension(register_loads_stores droption)
