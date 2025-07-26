cmake_minimum_required(VERSION 3.14)
project(dnatool VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if (CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
  message(FATAL_ERROR
    "Please do out-of-source builds:\n"
    "  mkdir build && cd build && cmake ..")
endif()

# ─── Main executable ──────────────────────────────────────────────────────────

# Gather all .cpp files, excluding web_api.cpp if present
file(GLOB_RECURSE DNATOOL_SOURCES
    ${PROJECT_SOURCE_DIR}/src/*.cpp
)
list(FILTER DNATOOL_SOURCES EXCLUDE REGEX "web_api\\.cpp$")

# Define the CLI tool
add_executable(dnatool ${DNATOOL_SOURCES})

# Make sure our own headers in include/ are found
target_include_directories(dnatool
    PRIVATE ${PROJECT_SOURCE_DIR}/include
)

# No external libraries to find/link now (json.hpp is vendored)

# ─── (No tests target) ─────────────────────────────────────────────────────────
# Tests have been skipped per your request.
