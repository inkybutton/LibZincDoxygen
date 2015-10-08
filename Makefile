html: 
	rm -rf .working
	cp -r zinc .working
	cp api_2_api++_doc.py .working
	cp -r libzinc_doxgen_script .working
	cd .working; python api_2_api++_doc.py
	cd .working/libzinc_doxgen_script; doxygen cpp_comments.doxygen
	cp -r .working/libzinc_doxgen_script/libzinc_dox_output/html build

