cmake_minimum_required(VERSION 3.13.4)

project(UnitySlicerPlugin)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/UnitySlicerPlugin")
set(EXTENSION_CATEGORY "UnitySlicerPlugin")
set(EXTENSION_CONTRIBUTORS "Lihaowei (Tsinghua University)")
set(EXTENSION_DESCRIPTION "This is an UnitySlicerPlugin")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/UnitySlicerPlugin.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/UnitySlicerPlugin/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(CollborativeAREVDGuiding)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
