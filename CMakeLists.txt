cmake_minimum_required(VERSION 2.8.9)

project(CISC472_SpineSegmentation)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/CISC472_SpineSegmentation")
set(EXTENSION_CATEGORY "CISC472")
set(EXTENSION_CONTRIBUTORS "Justin Gerolami (Queen's University)")
set(EXTENSION_DESCRIPTION "This project is part of CISC 472. This project deals with segmenting spine CT scans of children with scoliosis.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/CISC472_SpineSegmentation.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/CISC472_SpineSegmentation/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SpineSegmentation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
