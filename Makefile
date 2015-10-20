html: clean sync
	cp -r zinc .working
	cp api_2_api++_doc.py .working
	cp -r libzinc_doxgen_script .working
	cd .working; python api_2_api++_doc.py
	cd .working/libzinc_doxgen_script; doxygen cpp_comments.doxygen
	mkdir -p build/zinc-apidoc/latest/
	cp -r .working/libzinc_doxgen_script/libzinc_dox_output/html/* build/zinc-apidoc/latest

sync:
	git submodule update --recursive --remote

clean:
	rm -rf .working
	rm -rf build

