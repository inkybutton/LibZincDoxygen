LibZincDoxygen
===============

Use this script provide to generate C++ header with commets and doxygen page.

Instructions:

1. Copy api_2_api++_doc.py and libzinc_doxgen_script folder into your libZinc directory.

2. Run the following command "python api_2_api++_doc.py"

3. Navigate into the libzinc_doxgen_script folder

4. Run the following command "doxygen cpp_comments.doxygen"

5. A new "libzinc_dox_output/html/index.html" file should now be created, browse this file using your favourite browser for the created libZinc-doxygen page.

6. To update the documentations, remove all hpp files in "libzinc_doxgen_script/auto_comments_output folder" and repeats step 2 to 5.