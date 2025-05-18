cmake_minimum_required(VERSION 3.12)
project(cache_writer)

set(CMAKE_CXX_STANDARD 17)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)
find_package(SQLite3 REQUIRED)

pybind11_add_module(cache_writer cache_writer.cpp)
target_link_libraries(cache_writer PRIVATE SQLite::SQLite3)